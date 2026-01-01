"""
Override - UI Element Generation

Re-exports individual UI generators from ui_elements/ subfolder.
"""

from pathlib import Path
from typing import Dict

from procgen.lib.pixel_art import export_png

# Re-export UI element generators
from .ui_elements import (
    generate_energy_bar_bg,
    generate_energy_bar_fill,
    generate_timer_digit,
    generate_indicator,
    generate_power_button,
    generate_button,
)


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


__all__ = [
    # UI Elements
    "generate_energy_bar_bg",
    "generate_energy_bar_fill",
    "generate_timer_digit",
    "generate_indicator",
    "generate_power_button",
    "generate_button",
    # Batch generator
    "generate_all_ui",
]
