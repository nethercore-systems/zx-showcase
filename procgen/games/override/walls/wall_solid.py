"""Override - Solid Wall Tile (8x8)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, blend, add_noise, PixelGrid
from ..utils import create_grid


def generate_wall_solid(palette: Dict[str, str]) -> PixelGrid:
    """Generate solid wall tile (8x8)."""
    dark_metal = hex_to_rgba(palette["dark_metal"])
    shadow = hex_to_rgba(palette["shadow"])
    metal = hex_to_rgba(palette["metal"])

    tile = create_grid(8, 8, dark_metal)

    # Vertical gradient with noise
    for y in range(8):
        for x in range(8):
            t = y / 8.0
            color = blend(dark_metal, shadow, t * 0.3)
            seed = (y * 8 + x) * 11111
            tile[y][x] = add_noise(color, 3, seed)

    # Horizontal details
    for x in range(8):
        tile[0][x] = metal
        tile[4][x] = shadow

    return tile
