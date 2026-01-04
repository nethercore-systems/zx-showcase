#!/usr/bin/env python3
"""Generate Drone enemy mesh.

Output: ../../generated/meshes/drone.glb

Drone: Flying AI enemy controlled by Overseer.
Dark industrial sci-fi aesthetic. 400-600 tris.
"""
import bpy
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from bpy_utils import setup_scene, export_glb, get_output_dir, create_dark_industrial_material

OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated" / "meshes"
ASSET_NAME = "drone"


def generate():
    """Generate Drone enemy mesh."""
    setup_scene()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    parts = []

    # Main body (flattened sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.3, location=(0, 0, 0.3))
    body = bpy.context.active_object
    body.name = "Body"
    body.scale = (1, 1, 0.6)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(body)

    # Eye (red glow in center)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.08, location=(0, -0.25, 0.3))
    eye = bpy.context.active_object
    eye.name = "Eye"
    parts.append(eye)

    # Propeller arms (4 directions)
    for i, angle in enumerate([0, 90, 180, 270]):
        rad = math.radians(angle)
        x = math.cos(rad) * 0.4
        y = math.sin(rad) * 0.4

        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.3, location=(x, y, 0.3))
        arm = bpy.context.active_object
        arm.name = f"Arm_{i}"
        arm.rotation_euler.z = rad
        bpy.ops.object.transform_apply(rotation=True)
        parts.append(arm)

        # Propeller disc at end
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.02, location=(x, y, 0.3))
        prop = bpy.context.active_object
        prop.name = f"Prop_{i}"
        parts.append(prop)

    # Join all parts
    bpy.ops.object.select_all(action='DESELECT')
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()

    drone = bpy.context.active_object
    drone.name = ASSET_NAME

    # Apply material
    mat = create_dark_industrial_material(f"{ASSET_NAME}_mat")
    drone.data.materials.append(mat)

    # Export
    output_path = OUTPUT_DIR / f"{ASSET_NAME}.glb"
    export_glb(drone, output_path)
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    generate()
