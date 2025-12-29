"""
Procedural noise pattern generators.

Generates various noise textures for use in material creation.
All functions return numpy arrays that can be saved as images.
"""

import math
from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class TextureData:
    """Raw texture data."""
    pixels: List[List[Tuple[int, int, int, int]]]  # RGBA
    width: int
    height: int

    def get_flat_rgba(self) -> bytes:
        """Get flat RGBA bytes for image creation."""
        data = []
        for row in self.pixels:
            for r, g, b, a in row:
                data.extend([r, g, b, a])
        return bytes(data)


def generate_perlin(
    width: int = 256,
    height: int = 256,
    scale: float = 4.0,
    octaves: int = 4,
    seed: int = 42,
) -> TextureData:
    """
    Generate a Perlin-like noise texture.

    Args:
        width: Texture width
        height: Texture height
        scale: Noise scale (larger = coarser)
        octaves: Number of noise octaves
        seed: Random seed
    """
    import random
    random.seed(seed)

    # Generate permutation table
    perm = list(range(256))
    random.shuffle(perm)
    perm = perm + perm  # Double for wrapping

    def fade(t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(t, a, b):
        return a + t * (b - a)

    def grad(hash_val, x, y):
        h = hash_val & 3
        u = x if h < 2 else y
        v = y if h < 2 else x
        return (u if h & 1 == 0 else -u) + (v if h & 2 == 0 else -v)

    def noise2d(x, y):
        xi = int(x) & 255
        yi = int(y) & 255
        xf = x - int(x)
        yf = y - int(y)

        u = fade(xf)
        v = fade(yf)

        aa = perm[perm[xi] + yi]
        ab = perm[perm[xi] + yi + 1]
        ba = perm[perm[xi + 1] + yi]
        bb = perm[perm[xi + 1] + yi + 1]

        x1 = lerp(u, grad(aa, xf, yf), grad(ba, xf - 1, yf))
        x2 = lerp(u, grad(ab, xf, yf - 1), grad(bb, xf - 1, yf - 1))

        return lerp(v, x1, x2)

    pixels = []
    for y in range(height):
        row = []
        for x in range(width):
            value = 0.0
            amplitude = 1.0
            frequency = 1.0

            for _ in range(octaves):
                nx = x / width * scale * frequency
                ny = y / height * scale * frequency
                value += noise2d(nx, ny) * amplitude
                amplitude *= 0.5
                frequency *= 2.0

            # Normalize to 0-255
            value = (value + 1) / 2  # -1..1 to 0..1
            value = max(0, min(1, value))
            gray = int(value * 255)
            row.append((gray, gray, gray, 255))
        pixels.append(row)

    return TextureData(pixels=pixels, width=width, height=height)


def generate_voronoi(
    width: int = 256,
    height: int = 256,
    num_points: int = 32,
    seed: int = 42,
    invert: bool = False,
) -> TextureData:
    """
    Generate a Voronoi cell texture.

    Args:
        width: Texture width
        height: Texture height
        num_points: Number of cell centers
        seed: Random seed
        invert: Invert the result (cells vs edges)
    """
    import random
    random.seed(seed)

    # Generate random points
    points = [(random.random() * width, random.random() * height) for _ in range(num_points)]

    pixels = []
    for y in range(height):
        row = []
        for x in range(width):
            # Find distance to nearest point
            min_dist = float('inf')
            for px, py in points:
                dist = math.sqrt((x - px) ** 2 + (y - py) ** 2)
                if dist < min_dist:
                    min_dist = dist

            # Normalize distance
            max_possible = math.sqrt(width ** 2 + height ** 2) / math.sqrt(num_points)
            value = min(1.0, min_dist / max_possible)

            if invert:
                value = 1.0 - value

            gray = int(value * 255)
            row.append((gray, gray, gray, 255))
        pixels.append(row)

    return TextureData(pixels=pixels, width=width, height=height)


def generate_cellular(
    width: int = 256,
    height: int = 256,
    cell_size: int = 32,
    border_width: int = 2,
    seed: int = 42,
) -> TextureData:
    """
    Generate a cellular/grid texture.

    Args:
        width: Texture width
        height: Texture height
        cell_size: Size of each cell
        border_width: Width of cell borders
        seed: Random seed for variation
    """
    import random
    random.seed(seed)

    pixels = []
    for y in range(height):
        row = []
        for x in range(width):
            # Check if on border
            x_mod = x % cell_size
            y_mod = y % cell_size

            on_border = (
                x_mod < border_width or
                x_mod >= cell_size - border_width or
                y_mod < border_width or
                y_mod >= cell_size - border_width
            )

            if on_border:
                gray = 200 + random.randint(-20, 20)  # Bright border with variation
            else:
                gray = 40 + random.randint(-10, 10)  # Dark interior

            gray = max(0, min(255, gray))
            row.append((gray, gray, gray, 255))
        pixels.append(row)

    return TextureData(pixels=pixels, width=width, height=height)


def generate_gradient(
    width: int = 256,
    height: int = 256,
    direction: str = "vertical",
    color_start: Tuple[int, int, int] = (0, 0, 0),
    color_end: Tuple[int, int, int] = (255, 255, 255),
) -> TextureData:
    """
    Generate a gradient texture.

    Args:
        width: Texture width
        height: Texture height
        direction: "vertical", "horizontal", "radial", "diagonal"
        color_start: Starting color RGB
        color_end: Ending color RGB
    """
    pixels = []

    for y in range(height):
        row = []
        for x in range(width):
            if direction == "vertical":
                t = y / height
            elif direction == "horizontal":
                t = x / width
            elif direction == "radial":
                cx, cy = width / 2, height / 2
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                max_dist = math.sqrt(cx ** 2 + cy ** 2)
                t = dist / max_dist
            elif direction == "diagonal":
                t = (x + y) / (width + height)
            else:
                t = 0.5

            t = max(0, min(1, t))

            r = int(color_start[0] + t * (color_end[0] - color_start[0]))
            g = int(color_start[1] + t * (color_end[1] - color_start[1]))
            b = int(color_start[2] + t * (color_end[2] - color_start[2]))

            row.append((r, g, b, 255))
        pixels.append(row)

    return TextureData(pixels=pixels, width=width, height=height)


def generate_hexagon_grid(
    width: int = 256,
    height: int = 256,
    hex_size: int = 24,
    line_width: int = 2,
    line_color: Tuple[int, int, int] = (100, 200, 255),
    bg_color: Tuple[int, int, int] = (10, 15, 25),
) -> TextureData:
    """
    Generate a hexagonal grid texture (useful for crystalline/tech aesthetics).

    Args:
        width: Texture width
        height: Texture height
        hex_size: Size of hexagon cells
        line_width: Width of grid lines
        line_color: RGB color for lines
        bg_color: RGB color for background
    """
    pixels = [[bg_color + (255,) for _ in range(width)] for _ in range(height)]

    # Calculate hex dimensions
    hex_width = hex_size * 2
    hex_height = int(hex_size * math.sqrt(3))

    def point_to_hex_distance(x, y, cx, cy, size):
        """Distance from point to nearest hex edge."""
        dx = abs(x - cx)
        dy = abs(y - cy)

        # Hexagon distance approximation
        return max(dx * 2 / 3, dy * 0.5 + dx * 0.25) - size * 0.5

    for row_idx in range(int(height / hex_height) + 2):
        for col_idx in range(int(width / hex_width) + 2):
            # Calculate hex center
            cx = col_idx * hex_width * 0.75
            cy = row_idx * hex_height + (col_idx % 2) * hex_height * 0.5

            # Draw hex outline in nearby pixels
            for py in range(max(0, int(cy - hex_size)), min(height, int(cy + hex_size))):
                for px in range(max(0, int(cx - hex_size)), min(width, int(cx + hex_size))):
                    dist = point_to_hex_distance(px, py, cx, cy, hex_size)
                    if abs(dist) < line_width:
                        pixels[py][px] = line_color + (255,)

    return TextureData(pixels=pixels, width=width, height=height)
