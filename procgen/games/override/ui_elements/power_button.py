"""Override - Power Button UI Element (12x12)"""

import math
from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from ..utils import create_grid


def generate_power_button(palette: Dict[str, str], active: bool = False) -> PixelGrid:
    """Generate power button (12x12)."""
    dark_bg = hex_to_rgba(palette["dark_bg"])
    light_metal = hex_to_rgba(palette["light_metal"])
    metal = hex_to_rgba(palette["metal"])
    green_bright = hex_to_rgba(palette["green_bright"])

    ui = create_grid(12, 12, dark_bg)

    # Border
    for x in range(12):
        ui[0][x] = light_metal
        ui[11][x] = light_metal
    for y in range(12):
        ui[y][0] = light_metal
        ui[y][11] = light_metal

    # Power icon (ring with gap at top)
    color = green_bright if active else metal
    center = 6.0

    for y in range(12):
        for x in range(12):
            dist = math.sqrt((x - center) ** 2 + (y - center) ** 2)
            if 3.0 <= dist <= 4.0:
                ui[y][x] = color

    # Vertical bar at top
    for y in range(2, 6):
        ui[y][6] = color

    return ui
