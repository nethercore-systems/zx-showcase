"""Override - Core Glow VFX"""

import math
from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from ..utils import create_grid


def generate_core_glow(palette: Dict[str, str], size: int = 8) -> PixelGrid:
    """Generate glowing core VFX (size x size)."""
    glow_core = hex_to_rgba(palette.get("glow_core", "#91EBFF"))
    transparent = (0, 0, 0, 0)

    vfx = create_grid(size, size, transparent)
    center_x, center_y = size // 2, size // 2

    for y in range(size):
        for x in range(size):
            dx = (x - center_x) / (size / 2)
            dy = (y - center_y) / (size / 2)
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 1.0:
                # Radial gradient
                alpha = int(255 * (1 - dist))
                # Brighten center
                if dist < 0.3:
                    vfx[y][x] = (255, 255, 255, alpha)
                else:
                    vfx[y][x] = (glow_core[0], glow_core[1], glow_core[2], alpha)

    return vfx
