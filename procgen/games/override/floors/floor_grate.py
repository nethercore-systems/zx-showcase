"""Override - Grate Floor Tile (8x8)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, add_noise, PixelGrid
from ..utils import create_grid


def generate_floor_grate(palette: Dict[str, str]) -> PixelGrid:
    """Generate grate floor tile (8x8)."""
    metal = hex_to_rgba(palette["metal"])
    dark_bg = hex_to_rgba(palette["dark_bg"])
    light_metal = hex_to_rgba(palette["light_metal"])

    tile = create_grid(8, 8, metal)

    # Base metal with noise
    for y in range(8):
        for x in range(8):
            seed = (y * 8 + x) * 54321
            tile[y][x] = add_noise(metal, 2, seed)

    # Grate holes
    for y in range(1, 7, 2):
        for x in range(1, 7, 2):
            tile[y][x] = dark_bg
            if x + 1 < 8:
                tile[y][x + 1] = dark_bg

    # Horizontal bars
    for x in range(8):
        tile[0][x] = light_metal
        tile[3][x] = light_metal
        tile[6][x] = light_metal

    return tile
