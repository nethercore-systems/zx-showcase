"""Override - Pipe Wall Tile (8x8)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from .wall_solid import generate_wall_solid


def generate_wall_pipe(palette: Dict[str, str]) -> PixelGrid:
    """Generate wall tile with pipe (8x8)."""
    shadow = hex_to_rgba(palette["shadow"])
    metal = hex_to_rgba(palette["metal"])
    light_metal = hex_to_rgba(palette["light_metal"])

    tile = generate_wall_solid(palette)

    # Vertical pipe
    for y in range(8):
        tile[y][2] = shadow
        tile[y][3] = metal
        tile[y][4] = light_metal

    # Pipe joint
    for x in range(2, 5):
        tile[4][x] = metal

    return tile
