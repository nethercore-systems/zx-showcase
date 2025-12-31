"""
Noise-based texture generators.

Provides Perlin, Voronoi, cellular, and procedural material textures.
"""

import math
from typing import Tuple, Optional, List
from ...lib.texture_buffer import TextureData
from ...lib.noise import (
    perlin_2d, fbm_2d, voronoi_2d, cellular_2d,
    worley_2d, turbulence_2d,
)
from ...lib.color_utils import lerp_color


def generate_perlin_texture(
    width: int,
    height: int,
    scale: float = 0.05,
    octaves: int = 1,
    color_low: Tuple[int, int, int] = (0, 0, 0),
    color_high: Tuple[int, int, int] = (255, 255, 255),
) -> TextureData:
    """
    Generate a Perlin noise texture.

    Args:
        width: Texture width
        height: Texture height
        scale: Noise scale (smaller = more zoomed in)
        octaves: Number of octaves for detail
        color_low: Color for low values
        color_high: Color for high values
    """
    tex = TextureData(width, height)

    for y in range(height):
        for x in range(width):
            if octaves > 1:
                value = fbm_2d(x * scale, y * scale, octaves)
            else:
                value = perlin_2d(x * scale, y * scale)

            # Normalize from [-1,1] to [0,1]
            t = (value + 1) / 2
            color = lerp_color(color_low, color_high, t)
            tex.set_pixel(x, y, color)

    return tex


def generate_voronoi_texture(
    width: int,
    height: int,
    cell_count: int = 20,
    color_mode: str = "distance",
    color_low: Tuple[int, int, int] = (0, 0, 0),
    color_high: Tuple[int, int, int] = (255, 255, 255),
    colors: Optional[List[Tuple[int, int, int]]] = None,
) -> TextureData:
    """
    Generate a Voronoi noise texture.

    Args:
        width: Texture width
        height: Texture height
        cell_count: Approximate number of cells
        color_mode: "distance" (grayscale) or "cells" (colored per cell)
        color_low: Color for nearest distance
        color_high: Color for farthest distance
        colors: Optional palette for cell coloring
    """
    tex = TextureData(width, height)
    scale = cell_count / max(width, height)

    for y in range(height):
        for x in range(width):
            value, cell_id = voronoi_2d(x * scale, y * scale)

            if color_mode == "cells" and colors:
                color = colors[cell_id % len(colors)]
            else:
                t = min(1, value * 2)  # Normalize distance
                color = lerp_color(color_low, color_high, t)

            tex.set_pixel(x, y, color)

    return tex


def generate_cellular_texture(
    width: int,
    height: int,
    scale: float = 0.1,
    color_low: Tuple[int, int, int] = (0, 0, 0),
    color_high: Tuple[int, int, int] = (255, 255, 255),
) -> TextureData:
    """
    Generate a cellular/Worley noise texture.

    Args:
        width: Texture width
        height: Texture height
        scale: Noise scale
        color_low: Color for low values
        color_high: Color for high values
    """
    tex = TextureData(width, height)

    for y in range(height):
        for x in range(width):
            value = cellular_2d(x * scale, y * scale)
            t = min(1, max(0, value))
            color = lerp_color(color_low, color_high, t)
            tex.set_pixel(x, y, color)

    return tex


def generate_fbm_texture(
    width: int,
    height: int,
    scale: float = 0.02,
    octaves: int = 6,
    persistence: float = 0.5,
    lacunarity: float = 2.0,
    color_low: Tuple[int, int, int] = (0, 0, 0),
    color_high: Tuple[int, int, int] = (255, 255, 255),
) -> TextureData:
    """
    Generate a Fractional Brownian Motion texture.

    Args:
        width: Texture width
        height: Texture height
        scale: Base scale
        octaves: Number of noise layers
        persistence: Amplitude multiplier per octave
        lacunarity: Frequency multiplier per octave
        color_low: Color for low values
        color_high: Color for high values
    """
    tex = TextureData(width, height)

    for y in range(height):
        for x in range(width):
            value = fbm_2d(
                x * scale, y * scale,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity
            )
            t = (value + 1) / 2
            color = lerp_color(color_low, color_high, t)
            tex.set_pixel(x, y, color)

    return tex


def generate_marble_texture(
    width: int,
    height: int,
    scale: float = 0.02,
    frequency: float = 5.0,
    turbulence: float = 5.0,
    color_vein: Tuple[int, int, int] = (80, 80, 80),
    color_base: Tuple[int, int, int] = (230, 230, 230),
) -> TextureData:
    """
    Generate a marble-like texture.

    Args:
        width: Texture width
        height: Texture height
        scale: Noise scale
        frequency: Vein frequency
        turbulence: Amount of turbulence distortion
        color_vein: Color of marble veins
        color_base: Base marble color
    """
    tex = TextureData(width, height)

    for y in range(height):
        for x in range(width):
            noise_val = turbulence_2d(x * scale, y * scale, octaves=4)
            marble = math.sin(frequency * x / width + turbulence * noise_val)
            t = (marble + 1) / 2
            color = lerp_color(color_vein, color_base, t)
            tex.set_pixel(x, y, color)

    return tex


def generate_wood_texture(
    width: int,
    height: int,
    scale: float = 0.05,
    ring_frequency: float = 20.0,
    turbulence_amount: float = 0.3,
    color_dark: Tuple[int, int, int] = (80, 50, 30),
    color_light: Tuple[int, int, int] = (180, 130, 80),
) -> TextureData:
    """
    Generate a wood grain texture.

    Args:
        width: Texture width
        height: Texture height
        scale: Noise scale
        ring_frequency: Frequency of wood rings
        turbulence_amount: Grain irregularity
        color_dark: Dark wood color
        color_light: Light wood color
    """
    tex = TextureData(width, height)
    cx, cy = width / 2, height / 2

    for y in range(height):
        for x in range(width):
            # Distance from center
            dx = (x - cx) / width
            dy = (y - cy) / height
            dist = math.sqrt(dx * dx + dy * dy)

            # Add turbulence
            noise_val = perlin_2d(x * scale, y * scale)
            ring_value = math.sin(ring_frequency * dist + turbulence_amount * noise_val)

            t = (ring_value + 1) / 2
            color = lerp_color(color_dark, color_light, t)
            tex.set_pixel(x, y, color)

    return tex
