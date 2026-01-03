"""Prism Survivors - Enemy Generators.

Generates 13 enemy types:

Basic Enemies (7) - 200-600 tris:
- Crawler: Small spider-like, swarm behavior
- Skeleton: Humanoid, melee attacks
- Wisp: Floating orb, erratic movement
- Golem: Large rock creature, slow but tough
- Shade: Ghost-like, fast movement
- Berserker: Aggressive humanoid, charges
- Arcane Sentinel: Floating construct, ranged

Elite Enemies (4) - 500-1000 tris:
- Crystal Knight: Armored humanoid, tank
- Void Mage: Dark caster, teleports
- Golem Titan: Massive rock golem
- Specter Lord: Powerful ghost

Bosses (2) - 1500-2000 tris:
- Prism Colossus: Giant crystalline construct
- Void Dragon: Dark dragon boss

Requires Blender to run.
"""

import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

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
class EnemySpec:
    """Enemy specification."""
    name: str
    tier: str  # basic, elite, boss
    color_base: Tuple[float, float, float]
    color_glow: Tuple[float, float, float]
    scale: float
    shape: str  # humanoid, crawler, orb, golem, ghost, dragon, construct
    features: List[str]


# Enemy specifications
ENEMIES = [
    # === Basic Enemies (7) ===
    EnemySpec("crawler", "basic", (0.15, 0.1, 0.2), (0.3, 0.1, 0.35),
              0.6, "crawler", ["spider_legs", "mandibles"]),

    EnemySpec("skeleton", "basic", (0.9, 0.85, 0.75), (0.6, 0.55, 0.45),
              0.8, "humanoid", ["bone_armor", "sword"]),

    EnemySpec("wisp", "basic", (0.3, 0.6, 1.0), (0.8, 0.9, 1.0),
              0.5, "orb", ["trailing_particles", "pulsing"]),

    EnemySpec("golem", "basic", (0.4, 0.38, 0.35), (0.55, 0.5, 0.45),
              1.2, "golem", ["rock_plates", "glowing_core"]),

    EnemySpec("shade", "basic", (0.1, 0.05, 0.15), (0.3, 0.2, 0.4),
              0.7, "ghost", ["wispy_form", "glowing_eyes"]),

    EnemySpec("berserker", "basic", (0.5, 0.15, 0.1), (0.9, 0.3, 0.2),
              1.0, "humanoid", ["spiked_armor", "twin_axes"]),

    EnemySpec("arcane_sentinel", "basic", (0.2, 0.3, 0.5), (0.4, 0.6, 1.0),
              0.9, "construct", ["floating_shards", "energy_core"]),

    # === Elite Enemies (4) ===
    EnemySpec("crystal_knight", "elite", (0.4, 0.2, 0.5), (0.8, 0.5, 1.0),
              1.3, "humanoid", ["crystal_armor", "crystal_sword", "shoulder_crystals"]),

    EnemySpec("void_mage", "elite", (0.1, 0.05, 0.15), (0.4, 0.2, 0.6),
              1.1, "humanoid", ["void_robe", "void_staff", "floating_runes"]),

    EnemySpec("golem_titan", "elite", (0.35, 0.3, 0.25), (0.6, 0.5, 0.4),
              1.6, "golem", ["massive_plates", "multiple_cores", "crystal_growth"]),

    EnemySpec("specter_lord", "elite", (0.15, 0.15, 0.2), (0.5, 0.5, 0.8),
              1.2, "ghost", ["crown", "spectral_cape", "soul_orbs"]),

    # === Bosses (2) ===
    EnemySpec("prism_colossus", "boss", (0.3, 0.4, 0.5), (1.0, 0.3, 0.3),
              2.5, "construct", ["crystal_body", "rotating_shards", "core_exposed"]),

    EnemySpec("void_dragon", "boss", (0.15, 0.05, 0.2), (0.8, 0.2, 0.3),
              2.2, "dragon", ["wings", "tail", "horns", "void_breath"]),
]


if BLENDER_AVAILABLE:

    def clear_scene():
        """Remove all objects from scene."""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)

    def create_beveled_box(sx: float, sy: float, sz: float,
                           bevel: float = 0.02, segments: int = 1):
        """Create a box with beveled edges."""
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj = bpy.context.active_object
        obj.scale = (sx, sy, sz)
        bpy.ops.object.transform_apply(scale=True)

        if bevel > 0:
            bevel_mod = obj.modifiers.new(name="Bevel", type='BEVEL')
            bevel_mod.width = bevel
            bevel_mod.segments = segments
            bpy.ops.object.modifier_apply(modifier="Bevel")

        return obj

    def build_crawler(spec: EnemySpec):
        """Build crawler enemy (spider-like)."""
        parts = []
        scale = spec.scale

        # Body (oval)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15 * scale, segments=10, ring_count=6)
        body = bpy.context.active_object
        body.scale = (1.2, 1.0, 0.6)
        bpy.ops.object.transform_apply(scale=True)
        body.location = (0, 0, 0.1 * scale)
        parts.append(body)

        # Legs (6)
        for i in range(6):
            angle = (i - 2.5) * 0.5
            for side in [-1, 1]:
                bpy.ops.mesh.primitive_cylinder_add(radius=0.015 * scale, depth=0.2 * scale, vertices=6)
                leg = bpy.context.active_object
                leg.rotation_euler = (math.radians(60), 0, angle)
                leg.location = (side * 0.1 * scale, i * 0.05 * scale - 0.1 * scale, 0.08 * scale)
                parts.append(leg)

        return parts

    def build_humanoid_enemy(spec: EnemySpec):
        """Build humanoid enemy (skeleton, berserker, etc.)."""
        parts = []
        scale = spec.scale

        # Torso
        torso = create_beveled_box(0.25 * scale, 0.15 * scale, 0.35 * scale, bevel=0.02)
        torso.location = (0, 0, 0.55 * scale)
        parts.append(torso)

        # Head
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1 * scale, segments=10, ring_count=6)
        head = bpy.context.active_object
        head.location = (0, 0, 0.85 * scale)
        parts.append(head)

        # Legs
        for x in [-0.08, 0.08]:
            leg = create_beveled_box(0.08 * scale, 0.08 * scale, 0.35 * scale, bevel=0.01)
            leg.location = (x * scale, 0, 0.175 * scale)
            parts.append(leg)

        # Arms
        for x in [-0.2, 0.2]:
            arm = create_beveled_box(0.06 * scale, 0.06 * scale, 0.3 * scale, bevel=0.01)
            arm.location = (x * scale, 0, 0.55 * scale)
            parts.append(arm)

        # Add weapons for berserker
        if "twin_axes" in spec.features:
            for x in [-0.3, 0.3]:
                axe = create_beveled_box(0.08 * scale, 0.02 * scale, 0.15 * scale, bevel=0.005)
                axe.location = (x * scale, 0, 0.4 * scale)
                parts.append(axe)

        # Add sword for skeleton/crystal_knight
        if "sword" in spec.features or "crystal_sword" in spec.features:
            sword = create_beveled_box(0.02 * scale, 0.02 * scale, 0.4 * scale, bevel=0.005)
            sword.location = (0.25 * scale, 0, 0.45 * scale)
            parts.append(sword)

        # Crystal armor features
        if "crystal_armor" in spec.features:
            for x in [-0.18, 0.18]:
                crystal = create_beveled_box(0.08 * scale, 0.06 * scale, 0.1 * scale, bevel=0.01)
                crystal.location = (x * scale, 0, 0.7 * scale)
                parts.append(crystal)

        return parts

    def build_orb(spec: EnemySpec):
        """Build orb enemy (wisp)."""
        parts = []
        scale = spec.scale

        # Core orb
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15 * scale, segments=12, ring_count=8)
        core = bpy.context.active_object
        core.location = (0, 0, 0.2 * scale)
        parts.append(core)

        # Outer glow ring
        bpy.ops.mesh.primitive_torus_add(major_radius=0.18 * scale, minor_radius=0.02 * scale,
                                          major_segments=16, minor_segments=6)
        ring = bpy.context.active_object
        ring.location = (0, 0, 0.2 * scale)
        parts.append(ring)

        return parts

    def build_golem(spec: EnemySpec):
        """Build golem enemy (rock creature)."""
        parts = []
        scale = spec.scale

        # Main body (chunky)
        body = create_beveled_box(0.4 * scale, 0.3 * scale, 0.5 * scale, bevel=0.03)
        body.location = (0, 0, 0.45 * scale)
        parts.append(body)

        # Head (smaller box)
        head = create_beveled_box(0.2 * scale, 0.18 * scale, 0.2 * scale, bevel=0.02)
        head.location = (0, 0, 0.8 * scale)
        parts.append(head)

        # Arms (thick)
        for x in [-0.35, 0.35]:
            arm = create_beveled_box(0.12 * scale, 0.1 * scale, 0.35 * scale, bevel=0.02)
            arm.location = (x * scale, 0, 0.45 * scale)
            parts.append(arm)

        # Legs (stumpy)
        for x in [-0.15, 0.15]:
            leg = create_beveled_box(0.12 * scale, 0.12 * scale, 0.25 * scale, bevel=0.02)
            leg.location = (x * scale, 0, 0.125 * scale)
            parts.append(leg)

        # Glowing core
        if "glowing_core" in spec.features or "multiple_cores" in spec.features:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08 * scale, segments=8, ring_count=6)
            core = bpy.context.active_object
            core.location = (0, 0.15 * scale, 0.45 * scale)
            parts.append(core)

        return parts

    def build_ghost(spec: EnemySpec):
        """Build ghost enemy (shade, specter_lord)."""
        parts = []
        scale = spec.scale

        # Main wispy body (cone)
        bpy.ops.mesh.primitive_cone_add(radius1=0.25 * scale, radius2=0.05 * scale,
                                         depth=0.6 * scale, vertices=12)
        body = bpy.context.active_object
        body.location = (0, 0, 0.35 * scale)
        parts.append(body)

        # Head
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12 * scale, segments=10, ring_count=6)
        head = bpy.context.active_object
        head.location = (0, 0, 0.7 * scale)
        parts.append(head)

        # Crown for specter_lord
        if "crown" in spec.features:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.08 * scale, depth=0.06 * scale, vertices=6)
            crown = bpy.context.active_object
            crown.location = (0, 0, 0.85 * scale)
            parts.append(crown)

        # Soul orbs
        if "soul_orbs" in spec.features:
            for angle in [0, 2.1, 4.2]:
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04 * scale, segments=6, ring_count=4)
                orb = bpy.context.active_object
                orb.location = (math.cos(angle) * 0.25 * scale,
                               math.sin(angle) * 0.25 * scale,
                               0.5 * scale)
                parts.append(orb)

        return parts

    def build_construct(spec: EnemySpec):
        """Build construct enemy (arcane_sentinel, prism_colossus)."""
        parts = []
        scale = spec.scale

        # Central core
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2 * scale, segments=12, ring_count=8)
        core = bpy.context.active_object
        core.location = (0, 0, 0.5 * scale)
        parts.append(core)

        # Floating shards
        shard_count = 8 if spec.tier == "boss" else 4
        for i in range(shard_count):
            angle = i * (2 * math.pi / shard_count)
            shard = create_beveled_box(0.08 * scale, 0.03 * scale, 0.2 * scale, bevel=0.01)
            shard.location = (math.cos(angle) * 0.35 * scale,
                             math.sin(angle) * 0.35 * scale,
                             0.5 * scale)
            shard.rotation_euler.z = angle
            bpy.ops.object.transform_apply(rotation=True)
            parts.append(shard)

        # Base platform for boss
        if spec.tier == "boss":
            bpy.ops.mesh.primitive_cylinder_add(radius=0.5 * scale, depth=0.15 * scale, vertices=8)
            base = bpy.context.active_object
            base.location = (0, 0, 0.1 * scale)
            parts.append(base)

        return parts

    def build_dragon(spec: EnemySpec):
        """Build dragon boss."""
        parts = []
        scale = spec.scale

        # Body (elongated)
        body = create_beveled_box(0.6 * scale, 0.35 * scale, 0.4 * scale, bevel=0.03)
        body.location = (0, 0, 0.5 * scale)
        parts.append(body)

        # Head (angular)
        head = create_beveled_box(0.25 * scale, 0.2 * scale, 0.2 * scale, bevel=0.02)
        head.location = (0.5 * scale, 0, 0.6 * scale)
        parts.append(head)

        # Neck
        neck = create_beveled_box(0.15 * scale, 0.12 * scale, 0.15 * scale, bevel=0.02)
        neck.location = (0.35 * scale, 0, 0.55 * scale)
        parts.append(neck)

        # Wings (2)
        for y in [-0.4, 0.4]:
            wing = create_beveled_box(0.5 * scale, 0.02 * scale, 0.35 * scale, bevel=0.01)
            wing.location = (0, y * scale, 0.65 * scale)
            wing.rotation_euler.x = math.radians(15) if y > 0 else math.radians(-15)
            bpy.ops.object.transform_apply(rotation=True)
            parts.append(wing)

        # Tail
        for i in range(3):
            segment = create_beveled_box(0.1 * scale, 0.08 * scale, 0.08 * scale, bevel=0.01)
            segment.location = (-(0.4 + i * 0.15) * scale, 0, 0.4 * scale)
            parts.append(segment)

        # Legs (4)
        for x, z in [(0.2, 0.2), (-0.2, 0.2)]:
            for y in [-0.2, 0.2]:
                leg = create_beveled_box(0.08 * scale, 0.08 * scale, 0.25 * scale, bevel=0.01)
                leg.location = (x * scale, y * scale, z * scale)
                parts.append(leg)

        # Horns
        if "horns" in spec.features:
            for y in [-0.1, 0.1]:
                bpy.ops.mesh.primitive_cone_add(radius1=0.04 * scale, radius2=0.01 * scale,
                                                 depth=0.15 * scale, vertices=6)
                horn = bpy.context.active_object
                horn.location = (0.6 * scale, y * scale, 0.75 * scale)
                horn.rotation_euler.x = math.radians(-30)
                bpy.ops.object.transform_apply(rotation=True)
                parts.append(horn)

        return parts

    def join_enemy_parts(parts: List, name: str):
        """Join all parts into single mesh."""
        if not parts:
            return None

        bpy.ops.object.select_all(action='DESELECT')
        for part in parts:
            part.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]

        bpy.ops.object.join()
        enemy = bpy.context.active_object
        enemy.name = name

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.shade_smooth()

        return enemy

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

    def build_enemy(spec: EnemySpec):
        """Build enemy mesh based on shape type."""
        builders = {
            "crawler": build_crawler,
            "humanoid": build_humanoid_enemy,
            "orb": build_orb,
            "golem": build_golem,
            "ghost": build_ghost,
            "construct": build_construct,
            "dragon": build_dragon,
        }

        builder = builders.get(spec.shape, build_humanoid_enemy)
        parts = builder(spec)
        return join_enemy_parts(parts, spec.name)

    def generate_enemy(spec: EnemySpec, meshes_dir: Path, textures_dir: Path) -> int:
        """Generate a single enemy."""
        clear_scene()

        enemy = build_enemy(spec)

        if enemy is None:
            print(f"  Warning: Failed to build {spec.name}")
            return 0

        tri_count = count_triangles(enemy)

        # Tier-specific budget checks
        budgets = {"basic": (200, 600), "elite": (500, 1000), "boss": (1500, 2000)}
        min_tris, max_tris = budgets.get(spec.tier, (200, 600))

        status = "OK" if min_tris <= tri_count <= max_tris else "WARN"
        print(f"  {spec.name} ({spec.tier}): {tri_count} tris [{status}]")

        export_glb(enemy, meshes_dir / f"{spec.name}.glb")

        return 1

    def generate_all_enemies(meshes_dir: Path, textures_dir: Path = None) -> int:
        """Generate all enemy meshes."""
        if textures_dir is None:
            textures_dir = meshes_dir.parent / "textures"

        meshes_dir.mkdir(parents=True, exist_ok=True)
        textures_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for spec in ENEMIES:
            count += generate_enemy(spec, meshes_dir, textures_dir)

        return count


# Fallback when Blender is not available
if not BLENDER_AVAILABLE:
    def generate_all_enemies(meshes_dir: Path, textures_dir: Path = None) -> int:
        """Stub when Blender not available."""
        print("Warning: Blender not available, skipping enemy generation")
        return 0


__all__ = [
    "ENEMIES",
    "EnemySpec",
    "generate_all_enemies",
    "BLENDER_AVAILABLE",
]


if __name__ == "__main__" and BLENDER_AVAILABLE:
    script_dir = Path(__file__).parent
    output_base = script_dir.parent.parent / "generated"
    meshes_dir = output_base / "meshes"
    textures_dir = output_base / "textures"

    print("\n" + "=" * 60)
    print("  PRISM SURVIVORS - Enemy Generator")
    print("=" * 60)

    count = generate_all_enemies(meshes_dir, textures_dir)

    print(f"\nGenerated {count} enemies")
    print("=" * 60)
