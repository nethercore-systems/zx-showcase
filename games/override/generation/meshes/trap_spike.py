#!/usr/bin/env python3
"""Generate spike trap mesh.

Output: ../../generated/meshes/trap_spike.glb

Retractable spike trap. 3x3 grid of spikes on base plate.
Dark industrial aesthetic.
"""
import bpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from bpy_utils import setup_scene, export_glb, get_output_dir, create_dark_industrial_material

OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated" / "meshes"
ASSET_NAME = "trap_spike"


def generate():
    """Generate spike trap."""
    setup_scene()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    parts = []

    # Base plate
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.02))
    base = bpy.context.active_object
    base.name = "Base"
    base.scale = (1, 1, 0.02)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(base)

    # Spikes (3x3 grid)
    for x in [-0.3, 0, 0.3]:
        for y in [-0.3, 0, 0.3]:
            bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.08, depth=0.4, location=(x, y, 0.25))
            spike = bpy.context.active_object
            spike.name = f"Spike_{x}_{y}"
            parts.append(spike)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()

    trap = bpy.context.active_object
    trap.name = ASSET_NAME

    mat = create_dark_industrial_material(f"{ASSET_NAME}_mat")
    trap.data.materials.append(mat)

    output_path = OUTPUT_DIR / f"{ASSET_NAME}.glb"
    export_glb(trap, output_path)
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    generate()
