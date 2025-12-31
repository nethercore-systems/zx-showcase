"""
Override - UI Element Generation

Generates UI elements: energy bars, timers, indicators, buttons.
"""

from pathlib import Path
from typing import Dict
import math

from procgen.lib.pixel_art import (
    hex_to_rgba, blend, export_png,
    RGBA, PixelGrid,
)


def create_ui(width: int, height: int, fill: RGBA = (0, 0, 0, 0)) -> PixelGrid:
    """Create an empty UI element with a fill color."""
    return [[fill for _ in range(width)] for _ in range(height)]


def draw_rect(
    ui: PixelGrid,
    x: int, y: int,
    w: int, h: int,
    color: RGBA,
) -> None:
    """Draw a filled rectangle on a UI element."""
    height = len(ui)
    width = len(ui[0]) if height > 0 else 0
    for py in range(max(0, y), min(height, y + h)):
        for px in range(max(0, x), min(width, x + w)):
            ui[py][px] = color


def generate_energy_bar_bg(palette: Dict[str, str], width: int = 32, height: int = 4) -> PixelGrid:
    """Generate energy bar background."""
    shadow = hex_to_rgba(palette["shadow"])
    dark_metal = hex_to_rgba(palette["dark_metal"])

    ui = create_ui(width, height, shadow)

    # Inner darker area
    draw_rect(ui, 1, 1, width - 2, height - 2, dark_metal)

    return ui


def generate_energy_bar_fill(palette: Dict[str, str], width: int = 30, height: int = 2) -> PixelGrid:
    """Generate energy bar fill (fits inside bg)."""
    cyan = hex_to_rgba(palette["cyan"])
    cyan_bright = hex_to_rgba(palette["cyan_bright"])

    ui = create_ui(width, height)

    for y in range(height):
        for x in range(width):
            # Gradient left to right
            t = x / width
            if t < 0.7:
                ui[y][x] = cyan
            else:
                ui[y][x] = blend(cyan, cyan_bright, (t - 0.7) / 0.3)

    return ui


def generate_timer_digit(palette: Dict[str, str], digit: int = 8) -> PixelGrid:
    """Generate 7-segment timer digit (5x7)."""
    cyan_bright = hex_to_rgba(palette["cyan_bright"])
    transparent = (0, 0, 0, 0)

    ui = create_ui(5, 7, transparent)

    # 7-segment patterns: top, top-right, bottom-right, bottom, bottom-left, top-left, middle
    segments = [
        [True, True, True, True, True, True, False],     # 0
        [False, True, True, False, False, False, False], # 1
        [True, True, False, True, True, False, True],    # 2
        [True, True, True, True, False, False, True],    # 3
        [False, True, True, False, False, True, True],   # 4
        [True, False, True, True, False, True, True],    # 5
        [True, False, True, True, True, True, True],     # 6
        [True, True, True, False, False, False, False],  # 7
        [True, True, True, True, True, True, True],      # 8
        [True, True, True, True, False, True, True],     # 9
    ]

    pattern = segments[digit % 10]

    # Draw segments
    # Top
    if pattern[0]:
        for x in range(1, 4):
            ui[0][x] = cyan_bright
    # Top-right
    if pattern[1]:
        for y in range(1, 3):
            ui[y][4] = cyan_bright
    # Bottom-right
    if pattern[2]:
        for y in range(4, 6):
            ui[y][4] = cyan_bright
    # Bottom
    if pattern[3]:
        for x in range(1, 4):
            ui[6][x] = cyan_bright
    # Bottom-left
    if pattern[4]:
        for y in range(4, 6):
            ui[y][0] = cyan_bright
    # Top-left
    if pattern[5]:
        for y in range(1, 3):
            ui[y][0] = cyan_bright
    # Middle
    if pattern[6]:
        for x in range(1, 4):
            ui[3][x] = cyan_bright

    return ui


def generate_indicator(palette: Dict[str, str], active: bool = True) -> PixelGrid:
    """Generate status indicator (8x8)."""
    shadow = hex_to_rgba(palette["shadow"])
    dark_metal = hex_to_rgba(palette["dark_metal"])
    cyan_bright = hex_to_rgba(palette["cyan_bright"])

    ui = create_ui(8, 8, dark_metal)

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


def generate_power_button(palette: Dict[str, str], active: bool = False) -> PixelGrid:
    """Generate power button (12x12)."""
    dark_bg = hex_to_rgba(palette["dark_bg"])
    light_metal = hex_to_rgba(palette["light_metal"])
    metal = hex_to_rgba(palette["metal"])
    green_bright = hex_to_rgba(palette["green_bright"])

    ui = create_ui(12, 12, dark_bg)

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

    ui = create_ui(width, height, bg_color)

    # Border
    for x in range(width):
        ui[0][x] = border_color
        ui[height - 1][x] = border_color
    for y in range(height):
        ui[y][0] = border_color
        ui[y][width - 1] = border_color

    return ui


def generate_all_ui(output_dir: Path, palette: Dict[str, str]) -> int:
    """
    Generate all UI elements and save to output directory.

    Args:
        output_dir: Output directory
        palette: Color palette

    Returns:
        Number of UI elements generated
    """
    count = 0

    # Energy bars
    export_png(generate_energy_bar_bg(palette), output_dir / "energy_bar_bg.png")
    print("  Exported: energy_bar_bg.png")
    count += 1

    export_png(generate_energy_bar_fill(palette), output_dir / "energy_bar_fill.png")
    print("  Exported: energy_bar_fill.png")
    count += 1

    # Timer digits (0-9)
    for digit in range(10):
        pixels = generate_timer_digit(palette, digit)
        export_png(pixels, output_dir / f"timer_digit_{digit}.png")
        print(f"  Exported: timer_digit_{digit}.png")
        count += 1

    # Indicators
    export_png(generate_indicator(palette, True), output_dir / "indicator_active.png")
    print("  Exported: indicator_active.png")
    count += 1

    export_png(generate_indicator(palette, False), output_dir / "indicator_inactive.png")
    print("  Exported: indicator_inactive.png")
    count += 1

    # Power buttons
    export_png(generate_power_button(palette, False), output_dir / "power_button_off.png")
    print("  Exported: power_button_off.png")
    count += 1

    export_png(generate_power_button(palette, True), output_dir / "power_button_on.png")
    print("  Exported: power_button_on.png")
    count += 1

    # Buttons
    for state in ["normal", "hover", "pressed"]:
        pixels = generate_button(palette, state)
        export_png(pixels, output_dir / f"button_{state}.png")
        print(f"  Exported: button_{state}.png")
        count += 1

    return count
