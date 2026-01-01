"""Override - Energy Bar UI Elements"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, blend, PixelGrid
from ..utils import create_grid, draw_rect


def generate_energy_bar_bg(palette: Dict[str, str], width: int = 32, height: int = 4) -> PixelGrid:
    """Generate energy bar background."""
    shadow = hex_to_rgba(palette["shadow"])
    dark_metal = hex_to_rgba(palette["dark_metal"])

    ui = create_grid(width, height, shadow)

    # Inner darker area
    draw_rect(ui, 1, 1, width - 2, height - 2, dark_metal)

    return ui


def generate_energy_bar_fill(palette: Dict[str, str], width: int = 30, height: int = 2) -> PixelGrid:
    """Generate energy bar fill (fits inside bg)."""
    cyan = hex_to_rgba(palette["cyan"])
    cyan_bright = hex_to_rgba(palette["cyan_bright"])

    ui = create_grid(width, height)

    for y in range(height):
        for x in range(width):
            # Gradient left to right
            t = x / width
            if t < 0.7:
                ui[y][x] = cyan
            else:
                ui[y][x] = blend(cyan, cyan_bright, (t - 0.7) / 0.3)

    return ui
