#!/usr/bin/env python3
"""Generate wall with window cutout mesh.

Output: ../../generated/meshes/wall_window.glb

1x1 unit wall tile with window opening. Dark industrial aesthetic.
"""
import bpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from bpy_utils import setup_scene, export_glb, get_output_dir, create_dark_industrial_material

OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated" / "meshes"
ASSET_NAME = "wall_window"


def generate():
    """Generate wall with window cutout."""
    setup_scene()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Base wall
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
    wall = bpy.context.active_object
    wall.name = ASSET_NAME
    wall.scale = (1, 0.1, 1)
    bpy.ops.object.transform_apply(scale=True)

    # Window cutout
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.6))
    window = bpy.context.active_object
    window.scale = (0.6, 0.2, 0.4)
    bpy.ops.object.transform_apply(scale=True)

    # Boolean
    mod = wall.modifiers.new(name='Window', type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = window
    bpy.ops.object.modifier_apply(modifier='Window')
    bpy.data.objects.remove(window)

    mat = create_dark_industrial_material(f"{ASSET_NAME}_mat")
    wall.data.materials.append(mat)

    output_path = OUTPUT_DIR / f"{ASSET_NAME}.glb"
    export_glb(wall, output_path)
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    generate()
