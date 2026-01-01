"""Override - Window Wall Tile (8x8)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, blend, PixelGrid
from .wall_solid import generate_wall_solid


def generate_wall_window(palette: Dict[str, str]) -> PixelGrid:
    """Generate wall tile with window (8x8)."""
    glass = hex_to_rgba(palette.get("glass", "#55697D"))
    glass_dark = hex_to_rgba(palette.get("glass_dark", "#2D3744"))
    light_metal = hex_to_rgba(palette["light_metal"])

    tile = generate_wall_solid(palette)

    # Window glass
    for y in range(2, 6):
        for x in range(2, 6):
            t = (y - 2) / 4.0
            tile[y][x] = blend(glass, glass_dark, t)

    # Frame
    for x in range(1, 7):
        tile[1][x] = light_metal
        tile[6][x] = light_metal
    for y in range(1, 7):
        tile[y][1] = light_metal
        tile[y][6] = light_metal

    return tile
