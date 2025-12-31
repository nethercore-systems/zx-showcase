"""
Texture buffer utilities for procedural texture generation.

Provides the TextureData class and pixel manipulation functions.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import math


@dataclass
class TextureData:
    """Raw texture data container."""
    pixels: List[List[Tuple[int, int, int, int]]]  # RGBA
    width: int
    height: int
    name: str = ""

    def get_flat_rgba(self) -> bytes:
        """Get flat RGBA bytes for image creation."""
        data = []
        for row in self.pixels:
            for r, g, b, a in row:
                data.extend([r, g, b, a])
        return bytes(data)

    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int, int]:
        """Get pixel at position (clamped to bounds)."""
        x = max(0, min(self.width - 1, x))
        y = max(0, min(self.height - 1, y))
        return self.pixels[y][x]

    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int, int]) -> None:
        """Set pixel at position (clamped to bounds)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color

    def fill(self, color: Tuple[int, int, int, int]) -> None:
        """Fill entire texture with color."""
        for y in range(self.height):
            for x in range(self.width):
                self.pixels[y][x] = color

    def blend(self, other: "TextureData", mode: str = "multiply", factor: float = 1.0) -> "TextureData":
        """
        Blend another texture onto this one.

        Modes: multiply, add, overlay, screen
        """
        if other.width != self.width or other.height != self.height:
            raise ValueError("Textures must be same size for blending")

        result = create_texture(self.width, self.height)

        for y in range(self.height):
            for x in range(self.width):
                c1 = self.pixels[y][x]
                c2 = other.pixels[y][x]

                if mode == "multiply":
                    r = int(c1[0] * c2[0] / 255 * factor + c1[0] * (1 - factor))
                    g = int(c1[1] * c2[1] / 255 * factor + c1[1] * (1 - factor))
                    b = int(c1[2] * c2[2] / 255 * factor + c1[2] * (1 - factor))
                elif mode == "add":
                    r = min(255, int(c1[0] + c2[0] * factor))
                    g = min(255, int(c1[1] + c2[1] * factor))
                    b = min(255, int(c1[2] + c2[2] * factor))
                elif mode == "screen":
                    r = int(255 - (255 - c1[0]) * (255 - c2[0]) / 255 * factor)
                    g = int(255 - (255 - c1[1]) * (255 - c2[1]) / 255 * factor)
                    b = int(255 - (255 - c1[2]) * (255 - c2[2]) / 255 * factor)
                else:  # overlay
                    r = _overlay_channel(c1[0], c2[0], factor)
                    g = _overlay_channel(c1[1], c2[1], factor)
                    b = _overlay_channel(c1[2], c2[2], factor)

                result.pixels[y][x] = (
                    max(0, min(255, r)),
                    max(0, min(255, g)),
                    max(0, min(255, b)),
                    255
                )

        return result

    def resize(self, new_width: int, new_height: int) -> "TextureData":
        """Resize texture using nearest neighbor sampling."""
        result = create_texture(new_width, new_height)

        for y in range(new_height):
            for x in range(new_width):
                src_x = int(x * self.width / new_width)
                src_y = int(y * self.height / new_height)
                result.pixels[y][x] = self.get_pixel(src_x, src_y)

        return result


def _overlay_channel(base: int, blend: int, factor: float) -> int:
    """Overlay blend mode for single channel."""
    if base < 128:
        result = 2 * base * blend / 255
    else:
        result = 255 - 2 * (255 - base) * (255 - blend) / 255
    return int(base * (1 - factor) + result * factor)


def create_texture(
    width: int,
    height: int,
    fill_color: Tuple[int, int, int, int] = (0, 0, 0, 255)
) -> TextureData:
    """Create a new texture filled with a color."""
    pixels = [[fill_color for _ in range(width)] for _ in range(height)]
    return TextureData(pixels=pixels, width=width, height=height)


def draw_line(
    tex: TextureData,
    x1: int, y1: int,
    x2: int, y2: int,
    color: Tuple[int, int, int, int],
    width: int = 1
) -> None:
    """Draw a line using Bresenham's algorithm."""
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    x, y = x1, y1

    while True:
        # Draw with width
        for wx in range(-width // 2, width // 2 + 1):
            for wy in range(-width // 2, width // 2 + 1):
                tex.set_pixel(x + wx, y + wy, color)

        if x == x2 and y == y2:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def draw_rect(
    tex: TextureData,
    x: int, y: int,
    w: int, h: int,
    color: Tuple[int, int, int, int],
    filled: bool = True
) -> None:
    """Draw a rectangle."""
    if filled:
        for py in range(y, y + h):
            for px in range(x, x + w):
                tex.set_pixel(px, py, color)
    else:
        # Top and bottom
        for px in range(x, x + w):
            tex.set_pixel(px, y, color)
            tex.set_pixel(px, y + h - 1, color)
        # Left and right
        for py in range(y, y + h):
            tex.set_pixel(x, py, color)
            tex.set_pixel(x + w - 1, py, color)


def draw_circle(
    tex: TextureData,
    cx: int, cy: int,
    radius: int,
    color: Tuple[int, int, int, int],
    filled: bool = True
) -> None:
    """Draw a circle using midpoint algorithm."""
    if filled:
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                    tex.set_pixel(x, y, color)
    else:
        x = radius
        y = 0
        err = 0

        while x >= y:
            tex.set_pixel(cx + x, cy + y, color)
            tex.set_pixel(cx + y, cy + x, color)
            tex.set_pixel(cx - y, cy + x, color)
            tex.set_pixel(cx - x, cy + y, color)
            tex.set_pixel(cx - x, cy - y, color)
            tex.set_pixel(cx - y, cy - x, color)
            tex.set_pixel(cx + y, cy - x, color)
            tex.set_pixel(cx + x, cy - y, color)

            y += 1
            err += 1 + 2 * y
            if 2 * (err - x) + 1 > 0:
                x -= 1
                err += 1 - 2 * x


def draw_gradient(
    tex: TextureData,
    direction: str,
    color_start: Tuple[int, int, int],
    color_end: Tuple[int, int, int]
) -> None:
    """
    Fill texture with a gradient.

    Direction: "vertical", "horizontal", "radial", "diagonal"
    """
    for y in range(tex.height):
        for x in range(tex.width):
            if direction == "vertical":
                t = y / tex.height
            elif direction == "horizontal":
                t = x / tex.width
            elif direction == "radial":
                cx, cy = tex.width / 2, tex.height / 2
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                max_dist = math.sqrt(cx ** 2 + cy ** 2)
                t = dist / max_dist
            elif direction == "diagonal":
                t = (x + y) / (tex.width + tex.height)
            else:
                t = 0.5

            t = max(0, min(1, t))

            r = int(color_start[0] + t * (color_end[0] - color_start[0]))
            g = int(color_start[1] + t * (color_end[1] - color_start[1]))
            b = int(color_start[2] + t * (color_end[2] - color_start[2]))

            tex.set_pixel(x, y, (r, g, b, 255))
