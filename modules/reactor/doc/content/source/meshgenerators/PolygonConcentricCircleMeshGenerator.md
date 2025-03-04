# PolygonConcentricCircleMeshGenerator

!syntax description /Mesh/PolygonConcentricCircleMeshGenerator

## Overview

!media media/meshgenerators/polycc.png
      style=display: block;margin-left:auto;margin-right:auto;width:40%;
      id=sample
      caption=A typical mesh generated by this `PolygonConcentricCircleMeshGenerator` object.

The `PolygonConcentricCircleMeshGenerator` object generates a 2D mesh for concentric circles with a regular polygon enclosure with or without external ducts. A typical mesh generated by this object is shown in [Figure 1](#sample). Polygons with 3 or more sides (e.g. triangle, square, pentagon, hexagon,...) can be meshed using this object. The central concentric circular regions (termed `rings`) as well as the peripheral polygonal regions (termed `ducts`) are optional (see [Figure 2](#schematic)). The region excluding any rings and ducts is termed the `background` region.

## Geometry Information

The most fundamental geometry parameters that are needed by this object is:

- [!param](/Mesh/PolygonConcentricCircleMeshGenerator/num_sides): the number of sides of the polygon enclosure;
- [!param](/Mesh/PolygonConcentricCircleMeshGenerator/polygon_size_style): the style in which the parameter [!param](/Mesh/PolygonConcentricCircleMeshGenerator/polygon_size) will be given. This parameter can be either `apothem` (center to side distance) or `radius` (center to vertex distance).
- [!param](/Mesh/PolygonConcentricCircleMeshGenerator/polygon_size): the size of the polygon enclosure in terms of either `apothem` or `radius` (selected by another parameter, [!param](/Mesh/PolygonConcentricCircleMeshGenerator/polygon_size_style)

!media media/meshgenerators/polygon.png
      style=display: block;margin-left:auto;margin-right:auto;width:40%;
      id=schematic
      caption=A schematic drawing showing the different regions that can be generated by this `PolygonConcentricCircleMeshGenerator` object.

If concentric circle regions are needed, [!param](/Mesh/PolygonConcentricCircleMeshGenerator/ring_radii) must be provided to define the outer radius of each ring. If duct regions are needed, [!param](/Mesh/PolygonConcentricCircleMeshGenerator/duct_sizes) must be provided to define the inner boundary of each duct. Similar to [!param](/Mesh/PolygonConcentricCircleMeshGenerator/polygon_size), [!param](/Mesh/PolygonConcentricCircleMeshGenerator/duct_sizes) can either be apothems or radii of the corresponding ducts, decided by [!param](/Mesh/PolygonConcentricCircleMeshGenerator/duct_sizes_style).

## Mesh Information

The parameters that are needed for meshing can be categorized into azimuthal and radial information, which determine the mesh density.

The azimuthal mesh discretization is controlled by [!param](/Mesh/PolygonConcentricCircleMeshGenerator/num_sectors_per_side), which is a vector that has the same length as [!param](/Mesh/PolygonConcentricCircleMeshGenerator/num_sides). Each element of [!param](/Mesh/PolygonConcentricCircleMeshGenerator/num_sectors_per_side) must be an even integer, which is the number of azimuthal intervals of the corresponding side. The sides are indexed counterclockwise with the upper-right polygon side being the first side as shown in [Figure 2](#schematic).

The radial mesh discretization is controlled by separate parameters for `rings`, `background` and `ducts` regions, which are [!param](/Mesh/PolygonConcentricCircleMeshGenerator/ring_intervals), [!param](/Mesh/PolygonConcentricCircleMeshGenerator/background_intervals), and [!param](/Mesh/PolygonConcentricCircleMeshGenerator/duct_intervals), respectively.

## MeshMeshData Generation

When [!param](/Mesh/PolygonConcentricCircleMeshGenerator/num_sides) is set as 6, the hexagonal meshes produced by `PolygonConcentricCircleMeshGenerator` can be used by [`PatternedHexMeshGenerator`](/PatternedHexMeshGenerator.md) to create patterned meshes. This functionality relies on a series of `MeshMetaData` generated by `PolygonConcentricCircleMeshGenerator`, including:

- `pitch_meta`, type `Real`: Provides the side-to-side distance of the hexagon generated.
- `pattern_pitch_meta`, type `Real`: Similar to `pitch_meta`. This is only used when the mesh produced here is stitched with assembly hexagon meshes generated by `PatternedHexMeshGenerator`.
- `background_intervals_meta`, type `unsigned int`: Makes the value of the input parameter [!param](/Mesh/PolygonConcentricCircleMeshGenerator/background_intervals) available to other mesh generators.
- `node_id_background_meta`, type `dof_id_type`: Records the maximum node id of the background nodes to provide a reference for node modifications.
- `max_radius_meta`, type `Real`: Provides the maximum radius of the ring regions so that `PatternedHexMeshGenerator` does not compromise the circular geometry.
- `num_sectors_per_side_meta`, type `std::vector<unsigned int>`: Makes the value of the input parameter [!param](/Mesh/PolygonConcentricCircleMeshGenerator/num_sectors_per_side) available to other mesh generators.
- `azimuthal_angle_meta`, type `std::vector<Real>`: Contains the sorted azimuthal angles of all the nodes on the external boundary.

## Other Information

By default, the mesh generated by this object contains a mixture of QUAD4 and TRI3 elements. To be specific, the central region of the mesh consists of triangular elements, whereas the rest of the mesh consists of quadrilateral elements. The users also have an option to generate a purely QUAD4 mesh by setting `quad_center_elements` as true (see [Figure 3](#TRI3_and_QUAD4)).

!media media/meshgenerators/tri_quad.png
      style=display: block;margin-left:auto;margin-right:auto;width:40%;
      id=TRI3_and_QUAD4
      caption=A schematic drawing showing the different meshing algorithms when [!param](/Mesh/PolygonConcentricCircleMeshGenerator/quad_center_elements) is set as `false` and `true`.

When `rings` regions are present, the radii of these `rings` can be auto-adjusted to preserve the meshed annular area (volume) to the true area (volume) by setting [!param](/Mesh/PolygonConcentricCircleMeshGenerator/preserve_volumes) as true.

By default, the azimuthal angles used to discretize the mesh are uniformly spaced in _angle_ on each sector of the polygon. However, uniform spacing of angles leads to non-uniform mesh intervals on the polygon external sides (unless exactly 2 sectors per side are used). However, as a uniformly spaced mesh on the polygon external boundary may facilitate mesh stitching, the user may force a uniform mesh on the polygon external boundary by setting [!param](/Mesh/PolygonConcentricCircleMeshGenerator/uniform_mesh_on_sides) as true.

The default block id numbering starts with 0 at the center region and increments by 1 for each mesh region radially outward. The user may instead set specific block id and name values to rings, background, and duct regions through the use of [!param](/Mesh/PolygonConcentricCircleMeshGenerator/ring_block_ids), [!param](/Mesh/PolygonConcentricCircleMeshGenerator/background_block_ids), [!param](/Mesh/PolygonConcentricCircleMeshGenerator/duct_block_ids), [!param](/Mesh/PolygonConcentricCircleMeshGenerator/ring_block_names), [!param](/Mesh/PolygonConcentricCircleMeshGenerator/background_block_names),  and [!param](/Mesh/PolygonConcentricCircleMeshGenerator/duct_block_names).

The user should be aware that in two cases, the central geometric region is defined as two blocks instead of one:
- When rings are not present, and [!param](/Mesh/PolygonConcentricCircleMeshGenerator/background_intervals) > 1
- When rings are present, and the first entry of [!param](/Mesh/PolygonConcentricCircleMeshGenerator/ring_radii) > 1

In both of these cases, the central geometric region will contain both blocks 0 and 1 by default. Any additional usage of block ids or name arrays will require an extra entry for the first geometric region. This extra block definition is needed to accommodate flexibility in defining the central region as either quadrilateral or triangular elements while still stitching properly to the neighboring region.

The external boundary has a default boundary id of 10000. The user may instead set specific boundary id and/or name values through the use of `external_boundary_id` and `external_boundary_name`.

## Example Syntax

!listing modules/reactor/test/tests/meshgenerators/patterned_hex_mesh_generator/patterned_pattern.i block=Mesh/hex_1

!syntax parameters /Mesh/PolygonConcentricCircleMeshGenerator

!syntax inputs /Mesh/PolygonConcentricCircleMeshGenerator

!syntax children /Mesh/PolygonConcentricCircleMeshGenerator
