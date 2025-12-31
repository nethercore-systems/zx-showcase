"""
Pixel art utility functions for 2D sprite generation.

Provides common operations for procedural pixel art:
- Color blending and manipulation
- Noise and dithering
- Palette management
- Image export (PNG)
"""

from typing import List, Tuple, Dict, Optional, Union
from pathlib import Path
import struct


# Type aliases
RGBA = Tuple[int, int, int, int]
RGB = Tuple[int, int, int]
PixelGrid = List[List[RGBA]]


def hex_to_rgba(hex_color: str, alpha: int = 255) -> RGBA:
    """
    Convert hex color string to RGBA tuple.

    Args:
        hex_color: Hex color string (e.g., "#FF00FF" or "FF00FF")
        alpha: Alpha value (0-255)

    Returns:
        RGBA tuple (r, g, b, a)
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 8:
        # RGBA hex
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
            int(hex_color[6:8], 16),
        )
    else:
        # RGB hex
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
            alpha,
        )


def rgba_to_hex(color: RGBA, include_alpha: bool = False) -> str:
    """
    Convert RGBA tuple to hex color string.

    Args:
        color: RGBA tuple
        include_alpha: Whether to include alpha in output

    Returns:
        Hex color string
    """
    if include_alpha:
        return f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}{color[3]:02X}"
    return f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}"


def blend(c1: RGBA, c2: RGBA, t: float) -> RGBA:
    """
    Linear blend between two colors.

    Args:
        c1: First color
        c2: Second color
        t: Blend factor (0.0 = c1, 1.0 = c2)

    Returns:
        Blended color
    """
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] * (1 - t) + c2[0] * t),
        int(c1[1] * (1 - t) + c2[1] * t),
        int(c1[2] * (1 - t) + c2[2] * t),
        int(c1[3] * (1 - t) + c2[3] * t),
    )


def blend_additive(base: RGBA, add: RGBA) -> RGBA:
    """
    Additive blend (useful for lights/glows).

    Args:
        base: Base color
        add: Color to add

    Returns:
        Blended color (clamped to 255)
    """
    return (
        min(255, base[0] + add[0]),
        min(255, base[1] + add[1]),
        min(255, base[2] + add[2]),
        max(base[3], add[3]),
    )


def blend_multiply(base: RGBA, mult: RGBA) -> RGBA:
    """
    Multiplicative blend (useful for shadows).

    Args:
        base: Base color
        mult: Color to multiply by

    Returns:
        Blended color
    """
    return (
        (base[0] * mult[0]) // 255,
        (base[1] * mult[1]) // 255,
        (base[2] * mult[2]) // 255,
        (base[3] * mult[3]) // 255,
    )


def with_alpha(color: RGBA, alpha: int) -> RGBA:
    """
    Return color with modified alpha.

    Args:
        color: Original color
        alpha: New alpha value (0-255)

    Returns:
        Color with new alpha
    """
    return (color[0], color[1], color[2], alpha)


def darken(color: RGBA, amount: float) -> RGBA:
    """
    Darken a color.

    Args:
        color: Original color
        amount: Darkening amount (0.0 = unchanged, 1.0 = black)

    Returns:
        Darkened color
    """
    amount = max(0.0, min(1.0, amount))
    factor = 1.0 - amount
    return (
        int(color[0] * factor),
        int(color[1] * factor),
        int(color[2] * factor),
        color[3],
    )


def lighten(color: RGBA, amount: float) -> RGBA:
    """
    Lighten a color.

    Args:
        color: Original color
        amount: Lightening amount (0.0 = unchanged, 1.0 = white)

    Returns:
        Lightened color
    """
    amount = max(0.0, min(1.0, amount))
    return (
        int(color[0] + (255 - color[0]) * amount),
        int(color[1] + (255 - color[1]) * amount),
        int(color[2] + (255 - color[2]) * amount),
        color[3],
    )


def add_noise(color: RGBA, amount: int, seed: int) -> RGBA:
    """
    Add deterministic noise to a color.

    Args:
        color: Original color
        amount: Maximum noise offset per channel
        seed: Random seed for determinism

    Returns:
        Color with noise applied
    """
    def hash_fn(s: int) -> int:
        # Simple deterministic hash
        x = (s * 0x5851f42d4c957f2d) & 0xFFFFFFFFFFFFFFFF
        return ((x >> 32) % (amount * 2 + 1)) - amount

    return (
        max(0, min(255, color[0] + hash_fn(seed))),
        max(0, min(255, color[1] + hash_fn(seed + 1))),
        max(0, min(255, color[2] + hash_fn(seed + 2))),
        color[3],
    )


def dither_2x2(c1: RGBA, c2: RGBA) -> List[List[RGBA]]:
    """
    Create a 2x2 ordered dither pattern.

    Args:
        c1: First color
        c2: Second color

    Returns:
        2x2 pixel grid with dither pattern
    """
    return [
        [c1, c2],
        [c2, c1],
    ]


def dither_4x4(c1: RGBA, c2: RGBA, threshold: float = 0.5) -> List[List[RGBA]]:
    """
    Create a 4x4 Bayer dither pattern.

    Args:
        c1: Color for below threshold
        c2: Color for above threshold
        threshold: Dither threshold (0.0 to 1.0)

    Returns:
        4x4 pixel grid with dither pattern
    """
    # Bayer 4x4 matrix (normalized 0-1)
    bayer = [
        [0/16, 8/16, 2/16, 10/16],
        [12/16, 4/16, 14/16, 6/16],
        [3/16, 11/16, 1/16, 9/16],
        [15/16, 7/16, 13/16, 5/16],
    ]

    result = []
    for row in bayer:
        result_row = []
        for val in row:
            result_row.append(c1 if val < threshold else c2)
        result.append(result_row)

    return result


def create_gradient_horizontal(
    width: int,
    height: int,
    color_left: RGBA,
    color_right: RGBA,
) -> PixelGrid:
    """
    Create a horizontal gradient.

    Args:
        width: Image width
        height: Image height
        color_left: Left color
        color_right: Right color

    Returns:
        Pixel grid with gradient
    """
    pixels = []
    for _ in range(height):
        row = []
        for x in range(width):
            t = x / (width - 1) if width > 1 else 0
            row.append(blend(color_left, color_right, t))
        pixels.append(row)
    return pixels


def create_gradient_vertical(
    width: int,
    height: int,
    color_top: RGBA,
    color_bottom: RGBA,
) -> PixelGrid:
    """
    Create a vertical gradient.

    Args:
        width: Image width
        height: Image height
        color_top: Top color
        color_bottom: Bottom color

    Returns:
        Pixel grid with gradient
    """
    pixels = []
    for y in range(height):
        t = y / (height - 1) if height > 1 else 0
        color = blend(color_top, color_bottom, t)
        pixels.append([color for _ in range(width)])
    return pixels


def create_radial_gradient(
    width: int,
    height: int,
    color_center: RGBA,
    color_edge: RGBA,
    center: Optional[Tuple[float, float]] = None,
) -> PixelGrid:
    """
    Create a radial gradient.

    Args:
        width: Image width
        height: Image height
        color_center: Center color
        color_edge: Edge color
        center: Center point (normalized 0-1), defaults to (0.5, 0.5)

    Returns:
        Pixel grid with gradient
    """
    import math

    if center is None:
        center = (0.5, 0.5)

    cx = center[0] * width
    cy = center[1] * height
    max_dist = math.sqrt((width / 2) ** 2 + (height / 2) ** 2)

    pixels = []
    for y in range(height):
        row = []
        for x in range(width):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            t = min(1.0, dist / max_dist)
            row.append(blend(color_center, color_edge, t))
        pixels.append(row)

    return pixels


def export_png(
    pixels: PixelGrid,
    filepath: Union[str, Path],
) -> None:
    """
    Export pixel grid to PNG file.

    Uses a minimal PNG encoder (no PIL required).

    Args:
        pixels: 2D list of RGBA tuples
        filepath: Output file path
    """
    import zlib

    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    height = len(pixels)
    width = len(pixels[0]) if height > 0 else 0

    def make_chunk(chunk_type: bytes, data: bytes) -> bytes:
        """Create a PNG chunk with CRC."""
        chunk = chunk_type + data
        crc = zlib.crc32(chunk) & 0xffffffff
        return struct.pack('>I', len(data)) + chunk + struct.pack('>I', crc)

    # PNG signature
    png_data = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    png_data += make_chunk(b'IHDR', ihdr_data)

    # IDAT chunk (image data)
    raw_data = b''
    for row in pixels:
        raw_data += b'\x00'  # Filter byte (none)
        for r, g, b, a in row:
            raw_data += bytes([r, g, b, a])

    compressed = zlib.compress(raw_data, 9)
    png_data += make_chunk(b'IDAT', compressed)

    # IEND chunk
    png_data += make_chunk(b'IEND', b'')

    filepath.write_bytes(png_data)


def export_ppm(
    pixels: PixelGrid,
    filepath: Union[str, Path],
) -> None:
    """
    Export pixel grid to PPM file (no alpha).

    Args:
        pixels: 2D list of RGBA tuples
        filepath: Output file path
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    height = len(pixels)
    width = len(pixels[0]) if height > 0 else 0

    with open(filepath, 'wb') as f:
        # PPM header
        header = f"P6\n{width} {height}\n255\n"
        f.write(header.encode('ascii'))

        # Pixel data (RGB only)
        for row in pixels:
            for r, g, b, a in row:
                f.write(bytes([r, g, b]))


def quantize_to_palette(
    color: RGBA,
    palette: List[RGBA],
) -> RGBA:
    """
    Quantize a color to the nearest palette color.

    Args:
        color: Original color
        palette: List of palette colors

    Returns:
        Nearest palette color
    """
    if not palette:
        return color

    def color_distance(c1: RGBA, c2: RGBA) -> float:
        # Simple Euclidean distance in RGB space
        return (
            (c1[0] - c2[0]) ** 2 +
            (c1[1] - c2[1]) ** 2 +
            (c1[2] - c2[2]) ** 2
        )

    nearest = palette[0]
    min_dist = color_distance(color, palette[0])

    for pal_color in palette[1:]:
        dist = color_distance(color, pal_color)
        if dist < min_dist:
            min_dist = dist
            nearest = pal_color

    return nearest


def apply_palette(
    pixels: PixelGrid,
    palette: List[RGBA],
) -> PixelGrid:
    """
    Quantize all pixels to a palette.

    Args:
        pixels: Original pixel grid
        palette: List of palette colors

    Returns:
        Quantized pixel grid
    """
    return [
        [quantize_to_palette(pixel, palette) for pixel in row]
        for row in pixels
    ]
