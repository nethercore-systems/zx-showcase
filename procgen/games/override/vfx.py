"""
Override - VFX Sprite Generation

Re-exports individual VFX generators from effects/ subfolder.
"""

from pathlib import Path
from typing import Dict

from procgen.lib.pixel_art import export_png

# Re-export effect generators
from .effects import (
    generate_gas_cloud,
    generate_laser_beam,
    generate_core_glow,
    generate_dust_particle,
    generate_flash,
    generate_spark,
)


def generate_all_vfx(output_dir: Path, palette: Dict[str, str]) -> int:
    """
    Generate all VFX sprites and save to output directory.

    Args:
        output_dir: Output directory
        palette: Color palette

    Returns:
        Number of VFX sprites generated
    """
    vfx_sprites = {
        "gas_cloud": generate_gas_cloud(palette, 16),
        "gas_cloud_small": generate_gas_cloud(palette, 8),
        "laser_beam": generate_laser_beam(palette, 16, 4),
        "laser_beam_wide": generate_laser_beam(palette, 16, 8),
        "core_glow": generate_core_glow(palette, 8),
        "core_glow_large": generate_core_glow(palette, 16),
        "dust_particle": generate_dust_particle(palette, 4),
        "flash": generate_flash(palette, 8),
        "flash_large": generate_flash(palette, 16),
        "spark": generate_spark(palette, 4),
    }

    for name, pixels in vfx_sprites.items():
        filepath = output_dir / f"{name}.png"
        export_png(pixels, filepath)
        print(f"  Exported: {name}.png")

    return len(vfx_sprites)


__all__ = [
    # Effects
    "generate_gas_cloud",
    "generate_laser_beam",
    "generate_core_glow",
    "generate_dust_particle",
    "generate_flash",
    "generate_spark",
    # Batch generator
    "generate_all_vfx",
]
