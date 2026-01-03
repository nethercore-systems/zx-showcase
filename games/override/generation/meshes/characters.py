#!/usr/bin/env python3
"""Generate 3D character meshes for Override.

Characters:
- Runner: Humanoid player character (3 instances in multiplayer)
- Drone: Flying AI enemy controlled by Overseer

Dark industrial sci-fi aesthetic.
"""

import bpy
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from bpy_utils import setup_scene, export_glb, get_output_dir, create_dark_industrial_material, create_glow_material


def generate_runner():
    """Generate Runner character mesh (800-1000 tris)."""
    setup_scene()

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
    runner.name = "runner"

    # Apply material
    mat = create_dark_industrial_material("runner_mat")
    runner.data.materials.append(mat)

    # Export
    output_path = get_output_dir() / "runner.glb"
    export_glb(runner, output_path)

    print(f"✓ Runner character generated")


def generate_drone():
    """Generate Drone enemy mesh (400-600 tris)."""
    setup_scene()

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
        import math
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
    drone.name = "drone"

    # Apply material
    mat = create_dark_industrial_material("drone_mat")
    drone.data.materials.append(mat)

    # Export
    output_path = get_output_dir() / "drone.glb"
    export_glb(drone, output_path)

    print(f"✓ Drone enemy generated")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("OVERRIDE - Character Generation")
    print("="*60 + "\n")

    generate_runner()
    generate_drone()

    print("\n" + "="*60)
    print("✓ All characters generated!")
    print("="*60)
