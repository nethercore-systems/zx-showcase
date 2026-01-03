"""Blender utilities for mesh generation.

Provides consistent GLB export and scene management.
"""

import bpy
from pathlib import Path


def clear_scene():
    """Remove all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def export_glb(output_path: str):
    """Export scene to GLB format.

    Args:
        output_path: Path to output .glb file
    """
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Export to GLB with proper settings
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_texcoords=True,
        export_normals=True,
        export_materials='EXPORT',
        export_colors=True,
        use_selection=False,
        export_apply=True,
    )


def apply_modifiers(obj):
    """Apply all modifiers to an object."""
    bpy.context.view_layer.objects.active = obj
    for modifier in obj.modifiers:
        try:
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        except RuntimeError:
            # Some modifiers can't be applied, skip them
            pass
