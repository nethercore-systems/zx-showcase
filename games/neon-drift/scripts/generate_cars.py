#!/usr/bin/env python3
"""
Neon Drift - Car Asset Generator

Generates 7 car meshes using proper Blender primitives.
Run with: blender --background --python generate_cars.py
"""

import sys
import math
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple

try:
    import bpy
    import bmesh
except ImportError:
    print("Error: Must run from Blender.")
    sys.exit(1)


@dataclass
class CarSpec:
    name: str
    body_color: Tuple[float, float, float]  # RGB 0-1
    accent_color: Tuple[float, float, float]  # RGB 0-1 for neon/emissive
    length: float
    width: float
    height: float
    cabin_offset: float  # 0-1, where cabin sits along length


# Car specifications
CARS = [
    CarSpec("speedster", (0.9, 0.1, 0.3), (1.0, 0.0, 0.5), 4.0, 1.8, 1.0, 0.4),
    CarSpec("muscle", (0.2, 0.3, 0.8), (0.0, 0.5, 1.0), 4.5, 2.0, 1.2, 0.5),
    CarSpec("racer", (0.1, 0.8, 0.3), (0.0, 1.0, 0.5), 4.2, 1.7, 0.9, 0.35),
    CarSpec("drift", (0.9, 0.5, 0.1), (1.0, 0.3, 0.0), 3.8, 1.9, 1.1, 0.45),
    CarSpec("phantom", (0.15, 0.15, 0.2), (0.8, 0.0, 1.0), 4.8, 1.8, 1.0, 0.4),
    CarSpec("titan", (0.6, 0.6, 0.65), (0.0, 1.0, 1.0), 5.0, 2.2, 1.4, 0.5),
    CarSpec("viper", (0.8, 0.8, 0.1), (1.0, 1.0, 0.0), 3.5, 1.6, 0.85, 0.3),
]


def clear_scene():
    """Remove all objects from scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Clean up orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def create_car_mesh(spec: CarSpec) -> bpy.types.Object:
    """Create a car mesh using Blender primitives."""
    clear_scene()

    L, W, H = spec.length, spec.width, spec.height
    parts = []

    # === BODY (main chassis) ===
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, H * 0.4))
    body = bpy.context.active_object
    body.scale = (L * 0.45, W * 0.45, H * 0.35)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(body)

    # === CABIN ===
    cabin_x = L * (spec.cabin_offset - 0.5) * 0.5
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cabin_x, 0, H * 0.85))
    cabin = bpy.context.active_object
    cabin.scale = (L * 0.25, W * 0.4, H * 0.3)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(cabin)

    # === HOOD (front slope) ===
    bpy.ops.mesh.primitive_cube_add(size=1, location=(L * 0.3, 0, H * 0.5))
    hood = bpy.context.active_object
    hood.scale = (L * 0.15, W * 0.42, H * 0.2)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(hood)

    # === TRUNK (rear) ===
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-L * 0.35, 0, H * 0.45))
    trunk = bpy.context.active_object
    trunk.scale = (L * 0.1, W * 0.42, H * 0.25)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(trunk)

    # === WHEELS (4 cylinders) ===
    wheel_radius = H * 0.3
    wheel_width = W * 0.08
    wheel_positions = [
        (L * 0.28, W * 0.5, wheel_radius),   # Front right
        (L * 0.28, -W * 0.5, wheel_radius),  # Front left
        (-L * 0.28, W * 0.5, wheel_radius),  # Rear right
        (-L * 0.28, -W * 0.5, wheel_radius), # Rear left
    ]

    for wx, wy, wz in wheel_positions:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=wheel_radius,
            depth=wheel_width,
            vertices=12,
            location=(wx, wy, wz),
            rotation=(math.pi / 2, 0, 0)
        )
        wheel = bpy.context.active_object
        parts.append(wheel)

    # === SPOILER (for sporty cars) ===
    if spec.name in ["racer", "drift", "viper"]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-L * 0.4, 0, H * 1.0))
        spoiler = bpy.context.active_object
        spoiler.scale = (L * 0.05, W * 0.45, H * 0.05)
        bpy.ops.object.transform_apply(scale=True)
        parts.append(spoiler)

        # Spoiler supports
        for sy in [W * 0.3, -W * 0.3]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(-L * 0.4, sy, H * 0.85))
            support = bpy.context.active_object
            support.scale = (0.03, 0.03, H * 0.15)
            bpy.ops.object.transform_apply(scale=True)
            parts.append(support)

    # === JOIN ALL PARTS ===
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()

    car = bpy.context.active_object
    car.name = spec.name

    # === UV UNWRAP & NORMALS ===
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    return car


def create_material(name: str, color: Tuple[float, float, float],
                   metallic: float = 0.8, roughness: float = 0.3) -> bpy.types.Material:
    """Create a PBR material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    # Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness

    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat


def generate_texture(size: int, color: Tuple[float, float, float],
                    is_emissive: bool = False) -> bpy.types.Image:
    """Generate a simple colored texture."""
    img = bpy.data.images.new(name="temp_texture", width=size, height=size, alpha=True)

    pixels = []
    for y in range(size):
        for x in range(size):
            if is_emissive:
                # Emissive: bright color with some pattern
                intensity = 0.8 + 0.2 * ((x + y) % 32 < 16)
                r, g, b = color[0] * intensity, color[1] * intensity, color[2] * intensity
            else:
                # Albedo: base color with subtle variation
                noise = ((x * 17 + y * 31) % 100) / 500.0 - 0.1
                r = max(0, min(1, color[0] + noise))
                g = max(0, min(1, color[1] + noise))
                b = max(0, min(1, color[2] + noise))
            pixels.extend([r, g, b, 1.0])

    img.pixels = pixels
    return img


def save_texture(img: bpy.types.Image, filepath: Path):
    """Save texture to file."""
    img.filepath_raw = str(filepath)
    img.file_format = 'PNG'
    img.save()
    print(f"  Texture: {filepath.name}")


def export_glb(obj: bpy.types.Object, filepath: Path):
    """Export mesh to GLB."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Apply transforms
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    filepath.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(filepath),
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
        export_normals=True,
        export_texcoords=True,
    )
    print(f"  Mesh: {filepath.name}")


def main():
    print("\n" + "=" * 60)
    print("  NEON DRIFT - CAR GENERATOR (Proper Primitives)")
    print("=" * 60)

    script_dir = Path(__file__).parent
    output_base = script_dir.parent / "assets" / "models"
    meshes_dir = output_base / "meshes"
    textures_dir = output_base / "textures"
    meshes_dir.mkdir(parents=True, exist_ok=True)
    textures_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nOutput: {output_base}")

    for spec in CARS:
        print(f"\n--- {spec.name.upper()} ---")

        # Create mesh
        car = create_car_mesh(spec)

        # Create and assign material
        mat = create_material(f"{spec.name}_mat", spec.body_color)
        car.data.materials.append(mat)

        # Generate textures
        albedo_tex = generate_texture(256, spec.body_color, is_emissive=False)
        save_texture(albedo_tex, textures_dir / f"{spec.name}.png")
        bpy.data.images.remove(albedo_tex)

        emissive_tex = generate_texture(256, spec.accent_color, is_emissive=True)
        save_texture(emissive_tex, textures_dir / f"{spec.name}_emissive.png")
        bpy.data.images.remove(emissive_tex)

        # Export mesh
        export_glb(car, meshes_dir / f"{spec.name}.glb")

    print("\n" + "=" * 60)
    print(f"  Generated {len(CARS)} cars")
    print("=" * 60)


if __name__ == "__main__":
    main()
