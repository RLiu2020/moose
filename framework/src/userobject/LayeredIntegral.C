//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#include "LayeredIntegral.h"

#include "libmesh/mesh_tools.h"

registerMooseObject("MooseApp", LayeredIntegral);

defineLegacyParams(LayeredIntegral);

InputParameters
LayeredIntegral::validParams()
{
  InputParameters params = ElementIntegralVariableUserObject::validParams();
  params += LayeredBase::validParams();
  return params;
}

LayeredIntegral::LayeredIntegral(const InputParameters & parameters)
  : ElementIntegralVariableUserObject(parameters), LayeredBase(parameters)
{
}

void
LayeredIntegral::initialize()
{
  ElementIntegralVariableUserObject::initialize();
  LayeredBase::initialize();
}

void
LayeredIntegral::execute()
{
  Real integral_value = computeIntegral();

  unsigned int layer = getLayer(_current_elem->vertex_average());

  setLayerValue(layer, getLayerValue(layer) + integral_value);
}

void
LayeredIntegral::finalize()
{
  LayeredBase::finalize();
}

void
LayeredIntegral::threadJoin(const UserObject & y)
{
  ElementIntegralVariableUserObject::threadJoin(y);
  LayeredBase::threadJoin(y);
}
