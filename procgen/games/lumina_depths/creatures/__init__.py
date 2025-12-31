"""Lumina Depths Creatures - One file per creature pattern.

Zone 1 (0-200m): Sunlit Waters
- reef_fish, sea_turtle, manta_ray, coral_crab

Zone 2 (200-1000m): Twilight Realm
- moon_jelly, lanternfish, siphonophore, giant_squid

Zone 3 (1000-4000m): Midnight Abyss
- anglerfish, gulper_eel, dumbo_octopus, vampire_squid

Zone 4 (4000-5000m): Hydrothermal Vents
- tube_worms, vent_shrimp, ghost_fish, vent_octopus
"""

from pathlib import Path
from typing import Dict, List, Tuple

from procgen.lib.mesh_primitives import write_obj

# Zone 1 creatures
from .zone1_reef_fish import generate_reef_fish
from .zone1_sea_turtle import generate_sea_turtle
from .zone1_manta_ray import generate_manta_ray
from .zone1_coral_crab import generate_coral_crab

# Zone 2 creatures
from .zone2_moon_jelly import generate_moon_jelly
from .zone2_lanternfish import generate_lanternfish

# Zone 3 creatures
from .zone3_anglerfish import generate_anglerfish

# Zone 4 creatures
from .zone4_tube_worms import generate_tube_worms


# Registry of all creatures
CREATURES: List[Tuple[str, callable, str, str]] = [
    # (filename, generator_func, display_name, zone)
    # Zone 1
    ("reef_fish", generate_reef_fish, "Reef Fish", "Zone 1: Sunlit Waters"),
    ("sea_turtle", generate_sea_turtle, "Sea Turtle", "Zone 1: Sunlit Waters"),
    ("manta_ray", generate_manta_ray, "Manta Ray", "Zone 1: Sunlit Waters"),
    ("coral_crab", generate_coral_crab, "Coral Crab", "Zone 1: Sunlit Waters"),
    # Zone 2
    ("moon_jelly", generate_moon_jelly, "Moon Jelly", "Zone 2: Twilight Realm"),
    ("lanternfish", generate_lanternfish, "Lanternfish", "Zone 2: Twilight Realm"),
    # Zone 3
    ("anglerfish", generate_anglerfish, "Anglerfish", "Zone 3: Midnight Abyss"),
    # Zone 4
    ("tube_worms", generate_tube_worms, "Tube Worms", "Zone 4: Hydrothermal Vents"),
]


def generate_all_creatures(output_dir: Path) -> int:
    """Generate all creature meshes."""
    count = 0

    for filename, generator, display_name, zone in CREATURES:
        print(f"Generating {display_name} ({zone})...")
        vertices, faces = generator()
        output_path = output_dir / f"{filename}.obj"

        write_obj(
            str(output_path),
            vertices, faces,
            name=display_name,
            comment=f"Lumina Depths - {zone}"
        )

        print(f"  -> {output_path.name}")
        print(f"     Vertices: {len(vertices)}, Faces: {len(faces)}")
        count += 1

    return count


def generate_zone_creatures(output_dir: Path, zone: int) -> int:
    """Generate creatures for a specific zone (1-4)."""
    zone_names = {
        1: "Zone 1: Sunlit Waters",
        2: "Zone 2: Twilight Realm",
        3: "Zone 3: Midnight Abyss",
        4: "Zone 4: Hydrothermal Vents",
    }

    zone_name = zone_names.get(zone)
    if not zone_name:
        raise ValueError(f"Invalid zone: {zone}")

    count = 0
    for filename, generator, display_name, creature_zone in CREATURES:
        if creature_zone == zone_name:
            print(f"Generating {display_name}...")
            vertices, faces = generator()
            output_path = output_dir / f"{filename}.obj"
            write_obj(str(output_path), vertices, faces, name=display_name)
            count += 1

    return count


__all__ = [
    "generate_all_creatures",
    "generate_zone_creatures",
    "CREATURES",
]
