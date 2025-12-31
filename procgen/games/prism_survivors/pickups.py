"""Prism Survivors - Pickup Generators.

Generates 3 pickup types:
- XP Gem: Faceted crystal, green glow
- Coin: Spinning disc, gold
- Powerup Orb: Pulsing sphere, rainbow

50-150 triangles per pickup (swarm-friendly).
Requires Blender to run.
"""

import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

try:
    import bpy
    import bmesh
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False
    bpy = None
    bmesh = None


@dataclass
class PickupSpec:
    """Pickup specification."""
    name: str
    color: Tuple[float, float, float]
    glow_color: Tuple[float, float, float]
    shape: str  # gem, coin, orb
    size: float


PICKUPS = [
    PickupSpec("xp_gem", (0.2, 0.8, 0.3), (0.4, 1.0, 0.5), "gem", 0.15),
    PickupSpec("coin", (0.95, 0.8, 0.2), (1.0, 0.9, 0.4), "coin", 0.12),
    PickupSpec("powerup_orb", (0.8, 0.3, 0.9), (1.0, 0.5, 1.0), "orb", 0.18),
]


if BLENDER_AVAILABLE:

    def clear_scene():
        """Remove all objects from scene."""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)

    def build_gem(spec: PickupSpec):
        """Build faceted gem pickup."""
        size = spec.size

        # Octahedron-based gem
        bpy.ops.mesh.primitive_cone_add(radius1=size, radius2=0, depth=size * 1.2, vertices=6)
        top = bpy.context.active_object
        top.location.z = size * 0.3

        bpy.ops.mesh.primitive_cone_add(radius1=size, radius2=0, depth=size * 0.8, vertices=6)
        bottom = bpy.context.active_object
        bottom.rotation_euler.x = math.pi
        bottom.location.z = -size * 0.2
        bpy.ops.object.transform_apply(rotation=True)

        # Join
        bpy.ops.object.select_all(action='DESELECT')
        top.select_set(True)
        bottom.select_set(True)
        bpy.context.view_layer.objects.active = top
        bpy.ops.object.join()

        gem = bpy.context.active_object
        gem.name = spec.name

        # UV and smooth
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.shade_smooth()

        return gem

    def build_coin(spec: PickupSpec):
        """Build coin pickup."""
        size = spec.size

        bpy.ops.mesh.primitive_cylinder_add(radius=size, depth=size * 0.15, vertices=16)
        coin = bpy.context.active_object
        coin.name = spec.name

        # Add rim detail
        bpy.ops.mesh.primitive_torus_add(major_radius=size * 0.9, minor_radius=size * 0.08,
                                          major_segments=16, minor_segments=6)
        rim = bpy.context.active_object

        # Join
        bpy.ops.object.select_all(action='DESELECT')
        coin.select_set(True)
        rim.select_set(True)
        bpy.context.view_layer.objects.active = coin
        bpy.ops.object.join()

        coin = bpy.context.active_object

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.shade_smooth()

        return coin

    def build_orb(spec: PickupSpec):
        """Build powerup orb pickup."""
        size = spec.size

        # Core sphere
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size, segments=12, ring_count=8)
        orb = bpy.context.active_object
        orb.name = spec.name

        # Inner glow sphere
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size * 0.6, segments=8, ring_count=6)
        inner = bpy.context.active_object

        # Join
        bpy.ops.object.select_all(action='DESELECT')
        orb.select_set(True)
        inner.select_set(True)
        bpy.context.view_layer.objects.active = orb
        bpy.ops.object.join()

        orb = bpy.context.active_object

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.shade_smooth()

        return orb

    def count_triangles(obj) -> int:
        """Count triangles in mesh."""
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        count = len(bm.faces)
        bm.free()
        return count

    def export_glb(obj, filepath: Path):
        """Export mesh to GLB format."""
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        filepath.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.export_scene.gltf(
            filepath=str(filepath),
            export_format='GLB',
            use_selection=True,
            export_apply=True,
        )

    def generate_pickup(spec: PickupSpec, meshes_dir: Path, textures_dir: Path) -> int:
        """Generate a single pickup."""
        clear_scene()

        builders = {
            "gem": build_gem,
            "coin": build_coin,
            "orb": build_orb,
        }

        builder = builders.get(spec.shape, build_orb)
        pickup = builder(spec)

        tri_count = count_triangles(pickup)
        status = "OK" if 50 <= tri_count <= 200 else "WARN"
        print(f"  {spec.name}: {tri_count} tris [{status}]")

        export_glb(pickup, meshes_dir / f"{spec.name}.glb")

        return 1

    def generate_all_pickups(meshes_dir: Path, textures_dir: Path = None) -> int:
        """Generate all pickup meshes."""
        if textures_dir is None:
            textures_dir = meshes_dir.parent / "textures"

        meshes_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for spec in PICKUPS:
            count += generate_pickup(spec, meshes_dir, textures_dir)

        return count


if not BLENDER_AVAILABLE:
    def generate_all_pickups(meshes_dir: Path, textures_dir: Path = None) -> int:
        """Stub when Blender not available."""
        print("Warning: Blender not available, skipping pickup generation")
        return 0


__all__ = [
    "PICKUPS",
    "PickupSpec",
    "generate_all_pickups",
    "BLENDER_AVAILABLE",
]


if __name__ == "__main__" and BLENDER_AVAILABLE:
    script_dir = Path(__file__).parent
    output_base = script_dir.parent.parent.parent / "games" / "prism-survivors" / "assets" / "models"
    meshes_dir = output_base / "meshes"

    print("\n" + "=" * 60)
    print("  PRISM SURVIVORS - Pickup Generator")
    print("=" * 60)

    count = generate_all_pickups(meshes_dir)

    print(f"\nGenerated {count} pickups")
    print("=" * 60)
