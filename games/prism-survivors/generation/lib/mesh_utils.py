"""Shared mesh building utilities for PRISM SURVIVORS.

Common primitives and helpers used across all asset generators.
"""

import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

try:
    import bpy
    import bmesh
    from mathutils import Vector, Matrix
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False
    bpy = None
    bmesh = None


@dataclass
class MeshSpec:
    """Base specification for any mesh asset."""
    name: str
    color_primary: Tuple[float, float, float] = (0.5, 0.5, 0.5)
    color_accent: Tuple[float, float, float] = (0.8, 0.8, 0.8)
    color_glow: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    glow_strength: float = 1.0


if BLENDER_AVAILABLE:

    def clear_scene():
        """Remove all mesh objects from scene."""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

        # Clean orphan data
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)

    def create_prism(name: str, radius: float, height: float,
                     segments: int = 6, location: Tuple[float, float, float] = (0, 0, 0)):
        """Create a prismatic cylinder (hexagonal default)."""
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=segments,
            radius=radius,
            depth=height,
            location=location
        )
        obj = bpy.context.active_object
        obj.name = name
        return obj

    def create_beveled_box(name: str, size: Tuple[float, float, float],
                           bevel_width: float = 0.02, bevel_segments: int = 1,
                           location: Tuple[float, float, float] = (0, 0, 0)):
        """Create a box with beveled edges for prismatic look."""
        bpy.ops.mesh.primitive_cube_add(size=1, location=location)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = size
        bpy.ops.object.transform_apply(scale=True)

        if bevel_width > 0:
            bevel = obj.modifiers.new(name='Bevel', type='BEVEL')
            bevel.width = bevel_width
            bevel.segments = bevel_segments
            bevel.limit_method = 'ANGLE'
            bevel.angle_limit = math.radians(30)
            bpy.ops.object.modifier_apply(modifier='Bevel')

        return obj

    def create_spike(name: str, base_radius: float, height: float,
                     segments: int = 6, location: Tuple[float, float, float] = (0, 0, 0)):
        """Create an upward-pointing spike (cone)."""
        bpy.ops.mesh.primitive_cone_add(
            vertices=segments,
            radius1=base_radius,
            radius2=0,
            depth=height,
            location=location
        )
        obj = bpy.context.active_object
        obj.name = name
        return obj

    def create_sphere(name: str, radius: float, segments: int = 8,
                      location: Tuple[float, float, float] = (0, 0, 0)):
        """Create a low-poly sphere (ico subdivision)."""
        subdivisions = max(1, min(3, segments // 4))
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=subdivisions,
            radius=radius,
            location=location
        )
        obj = bpy.context.active_object
        obj.name = name
        return obj

    def create_torus(name: str, major_radius: float, minor_radius: float,
                     major_segments: int = 16, minor_segments: int = 8,
                     location: Tuple[float, float, float] = (0, 0, 0)):
        """Create a torus (ring)."""
        bpy.ops.mesh.primitive_torus_add(
            major_segments=major_segments,
            minor_segments=minor_segments,
            major_radius=major_radius,
            minor_radius=minor_radius,
            location=location
        )
        obj = bpy.context.active_object
        obj.name = name
        return obj

    def join_objects(objects: List, name: str):
        """Join multiple objects into one mesh."""
        if not objects:
            return None

        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        bpy.ops.object.join()

        result = bpy.context.active_object
        result.name = name
        return result

    def apply_transform(obj, location=True, rotation=True, scale=True):
        """Apply transformations to mesh data."""
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)

    def set_origin_to_bottom(obj):
        """Set object origin to bottom center."""
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

        # Move origin to bottom
        bbox = obj.bound_box
        min_z = min(v[2] for v in bbox)
        obj.location.z -= min_z

    def get_tri_count(obj) -> int:
        """Get triangle count for mesh object."""
        if obj.type != 'MESH':
            return 0

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        count = len(bm.faces)
        bm.free()
        return count

    def export_glb(obj, filepath: str):
        """Export object as GLB."""
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.export_scene.gltf(
            filepath=filepath,
            export_format='GLB',
            use_selection=True,
            export_apply=True
        )

    def create_material(name: str, base_color: Tuple[float, float, float],
                        emission_color: Optional[Tuple[float, float, float]] = None,
                        emission_strength: float = 0.0,
                        metallic: float = 0.0, roughness: float = 0.5):
        """Create a PBR material."""
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Clear default nodes
        nodes.clear()

        # Create shader nodes
        output = nodes.new('ShaderNodeOutputMaterial')
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')

        # Set values
        bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness

        if emission_color and emission_strength > 0:
            bsdf.inputs['Emission Color'].default_value = (*emission_color, 1.0)
            bsdf.inputs['Emission Strength'].default_value = emission_strength

        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

        return mat

else:
    # Stub functions for non-Blender environments
    def clear_scene(): pass
    def create_prism(*args, **kwargs): return None
    def create_beveled_box(*args, **kwargs): return None
    def create_spike(*args, **kwargs): return None
    def create_sphere(*args, **kwargs): return None
    def create_torus(*args, **kwargs): return None
    def join_objects(*args, **kwargs): return None
    def apply_transform(*args, **kwargs): pass
    def set_origin_to_bottom(*args, **kwargs): pass
    def get_tri_count(*args, **kwargs): return 0
    def export_glb(*args, **kwargs): pass
    def create_material(*args, **kwargs): return None
