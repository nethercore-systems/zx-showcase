#!/usr/bin/env python3
"""Generate metal floor tile mesh.

Output: ../../generated/meshes/floor_metal.glb

1x1 unit floor tile with panel grooves. Dark industrial aesthetic.
"""
import bpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from bpy_utils import setup_scene, export_glb, get_output_dir, create_dark_industrial_material

OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated" / "meshes"
ASSET_NAME = "floor_metal"


def generate():
    """Generate metal floor tile."""
    setup_scene()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = ASSET_NAME

    # Add subdivision for detail
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=2)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Panel grooves (boolean cuts)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.02))
    groove = bpy.context.active_object
    groove.scale = (0.02, 0.9, 0.02)
    bpy.ops.object.transform_apply(scale=True)

    # Boolean modifier
    mod = floor.modifiers.new(name='Groove', type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = groove
    bpy.ops.object.modifier_apply(modifier='Groove')
    bpy.data.objects.remove(groove)

    mat = create_dark_industrial_material(f"{ASSET_NAME}_mat")
    floor.data.materials.append(mat)

    output_path = OUTPUT_DIR / f"{ASSET_NAME}.glb"
    export_glb(floor, output_path)
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    generate()
