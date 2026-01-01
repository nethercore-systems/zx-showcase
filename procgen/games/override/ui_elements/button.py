"""Override - Button UI Element"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from ..utils import create_grid


def generate_button(
    palette: Dict[str, str],
    state: str = "normal",  # normal, hover, pressed
    width: int = 24,
    height: int = 12,
) -> PixelGrid:
    """Generate UI button."""
    metal = hex_to_rgba(palette["metal"])
    light_metal = hex_to_rgba(palette["light_metal"])
    dark_metal = hex_to_rgba(palette["dark_metal"])
    highlight = hex_to_rgba(palette["highlight"])
    cyan = hex_to_rgba(palette["cyan"])
    cyan_bright = hex_to_rgba(palette["cyan_bright"])

    if state == "pressed":
        bg_color = dark_metal
        border_color = cyan_bright
    elif state == "hover":
        bg_color = light_metal
        border_color = cyan
    else:
        bg_color = metal
        border_color = highlight

    ui = create_grid(width, height, bg_color)

    # Border
    for x in range(width):
        ui[0][x] = border_color
        ui[height - 1][x] = border_color
    for y in range(height):
        ui[y][0] = border_color
        ui[y][width - 1] = border_color

    return ui
