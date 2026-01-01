"""Override - Gas Trap Sprite (8x8)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, add_noise, PixelGrid
from ..utils import create_grid


def generate_trap_gas(palette: Dict[str, str]) -> PixelGrid:
    """Generate gas trap sprite (8x8)."""
    dark_metal = hex_to_rgba(palette["dark_metal"])
    shadow = hex_to_rgba(palette["shadow"])
    yellow = hex_to_rgba(palette["yellow"])

    sprite = create_grid(8, 8, dark_metal)

    # Add noise
    for y in range(8):
        for x in range(8):
            seed = (y * 8 + x) * 44444
            sprite[y][x] = add_noise(dark_metal, 2, seed)

    # Vent holes
    for y in range(1, 7, 2):
        for x in range(1, 7, 2):
            sprite[y][x] = shadow

    # Hazard stripes
    for x in range(8):
        sprite[0][x] = yellow
        sprite[7][x] = yellow

    return sprite
