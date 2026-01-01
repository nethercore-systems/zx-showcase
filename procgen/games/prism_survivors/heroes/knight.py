"""PRISM SURVIVORS - Knight Hero

Heavy armored warrior with sword and shield.
Silhouette: Broad squared stance, large pauldrons, kite shield, tabard.
Triangle budget: ~1200 tris
"""

import math
from dataclasses import dataclass
from typing import Tuple

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mesh_utils import (
    BLENDER_AVAILABLE, clear_scene, create_prism, create_beveled_box,
    create_spike, create_sphere, join_objects, apply_transform,
    set_origin_to_bottom, get_tri_count, export_glb, create_material
)

if BLENDER_AVAILABLE:
    import bpy


@dataclass
class KnightSpec:
    """Knight hero specification."""
    name: str = "knight"
    color_primary: Tuple[float, float, float] = (0.35, 0.45, 0.6)  # Steel blue
    color_accent: Tuple[float, float, float] = (0.85, 0.7, 0.2)    # Gold trim
    color_glow: Tuple[float, float, float] = (0.3, 0.4, 0.8)       # Blue glow
    height: float = 1.8
    bulk: float = 1.2


KNIGHT_SPEC = KnightSpec()


def build_knight(spec: KnightSpec = None) -> 'bpy.types.Object':
    """
    Build Knight hero mesh with unique silhouette.

    Features:
    - Angular helmet with visor slit
    - Massive squared pauldrons
    - Kite shield (left arm)
    - Straight sword (right arm)
    - Tabard over armor
    - Wide planted stance

    Returns Blender object, call export_glb() to save.
    """
    if not BLENDER_AVAILABLE:
        raise RuntimeError("Blender not available")

    spec = spec or KNIGHT_SPEC
    clear_scene()
    parts = []

    h = spec.height
    bulk = spec.bulk

    # === HEAD (angular helmet with visor) ===
    helmet = create_beveled_box("helmet", (0.22 * bulk, 0.24, 0.26), bevel_width=0.02)
    helmet.location = (0, 0, h * 0.92)
    apply_transform(helmet)
    parts.append(helmet)

    # Visor slit (thin horizontal box)
    visor = create_beveled_box("visor", (0.18 * bulk, 0.03, 0.02), bevel_width=0.005)
    visor.location = (0, 0.12, h * 0.90)
    apply_transform(visor)
    parts.append(visor)

    # === TORSO (broad armored chest) ===
    chest = create_beveled_box("chest", (0.40 * bulk, 0.28, 0.50), bevel_width=0.03)
    chest.location = (0, 0, h * 0.68)
    apply_transform(chest)
    parts.append(chest)

    # Tabard (front cloth panel)
    tabard = create_beveled_box("tabard", (0.25 * bulk, 0.04, 0.35), bevel_width=0.01)
    tabard.location = (0, 0.14, h * 0.55)
    apply_transform(tabard)
    parts.append(tabard)

    # === SHOULDERS (massive squared pauldrons) ===
    for side in [-1, 1]:
        pauldron = create_beveled_box(f"pauldron_{side}", (0.20, 0.18, 0.22), bevel_width=0.02)
        pauldron.location = (side * 0.28 * bulk, 0, h * 0.78)
        apply_transform(pauldron)
        parts.append(pauldron)

        # Pauldron rim (raised edge)
        rim = create_prism(f"pauldron_rim_{side}", radius=0.11, height=0.04, segments=6)
        rim.location = (side * 0.28 * bulk, 0, h * 0.82)
        apply_transform(rim)
        parts.append(rim)

    # === ARMS ===
    for side in [-1, 1]:
        # Upper arm
        upper_arm = create_prism(f"upper_arm_{side}", radius=0.07 * bulk, height=0.28, segments=6)
        upper_arm.location = (side * 0.28 * bulk, 0, h * 0.58)
        apply_transform(upper_arm)
        parts.append(upper_arm)

        # Elbow guard
        elbow = create_beveled_box(f"elbow_{side}", (0.10, 0.10, 0.10), bevel_width=0.015)
        elbow.location = (side * 0.28 * bulk, 0, h * 0.48)
        apply_transform(elbow)
        parts.append(elbow)

        # Forearm
        forearm = create_prism(f"forearm_{side}", radius=0.06 * bulk, height=0.26, segments=6)
        forearm.location = (side * 0.28 * bulk, 0, h * 0.36)
        apply_transform(forearm)
        parts.append(forearm)

        # Gauntlet
        gauntlet = create_beveled_box(f"gauntlet_{side}", (0.09, 0.08, 0.12), bevel_width=0.01)
        gauntlet.location = (side * 0.28 * bulk, 0, h * 0.24)
        apply_transform(gauntlet)
        parts.append(gauntlet)

    # === SHIELD (left arm - kite shape) ===
    # Main shield body (tall narrow box)
    shield = create_beveled_box("shield", (0.04, 0.30, 0.50), bevel_width=0.02)
    shield.location = (-0.38 * bulk, 0.08, h * 0.50)
    shield.rotation_euler = (0, math.radians(-15), 0)
    apply_transform(shield)
    parts.append(shield)

    # Shield boss (center bump)
    boss = create_prism("shield_boss", radius=0.08, height=0.06, segments=6)
    boss.location = (-0.36 * bulk, 0.12, h * 0.55)
    boss.rotation_euler = (math.radians(90), 0, 0)
    apply_transform(boss)
    parts.append(boss)

    # === SWORD (right arm) ===
    # Blade
    blade = create_beveled_box("blade", (0.04, 0.06, 0.55), bevel_width=0.008)
    blade.location = (0.35 * bulk, 0.05, h * 0.45)
    apply_transform(blade)
    parts.append(blade)

    # Guard (crossguard)
    guard = create_beveled_box("guard", (0.03, 0.18, 0.04), bevel_width=0.005)
    guard.location = (0.35 * bulk, 0.05, h * 0.22)
    apply_transform(guard)
    parts.append(guard)

    # Handle
    handle = create_prism("handle", radius=0.025, height=0.12, segments=6)
    handle.location = (0.35 * bulk, 0.05, h * 0.15)
    apply_transform(handle)
    parts.append(handle)

    # Pommel
    pommel = create_sphere("pommel", radius=0.035, segments=6)
    pommel.location = (0.35 * bulk, 0.05, h * 0.08)
    apply_transform(pommel)
    parts.append(pommel)

    # === WAIST (belt and tassets) ===
    belt = create_beveled_box("belt", (0.38 * bulk, 0.22, 0.10), bevel_width=0.015)
    belt.location = (0, 0, h * 0.42)
    apply_transform(belt)
    parts.append(belt)

    # Tassets (hip armor plates)
    for side in [-1, 1]:
        tasset = create_beveled_box(f"tasset_{side}", (0.14, 0.12, 0.18), bevel_width=0.01)
        tasset.location = (side * 0.12 * bulk, 0.06, h * 0.35)
        apply_transform(tasset)
        parts.append(tasset)

    # === LEGS (wide stance) ===
    leg_spread = 0.14 * bulk
    for side in [-1, 1]:
        # Upper leg (thigh armor)
        thigh = create_prism(f"thigh_{side}", radius=0.10 * bulk, height=0.32, segments=6)
        thigh.location = (side * leg_spread, 0, h * 0.26)
        apply_transform(thigh)
        parts.append(thigh)

        # Knee guard
        knee = create_beveled_box(f"knee_{side}", (0.12, 0.12, 0.10), bevel_width=0.015)
        knee.location = (side * leg_spread, 0.04, h * 0.14)
        apply_transform(knee)
        parts.append(knee)

        # Lower leg (greave)
        greave = create_prism(f"greave_{side}", radius=0.08 * bulk, height=0.28, segments=6)
        greave.location = (side * leg_spread, 0, h * 0.06)
        apply_transform(greave)
        parts.append(greave)

        # Boot
        boot = create_beveled_box(f"boot_{side}", (0.10, 0.14, 0.08), bevel_width=0.01)
        boot.location = (side * leg_spread, 0.02, h * -0.04)
        apply_transform(boot)
        parts.append(boot)

    # === JOIN AND FINALIZE ===
    knight = join_objects(parts, "knight")

    # Apply material
    mat = create_material(
        "knight_mat",
        base_color=spec.color_primary,
        emission_color=spec.color_glow,
        emission_strength=0.3,
        metallic=0.8,
        roughness=0.4
    )
    knight.data.materials.append(mat)

    # Set origin to bottom center
    set_origin_to_bottom(knight)

    # Report triangle count
    tri_count = get_tri_count(knight)
    print(f"Knight: {tri_count} triangles (budget: 1200)")

    return knight


if __name__ == "__main__":
    import sys
    from pathlib import Path

    output_path = sys.argv[1] if len(sys.argv) > 1 else "knight.glb"

    knight = build_knight()
    export_glb(knight, output_path)
    print(f"Exported: {output_path}")
