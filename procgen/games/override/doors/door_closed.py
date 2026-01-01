"""Override - Closed Door Sprite (8x16)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, add_noise, PixelGrid
from ..utils import create_grid


def generate_door_closed(palette: Dict[str, str]) -> PixelGrid:
    """Generate closed door sprite (8x16)."""
    dark_metal = hex_to_rgba(palette["dark_metal"])
    shadow = hex_to_rgba(palette["shadow"])
    light_metal = hex_to_rgba(palette["light_metal"])
    yellow = hex_to_rgba(palette["yellow"])

    sprite = create_grid(8, 16)

    # Base metal
    for y in range(16):
        for x in range(8):
            seed = (y * 8 + x) * 22222
            sprite[y][x] = add_noise(dark_metal, 2, seed)

    # Panel lines
    for y in [0, 5, 10, 15]:
        for x in range(8):
            sprite[y][x] = shadow

    # Center line
    for y in range(16):
        sprite[y][4] = shadow

    # Highlights
    for y in [1, 6, 11]:
        for x in range(8):
            sprite[y][x] = light_metal

    # Lock indicator
    sprite[8][6] = yellow
    sprite[8][5] = shadow

    return sprite
