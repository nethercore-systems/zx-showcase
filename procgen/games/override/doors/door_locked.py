"""Override - Locked Door Sprite (8x16)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from .door_closed import generate_door_closed


def generate_door_locked(palette: Dict[str, str]) -> PixelGrid:
    """Generate locked door sprite (8x16)."""
    red_bright = hex_to_rgba(palette["red_bright"])
    yellow = hex_to_rgba(palette["yellow"])

    sprite = generate_door_closed(palette)

    # Red lock indicator
    for y in range(7, 10):
        for x in range(5, 7):
            sprite[y][x] = red_bright

    # Warning stripes
    for i in range(16):
        x = (i // 2) % 8
        if i % 4 < 2:
            sprite[i][x] = yellow

    return sprite
