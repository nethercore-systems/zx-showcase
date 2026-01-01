"""Override - Vent Wall Tile (8x8)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from .wall_solid import generate_wall_solid


def generate_wall_vent(palette: Dict[str, str]) -> PixelGrid:
    """Generate wall tile with vent (8x8)."""
    black = hex_to_rgba(palette["black"])
    light_metal = hex_to_rgba(palette["light_metal"])
    shadow = hex_to_rgba(palette["shadow"])

    tile = generate_wall_solid(palette)

    # Vent opening
    for y in range(2, 6):
        for x in range(2, 6):
            tile[y][x] = black
        tile[y][1] = light_metal
        tile[y][6] = shadow

    return tile
