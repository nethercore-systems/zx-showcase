"""
VFX sprite generation for 2D games.

Generates visual effect sprites (gas clouds, laser beams, glows, particles).
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math

from ..base_params import UniversalStyleParams


@dataclass
class VFXData:
    """Raw VFX pixel data."""
    width: int
    height: int
    pixels: List[List[Tuple[int, int, int, int]]]  # RGBA
    name: str = ""


def hex_to_rgba(hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    """Convert hex color to RGBA tuple."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b, alpha)


def create_vfx(width: int, height: int, fill: Tuple[int, int, int, int] = (0, 0, 0, 0)) -> VFXData:
    """Create an empty VFX sprite with a fill color."""
    pixels = [[fill for _ in range(width)] for _ in range(height)]
    return VFXData(width=width, height=height, pixels=pixels)


def blend_additive(base: Tuple[int, int, int, int], add: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    """Additive blend two colors."""
    return (
        min(255, base[0] + add[0]),
        min(255, base[1] + add[1]),
        min(255, base[2] + add[2]),
        max(base[3], add[3]),
    )


def generate_vfx_sprite(
    vfx_type: str,
    palette: Dict[str, str],
    size: Tuple[int, int] = (16, 16),
) -> VFXData:
    """
    Generate a VFX sprite.

    Args:
        vfx_type: Type of VFX (gas_cloud, laser_beam, core_glow, dust, flash)
        palette: Color palette dict with hex colors
        size: Sprite size (width, height)

    Returns:
        VFXData with generated VFX sprite
    """
    width, height = size
    transparent = (0, 0, 0, 0)
    vfx = create_vfx(width, height, transparent)

    if vfx_type == "gas_cloud":
        color = hex_to_rgba(palette.get("green", "#2D874B"))
        center_x, center_y = width // 2, height // 2

        for y in range(height):
            for x in range(width):
                # Distance from center
                dx = (x - center_x) / (width / 2)
                dy = (y - center_y) / (height / 2)
                dist = math.sqrt(dx * dx + dy * dy)

                # Organic cloud shape with noise
                seed = x * 31 + y * 17
                noise = ((seed * 0x5851f42d) % 100) / 100.0
                threshold = 0.8 + noise * 0.3

                if dist < threshold:
                    # Fade alpha based on distance
                    alpha = int(180 * (1 - dist / threshold))
                    vfx.pixels[y][x] = (color[0], color[1], color[2], alpha)

    elif vfx_type == "laser_beam":
        color = hex_to_rgba(palette.get("red_bright", "#E14141"))
        core_color = hex_to_rgba(palette.get("yellow_bright", "#F5D75F"))

        # Horizontal beam
        beam_y = height // 2
        for x in range(width):
            # Core (white-hot)
            vfx.pixels[beam_y][x] = core_color

            # Glow above and below
            for offset in range(1, min(3, height // 2)):
                alpha = int(200 / (offset + 1))
                glow = (color[0], color[1], color[2], alpha)
                if beam_y - offset >= 0:
                    vfx.pixels[beam_y - offset][x] = glow
                if beam_y + offset < height:
                    vfx.pixels[beam_y + offset][x] = glow

    elif vfx_type == "core_glow":
        color = hex_to_rgba(palette.get("glow_core", "#91EBFF"))
        center_x, center_y = width // 2, height // 2

        for y in range(height):
            for x in range(width):
                dx = (x - center_x) / (width / 2)
                dy = (y - center_y) / (height / 2)
                dist = math.sqrt(dx * dx + dy * dy)

                if dist < 1.0:
                    # Radial gradient
                    alpha = int(255 * (1 - dist))
                    # Brighten center
                    if dist < 0.3:
                        vfx.pixels[y][x] = (255, 255, 255, alpha)
                    else:
                        vfx.pixels[y][x] = (color[0], color[1], color[2], alpha)

    elif vfx_type == "dust":
        color = hex_to_rgba(palette.get("metal", "#343E4E"))

        # Scattered particles
        for i in range(width * height // 8):
            seed = i * 12345
            x = (seed * 7) % width
            y = (seed * 13) % height
            alpha = 100 + (seed % 100)
            vfx.pixels[y][x] = (color[0], color[1], color[2], alpha)

    elif vfx_type == "flash":
        color = hex_to_rgba(palette.get("bright", "#7D91AC"))
        center_x, center_y = width // 2, height // 2

        for y in range(height):
            for x in range(width):
                dx = abs(x - center_x)
                dy = abs(y - center_y)

                # Diamond shape
                if dx + dy < max(width, height) // 2:
                    alpha = int(255 * (1 - (dx + dy) / (max(width, height) // 2)))
                    vfx.pixels[y][x] = (color[0], color[1], color[2], alpha)

    vfx.name = vfx_type
    return vfx


def generate_particle(
    particle_type: str,
    color: str,
    size: int = 4,
) -> VFXData:
    """
    Generate a small particle sprite.

    Args:
        particle_type: Type of particle (dot, spark, smoke)
        color: Hex color
        size: Particle size in pixels

    Returns:
        VFXData with generated particle
    """
    vfx = create_vfx(size, size)
    rgba = hex_to_rgba(color)
    center = size // 2

    if particle_type == "dot":
        # Simple filled circle
        for y in range(size):
            for x in range(size):
                dx = (x - center) / (size / 2)
                dy = (y - center) / (size / 2)
                if dx * dx + dy * dy < 1.0:
                    vfx.pixels[y][x] = rgba

    elif particle_type == "spark":
        # Cross shape with fade
        for i in range(size):
            alpha = int(255 * (1 - abs(i - center) / center)) if center > 0 else 255
            spark_color = (rgba[0], rgba[1], rgba[2], alpha)
            vfx.pixels[center][i] = spark_color
            vfx.pixels[i][center] = spark_color

    elif particle_type == "smoke":
        # Soft circle with alpha gradient
        for y in range(size):
            for x in range(size):
                dx = (x - center) / (size / 2)
                dy = (y - center) / (size / 2)
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < 1.0:
                    alpha = int(150 * (1 - dist))
                    vfx.pixels[y][x] = (rgba[0], rgba[1], rgba[2], alpha)

    vfx.name = f"particle_{particle_type}"
    return vfx


def generate_ui_elements(
    palette: Dict[str, str],
) -> Dict[str, VFXData]:
    """
    Generate UI element sprites.

    Args:
        palette: Color palette dict with hex colors

    Returns:
        Dict of UI element sprites
    """
    elements = {}

    # Energy bar background (32x4)
    bg = create_vfx(32, 4)
    shadow = hex_to_rgba(palette.get("shadow", "#191E26"))
    for y in range(4):
        for x in range(32):
            bg.pixels[y][x] = shadow
    bg.name = "energy_bar_bg"
    elements["energy_bar_bg"] = bg

    # Energy bar fill (30x2, fits inside bg)
    fill = create_vfx(30, 2)
    cyan = hex_to_rgba(palette.get("cyan", "#2D7D91"))
    cyan_bright = hex_to_rgba(palette.get("cyan_bright", "#55B9D7"))
    for y in range(2):
        for x in range(30):
            # Gradient left to right
            t = x / 30
            if t < 0.5:
                fill.pixels[y][x] = cyan
            else:
                fill.pixels[y][x] = cyan_bright
    fill.name = "energy_bar_fill"
    elements["energy_bar_fill"] = fill

    # Timer digit (8x12)
    digit = create_vfx(8, 12)
    yellow = hex_to_rgba(palette.get("yellow", "#C3A52D"))
    # Simple "8" shape as placeholder
    for y in range(12):
        for x in range(8):
            if x in [0, 7] or y in [0, 5, 11]:
                digit.pixels[y][x] = yellow
    digit.name = "timer_digit"
    elements["timer_digit"] = digit

    # Indicator active
    indicator = create_vfx(4, 4)
    green = hex_to_rgba(palette.get("green_bright", "#55CD7D"))
    for y in range(4):
        for x in range(4):
            indicator.pixels[y][x] = green
    indicator.name = "indicator_active"
    elements["indicator_active"] = indicator

    # Indicator inactive
    inactive = create_vfx(4, 4)
    dark = hex_to_rgba(palette.get("dark_metal", "#232A34"))
    for y in range(4):
        for x in range(4):
            inactive.pixels[y][x] = dark
    inactive.name = "indicator_inactive"
    elements["indicator_inactive"] = inactive

    return elements
