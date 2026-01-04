#!/usr/bin/env python3
"""Generate Runner character mesh.

Output: ../../generated/meshes/runner.glb

Runner: Humanoid player character (3 instances in multiplayer).
Dark industrial sci-fi aesthetic. 800-1000 tris.
"""
import bpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from bpy_utils import setup_scene, export_glb, get_output_dir, create_dark_industrial_material

OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated" / "meshes"
ASSET_NAME = "runner"


def generate():
    """Generate Runner character mesh."""
    setup_scene()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    parts = []

    # Torso (rectangular core)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.2))
    torso = bpy.context.active_object
    torso.name = "Torso"
    torso.scale = (0.4, 0.25, 0.6)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(torso)

    # Head (smaller cube)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 2.0))
    head = bpy.context.active_object
    head.name = "Head"
    head.scale = (0.25, 0.25, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(head)

    # Visor (cyan glow)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.15, 2.05))
    visor = bpy.context.active_object
    visor.name = "Visor"
    visor.scale = (0.2, 0.05, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(visor)

    # Arms
    for x in [-0.5, 0.5]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 1.1))
        arm = bpy.context.active_object
        arm.name = f"Arm_{x}"
        arm.scale = (0.12, 0.12, 0.5)
        bpy.ops.object.transform_apply(scale=True)
        parts.append(arm)

    # Legs
    for x in [-0.15, 0.15]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0.4))
        leg = bpy.context.active_object
        leg.name = f"Leg_{x}"
        leg.scale = (0.12, 0.12, 0.4)
        bpy.ops.object.transform_apply(scale=True)
        parts.append(leg)

    # Join all parts
    bpy.ops.object.select_all(action='DESELECT')
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()

    runner = bpy.context.active_object
    runner.name = ASSET_NAME

    # Apply material
    mat = create_dark_industrial_material(f"{ASSET_NAME}_mat")
    runner.data.materials.append(mat)

    # Export
    output_path = OUTPUT_DIR / f"{ASSET_NAME}.glb"
    export_glb(runner, output_path)
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    generate()
