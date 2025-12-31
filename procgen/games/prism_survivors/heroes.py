"""Prism Survivors - Hero Character Generators.

Generates 6 hero classes with distinct silhouettes:
- Knight: Heavy armor, sword & shield
- Mage: Robes, staff, magical particles
- Ranger: Leather, bow, quiver
- Cleric: White robes, holy symbol
- Necromancer: Dark robes, skull staff
- Paladin: Golden armor, warhammer

800-1500 triangles per hero (ZX budget compliant).
Requires Blender to run.
"""

import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional

try:
    import bpy
    import bmesh
    from mathutils import Vector
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False
    bpy = None
    bmesh = None


@dataclass
class HeroSpec:
    """Hero specification with appearance and stats."""
    name: str
    color_primary: Tuple[float, float, float]  # RGB 0-1
    color_accent: Tuple[float, float, float]   # RGB 0-1
    color_glow: Tuple[float, float, float]     # Emission color
    style: str  # armored, robed, leather
    height: float  # Character height in units
    bulk: float  # Body width multiplier
    features: List[str]  # Special geometry features


# Hero specifications with distinct visual identities
HEROES = [
    HeroSpec("knight", (0.35, 0.45, 0.6), (0.85, 0.7, 0.2), (0.3, 0.4, 0.8),
             "armored", 1.8, 1.2,
             ["helmet_visor", "shoulder_plates", "shield", "sword"]),

    HeroSpec("mage", (0.35, 0.15, 0.55), (0.3, 0.8, 0.95), (0.5, 0.3, 1.0),
             "robed", 1.7, 0.9,
             ["wizard_hat", "long_robe", "staff", "magic_orb"]),

    HeroSpec("ranger", (0.2, 0.45, 0.25), (0.55, 0.4, 0.25), (0.3, 0.6, 0.3),
             "leather", 1.75, 1.0,
             ["hood", "cloak", "bow", "quiver"]),

    HeroSpec("cleric", (0.95, 0.92, 0.85), (1.0, 0.8, 0.3), (1.0, 0.9, 0.5),
             "robed", 1.7, 1.0,
             ["halo", "holy_symbol", "mace", "tome"]),

    HeroSpec("necromancer", (0.15, 0.1, 0.2), (0.4, 0.9, 0.3), (0.3, 0.8, 0.2),
             "robed", 1.75, 0.95,
             ["skull_mask", "tattered_robe", "skull_staff", "floating_souls"]),

    HeroSpec("paladin", (0.9, 0.75, 0.25), (1.0, 0.95, 0.8), (1.0, 0.85, 0.4),
             "armored", 1.85, 1.3,
             ["crown_helm", "heavy_plates", "cape", "warhammer"]),
]


if BLENDER_AVAILABLE:

    def clear_scene():
        """Remove all objects from scene."""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)
        for block in bpy.data.materials:
            if block.users == 0:
                bpy.data.materials.remove(block)

    def create_beveled_box(sx: float, sy: float, sz: float,
                           bevel: float = 0.02, segments: int = 1):
        """Create a box with beveled edges."""
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj = bpy.context.active_object
        obj.scale = (sx, sy, sz)
        bpy.ops.object.transform_apply(scale=True)

        bevel_mod = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel_mod.width = bevel
        bevel_mod.segments = segments
        bevel_mod.limit_method = 'ANGLE'
        bevel_mod.angle_limit = math.radians(30)
        bpy.ops.object.modifier_apply(modifier="Bevel")

        return obj

    def create_humanoid_base(height: float, bulk: float, style: str):
        """Create base humanoid mesh."""
        parts = []

        # Torso
        torso_height = height * 0.35
        torso_width = 0.4 * bulk
        torso = create_beveled_box(torso_width, 0.25 * bulk, torso_height, bevel=0.03)
        torso.location = (0, 0, height * 0.55)
        parts.append(torso)

        # Head
        head_size = height * 0.12
        bpy.ops.mesh.primitive_uv_sphere_add(radius=head_size, segments=12, ring_count=8)
        head = bpy.context.active_object
        head.location = (0, 0, height * 0.88)
        parts.append(head)

        # Legs (2)
        leg_height = height * 0.4
        leg_width = 0.12 * bulk
        for x_offset in [-0.12 * bulk, 0.12 * bulk]:
            leg = create_beveled_box(leg_width, leg_width, leg_height, bevel=0.02)
            leg.location = (x_offset, 0, leg_height * 0.5)
            parts.append(leg)

        # Arms (2)
        arm_length = height * 0.35
        arm_width = 0.08 * bulk
        for x_offset in [-(torso_width * 0.5 + arm_width), torso_width * 0.5 + arm_width]:
            arm = create_beveled_box(arm_width, arm_width, arm_length, bevel=0.015)
            arm.location = (x_offset, 0, height * 0.6)
            parts.append(arm)

        return parts

    def add_armor_features(parts: List, spec: HeroSpec, height: float):
        """Add armor-specific features."""
        bulk = spec.bulk

        # Shoulder plates
        if "shoulder_plates" in spec.features:
            for x_offset in [-0.35 * bulk, 0.35 * bulk]:
                plate = create_beveled_box(0.15 * bulk, 0.12 * bulk, 0.1, bevel=0.02)
                plate.location = (x_offset, 0, height * 0.72)
                parts.append(plate)

        # Helmet
        if "helmet_visor" in spec.features:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=height * 0.13, segments=10, ring_count=6)
            helmet = bpy.context.active_object
            helmet.location = (0, 0, height * 0.88)
            helmet.scale.z = 1.1
            bpy.ops.object.transform_apply(scale=True)
            parts.append(helmet)

        # Crown helm (paladin)
        if "crown_helm" in spec.features:
            bpy.ops.mesh.primitive_cylinder_add(radius=height * 0.1, depth=0.08, vertices=8)
            crown = bpy.context.active_object
            crown.location = (0, 0, height * 0.98)
            parts.append(crown)

        # Shield
        if "shield" in spec.features:
            shield = create_beveled_box(0.02, 0.25, 0.35, bevel=0.01)
            shield.location = (-0.4 * bulk, 0.1, height * 0.55)
            parts.append(shield)

        # Sword
        if "sword" in spec.features:
            blade = create_beveled_box(0.02, 0.03, 0.5, bevel=0.005)
            blade.location = (0.4 * bulk, 0, height * 0.5)
            parts.append(blade)

        # Warhammer
        if "warhammer" in spec.features:
            handle = create_beveled_box(0.03, 0.03, 0.6, bevel=0.005)
            handle.location = (0.45 * bulk, 0, height * 0.55)
            parts.append(handle)
            head_h = create_beveled_box(0.08, 0.15, 0.1, bevel=0.01)
            head_h.location = (0.45 * bulk, 0, height * 0.85)
            parts.append(head_h)

        # Cape
        if "cape" in spec.features:
            cape = create_beveled_box(0.35 * bulk, 0.02, height * 0.4, bevel=0.01)
            cape.location = (0, -0.15, height * 0.55)
            parts.append(cape)

    def add_robe_features(parts: List, spec: HeroSpec, height: float):
        """Add robe-specific features."""
        bulk = spec.bulk

        # Long robe skirt
        if "long_robe" in spec.features or "tattered_robe" in spec.features:
            bpy.ops.mesh.primitive_cone_add(radius1=0.3 * bulk, radius2=0.15 * bulk,
                                             depth=height * 0.5, vertices=12)
            robe = bpy.context.active_object
            robe.location = (0, 0, height * 0.28)
            parts.append(robe)

        # Wizard hat
        if "wizard_hat" in spec.features:
            bpy.ops.mesh.primitive_cone_add(radius1=height * 0.12, radius2=0.01,
                                             depth=height * 0.25, vertices=8)
            hat = bpy.context.active_object
            hat.location = (0, 0, height * 1.05)
            parts.append(hat)

        # Staff
        if "staff" in spec.features:
            staff = create_beveled_box(0.02, 0.02, height * 0.8, bevel=0.005)
            staff.location = (0.35 * bulk, 0, height * 0.5)
            parts.append(staff)
            # Orb on top
            if "magic_orb" in spec.features:
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, segments=8, ring_count=6)
                orb = bpy.context.active_object
                orb.location = (0.35 * bulk, 0, height * 0.95)
                parts.append(orb)

        # Skull staff (necromancer)
        if "skull_staff" in spec.features:
            staff = create_beveled_box(0.02, 0.02, height * 0.75, bevel=0.005)
            staff.location = (0.35 * bulk, 0, height * 0.45)
            parts.append(staff)
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, segments=8, ring_count=6)
            skull = bpy.context.active_object
            skull.location = (0.35 * bulk, 0, height * 0.88)
            skull.scale = (1.0, 0.8, 1.1)
            bpy.ops.object.transform_apply(scale=True)
            parts.append(skull)

        # Skull mask
        if "skull_mask" in spec.features:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=height * 0.11, segments=8, ring_count=6)
            mask = bpy.context.active_object
            mask.location = (0, 0.02, height * 0.88)
            mask.scale = (0.9, 0.7, 1.0)
            bpy.ops.object.transform_apply(scale=True)
            parts.append(mask)

        # Halo (cleric)
        if "halo" in spec.features:
            bpy.ops.mesh.primitive_torus_add(major_radius=height * 0.12,
                                              minor_radius=0.015, major_segments=16, minor_segments=6)
            halo = bpy.context.active_object
            halo.location = (0, 0, height * 1.05)
            parts.append(halo)

        # Holy symbol
        if "holy_symbol" in spec.features:
            symbol = create_beveled_box(0.08, 0.02, 0.12, bevel=0.005)
            symbol.location = (0, 0.15, height * 0.6)
            parts.append(symbol)

        # Mace
        if "mace" in spec.features:
            handle = create_beveled_box(0.02, 0.02, 0.35, bevel=0.005)
            handle.location = (0.35 * bulk, 0, height * 0.45)
            parts.append(handle)
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, segments=8, ring_count=6)
            mace_head = bpy.context.active_object
            mace_head.location = (0.35 * bulk, 0, height * 0.65)
            parts.append(mace_head)

    def add_leather_features(parts: List, spec: HeroSpec, height: float):
        """Add leather/ranger-specific features."""
        bulk = spec.bulk

        # Hood
        if "hood" in spec.features:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=height * 0.14, segments=10, ring_count=6)
            hood = bpy.context.active_object
            hood.location = (0, -0.02, height * 0.9)
            hood.scale = (1.0, 1.2, 1.0)
            bpy.ops.object.transform_apply(scale=True)
            parts.append(hood)

        # Cloak
        if "cloak" in spec.features:
            cape = create_beveled_box(0.3 * bulk, 0.02, height * 0.35, bevel=0.01)
            cape.location = (0, -0.12, height * 0.5)
            parts.append(cape)

        # Bow
        if "bow" in spec.features:
            # Simplified bow as curved shape
            bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.6, vertices=8)
            bow = bpy.context.active_object
            bow.location = (-0.35 * bulk, -0.1, height * 0.55)
            bow.rotation_euler.x = math.radians(15)
            bpy.ops.object.transform_apply(rotation=True)
            parts.append(bow)

        # Quiver
        if "quiver" in spec.features:
            quiver = create_beveled_box(0.06, 0.04, 0.25, bevel=0.01)
            quiver.location = (0.1, -0.18, height * 0.55)
            parts.append(quiver)

    def join_hero_parts(parts: List, name: str):
        """Join all parts into single mesh with UVs."""
        if not parts:
            return None

        bpy.ops.object.select_all(action='DESELECT')
        for part in parts:
            part.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]

        bpy.ops.object.join()
        hero = bpy.context.active_object
        hero.name = name

        # UV unwrap
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.shade_smooth()

        return hero

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
            export_materials='EXPORT',
            export_normals=True,
            export_texcoords=True,
        )

    def build_hero(spec: HeroSpec):
        """Build a hero character mesh."""
        height = spec.height
        bulk = spec.bulk

        # Create base humanoid
        parts = create_humanoid_base(height, bulk, spec.style)

        # Add style-specific features
        if spec.style == "armored":
            add_armor_features(parts, spec, height)
        elif spec.style == "robed":
            add_robe_features(parts, spec, height)
        elif spec.style == "leather":
            add_leather_features(parts, spec, height)

        return join_hero_parts(parts, spec.name)

    def generate_hero(spec: HeroSpec, meshes_dir: Path, textures_dir: Path) -> int:
        """Generate a single hero and export."""
        clear_scene()

        hero = build_hero(spec)

        if hero is None:
            print(f"  Warning: Failed to build {spec.name}")
            return 0

        tri_count = count_triangles(hero)
        print(f"  {spec.name}: {tri_count} triangles")

        export_glb(hero, meshes_dir / f"{spec.name}.glb")

        # Budget check
        if tri_count > 1500:
            print(f"  WARNING: Exceeds 1500 tri budget!")
        elif tri_count < 800:
            print(f"  Note: Under 800 tris, could add detail")

        return 1

    def generate_all_heroes(meshes_dir: Path, textures_dir: Path = None) -> int:
        """Generate all hero meshes."""
        if textures_dir is None:
            textures_dir = meshes_dir.parent / "textures"

        meshes_dir.mkdir(parents=True, exist_ok=True)
        textures_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for spec in HEROES:
            count += generate_hero(spec, meshes_dir, textures_dir)

        return count


# Fallback when Blender is not available
if not BLENDER_AVAILABLE:
    def generate_all_heroes(meshes_dir: Path, textures_dir: Path = None) -> int:
        """Stub when Blender not available."""
        print("Warning: Blender not available, skipping hero generation")
        print("Run with: blender --background --python heroes.py")
        return 0


__all__ = [
    "HEROES",
    "HeroSpec",
    "generate_all_heroes",
    "BLENDER_AVAILABLE",
]


# CLI entry point for Blender
if __name__ == "__main__" and BLENDER_AVAILABLE:
    script_dir = Path(__file__).parent
    output_base = script_dir.parent.parent.parent / "games" / "prism-survivors" / "assets" / "models"
    meshes_dir = output_base / "meshes"
    textures_dir = output_base / "textures"

    print("\n" + "=" * 60)
    print("  PRISM SURVIVORS - Hero Generator")
    print("=" * 60)
    print(f"\nOutput: {output_base}")

    count = generate_all_heroes(meshes_dir, textures_dir)

    print(f"\nGenerated {count} heroes")
    print("=" * 60)
