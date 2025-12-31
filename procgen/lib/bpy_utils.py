#!/usr/bin/env python3
"""Blender Python utilities for mesh generation.

Aligned with zx-procgen generator-patterns skill.

Requires: Blender 3.0+ (run via `blender --background --python script.py`)
"""
from pathlib import Path
from typing import List, Tuple, Optional

try:
    import bpy
    HAS_BPY = True
except ImportError:
    HAS_BPY = False


def clear_scene():
    """Remove all objects from the scene."""
    if not HAS_BPY:
        return

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Clear orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def apply_modifiers(obj):
    """Apply all modifiers to an object."""
    if not HAS_BPY:
        return

    bpy.context.view_layer.objects.active = obj
    for mod in obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=mod.name)


def apply_transforms(obj):
    """Apply location, rotation, and scale transforms."""
    if not HAS_BPY:
        return

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def set_origin_to_bottom(obj):
    """Set object origin to the bottom center."""
    if not HAS_BPY:
        return

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    # Move origin to bottom
    obj.location.z = obj.dimensions.z / 2


def set_origin_to_center(obj):
    """Set object origin to the center."""
    if not HAS_BPY:
        return

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')


def auto_uv_project(obj):
    """Apply automatic UV projection (smart UV project)."""
    if not HAS_BPY:
        return

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')


def box_uv_project(obj):
    """Apply box UV projection."""
    if not HAS_BPY:
        return

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project(cube_size=1.0)
    bpy.ops.object.mode_set(mode='OBJECT')


def cylinder_uv_project(obj):
    """Apply cylindrical UV projection."""
    if not HAS_BPY:
        return

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cylinder_project(direction='ALIGN_TO_OBJECT')
    bpy.ops.object.mode_set(mode='OBJECT')


def recalculate_normals(obj):
    """Recalculate normals to face outward."""
    if not HAS_BPY:
        return

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')


def triangulate_mesh(obj):
    """Convert all faces to triangles."""
    if not HAS_BPY:
        return

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris()
    bpy.ops.object.mode_set(mode='OBJECT')


def get_poly_count(obj) -> int:
    """Get triangle count for an object."""
    if not HAS_BPY:
        return 0
    return len(obj.data.polygons)


def get_vertex_count(obj) -> int:
    """Get vertex count for an object."""
    if not HAS_BPY:
        return 0
    return len(obj.data.vertices)


def decimate_to_target(obj, target_tris: int):
    """Add decimate modifier to reduce to target triangle count."""
    if not HAS_BPY:
        return

    current = get_poly_count(obj)
    if current <= target_tris:
        return

    ratio = target_tris / current
    mod = obj.modifiers.new("Decimate", 'DECIMATE')
    mod.ratio = ratio
    apply_modifiers(obj)


# === Modifiers ===

def add_bevel(obj, width: float = 0.02, segments: int = 2):
    """Add bevel modifier for rounded edges."""
    if not HAS_BPY:
        return None

    mod = obj.modifiers.new("Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    return mod


def add_solidify(obj, thickness: float = 0.1):
    """Add solidify modifier for thickness."""
    if not HAS_BPY:
        return None

    mod = obj.modifiers.new("Solidify", 'SOLIDIFY')
    mod.thickness = thickness
    return mod


def add_mirror(obj, axis: str = 'X'):
    """Add mirror modifier."""
    if not HAS_BPY:
        return None

    mod = obj.modifiers.new("Mirror", 'MIRROR')
    mod.use_axis = [axis == 'X', axis == 'Y', axis == 'Z']
    return mod


def add_array(obj, count: int, offset: Tuple[float, float, float] = (1, 0, 0)):
    """Add array modifier."""
    if not HAS_BPY:
        return None

    mod = obj.modifiers.new("Array", 'ARRAY')
    mod.count = count
    mod.use_relative_offset = True
    mod.relative_offset_displace = offset
    return mod


def add_subdivision(obj, levels: int = 1, render_levels: int = 2):
    """Add subdivision surface modifier."""
    if not HAS_BPY:
        return None

    mod = obj.modifiers.new("Subdivision", 'SUBSURF')
    mod.levels = levels
    mod.render_levels = render_levels
    return mod


def add_displace(obj, strength: float = 0.1, texture=None):
    """Add displacement modifier."""
    if not HAS_BPY:
        return None

    mod = obj.modifiers.new("Displace", 'DISPLACE')
    mod.strength = strength
    if texture:
        mod.texture = texture
    return mod


# === Object Operations ===

def join_objects(objects: List):
    """Join multiple objects into one."""
    if not HAS_BPY or not objects:
        return None

    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    return objects[0]


def duplicate_object(obj, linked: bool = False):
    """Duplicate an object."""
    if not HAS_BPY:
        return None

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.duplicate(linked=linked)
    return bpy.context.active_object


def delete_object(obj):
    """Delete an object."""
    if not HAS_BPY:
        return

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.delete()


# === Materials ===

def create_material(name: str, color: Tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0)):
    """Create a basic material with given color."""
    if not HAS_BPY:
        return None

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
    return mat


def assign_material(obj, material):
    """Assign a material to an object."""
    if not HAS_BPY:
        return

    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def set_vertex_colors(obj, color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)):
    """Set vertex colors for an object."""
    if not HAS_BPY:
        return

    if not obj.data.vertex_colors:
        obj.data.vertex_colors.new()

    color_layer = obj.data.vertex_colors.active
    for poly in obj.data.polygons:
        for loop_idx in poly.loop_indices:
            color_layer.data[loop_idx].color = color


# === Export ===

def export_glb(filepath: str, selected_only: bool = False):
    """Export scene to GLB format."""
    if not HAS_BPY:
        return

    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format='GLB',
        use_selection=selected_only,
        export_apply=True,
        export_yup=True,
    )
    print(f"Exported: {path}")


def export_obj(filepath: str, selected_only: bool = False):
    """Export scene to OBJ format."""
    if not HAS_BPY:
        return

    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.obj_export(
        filepath=str(path),
        export_selected_objects=selected_only,
        apply_modifiers=True,
        export_uv=True,
        export_normals=True,
    )
    print(f"Exported: {path}")


# === Post-Processing ===

def post_process(obj):
    """Standard post-processing pipeline for game-ready mesh."""
    if not HAS_BPY:
        return

    apply_modifiers(obj)
    apply_transforms(obj)
    recalculate_normals(obj)
    auto_uv_project(obj)
    triangulate_mesh(obj)


def optimize_for_zx(obj, max_tris: int = 1000):
    """Optimize mesh for ZX console limits."""
    if not HAS_BPY:
        return

    # Apply and prepare
    apply_modifiers(obj)
    apply_transforms(obj)

    # Decimate if over budget
    decimate_to_target(obj, max_tris)

    # Finalize
    recalculate_normals(obj)
    auto_uv_project(obj)
    triangulate_mesh(obj)
