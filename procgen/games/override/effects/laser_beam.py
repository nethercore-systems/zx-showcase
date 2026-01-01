"""Override - Laser Beam VFX"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from ..utils import create_grid


def generate_laser_beam(palette: Dict[str, str], width: int = 16, height: int = 4) -> PixelGrid:
    """Generate horizontal laser beam VFX."""
    red_bright = hex_to_rgba(palette["red_bright"])
    yellow_bright = hex_to_rgba(palette["yellow_bright"])
    transparent = (0, 0, 0, 0)

    vfx = create_grid(width, height, transparent)
    beam_y = height // 2

    for x in range(width):
        # Core (white-hot)
        vfx[beam_y][x] = yellow_bright

        # Glow above and below
        for offset in range(1, height // 2):
            alpha = int(200 / (offset + 1))
            glow = (red_bright[0], red_bright[1], red_bright[2], alpha)
            if beam_y - offset >= 0:
                vfx[beam_y - offset][x] = glow
            if beam_y + offset < height:
                vfx[beam_y + offset][x] = glow

    return vfx
