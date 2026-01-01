"""Override - Doorframe Wall Tile (8x8)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from .wall_solid import generate_wall_solid


def generate_wall_doorframe(palette: Dict[str, str]) -> PixelGrid:
    """Generate wall tile with door frame (8x8)."""
    black = hex_to_rgba(palette["black"])
    light_metal = hex_to_rgba(palette["light_metal"])

    tile = generate_wall_solid(palette)

    # Door opening
    for y in range(8):
        tile[y][0] = light_metal
        tile[y][7] = light_metal
        for x in range(2, 6):
            tile[y][x] = black

    return tile
