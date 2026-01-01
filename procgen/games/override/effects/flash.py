"""Override - Flash/Impact VFX"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from ..utils import create_grid


def generate_flash(palette: Dict[str, str], size: int = 8) -> PixelGrid:
    """Generate flash/impact VFX."""
    bright = hex_to_rgba(palette["bright"])
    transparent = (0, 0, 0, 0)

    vfx = create_grid(size, size, transparent)
    center_x, center_y = size // 2, size // 2

    for y in range(size):
        for x in range(size):
            dx = abs(x - center_x)
            dy = abs(y - center_y)

            # Diamond shape
            if dx + dy < size // 2:
                alpha = int(255 * (1 - (dx + dy) / (size // 2)))
                vfx[y][x] = (bright[0], bright[1], bright[2], alpha)

    return vfx
