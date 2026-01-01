"""
Override - Shared Pixel Art Utilities

Common helper functions for pixel art generation used across all asset types.
"""

from typing import Dict
from procgen.lib.pixel_art import RGBA, PixelGrid


def create_grid(width: int, height: int, fill: RGBA = (0, 0, 0, 0)) -> PixelGrid:
    """Create an empty pixel grid with a fill color."""
    return [[fill for _ in range(width)] for _ in range(height)]


def draw_rect(
    grid: PixelGrid,
    x: int, y: int,
    w: int, h: int,
    color: RGBA,
) -> None:
    """Draw a filled rectangle on a pixel grid."""
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    for py in range(max(0, y), min(height, y + h)):
        for px in range(max(0, x), min(width, x + w)):
            grid[py][px] = color
