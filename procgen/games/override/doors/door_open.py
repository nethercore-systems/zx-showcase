"""Override - Open Door Sprite (8x16)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, add_noise, PixelGrid
from ..utils import create_grid


def generate_door_open(palette: Dict[str, str]) -> PixelGrid:
    """Generate open door sprite (8x16)."""
    dark_metal = hex_to_rgba(palette["dark_metal"])
    shadow = hex_to_rgba(palette["shadow"])
    transparent = (0, 0, 0, 0)

    sprite = create_grid(8, 16, transparent)

    # Door compressed to left side
    for y in range(16):
        for x in range(3):
            seed = (y * 8 + x) * 33333
            sprite[y][x] = add_noise(dark_metal, 2, seed)

    # Panel lines on compressed part
    for y in [0, 5, 10, 15]:
        for x in range(3):
            sprite[y][x] = shadow

    return sprite
