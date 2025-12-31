"""
Pattern texture generators.

Provides grid, hexagon, checkerboard, and other repeating patterns.
"""

import math
from typing import Tuple, Optional, List
from ...lib.texture_buffer import TextureData
from ...lib.color_utils import hex_to_rgb, lerp_color


def generate_grid_pattern(
    width: int,
    height: int,
    cell_size: int = 16,
    line_width: int = 1,
    line_color: Tuple[int, int, int] = (255, 255, 255),
    bg_color: Tuple[int, int, int] = (0, 0, 0),
) -> TextureData:
    """
    Generate a grid pattern texture.

    Args:
        width: Texture width in pixels
        height: Texture height in pixels
        cell_size: Size of each grid cell
        line_width: Width of grid lines
        line_color: RGB color for grid lines
        bg_color: RGB color for background
    """
    tex = TextureData(width, height)
    tex.fill(bg_color)

    # Draw vertical lines
    for x in range(0, width, cell_size):
        for lw in range(line_width):
            if x + lw < width:
                for y in range(height):
                    tex.set_pixel(x + lw, y, line_color)

    # Draw horizontal lines
    for y in range(0, height, cell_size):
        for lw in range(line_width):
            if y + lw < height:
                for x in range(width):
                    tex.set_pixel(x, y + lw, line_color)

    return tex


def generate_hexagon_pattern(
    width: int,
    height: int,
    hex_size: int = 20,
    line_width: int = 1,
    line_color: Tuple[int, int, int] = (255, 255, 255),
    bg_color: Tuple[int, int, int] = (0, 0, 0),
) -> TextureData:
    """
    Generate a hexagonal grid pattern.

    Args:
        width: Texture width
        height: Texture height
        hex_size: Size of hexagons (radius)
        line_width: Width of hexagon edges
        line_color: Edge color
        bg_color: Background color
    """
    tex = TextureData(width, height)
    tex.fill(bg_color)

    # Hexagon geometry
    h = hex_size * math.sqrt(3)
    w = hex_size * 2

    def draw_hex(cx: int, cy: int):
        """Draw a single hexagon at center (cx, cy)."""
        for i in range(6):
            angle1 = math.pi / 6 + i * math.pi / 3
            angle2 = math.pi / 6 + (i + 1) * math.pi / 3
            x1 = int(cx + hex_size * math.cos(angle1))
            y1 = int(cy + hex_size * math.sin(angle1))
            x2 = int(cx + hex_size * math.cos(angle2))
            y2 = int(cy + hex_size * math.sin(angle2))
            tex.draw_line(x1, y1, x2, y2, line_color)

    # Tile hexagons
    cols = int(width / (w * 0.75)) + 2
    rows = int(height / h) + 2

    for row in range(rows):
        for col in range(cols):
            cx = int(col * w * 0.75)
            cy = int(row * h + (col % 2) * h / 2)
            draw_hex(cx, cy)

    return tex


def generate_checkerboard(
    width: int,
    height: int,
    cell_size: int = 16,
    color1: Tuple[int, int, int] = (255, 255, 255),
    color2: Tuple[int, int, int] = (0, 0, 0),
) -> TextureData:
    """
    Generate a checkerboard pattern.

    Args:
        width: Texture width
        height: Texture height
        cell_size: Size of each checker square
        color1: First checker color
        color2: Second checker color
    """
    tex = TextureData(width, height)

    for y in range(height):
        for x in range(width):
            cell_x = x // cell_size
            cell_y = y // cell_size
            color = color1 if (cell_x + cell_y) % 2 == 0 else color2
            tex.set_pixel(x, y, color)

    return tex


def generate_dots(
    width: int,
    height: int,
    spacing: int = 16,
    dot_radius: int = 3,
    dot_color: Tuple[int, int, int] = (255, 255, 255),
    bg_color: Tuple[int, int, int] = (0, 0, 0),
    stagger: bool = True,
) -> TextureData:
    """
    Generate a dot pattern.

    Args:
        width: Texture width
        height: Texture height
        spacing: Space between dots
        dot_radius: Radius of each dot
        dot_color: Dot color
        bg_color: Background color
        stagger: Whether to stagger rows
    """
    tex = TextureData(width, height)
    tex.fill(bg_color)

    rows = height // spacing + 1
    cols = width // spacing + 1

    for row in range(rows):
        for col in range(cols):
            cx = col * spacing + (spacing // 2 if stagger and row % 2 else 0)
            cy = row * spacing
            if 0 <= cx < width and 0 <= cy < height:
                tex.draw_circle(cx, cy, dot_radius, dot_color, filled=True)

    return tex


def generate_stripes(
    width: int,
    height: int,
    stripe_width: int = 8,
    color1: Tuple[int, int, int] = (255, 255, 255),
    color2: Tuple[int, int, int] = (0, 0, 0),
    angle: float = 0.0,
) -> TextureData:
    """
    Generate a striped pattern.

    Args:
        width: Texture width
        height: Texture height
        stripe_width: Width of each stripe
        color1: First stripe color
        color2: Second stripe color
        angle: Rotation angle in degrees (0 = vertical)
    """
    tex = TextureData(width, height)
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    for y in range(height):
        for x in range(width):
            # Rotate coordinates
            rx = x * cos_a + y * sin_a
            stripe = int(rx / stripe_width) % 2
            color = color1 if stripe == 0 else color2
            tex.set_pixel(x, y, color)

    return tex


def generate_bricks(
    width: int,
    height: int,
    brick_width: int = 32,
    brick_height: int = 16,
    mortar_width: int = 2,
    brick_color: Tuple[int, int, int] = (180, 100, 80),
    mortar_color: Tuple[int, int, int] = (100, 100, 100),
    color_variance: float = 0.1,
) -> TextureData:
    """
    Generate a brick pattern.

    Args:
        width: Texture width
        height: Texture height
        brick_width: Width of each brick
        brick_height: Height of each brick
        mortar_width: Width of mortar lines
        brick_color: Base brick color
        mortar_color: Mortar color
        color_variance: Random color variation (0-1)
    """
    import random

    tex = TextureData(width, height)
    tex.fill(mortar_color)

    rows = height // brick_height + 1

    for row in range(rows):
        offset = (brick_width // 2) if row % 2 else 0
        y_start = row * brick_height + mortar_width
        y_end = (row + 1) * brick_height - mortar_width

        if y_start >= height:
            break

        col = 0
        x_pos = -offset
        while x_pos < width:
            x_start = max(0, x_pos + mortar_width)
            x_end = min(width, x_pos + brick_width - mortar_width)

            # Vary brick color slightly
            var = 1.0 + random.uniform(-color_variance, color_variance)
            r = max(0, min(255, int(brick_color[0] * var)))
            g = max(0, min(255, int(brick_color[1] * var)))
            b = max(0, min(255, int(brick_color[2] * var)))
            color = (r, g, b)

            for y in range(y_start, min(y_end, height)):
                for x in range(x_start, x_end):
                    tex.set_pixel(x, y, color)

            x_pos += brick_width
            col += 1

    return tex
