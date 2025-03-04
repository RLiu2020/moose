#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import re, os, shutil
from Tester import Tester
from TestHarness import util

class RunApp(Tester):

    @staticmethod
    def validParams():
        params = Tester.validParams()
        params.addParam('input',              "The input file to use for this test.")
        params.addParam('test_name',          "The name of the test - populated automatically")
        params.addParam('input_switch', '-i', "The default switch used for indicating an input to the executable")
        params.addParam('errors',             ['ERROR', 'command not found', 'terminate called after throwing an instance of'], "The error messages to detect a failed run")
        params.addParam('expect_out',         "A regular expression or literal string that must occur in the input in order for the test to be considered passing (see match_literal).")
        params.addParam('match_literal', False, "Treat expect_out as a string not a regular expression.")
        params.addParam('absent_out',         "A regular expression that must be *absent* from the output for the test to pass.")
        params.addParam('should_crash', False, "Inidicates that the test is expected to crash or otherwise terminate early")
        params.addParam('executable_pattern', "A test that only runs if the executable name matches the given pattern")
        params.addParam('delete_output_before_running',  True, "Delete pre-existing output files before running test. Only set to False if you know what you're doing!")
        params.addParam('delete_output_folders', True, "Delete output folders before running")

        # RunApp can also run arbitrary commands. If the "command" parameter is supplied
        # it'll be used in lieu of building up the command automatically
        params.addParam('command',            "The command line to execute for this test.")

        # Parallel/Thread testing
        params.addParam('max_parallel', 1000, "Maximum number of MPI processes this test can be run with      (Default: 1000)")
        params.addParam('min_parallel',    1, "Minimum number of MPI processes that this test can be run with (Default: 1)")
        params.addParam('max_threads',    16, "Max number of threads (Default: 16)")
        params.addParam('min_threads',     1, "Min number of threads (Default: 1)")
        params.addParam('redirect_output',  False, "Redirect stdout to files. Neccessary when expecting an error when using parallel options")

        params.addParam('allow_warnings',   True, "Whether or not warnings are allowed.  If this is False then a warning will be treated as an error.  Can be globally overridden by setting 'allow_warnings = False' in the testroot file.");
        params.addParam('allow_unused',   True, "Whether or not unused parameters are allowed in the input file.  Can be globally overridden by setting 'allow_unused = False' in the testroot file.");
        params.addParam('allow_override', True, "Whether or not overriding a parameter/block in the input file generates an error.  Can be globally overridden by setting 'allow_override = False' in the testroot file.");
        params.addParam('allow_deprecated', True, "Whether or not deprecated warnings are allowed.  Setting to False will cause deprecation warnings to be treated as test failures.  We do NOT recommend you globally set this permanently to False!  Deprecations are a part of the normal development flow and _SHOULD_ be allowed!")
        params.addParam('no_error_deprecated', False, "Don't pass --error-deprecated on the command line even when running the TestHarness with --error-deprecated")

        # Valgrind
        params.addParam('valgrind', 'NORMAL', "Set to (NONE, NORMAL, HEAVY) to determine which configurations where valgrind will run.")

        return params

    def __init__(self, name, params):
        Tester.__init__(self, name, params)
        if os.environ.get("MOOSE_MPI_COMMAND"):
            self.mpi_command = os.environ['MOOSE_MPI_COMMAND']
            self.force_mpi = True
        else:
            self.mpi_command = 'mpiexec'
            self.force_mpi = False

        # Make sure that either input or command is supplied
        if not (params.isValid('input') or params.isValid('command')):
            raise Exception('Either "input" or "command" must be supplied for a RunApp test')

    def getInputFile(self):
        if self.specs.isValid('input'):
            return self.specs['input'].strip()
        else:
            return None # Not all testers that inherit from RunApp have an input file

    def getInputFileContents(self):
        input_file = self.getInputFile()
        if input_file and os.path.exists(os.path.join(self.getTestDir(), input_file)):
            with open(os.path.join(self.getTestDir(), input_file), 'r') as f:
                input_file = f.read()
        # Test is supposed to have an input file, but we couldn't find it. Don't error on that event here, and
        # instead allow the TestHarness to continue. It will error appropriately elsewhere.
        else:
            input_file = None
        return input_file

    def checkRunnable(self, options):
        if options.enable_recover:
            if self.specs.isValid('expect_out') or self.specs.isValid('absent_out') or self.specs['should_crash'] == True:
                self.addCaveats('expect_out RECOVER')
                self.setStatus(self.skip)
                return False

        if self.specs.isValid('executable_pattern') and re.search(self.specs['executable_pattern'], self.specs['executable']) == None:
            self.addCaveats('EXECUTABLE PATTERN')
            self.setStatus(self.skip)
            return False

        if self.specs.isValid('min_threads') or self.specs.isValid('max_threads'):
            if 'NONE' in options._checks['threading'] and self.getThreads(options) > 1:
                self.addCaveats('threading_model=None')
                self.setStatus(self.skip)
                return False

        return True

    def getThreads(self, options):
        #Set number of threads to be used lower bound
        nthreads = max(options.nthreads, int(self.specs['min_threads']))
        #Set number of threads to be used upper bound
        nthreads = min(nthreads, int(self.specs['max_threads']))

        if nthreads > options.nthreads:
            self.addCaveats('min_threads=' + str(nthreads))
        elif nthreads < options.nthreads:
            self.addCaveats('max_threads=' + str(nthreads))

        return nthreads

    def getProcs(self, options):
        if options.parallel == None:
            default_ncpus = 1
        else:
            default_ncpus = options.parallel

        # Raise the floor
        ncpus = max(default_ncpus, int(self.specs['min_parallel']))
        # Lower the ceiling
        ncpus = min(ncpus, int(self.specs['max_parallel']))

        if ncpus > default_ncpus:
            self.addCaveats('min_cpus=' + str(ncpus))
        elif ncpus < default_ncpus:
            self.addCaveats('max_cpus=' + str(ncpus))

        return ncpus

    def getCommand(self, options):
        specs = self.specs

        # Just return an arbitrary command if one is supplied
        if specs.isValid('command'):
            return os.path.join('%s%s:%s; %s %s' % ('PATH=',
                                                    specs['test_dir'],
                                                    os.getenv('PATH'),
                                                    specs['command'],
                                                    ' '.join(specs['cli_args'])))

        # Create the additional command line arguments list
        cli_args = list(specs['cli_args'])

        # Check for built application
        if shutil.which(specs['executable']) is None:
            self.setStatus(self.fail, 'Application not found')
            return ''

        if (options.parallel_mesh or options.distributed_mesh) and ('--parallel-mesh' not in cli_args or '--distributed-mesh' not in cli_args):
            # The user has passed the parallel-mesh option to the test harness
            # and it is NOT supplied already in the cli-args option
            cli_args.append('--distributed-mesh')

        if '--error' not in cli_args and (not specs["allow_warnings"] or options.error):
            cli_args.append('--error')

        if '--error-unused' not in cli_args and (not specs["allow_unused"] or options.error_unused):
            cli_args.append('--error-unused')

        if '--error-override' not in cli_args and not specs["allow_override"]:
            cli_args.append('--error-override')

        if '--error-deprecated' not in cli_args and not specs["no_error_deprecated"] and (not specs["allow_deprecated"] or options.error_deprecated):
            cli_args.append('--error-deprecated')

        if self.getCheckInput():
            cli_args.append('--check-input')

        if options.timing and specs["timing"]:
            cli_args.append('--timing')
            cli_args.append('Outputs/perf_graph=true')

        if options.colored == False:
            cli_args.append('--color off')

        if options.cli_args:
            cli_args.insert(0, options.cli_args)

        if options.scaling and specs['scale_refine'] > 0:
            cli_args.insert(0, ' -r ' + str(specs['scale_refine']))

        # The test harness should never use GDB backtraces: they don't
        # work well when dozens of expect_err jobs run at the same time.
        cli_args.append('--no-gdb-backtrace')

        # Get the number of processors and threads the Tester requires
        ncpus = self.getProcs(options)
        nthreads = self.getThreads(options)

        if specs['redirect_output'] and ncpus > 1:
            cli_args.append('--keep-cout --redirect-output ' + self.name())

        command = specs['executable'] + ' ' + specs['input_switch'] + ' ' + specs['input'] + ' ' + ' '.join(cli_args)
        if options.valgrind_mode.upper() == specs['valgrind'].upper() or options.valgrind_mode.upper() == 'HEAVY' and specs['valgrind'].upper() == 'NORMAL':
            command = 'valgrind --suppressions=' + os.path.join(specs['moose_dir'], 'python', 'TestHarness', 'suppressions', 'errors.supp') + ' --leak-check=full --tool=memcheck --dsymutil=yes --track-origins=yes --demangle=yes -v ' + command
        elif nthreads > 1:
            command = command + ' --n-threads=' + str(nthreads)

        if self.force_mpi or options.parallel or ncpus > 1:
            command = self.mpi_command + ' -n ' + str(ncpus) + ' ' + command

        return command

    def processResults(self, moose_dir, options, output):
        return output
