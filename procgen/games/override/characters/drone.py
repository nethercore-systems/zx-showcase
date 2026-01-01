"""Override - Drone Character Sprite (8x8)"""

import math
from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from ..utils import create_grid


def generate_drone_idle(palette: Dict[str, str], frame: int = 0) -> PixelGrid:
    """Generate drone idle frame (8x8)."""
    red = hex_to_rgba(palette["red"])
    red_bright = hex_to_rgba(palette["red_bright"])
    metal = hex_to_rgba(palette["metal"])
    dark_metal = hex_to_rgba(palette["dark_metal"])
    transparent = (0, 0, 0, 0)

    sprite = create_grid(8, 8, transparent)

    # Oval body
    center_x, center_y = 4, 4
    for y in range(8):
        for x in range(8):
            dx = (x - center_x) / 3.5
            dy = (y - center_y) / 3.5
            dist = dx * dx + dy * dy
            if dist < 0.9:
                if dist < 0.3:
                    sprite[y][x] = metal
                elif dist < 0.6:
                    sprite[y][x] = dark_metal
                else:
                    sprite[y][x] = dark_metal

    # Eye (center, pulses with frame)
    eye_color = red_bright if frame % 2 == 0 else red
    sprite[center_y][center_x] = eye_color

    return sprite
