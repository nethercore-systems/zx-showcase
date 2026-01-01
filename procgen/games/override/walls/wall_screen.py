"""Override - Screen Wall Tile (8x8)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from .wall_solid import generate_wall_solid


def generate_wall_screen(palette: Dict[str, str]) -> PixelGrid:
    """Generate wall tile with screen (8x8)."""
    black = hex_to_rgba(palette["black"])
    cyan = hex_to_rgba(palette["cyan"])
    metal = hex_to_rgba(palette["metal"])

    tile = generate_wall_solid(palette)

    # Screen background
    for y in range(2, 6):
        for x in range(2, 6):
            tile[y][x] = black

    # Glowing elements
    tile[3][3] = cyan
    tile[3][4] = cyan
    tile[4][3] = cyan

    # Frame
    for x in range(1, 7):
        tile[1][x] = metal
        tile[6][x] = metal
    for y in range(1, 7):
        tile[y][1] = metal
        tile[y][6] = metal

    return tile
