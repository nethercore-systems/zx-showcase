"""
Gradient texture generators.

Provides linear, radial, angular, and diamond gradients.
"""

import math
from typing import Tuple, List, Optional
from ...lib.texture_buffer import TextureData
from ...lib.color_utils import hex_to_rgb, lerp_color


def generate_linear_gradient(
    width: int,
    height: int,
    color_start: Tuple[int, int, int],
    color_end: Tuple[int, int, int],
    angle: float = 0.0,
    stops: Optional[List[Tuple[float, Tuple[int, int, int]]]] = None,
) -> TextureData:
    """
    Generate a linear gradient texture.

    Args:
        width: Texture width
        height: Texture height
        color_start: Start color (RGB)
        color_end: End color (RGB)
        angle: Gradient angle in degrees (0 = left to right)
        stops: Optional list of (position, color) tuples for multi-color gradients
    """
    tex = TextureData(width, height)
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    # Calculate gradient length based on angle
    grad_len = abs(width * cos_a) + abs(height * sin_a)

    if stops:
        # Multi-color gradient
        for y in range(height):
            for x in range(width):
                # Project point onto gradient axis
                t = (x * cos_a + y * sin_a) / grad_len if grad_len > 0 else 0
                t = max(0, min(1, t))

                # Find color between stops
                color = _interpolate_stops(t, stops)
                tex.set_pixel(x, y, color)
    else:
        # Simple two-color gradient
        for y in range(height):
            for x in range(width):
                t = (x * cos_a + y * sin_a) / grad_len if grad_len > 0 else 0
                t = max(0, min(1, t))
                color = lerp_color(color_start, color_end, t)
                tex.set_pixel(x, y, color)

    return tex


def generate_radial_gradient(
    width: int,
    height: int,
    color_center: Tuple[int, int, int],
    color_edge: Tuple[int, int, int],
    center_x: Optional[float] = None,
    center_y: Optional[float] = None,
    radius: Optional[float] = None,
    stops: Optional[List[Tuple[float, Tuple[int, int, int]]]] = None,
) -> TextureData:
    """
    Generate a radial gradient texture.

    Args:
        width: Texture width
        height: Texture height
        color_center: Center color (RGB)
        color_edge: Edge color (RGB)
        center_x: Center X position (0-1, default 0.5)
        center_y: Center Y position (0-1, default 0.5)
        radius: Gradient radius (default: half diagonal)
        stops: Optional color stops
    """
    tex = TextureData(width, height)

    cx = (center_x if center_x is not None else 0.5) * width
    cy = (center_y if center_y is not None else 0.5) * height
    max_radius = radius if radius else math.sqrt(width**2 + height**2) / 2

    if stops:
        for y in range(height):
            for x in range(width):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                t = min(1, dist / max_radius)
                color = _interpolate_stops(t, stops)
                tex.set_pixel(x, y, color)
    else:
        for y in range(height):
            for x in range(width):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                t = min(1, dist / max_radius)
                color = lerp_color(color_center, color_edge, t)
                tex.set_pixel(x, y, color)

    return tex


def generate_angular_gradient(
    width: int,
    height: int,
    colors: List[Tuple[int, int, int]],
    center_x: Optional[float] = None,
    center_y: Optional[float] = None,
    start_angle: float = 0.0,
) -> TextureData:
    """
    Generate an angular (conic) gradient texture.

    Args:
        width: Texture width
        height: Texture height
        colors: List of colors to cycle through
        center_x: Center X position (0-1, default 0.5)
        center_y: Center Y position (0-1, default 0.5)
        start_angle: Starting angle in degrees
    """
    tex = TextureData(width, height)

    cx = (center_x if center_x is not None else 0.5) * width
    cy = (center_y if center_y is not None else 0.5) * height
    start_rad = math.radians(start_angle)
    n_colors = len(colors)

    for y in range(height):
        for x in range(width):
            angle = math.atan2(y - cy, x - cx) - start_rad
            if angle < 0:
                angle += 2 * math.pi

            # Map angle to color index
            t = angle / (2 * math.pi)
            idx = t * n_colors
            idx1 = int(idx) % n_colors
            idx2 = (idx1 + 1) % n_colors
            frac = idx - int(idx)

            color = lerp_color(colors[idx1], colors[idx2], frac)
            tex.set_pixel(x, y, color)

    return tex


def generate_diamond_gradient(
    width: int,
    height: int,
    color_center: Tuple[int, int, int],
    color_edge: Tuple[int, int, int],
    center_x: Optional[float] = None,
    center_y: Optional[float] = None,
) -> TextureData:
    """
    Generate a diamond-shaped gradient texture.

    Args:
        width: Texture width
        height: Texture height
        color_center: Center color
        color_edge: Edge color
        center_x: Center X position (0-1, default 0.5)
        center_y: Center Y position (0-1, default 0.5)
    """
    tex = TextureData(width, height)

    cx = (center_x if center_x is not None else 0.5) * width
    cy = (center_y if center_y is not None else 0.5) * height
    max_dist = max(cx, width - cx) + max(cy, height - cy)

    for y in range(height):
        for x in range(width):
            # Manhattan distance for diamond shape
            dist = abs(x - cx) + abs(y - cy)
            t = min(1, dist / max_dist)
            color = lerp_color(color_center, color_edge, t)
            tex.set_pixel(x, y, color)

    return tex


def _interpolate_stops(
    t: float,
    stops: List[Tuple[float, Tuple[int, int, int]]]
) -> Tuple[int, int, int]:
    """Interpolate color between gradient stops."""
    if not stops:
        return (0, 0, 0)

    # Sort stops by position
    sorted_stops = sorted(stops, key=lambda s: s[0])

    # Handle edge cases
    if t <= sorted_stops[0][0]:
        return sorted_stops[0][1]
    if t >= sorted_stops[-1][0]:
        return sorted_stops[-1][1]

    # Find surrounding stops
    for i in range(len(sorted_stops) - 1):
        pos1, color1 = sorted_stops[i]
        pos2, color2 = sorted_stops[i + 1]

        if pos1 <= t <= pos2:
            local_t = (t - pos1) / (pos2 - pos1) if pos2 > pos1 else 0
            return lerp_color(color1, color2, local_t)

    return sorted_stops[-1][1]
