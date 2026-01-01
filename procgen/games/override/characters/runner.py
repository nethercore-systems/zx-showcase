"""Override - Runner Character Sprite (8x12)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from ..utils import create_grid


def generate_runner_idle(palette: Dict[str, str], frame: int = 0) -> PixelGrid:
    """Generate runner idle frame (8x12)."""
    cyan = hex_to_rgba(palette["cyan"])
    cyan_bright = hex_to_rgba(palette["cyan_bright"])
    metal = hex_to_rgba(palette["metal"])
    light_metal = hex_to_rgba(palette["light_metal"])
    transparent = (0, 0, 0, 0)

    sprite = create_grid(8, 12, transparent)
    cx = 4

    # Head (3x3)
    for y in range(3):
        for x in range(cx - 1, cx + 2):
            if 0 <= x < 8:
                sprite[y][x] = cyan

    # Eyes
    sprite[1][cx - 1] = cyan_bright
    sprite[1][cx + 1] = cyan_bright

    # Body (4x5)
    for y in range(3, 8):
        for x in range(cx - 2, cx + 2):
            if 0 <= x < 8:
                sprite[y][x] = cyan

    # Belt/detail
    for x in range(cx - 2, cx + 2):
        if 0 <= x < 8:
            sprite[5][x] = metal

    # Legs (2x4 each)
    for y in range(8, 12):
        sprite[y][cx - 2] = cyan
        sprite[y][cx - 1] = cyan
        sprite[y][cx] = cyan
        sprite[y][cx + 1] = cyan

    # Feet
    sprite[11][cx - 2] = light_metal
    sprite[11][cx + 1] = light_metal

    # Breathing animation (slight offset for frames 1,2)
    if frame in [1, 2]:
        # Shift body down slightly (simulated by just changing colors)
        sprite[2][cx] = cyan_bright

    return sprite
