"""Override - Timer Digit UI Element (5x7)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from ..utils import create_grid


def generate_timer_digit(palette: Dict[str, str], digit: int = 8) -> PixelGrid:
    """Generate 7-segment timer digit (5x7)."""
    cyan_bright = hex_to_rgba(palette["cyan_bright"])
    transparent = (0, 0, 0, 0)

    ui = create_grid(5, 7, transparent)

    # 7-segment patterns: top, top-right, bottom-right, bottom, bottom-left, top-left, middle
    segments = [
        [True, True, True, True, True, True, False],     # 0
        [False, True, True, False, False, False, False], # 1
        [True, True, False, True, True, False, True],    # 2
        [True, True, True, True, False, False, True],    # 3
        [False, True, True, False, False, True, True],   # 4
        [True, False, True, True, False, True, True],    # 5
        [True, False, True, True, True, True, True],     # 6
        [True, True, True, False, False, False, False],  # 7
        [True, True, True, True, True, True, True],      # 8
        [True, True, True, True, False, True, True],     # 9
    ]

    pattern = segments[digit % 10]

    # Draw segments
    # Top
    if pattern[0]:
        for x in range(1, 4):
            ui[0][x] = cyan_bright
    # Top-right
    if pattern[1]:
        for y in range(1, 3):
            ui[y][4] = cyan_bright
    # Bottom-right
    if pattern[2]:
        for y in range(4, 6):
            ui[y][4] = cyan_bright
    # Bottom
    if pattern[3]:
        for x in range(1, 4):
            ui[6][x] = cyan_bright
    # Bottom-left
    if pattern[4]:
        for y in range(4, 6):
            ui[y][0] = cyan_bright
    # Top-left
    if pattern[5]:
        for y in range(1, 3):
            ui[y][0] = cyan_bright
    # Middle
    if pattern[6]:
        for x in range(1, 4):
            ui[3][x] = cyan_bright

    return ui
