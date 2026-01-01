"""Override - Spark Particle VFX"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from ..utils import create_grid


def generate_spark(palette: Dict[str, str], size: int = 4) -> PixelGrid:
    """Generate spark particle VFX."""
    yellow_bright = hex_to_rgba(palette["yellow_bright"])
    transparent = (0, 0, 0, 0)

    vfx = create_grid(size, size, transparent)
    center = size // 2

    # Cross shape with fade
    for i in range(size):
        alpha = int(255 * (1 - abs(i - center) / center)) if center > 0 else 255
        spark_color = (yellow_bright[0], yellow_bright[1], yellow_bright[2], alpha)
        vfx[center][i] = spark_color
        vfx[i][center] = spark_color

    return vfx
