"""Override - Status Indicator UI Element (8x8)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from ..utils import create_grid, draw_rect


def generate_indicator(palette: Dict[str, str], active: bool = True) -> PixelGrid:
    """Generate status indicator (8x8)."""
    shadow = hex_to_rgba(palette["shadow"])
    dark_metal = hex_to_rgba(palette["dark_metal"])
    cyan_bright = hex_to_rgba(palette["cyan_bright"])

    ui = create_grid(8, 8, dark_metal)

    # Border
    for x in range(8):
        ui[0][x] = shadow
        ui[7][x] = shadow
    for y in range(8):
        ui[y][0] = shadow
        ui[y][7] = shadow

    # Active center
    color = cyan_bright if active else shadow
    draw_rect(ui, 2, 2, 4, 4, color)

    return ui
