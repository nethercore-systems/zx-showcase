#!/usr/bin/env python3
"""Generate closed door mesh.

Output: ../../generated/meshes/door_closed.glb

Closed sliding door. Dark industrial aesthetic.
"""
import bpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from bpy_utils import setup_scene, export_glb, get_output_dir, create_dark_industrial_material

OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated" / "meshes"
ASSET_NAME = "door_closed"


def generate():
    """Generate closed door."""
    setup_scene()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
    door = bpy.context.active_object
    door.name = ASSET_NAME
    door.scale = (0.8, 0.1, 0.95)
    bpy.ops.object.transform_apply(scale=True)

    mat = create_dark_industrial_material(f"{ASSET_NAME}_mat")
    door.data.materials.append(mat)

    output_path = OUTPUT_DIR / f"{ASSET_NAME}.glb"
    export_glb(door, output_path)
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    generate()
