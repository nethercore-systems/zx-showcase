"""Override - Spike Trap Sprite (8x8)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from ..utils import create_grid


def generate_trap_spike(palette: Dict[str, str]) -> PixelGrid:
    """Generate spike trap sprite (8x8)."""
    dark_bg = hex_to_rgba(palette["dark_bg"])
    light_metal = hex_to_rgba(palette["light_metal"])
    bright = hex_to_rgba(palette["bright"])
    shadow = hex_to_rgba(palette["shadow"])

    sprite = create_grid(8, 8, dark_bg)

    # Spike triangle
    center_x = 4
    for y in range(4, 8):
        width = (8 - y) // 2
        for x in range(center_x - width, center_x + width + 1):
            if 0 <= x < 8:
                sprite[y][x] = light_metal

    # Tip
    sprite[4][4] = bright

    # Base plate
    for x in range(8):
        sprite[7][x] = shadow

    return sprite
