"""
Override - Tileset Generation

Re-exports individual tile generators from floors/ and walls/ subfolders.
"""

from pathlib import Path
from typing import Dict

from procgen.lib.pixel_art import export_png

# Re-export floor generators
from .floors import (
    generate_floor_metal,
    generate_floor_grate,
    generate_floor_panel,
    generate_floor_damaged,
)

# Re-export wall generators
from .walls import (
    generate_wall_solid,
    generate_wall_window,
    generate_wall_vent,
    generate_wall_pipe,
    generate_wall_screen,
    generate_wall_doorframe,
)


def generate_all_tilesets(output_dir: Path, palette: Dict[str, str]) -> int:
    """
    Generate all tilesets and save to output directory.

    Args:
        output_dir: Output directory
        palette: Color palette

    Returns:
        Number of tiles generated
    """
    tiles = {
        "floor_metal": generate_floor_metal(palette),
        "floor_grate": generate_floor_grate(palette),
        "floor_panel": generate_floor_panel(palette),
        "floor_damaged": generate_floor_damaged(palette),
        "wall_solid": generate_wall_solid(palette),
        "wall_window": generate_wall_window(palette),
        "wall_vent": generate_wall_vent(palette),
        "wall_pipe": generate_wall_pipe(palette),
        "wall_screen": generate_wall_screen(palette),
        "wall_doorframe": generate_wall_doorframe(palette),
    }

    for name, pixels in tiles.items():
        filepath = output_dir / f"{name}.png"
        export_png(pixels, filepath)
        print(f"  Exported: {name}.png")

    return len(tiles)


__all__ = [
    # Floors
    "generate_floor_metal",
    "generate_floor_grate",
    "generate_floor_panel",
    "generate_floor_damaged",
    # Walls
    "generate_wall_solid",
    "generate_wall_window",
    "generate_wall_vent",
    "generate_wall_pipe",
    "generate_wall_screen",
    "generate_wall_doorframe",
    # Batch generator
    "generate_all_tilesets",
]
