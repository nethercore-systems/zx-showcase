"""
Override - VFX Sprite Generation

Generates visual effects: gas clouds, laser beams, glows, particles.
"""

from pathlib import Path
from typing import Dict
import math

from procgen.lib.pixel_art import (
    hex_to_rgba, blend, export_png,
    RGBA, PixelGrid,
)


def create_vfx(width: int, height: int, fill: RGBA = (0, 0, 0, 0)) -> PixelGrid:
    """Create an empty VFX sprite with a fill color."""
    return [[fill for _ in range(width)] for _ in range(height)]


def generate_gas_cloud(palette: Dict[str, str], size: int = 16) -> PixelGrid:
    """Generate gas cloud VFX (size x size)."""
    green = hex_to_rgba(palette["green"])
    transparent = (0, 0, 0, 0)

    vfx = create_vfx(size, size, transparent)
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


def generate_laser_beam(palette: Dict[str, str], width: int = 16, height: int = 4) -> PixelGrid:
    """Generate horizontal laser beam VFX."""
    red_bright = hex_to_rgba(palette["red_bright"])
    yellow_bright = hex_to_rgba(palette["yellow_bright"])
    transparent = (0, 0, 0, 0)

    vfx = create_vfx(width, height, transparent)
    beam_y = height // 2

    for x in range(width):
        # Core (white-hot)
        vfx[beam_y][x] = yellow_bright

        # Glow above and below
        for offset in range(1, height // 2):
            alpha = int(200 / (offset + 1))
            glow = (red_bright[0], red_bright[1], red_bright[2], alpha)
            if beam_y - offset >= 0:
                vfx[beam_y - offset][x] = glow
            if beam_y + offset < height:
                vfx[beam_y + offset][x] = glow

    return vfx


def generate_core_glow(palette: Dict[str, str], size: int = 8) -> PixelGrid:
    """Generate glowing core VFX (size x size)."""
    glow_core = hex_to_rgba(palette.get("glow_core", "#91EBFF"))
    transparent = (0, 0, 0, 0)

    vfx = create_vfx(size, size, transparent)
    center_x, center_y = size // 2, size // 2

    for y in range(size):
        for x in range(size):
            dx = (x - center_x) / (size / 2)
            dy = (y - center_y) / (size / 2)
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 1.0:
                # Radial gradient
                alpha = int(255 * (1 - dist))
                # Brighten center
                if dist < 0.3:
                    vfx[y][x] = (255, 255, 255, alpha)
                else:
                    vfx[y][x] = (glow_core[0], glow_core[1], glow_core[2], alpha)

    return vfx


def generate_dust_particle(palette: Dict[str, str], size: int = 4) -> PixelGrid:
    """Generate dust particle VFX."""
    metal = hex_to_rgba(palette["metal"])
    transparent = (0, 0, 0, 0)

    vfx = create_vfx(size, size, transparent)

    # Scattered particles
    for i in range(size * size // 2):
        seed = i * 12345
        x = (seed * 7) % size
        y = (seed * 13) % size
        alpha = 100 + (seed % 100)
        vfx[y][x] = (metal[0], metal[1], metal[2], alpha)

    return vfx


def generate_flash(palette: Dict[str, str], size: int = 8) -> PixelGrid:
    """Generate flash/impact VFX."""
    bright = hex_to_rgba(palette["bright"])
    transparent = (0, 0, 0, 0)

    vfx = create_vfx(size, size, transparent)
    center_x, center_y = size // 2, size // 2

    for y in range(size):
        for x in range(size):
            dx = abs(x - center_x)
            dy = abs(y - center_y)

            # Diamond shape
            if dx + dy < size // 2:
                alpha = int(255 * (1 - (dx + dy) / (size // 2)))
                vfx[y][x] = (bright[0], bright[1], bright[2], alpha)

    return vfx


def generate_spark(palette: Dict[str, str], size: int = 4) -> PixelGrid:
    """Generate spark particle VFX."""
    yellow_bright = hex_to_rgba(palette["yellow_bright"])
    transparent = (0, 0, 0, 0)

    vfx = create_vfx(size, size, transparent)
    center = size // 2

    # Cross shape with fade
    for i in range(size):
        alpha = int(255 * (1 - abs(i - center) / center)) if center > 0 else 255
        spark_color = (yellow_bright[0], yellow_bright[1], yellow_bright[2], alpha)
        vfx[center][i] = spark_color
        vfx[i][center] = spark_color

    return vfx


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
