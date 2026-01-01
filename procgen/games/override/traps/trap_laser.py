"""Override - Laser Trap Sprite (8x8)"""

import math
from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from ..utils import create_grid


def generate_trap_laser(palette: Dict[str, str]) -> PixelGrid:
    """Generate laser trap sprite (8x8)."""
    dark_metal = hex_to_rgba(palette["dark_metal"])
    glass = hex_to_rgba(palette.get("glass", "#55697D"))
    red_bright = hex_to_rgba(palette["red_bright"])
    shadow = hex_to_rgba(palette["shadow"])
    light_metal = hex_to_rgba(palette["light_metal"])

    sprite = create_grid(8, 8, dark_metal)

    # Lens (center glow)
    center = 4.0
    for y in range(8):
        for x in range(8):
            dist = math.sqrt((x - center) ** 2 + (y - center) ** 2)
            if dist < 2.0:
                sprite[y][x] = glass
            if dist < 1.5:
                sprite[y][x] = red_bright

    # Edge details
    for x in range(8):
        sprite[0][x] = shadow
        sprite[7][x] = light_metal

    return sprite
