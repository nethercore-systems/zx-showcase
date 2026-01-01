"""Override - Panel Floor Tile (8x8)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, add_noise, PixelGrid
from ..utils import create_grid


def generate_floor_panel(palette: Dict[str, str]) -> PixelGrid:
    """Generate clean panel floor tile (8x8)."""
    light_metal = hex_to_rgba(palette["light_metal"])
    highlight = hex_to_rgba(palette["highlight"])

    tile = create_grid(8, 8, light_metal)

    # Noise
    for y in range(8):
        for x in range(8):
            seed = (y * 8 + x) * 98765
            tile[y][x] = add_noise(light_metal, 2, seed)

    # Edge highlights
    for x in range(8):
        tile[0][x] = highlight
    for y in range(8):
        tile[y][0] = highlight

    return tile
