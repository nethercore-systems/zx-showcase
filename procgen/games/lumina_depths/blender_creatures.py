"""
Lumina Depths - Blender-based Creature Generation using Metaballs.

This module generates all creatures for Lumina Depths using Blender's metaball
system for smooth, organic forms with proper bioluminescence materials.

Usage (via run_blender.py):
    blender --background --python run_blender.py -- --game lumina-depths --all
"""

from pathlib import Path
from typing import Dict, Tuple, Optional
import math

try:
    import bpy
    from procgen.core.blender_metaball import (
        MetaballCreature, export_metaball_creature,
        create_jellyfish, create_fish, create_octopus, create_turtle,
        create_manta_ray, create_anglerfish, create_squid, create_crab,
    )
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False


# === ZONE 1: SUNLIT WATERS (0-200m) ===
# Warm, colorful creatures with subtle bioluminescence

def generate_reef_fish(output_dir: Path) -> Path:
    """Colorful tropical reef fish."""
    creature = MetaballCreature("reef_fish", resolution=0.05)

    # Compact, tall body typical of reef fish
    creature.add_ball(0, 0, 0, 0.12, stiffness=1.5)
    creature.add_ball(0, 0.05, 0, 0.1, stiffness=2.0)
    creature.add_ball(0, -0.04, 0, 0.09, stiffness=2.0)

    # Tall dorsal fin
    creature.add_ellipsoid(0, 0.12, 0, 0.06, size_x=0.2, size_y=1.5, size_z=0.8, stiffness=3.5)

    # Tail fin (forked)
    creature.add_ellipsoid(0, 0.02, -0.18, 0.05, size_x=0.15, size_y=1.5, size_z=0.8, stiffness=3.0)
    creature.add_ellipsoid(0, -0.02, -0.18, 0.05, size_x=0.15, size_y=1.5, size_z=0.8, stiffness=3.0)

    # Head/snout
    creature.add_ball(0, 0, 0.12, 0.08, stiffness=2.0)
    creature.add_ball(0, 0, 0.18, 0.04, stiffness=3.0)

    # Pectoral fins
    for side in [-1, 1]:
        creature.add_ellipsoid(
            side * 0.1, -0.02, 0.05,
            0.04, size_x=0.3, size_y=1.0, size_z=0.5, stiffness=4.0
        )

    return export_metaball_creature(
        creature, output_dir / "reef_fish.glb",
        base_color=(0.9, 0.5, 0.2),  # Warm orange
        emission_color=(1.0, 0.8, 0.3),  # Subtle golden glow
        emission_strength=0.2,
        roughness=0.3,
        subsurface=0.15,
    )


def generate_sea_turtle(output_dir: Path) -> Path:
    """Graceful sea turtle with dome shell."""
    creature = create_turtle("sea_turtle", size=1.0)

    return export_metaball_creature(
        creature, output_dir / "sea_turtle.glb",
        base_color=(0.4, 0.5, 0.35),  # Olive green
        emission_color=None,  # No bioluminescence
        roughness=0.5,
        subsurface=0.1,
    )


def generate_manta_ray(output_dir: Path) -> Path:
    """Majestic manta ray with wide wings."""
    creature = create_manta_ray("manta_ray", size=1.2)

    return export_metaball_creature(
        creature, output_dir / "manta_ray.glb",
        base_color=(0.15, 0.15, 0.2),  # Dark blue-gray top
        emission_color=(0.3, 0.4, 0.5),  # Subtle blue shimmer on belly
        emission_strength=0.15,
        roughness=0.35,
        subsurface=0.1,
    )


def generate_coral_crab(output_dir: Path) -> Path:
    """Small colorful crab found in coral reefs."""
    creature = create_crab("coral_crab", size=0.6)

    return export_metaball_creature(
        creature, output_dir / "coral_crab.glb",
        base_color=(0.8, 0.3, 0.2),  # Coral red
        emission_color=None,
        roughness=0.6,
        subsurface=0.05,
    )


# === ZONE 2: TWILIGHT REALM (200-1000m) ===
# Ethereal creatures with increasing bioluminescence

def generate_moon_jelly(output_dir: Path) -> Path:
    """Translucent moon jellyfish with gentle pulsing glow."""
    creature = create_jellyfish("moon_jelly", size=0.8)

    return export_metaball_creature(
        creature, output_dir / "moon_jelly.glb",
        base_color=(0.7, 0.75, 0.9),  # Pale blue-white
        emission_color=(0.6, 0.7, 1.0),  # Blue glow
        emission_strength=0.6,
        roughness=0.2,
        subsurface=0.4,
        alpha=0.85,  # Translucent
    )


def generate_lanternfish(output_dir: Path) -> Path:
    """Small fish with bioluminescent photophores."""
    creature = MetaballCreature("lanternfish", resolution=0.05)

    # Slender body
    for i in range(4):
        t = i / 3
        z = -0.12 + t * 0.24
        radius = 0.06 * (1.0 - 0.5 * abs(t - 0.4))
        creature.add_ball(0, 0, z, radius, stiffness=1.8)

    # Large eyes (typical of twilight zone fish)
    for side in [-1, 1]:
        creature.add_ball(side * 0.04, 0.02, 0.1, 0.025, stiffness=3.0)

    # Dorsal fin
    creature.add_ellipsoid(0, 0.06, 0, 0.03, size_x=0.2, size_y=1.2, size_z=0.6, stiffness=4.0)

    # Tail
    creature.add_ellipsoid(0, 0, -0.18, 0.04, size_x=0.2, size_y=1.3, size_z=0.8, stiffness=3.5)

    # Photophore spots along body (represented as small balls)
    for i in range(4):
        z = -0.08 + i * 0.06
        creature.add_ball(0, -0.03, z, 0.012, stiffness=5.0)

    return export_metaball_creature(
        creature, output_dir / "lanternfish.glb",
        base_color=(0.2, 0.25, 0.35),  # Dark blue-gray
        emission_color=(0.3, 0.8, 0.9),  # Cyan photophores
        emission_strength=1.2,
        roughness=0.35,
        subsurface=0.15,
    )


def generate_siphonophore(output_dir: Path) -> Path:
    """Colonial organism - chain of connected units."""
    creature = MetaballCreature("siphonophore", resolution=0.04)

    # Main float (pneumatophore)
    creature.add_ball(0, 0, 0.3, 0.08, stiffness=1.5)
    creature.add_ball(0, 0, 0.25, 0.06, stiffness=2.0)

    # Chain of zooids (repeating units)
    for i in range(8):
        z = 0.2 - i * 0.08
        # Main body unit
        creature.add_ball(0, 0, z, 0.04, stiffness=2.5)
        # Side tentacles
        if i % 2 == 0:
            for side in [-1, 1]:
                creature.add_chain(
                    start=(side * 0.03, 0, z),
                    end=(side * 0.15, 0, z - 0.1),
                    count=4,
                    radius_start=0.015,
                    radius_end=0.005,
                    stiffness=4.0
                )

    # Trailing tentacles
    for angle in [0, math.pi * 0.5, math.pi, math.pi * 1.5]:
        x = 0.02 * math.cos(angle)
        y = 0.02 * math.sin(angle)
        creature.add_chain(
            start=(x, y, -0.4),
            end=(x * 2, y * 2, -0.8),
            count=6,
            radius_start=0.01,
            radius_end=0.003,
            stiffness=4.5
        )

    return export_metaball_creature(
        creature, output_dir / "siphonophore.glb",
        base_color=(0.9, 0.4, 0.5),  # Pinkish
        emission_color=(1.0, 0.5, 0.6),  # Pink glow
        emission_strength=0.8,
        roughness=0.2,
        subsurface=0.35,
        alpha=0.9,
    )


def generate_giant_squid(output_dir: Path) -> Path:
    """Massive squid from the twilight zone."""
    creature = create_squid("giant_squid", size=1.5)

    return export_metaball_creature(
        creature, output_dir / "giant_squid.glb",
        base_color=(0.5, 0.2, 0.25),  # Deep red
        emission_color=(0.4, 0.3, 0.5),  # Purple bioluminescence
        emission_strength=0.4,
        roughness=0.3,
        subsurface=0.2,
    )


# === ZONE 3: MIDNIGHT ABYSS (1000-4000m) ===
# Alien creatures with intense bioluminescence

def generate_anglerfish(output_dir: Path) -> Path:
    """Deep-sea anglerfish with glowing lure."""
    creature = create_anglerfish("anglerfish", size=1.0)

    return export_metaball_creature(
        creature, output_dir / "anglerfish.glb",
        base_color=(0.15, 0.1, 0.12),  # Nearly black
        emission_color=(0.2, 0.9, 0.7),  # Bright teal lure
        emission_strength=2.0,  # Intense glow on lure
        roughness=0.6,
        subsurface=0.1,
    )


def generate_gulper_eel(output_dir: Path) -> Path:
    """Bizarre eel with enormous hinged jaws."""
    creature = MetaballCreature("gulper_eel", resolution=0.05)

    # Huge head/jaw
    creature.add_ellipsoid(0, 0, 0.15, 0.15, size_x=1.0, size_y=0.8, size_z=1.5, stiffness=1.2)
    creature.add_ellipsoid(0, -0.08, 0.2, 0.12, size_x=1.2, size_y=0.6, size_z=1.3, stiffness=1.5)

    # Long tapered tail-body
    for i in range(10):
        t = i / 9
        z = 0 - t * 0.8
        radius = 0.08 * (1.0 - t * 0.9)
        creature.add_ball(0, 0, z, radius, stiffness=2.0 + t)

    # Bioluminescent tail tip
    creature.add_ball(0, 0, -0.85, 0.02, stiffness=4.0)

    return export_metaball_creature(
        creature, output_dir / "gulper_eel.glb",
        base_color=(0.1, 0.08, 0.1),  # Black
        emission_color=(1.0, 0.3, 0.5),  # Pink tail glow
        emission_strength=1.5,
        roughness=0.5,
        subsurface=0.1,
    )


def generate_dumbo_octopus(output_dir: Path) -> Path:
    """Cute octopus with ear-like fins."""
    creature = MetaballCreature("dumbo_octopus", resolution=0.06)

    # Round body/mantle
    creature.add_ball(0, 0, 0, 0.18, stiffness=1.2)
    creature.add_ball(0, 0, 0.1, 0.15, stiffness=1.5)

    # "Ear" fins
    for side in [-1, 1]:
        creature.add_ellipsoid(
            side * 0.15, 0.05, 0.05,
            0.1, size_x=0.3, size_y=1.5, size_z=1.0, stiffness=2.5
        )

    # Short stubby arms (8)
    for i in range(8):
        angle = (math.pi / 4) * i
        x = 0.1 * math.cos(angle)
        y = 0.1 * math.sin(angle)
        creature.add_chain(
            start=(x, y, -0.1),
            end=(x * 2, y * 2, -0.25),
            count=4,
            radius_start=0.04,
            radius_end=0.02,
            stiffness=3.0
        )

    return export_metaball_creature(
        creature, output_dir / "dumbo_octopus.glb",
        base_color=(0.7, 0.5, 0.6),  # Pinkish
        emission_color=(0.8, 0.6, 0.7),  # Soft pink glow
        emission_strength=0.5,
        roughness=0.3,
        subsurface=0.3,
    )


def generate_vampire_squid(output_dir: Path) -> Path:
    """Vampire squid with webbed arms and photophores."""
    creature = MetaballCreature("vampire_squid", resolution=0.06)

    # Bell-shaped body
    creature.add_ball(0, 0, 0.1, 0.15, stiffness=1.5)
    creature.add_ball(0, 0, 0.2, 0.12, stiffness=2.0)
    creature.add_ball(0, 0, 0, 0.13, stiffness=1.8)

    # Large eyes
    for side in [-1, 1]:
        creature.add_ball(side * 0.08, 0.03, 0.12, 0.04, stiffness=3.0)

    # Webbed arms (8, connected by web represented by overlapping balls)
    for i in range(8):
        angle = (math.pi / 4) * i
        x = 0.08 * math.cos(angle)
        y = 0.08 * math.sin(angle)
        creature.add_chain(
            start=(x, y, -0.05),
            end=(x * 2.5, y * 2.5, -0.2),
            count=4,
            radius_start=0.035,
            radius_end=0.02,
            stiffness=2.5
        )

    # Web between arms (represented by larger overlapping balls)
    for i in range(8):
        angle = (math.pi / 4) * i + (math.pi / 8)
        x = 0.1 * math.cos(angle)
        y = 0.1 * math.sin(angle)
        creature.add_ball(x, y, -0.08, 0.05, stiffness=3.0)

    # Filaments (two long trailing appendages)
    for side in [-1, 1]:
        creature.add_chain(
            start=(side * 0.05, 0, -0.1),
            end=(side * 0.15, 0, -0.5),
            count=6,
            radius_start=0.015,
            radius_end=0.005,
            stiffness=4.0
        )

    return export_metaball_creature(
        creature, output_dir / "vampire_squid.glb",
        base_color=(0.3, 0.1, 0.15),  # Dark red-black
        emission_color=(0.2, 0.5, 1.0),  # Blue photophores
        emission_strength=1.0,
        roughness=0.4,
        subsurface=0.2,
    )


# === ZONE 4: HYDROTHERMAL VENTS (4000m+) ===
# Chemosynthetic creatures adapted to extreme conditions

def generate_tube_worms(output_dir: Path) -> Path:
    """Giant tube worms clustered around vents."""
    creature = MetaballCreature("tube_worms", resolution=0.05)

    # Multiple tubes in a cluster
    tube_positions = [
        (0, 0, 1.0),
        (0.08, 0.05, 0.85),
        (-0.06, 0.07, 0.9),
        (0.04, -0.08, 0.75),
        (-0.09, -0.03, 0.8),
    ]

    for tx, ty, height in tube_positions:
        # Tube body
        for i in range(6):
            t = i / 5
            z = t * height * 0.8
            creature.add_ball(tx, ty, z, 0.025, stiffness=2.5)

        # Red plume at top
        for j in range(3):
            angle = (2 * math.pi / 3) * j
            px = tx + 0.02 * math.cos(angle)
            py = ty + 0.02 * math.sin(angle)
            creature.add_ball(px, py, height * 0.85, 0.03, stiffness=2.0)
            creature.add_ball(px * 1.3, py * 1.3, height * 0.9, 0.02, stiffness=3.0)

    return export_metaball_creature(
        creature, output_dir / "tube_worms.glb",
        base_color=(0.85, 0.85, 0.8),  # White tubes
        emission_color=(1.0, 0.2, 0.1),  # Red plume glow
        emission_strength=0.6,
        roughness=0.5,
        subsurface=0.15,
    )


def generate_vent_shrimp(output_dir: Path) -> Path:
    """Blind shrimp adapted to hydrothermal vents."""
    creature = MetaballCreature("vent_shrimp", resolution=0.05)

    # Segmented body
    for i in range(6):
        t = i / 5
        z = -0.15 + t * 0.3
        radius = 0.04 * (1.0 - 0.3 * abs(t - 0.5))
        creature.add_ball(0, 0, z, radius, stiffness=2.0)

    # Tail fan
    creature.add_ellipsoid(0, 0, -0.2, 0.04, size_x=0.2, size_y=1.5, size_z=0.8, stiffness=3.0)

    # Antennae (long)
    for side in [-1, 1]:
        creature.add_chain(
            start=(side * 0.02, 0, 0.15),
            end=(side * 0.1, 0, 0.35),
            count=4,
            radius_start=0.008,
            radius_end=0.003,
            stiffness=5.0
        )

    # Walking legs
    for i, z_pos in enumerate([-0.05, 0, 0.05, 0.1]):
        for side in [-1, 1]:
            creature.add_chain(
                start=(side * 0.03, -0.02, z_pos),
                end=(side * 0.08, -0.06, z_pos - 0.02),
                count=2,
                radius_start=0.008,
                radius_end=0.005,
                stiffness=4.5
            )

    return export_metaball_creature(
        creature, output_dir / "vent_shrimp.glb",
        base_color=(0.9, 0.85, 0.8),  # Pale/translucent
        emission_color=(1.0, 0.6, 0.4),  # Warm glow from bacteria
        emission_strength=0.3,
        roughness=0.4,
        subsurface=0.25,
        alpha=0.95,
    )


def generate_ghost_fish(output_dir: Path) -> Path:
    """Translucent hadal zone fish."""
    creature = create_fish("ghost_fish", size=0.8, elongation=1.2)

    return export_metaball_creature(
        creature, output_dir / "ghost_fish.glb",
        base_color=(0.9, 0.9, 0.95),  # Nearly white
        emission_color=(0.8, 0.9, 1.0),  # Faint blue
        emission_strength=0.3,
        roughness=0.2,
        subsurface=0.5,
        alpha=0.8,  # Translucent
    )


def generate_vent_octopus(output_dir: Path) -> Path:
    """Small octopus adapted to vent environments."""
    creature = create_octopus("vent_octopus", size=0.7)

    return export_metaball_creature(
        creature, output_dir / "vent_octopus.glb",
        base_color=(0.6, 0.5, 0.55),  # Pale purple-gray
        emission_color=(0.8, 0.7, 0.9),  # Lavender glow
        emission_strength=0.4,
        roughness=0.35,
        subsurface=0.25,
    )


# === EPIC ENCOUNTERS ===

def generate_blue_whale(output_dir: Path) -> Path:
    """Majestic blue whale - largest creature."""
    creature = MetaballCreature("blue_whale", resolution=0.08)

    # Massive body
    for i in range(8):
        t = i / 7
        z = -1.5 + t * 3.0
        # Taper at both ends, widest in middle
        width = 0.4 * (1.0 - 0.7 * abs(t - 0.4) ** 1.5)
        creature.add_ball(0, 0, z, width, stiffness=1.0)

    # Head - broader, blunter
    creature.add_ball(0, 0.05, 1.6, 0.35, stiffness=1.2)
    creature.add_ball(0, 0.1, 1.75, 0.25, stiffness=1.5)

    # Lower jaw
    creature.add_ellipsoid(0, -0.15, 1.4, 0.3, size_x=0.8, size_y=0.4, size_z=1.2, stiffness=1.5)

    # Flippers
    for side in [-1, 1]:
        creature.add_ellipsoid(
            side * 0.35, -0.1, 0.5,
            0.2, size_x=2.0, size_y=0.25, size_z=0.6, stiffness=2.0
        )

    # Dorsal fin (small for blue whale)
    creature.add_ellipsoid(0, 0.25, -0.8, 0.1, size_x=0.2, size_y=1.2, size_z=0.6, stiffness=3.0)

    # Tail flukes
    for side in [-1, 1]:
        creature.add_ellipsoid(
            side * 0.35, 0, -1.6,
            0.18, size_x=1.5, size_y=0.2, size_z=0.8, stiffness=2.5
        )

    return export_metaball_creature(
        creature, output_dir / "blue_whale.glb",
        base_color=(0.35, 0.45, 0.55),  # Blue-gray
        emission_color=None,
        roughness=0.4,
        subsurface=0.1,
        decimate_ratio=0.6,  # Reduce poly count for this large mesh
    )


def generate_sperm_whale(output_dir: Path) -> Path:
    """Deep-diving sperm whale with massive head."""
    creature = MetaballCreature("sperm_whale", resolution=0.08)

    # Distinctive huge head (1/3 of body length)
    creature.add_ball(0, 0, 1.2, 0.45, stiffness=1.0)
    creature.add_ball(0, 0.1, 1.0, 0.4, stiffness=1.2)
    creature.add_ball(0, 0.15, 0.7, 0.35, stiffness=1.3)

    # Narrower body
    for i in range(6):
        t = i / 5
        z = 0.5 - t * 2.0
        radius = 0.3 * (1.0 - t * 0.6)
        creature.add_ball(0, 0, z, radius, stiffness=1.5)

    # Lower jaw (narrow)
    creature.add_ellipsoid(0, -0.25, 0.9, 0.15, size_x=0.6, size_y=0.3, size_z=1.5, stiffness=2.0)

    # Flippers (small relative to body)
    for side in [-1, 1]:
        creature.add_ellipsoid(
            side * 0.25, -0.15, 0.3,
            0.12, size_x=1.5, size_y=0.2, size_z=0.5, stiffness=2.5
        )

    # Dorsal hump (no true fin)
    creature.add_ball(0, 0.2, -0.5, 0.12, stiffness=2.0)

    # Tail flukes
    for side in [-1, 1]:
        creature.add_ellipsoid(
            side * 0.3, 0, -1.6,
            0.15, size_x=1.3, size_y=0.2, size_z=0.7, stiffness=2.5
        )

    return export_metaball_creature(
        creature, output_dir / "sperm_whale.glb",
        base_color=(0.3, 0.3, 0.35),  # Dark gray
        emission_color=None,
        roughness=0.45,
        subsurface=0.1,
        decimate_ratio=0.6,
    )


def generate_giant_isopod(output_dir: Path) -> Path:
    """Giant deep-sea isopod."""
    creature = MetaballCreature("giant_isopod", resolution=0.05)

    # Segmented armored body
    for i in range(7):
        t = i / 6
        z = -0.2 + t * 0.4
        # Oval cross-section
        creature.add_ellipsoid(
            0, 0, z,
            0.08, size_x=1.0, size_y=0.6, size_z=0.7, stiffness=1.8
        )

    # Head
    creature.add_ball(0, 0, 0.25, 0.07, stiffness=2.0)

    # Compound eyes
    for side in [-1, 1]:
        creature.add_ball(side * 0.04, 0.02, 0.28, 0.025, stiffness=3.5)

    # Antennae
    for side in [-1, 1]:
        creature.add_chain(
            start=(side * 0.03, 0.01, 0.3),
            end=(side * 0.08, 0.02, 0.4),
            count=3,
            radius_start=0.01,
            radius_end=0.005,
            stiffness=4.0
        )

    # Tail (telson)
    creature.add_ellipsoid(0, 0, -0.28, 0.06, size_x=1.0, size_y=0.5, size_z=0.8, stiffness=2.5)

    # Legs (7 pairs)
    for i in range(7):
        z = -0.15 + i * 0.05
        for side in [-1, 1]:
            creature.add_chain(
                start=(side * 0.06, -0.02, z),
                end=(side * 0.12, -0.08, z),
                count=2,
                radius_start=0.012,
                radius_end=0.008,
                stiffness=4.0
            )

    return export_metaball_creature(
        creature, output_dir / "giant_isopod.glb",
        base_color=(0.6, 0.55, 0.5),  # Pale tan
        emission_color=None,
        roughness=0.6,
        subsurface=0.05,
    )


# === PLAYER VEHICLE ===

def generate_submersible(output_dir: Path) -> Path:
    """Player's deep-sea submersible vehicle."""
    creature = MetaballCreature("submersible", resolution=0.06)

    # Main pressure hull (rounded cylinder)
    for i in range(5):
        t = i / 4
        z = -0.3 + t * 0.6
        creature.add_ball(0, 0, z, 0.15, stiffness=1.5)

    # Viewport dome (front)
    creature.add_ball(0, 0.03, 0.35, 0.12, stiffness=2.0)
    creature.add_ball(0, 0.05, 0.42, 0.08, stiffness=2.5)

    # Engine housing (rear)
    creature.add_ellipsoid(0, 0, -0.4, 0.12, size_x=1.0, size_y=1.0, size_z=1.5, stiffness=2.0)

    # Propeller shroud
    creature.add_ellipsoid(0, 0, -0.55, 0.08, size_x=1.5, size_y=1.5, size_z=0.5, stiffness=3.0)

    # Side thrusters
    for side in [-1, 1]:
        creature.add_ellipsoid(
            side * 0.18, 0, 0,
            0.05, size_x=0.5, size_y=0.5, size_z=1.2, stiffness=3.0
        )

    # Light arrays (front)
    for side in [-1, 1]:
        creature.add_ball(side * 0.1, 0.08, 0.35, 0.03, stiffness=4.0)

    # Manipulator arms (folded)
    for side in [-1, 1]:
        creature.add_chain(
            start=(side * 0.12, -0.05, 0.2),
            end=(side * 0.15, -0.1, 0.05),
            count=3,
            radius_start=0.025,
            radius_end=0.018,
            stiffness=3.5
        )

    return export_metaball_creature(
        creature, output_dir / "submersible.glb",
        base_color=(0.2, 0.3, 0.4),  # Dark blue-gray
        emission_color=(1.0, 0.95, 0.8),  # Warm light from viewport
        emission_strength=0.8,
        roughness=0.3,
        subsurface=0.0,
    )


# === GENERATION FUNCTIONS ===

def generate_all_zone1(output_dir: Path) -> int:
    """Generate all Zone 1 creatures."""
    print("\n=== Zone 1: Sunlit Waters ===")
    generate_reef_fish(output_dir)
    generate_sea_turtle(output_dir)
    generate_manta_ray(output_dir)
    generate_coral_crab(output_dir)
    return 4


def generate_all_zone2(output_dir: Path) -> int:
    """Generate all Zone 2 creatures."""
    print("\n=== Zone 2: Twilight Realm ===")
    generate_moon_jelly(output_dir)
    generate_lanternfish(output_dir)
    generate_siphonophore(output_dir)
    generate_giant_squid(output_dir)
    return 4


def generate_all_zone3(output_dir: Path) -> int:
    """Generate all Zone 3 creatures."""
    print("\n=== Zone 3: Midnight Abyss ===")
    generate_anglerfish(output_dir)
    generate_gulper_eel(output_dir)
    generate_dumbo_octopus(output_dir)
    generate_vampire_squid(output_dir)
    return 4


def generate_all_zone4(output_dir: Path) -> int:
    """Generate all Zone 4 creatures."""
    print("\n=== Zone 4: Hydrothermal Vents ===")
    generate_tube_worms(output_dir)
    generate_vent_shrimp(output_dir)
    generate_ghost_fish(output_dir)
    generate_vent_octopus(output_dir)
    return 4


def generate_all_epic(output_dir: Path) -> int:
    """Generate all epic encounter creatures."""
    print("\n=== Epic Encounters ===")
    generate_blue_whale(output_dir)
    generate_sperm_whale(output_dir)
    generate_giant_isopod(output_dir)
    return 3


def generate_all_creatures(output_dir: Path) -> int:
    """Generate all lumina-depths creatures."""
    count = 0
    count += generate_all_zone1(output_dir)
    count += generate_all_zone2(output_dir)
    count += generate_all_zone3(output_dir)
    count += generate_all_zone4(output_dir)
    count += generate_all_epic(output_dir)

    print("\n=== Player Vehicle ===")
    generate_submersible(output_dir)
    count += 1

    return count


# Map of all generators for individual asset generation
CREATURE_GENERATORS = {
    # Zone 1
    "reef_fish": generate_reef_fish,
    "sea_turtle": generate_sea_turtle,
    "manta_ray": generate_manta_ray,
    "coral_crab": generate_coral_crab,
    # Zone 2
    "moon_jelly": generate_moon_jelly,
    "lanternfish": generate_lanternfish,
    "siphonophore": generate_siphonophore,
    "giant_squid": generate_giant_squid,
    # Zone 3
    "anglerfish": generate_anglerfish,
    "gulper_eel": generate_gulper_eel,
    "dumbo_octopus": generate_dumbo_octopus,
    "vampire_squid": generate_vampire_squid,
    # Zone 4
    "tube_worms": generate_tube_worms,
    "vent_shrimp": generate_vent_shrimp,
    "ghost_fish": generate_ghost_fish,
    "vent_octopus": generate_vent_octopus,
    # Epic
    "blue_whale": generate_blue_whale,
    "sperm_whale": generate_sperm_whale,
    "giant_isopod": generate_giant_isopod,
    # Player
    "submersible": generate_submersible,
}
