# Step 1 - First steps

Let's get started with a minimal input file.

!listing modules/tensor_mechanics/tutorials/introduction/step01.i

## Input file

### `GlobalParams`

In the `[GlobalParams]` we set a default value for the `displacements`
parameters. That way we do not have to specify it explicitly in the multiple
blocks below that all need this parameter set.

### `Mesh`

We create a simple regular orthogonal mesh block using the
[`GeneratedMeshGenerator`](GeneratedMeshGenerator.md). All subblocks under
`[Mesh]` are the so called [*MeshGenerators*](meshgenerators/MeshGenerator.md).
They can be chained together and MOOSE provides a multitude of generators to
create and modify meshes. Later on we will see how to create a second block and
combine it into a two block mesh. A commonly used MeshGenerator is the
[`FileMeshGenerator`](FileMeshGenerator.md), it is used to load a mesh file
generated by third party software like Cubit of Gmsh (or sometimes even meshes
generated by MOOSE). MOOSE provides a shorthand for the `FileMeshGenerator`
through the [!param](/Mesh/FileMesh/file) parameter inside `[Mesh]`, e.g.

```
[Mesh]
  file = pressure_vessel.e
[]
```

MOOSE supports a [variety of mesh file formats](FileMeshGenerator.md); most
commonly used is the Exodus II format.

### TensorMechanics `Master` Action

The third top level block has a path with three components in the title. You can
think of the MOOSE input file block structure like a directory.
[The `Master` action](Modules/TensorMechanics/Master/index.md) is nested
under `Modules` and `TensorMechanics`. A MOOSE Action is a convenience object
that can setup multiple aspects of a simulation for the user, resulting in a
more compact syntax. Actions can also enforce consistency in the simulation
definition. In this simple example the action will create the displacement
variables (as specified by the `GlobalParams/displacements` parameter). The
action will automatically determine if second order shape functions are needed,
based on the order of the mesh in the simulation. Furthermore the appropriate
*strain calculator* will be added for the chosen coordinate system
(axisymmetrix, spherical, cartesian).

Check the [master action documentation](Modules/TensorMechanics/Master/index.md)
for a full run-down of all objects it creates.

### `Materials`

The two subblocks under [`[Materials]`](Materials/index.md) define an
[isotropic elasticity tensor](ComputeIsotropicElasticityTensor.md) and a
[linear elastic stress calculator](ComputeLinearElasticStress.md). Neither
object is block restricted (using the `block` parameter), so they apply to the
entire simulation domain.

### `Executioner`

In the [`[Executioner]`](Executioner/index.md) block all parameters relevant to the sole of the current
problem are set. [`type = Transient`](Transient.md) selects a time-dependent simulation (as
opposed to [`type = Steady`](Steady.md)). We chose to run for five simulation steps; with a
timestep of `1`.

### `Outputs`

We use the `exodus = true` shorthand to setup an output object of type `Exodus` to write
an Exodus II mesh and solution file to the disk. You can visualize these outputs using
[Paraview](https://www.paraview.org).

## Questions

### Units

A question that comes up often is "What units does MOOSE use?".

>  Look through the input file and try to identify places where units might be
>  relevant.

[Click here for the answer.](tensor_mechanics/tutorials/introduction/answer01a.md)

### Expected outcome

> Before you run this first input file take a moment to think about what you
> expect to happen.

[Click here for the answer.](tensor_mechanics/tutorials/introduction/answer01b.md)

Once you've answered the questions and run the first example it is time to move
on to a slightly more complex scenario in [Step 2](tensor_mechanics/tutorials/introduction/step02.md).
