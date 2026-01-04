#!/usr/bin/env python3
"""Generate grate floor tile mesh.

Output: ../../generated/meshes/floor_grate.glb

1x1 unit floor tile with holes. Dark industrial aesthetic.
"""
import bpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from bpy_utils import setup_scene, export_glb, get_output_dir, create_dark_industrial_material

OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated" / "meshes"
ASSET_NAME = "floor_grate"


def generate():
    """Generate grate floor tile."""
    setup_scene()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = ASSET_NAME

    # Subdivide
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=4)

    # Inset for grate pattern
    bpy.ops.mesh.inset(thickness=0.05, depth=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

    mat = create_dark_industrial_material(f"{ASSET_NAME}_mat")
    floor.data.materials.append(mat)

    output_path = OUTPUT_DIR / f"{ASSET_NAME}.glb"
    export_glb(floor, output_path)
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    generate()
