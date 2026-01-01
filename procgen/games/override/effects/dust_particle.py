"""Override - Dust Particle VFX"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from ..utils import create_grid


def generate_dust_particle(palette: Dict[str, str], size: int = 4) -> PixelGrid:
    """Generate dust particle VFX."""
    metal = hex_to_rgba(palette["metal"])
    transparent = (0, 0, 0, 0)

    vfx = create_grid(size, size, transparent)

    # Scattered particles
    for i in range(size * size // 2):
        seed = i * 12345
        x = (seed * 7) % size
        y = (seed * 13) % size
        alpha = 100 + (seed % 100)
        vfx[y][x] = (metal[0], metal[1], metal[2], alpha)

    return vfx
