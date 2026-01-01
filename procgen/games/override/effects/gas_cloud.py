"""Override - Gas Cloud VFX"""

import math
from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from ..utils import create_grid


def generate_gas_cloud(palette: Dict[str, str], size: int = 16) -> PixelGrid:
    """Generate gas cloud VFX (size x size)."""
    green = hex_to_rgba(palette["green"])
    transparent = (0, 0, 0, 0)

    vfx = create_grid(size, size, transparent)
    center_x, center_y = size // 2, size // 2

    for y in range(size):
        for x in range(size):
            # Distance from center
            dx = (x - center_x) / (size / 2)
            dy = (y - center_y) / (size / 2)
            dist = math.sqrt(dx * dx + dy * dy)

            # Organic cloud shape with noise
            seed = x * 31 + y * 17
            noise = ((seed * 0x5851f42d) % 100) / 100.0
            threshold = 0.8 + noise * 0.3

            if dist < threshold:
                # Fade alpha based on distance
                alpha = int(180 * (1 - dist / threshold))
                vfx[y][x] = (green[0], green[1], green[2], alpha)

    return vfx
