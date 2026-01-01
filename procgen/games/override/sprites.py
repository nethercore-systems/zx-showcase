"""
Override - Sprite Generation

Re-exports individual sprite generators from doors/, traps/, and characters/ subfolders.
"""

from pathlib import Path
from typing import Dict

from procgen.lib.pixel_art import export_png

# Re-export door generators
from .doors import (
    generate_door_closed,
    generate_door_open,
    generate_door_locked,
)

# Re-export trap generators
from .traps import (
    generate_trap_spike,
    generate_trap_gas,
    generate_trap_laser,
)

# Re-export character generators
from .characters import (
    generate_runner_idle,
    generate_drone_idle,
)


def generate_all_sprites(output_dir: Path, palette: Dict[str, str]) -> int:
    """
    Generate all sprites and save to output directory.

    Args:
        output_dir: Output directory
        palette: Color palette

    Returns:
        Number of sprites generated
    """
    count = 0

    # Doors
    doors_dir = output_dir / "doors"
    doors_dir.mkdir(exist_ok=True)

    door_sprites = {
        "door_closed": generate_door_closed(palette),
        "door_open": generate_door_open(palette),
        "door_locked": generate_door_locked(palette),
    }
    for name, pixels in door_sprites.items():
        export_png(pixels, doors_dir / f"{name}.png")
        print(f"  Exported: doors/{name}.png")
        count += 1

    # Traps
    traps_dir = output_dir / "traps"
    traps_dir.mkdir(exist_ok=True)

    trap_sprites = {
        "trap_spike": generate_trap_spike(palette),
        "trap_gas": generate_trap_gas(palette),
        "trap_laser": generate_trap_laser(palette),
    }
    for name, pixels in trap_sprites.items():
        export_png(pixels, traps_dir / f"{name}.png")
        print(f"  Exported: traps/{name}.png")
        count += 1

    # Characters
    chars_dir = output_dir / "characters"
    chars_dir.mkdir(exist_ok=True)

    # Runner idle frames
    for frame in range(4):
        pixels = generate_runner_idle(palette, frame)
        export_png(pixels, chars_dir / f"runner_idle_{frame}.png")
        print(f"  Exported: characters/runner_idle_{frame}.png")
        count += 1

    # Drone idle frames
    for frame in range(4):
        pixels = generate_drone_idle(palette, frame)
        export_png(pixels, chars_dir / f"drone_idle_{frame}.png")
        print(f"  Exported: characters/drone_idle_{frame}.png")
        count += 1

    return count


__all__ = [
    # Doors
    "generate_door_closed",
    "generate_door_open",
    "generate_door_locked",
    # Traps
    "generate_trap_spike",
    "generate_trap_gas",
    "generate_trap_laser",
    # Characters
    "generate_runner_idle",
    "generate_drone_idle",
    # Batch generator
    "generate_all_sprites",
]
