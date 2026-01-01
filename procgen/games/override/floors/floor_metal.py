"""Override - Metal Floor Tile (8x8)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, blend, add_noise, PixelGrid
from ..utils import create_grid


def generate_floor_metal(palette: Dict[str, str]) -> PixelGrid:
    """Generate metal floor tile (8x8)."""
    metal = hex_to_rgba(palette["metal"])
    dark_metal = hex_to_rgba(palette["dark_metal"])
    shadow = hex_to_rgba(palette["shadow"])
    light_metal = hex_to_rgba(palette["light_metal"])
    highlight = hex_to_rgba(palette["highlight"])

    tile = create_grid(8, 8, metal)

    # Base gradient with noise
    for y in range(8):
        for x in range(8):
            t = (x + y) / 16.0
            color = blend(metal, dark_metal, t * 0.3)
            seed = (y * 8 + x) * 12345
            tile[y][x] = add_noise(color, 3, seed)

    # Panel lines
    for x in range(8):
        tile[0][x] = shadow
        tile[7][x] = light_metal
    for y in range(8):
        tile[y][0] = shadow

    # Rivets
    tile[1][1] = highlight
    tile[1][6] = highlight
    tile[6][1] = highlight
    tile[6][6] = highlight

    return tile
