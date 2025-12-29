"""
Glow effect texture generators.

Generates emission textures for neon, bioluminescence, and prismatic effects.
"""

import math
from typing import Tuple, List
from .noise_patterns import TextureData, generate_perlin


def generate_neon_glow(
    width: int = 256,
    height: int = 256,
    color: Tuple[int, int, int] = (0, 255, 255),
    pattern: str = "strips",
    glow_falloff: float = 0.5,
    intensity: float = 1.0,
) -> TextureData:
    """
    Generate a neon glow emission texture.

    Args:
        width: Texture width
        height: Texture height
        color: Base neon color RGB
        pattern: "strips", "border", "radial", "circuit"
        glow_falloff: How quickly glow fades (0-1)
        intensity: Overall intensity multiplier
    """
    pixels = []

    for y in range(height):
        row = []
        for x in range(width):
            glow = 0.0

            if pattern == "strips":
                # Horizontal strips with glow
                strip_spacing = height // 4
                for strip_y in range(0, height, strip_spacing):
                    dist = abs(y - strip_y)
                    glow = max(glow, math.exp(-dist * glow_falloff * 0.1))

            elif pattern == "border":
                # Glowing border
                border_dist = min(x, y, width - x - 1, height - y - 1)
                border_width = min(width, height) * 0.1
                if border_dist < border_width:
                    glow = 1.0 - (border_dist / border_width) ** glow_falloff

            elif pattern == "radial":
                # Radial glow from center
                cx, cy = width / 2, height / 2
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                max_dist = math.sqrt(cx ** 2 + cy ** 2)
                glow = 1.0 - (dist / max_dist) ** glow_falloff

            elif pattern == "circuit":
                # Circuit-like pattern
                cell_size = width // 8
                x_mod = x % cell_size
                y_mod = y % cell_size

                # Lines at certain positions
                line_width = 3
                on_line = (
                    x_mod < line_width or
                    y_mod < line_width or
                    (x_mod > cell_size // 2 - line_width and x_mod < cell_size // 2 + line_width) or
                    (y_mod > cell_size // 2 - line_width and y_mod < cell_size // 2 + line_width)
                )

                if on_line:
                    glow = 1.0
                else:
                    # Fade from lines
                    min_dist = min(
                        x_mod, y_mod,
                        abs(x_mod - cell_size // 2),
                        abs(y_mod - cell_size // 2)
                    )
                    glow = math.exp(-min_dist * glow_falloff * 0.3)

            glow = min(1.0, glow * intensity)

            r = int(color[0] * glow)
            g = int(color[1] * glow)
            b = int(color[2] * glow)

            row.append((r, g, b, 255))
        pixels.append(row)

    return TextureData(pixels=pixels, width=width, height=height)


def generate_bioluminescence(
    width: int = 256,
    height: int = 256,
    color_primary: Tuple[int, int, int] = (0, 255, 200),
    color_secondary: Tuple[int, int, int] = (100, 180, 255),
    spot_count: int = 12,
    spot_size: float = 0.15,
    blend_factor: float = 0.5,
    seed: int = 42,
) -> TextureData:
    """
    Generate a bioluminescent glow texture with organic spots.

    Args:
        width: Texture width
        height: Texture height
        color_primary: Primary glow color
        color_secondary: Secondary glow color
        spot_count: Number of glow spots
        spot_size: Size of spots relative to texture
        blend_factor: How much colors blend (0-1)
        seed: Random seed
    """
    import random
    random.seed(seed)

    # Generate spot positions
    spots = []
    for _ in range(spot_count):
        spots.append((
            random.random() * width,
            random.random() * height,
            spot_size * min(width, height) * (0.5 + random.random()),
            random.random(),  # Primary/secondary mix
        ))

    pixels = []
    for y in range(height):
        row = []
        for x in range(width):
            glow = 0.0
            color_mix = 0.0

            for sx, sy, size, mix in spots:
                # Distance to spot center
                dist = math.sqrt((x - sx) ** 2 + (y - sy) ** 2)

                if dist < size:
                    # Organic falloff (smooth)
                    spot_glow = (1.0 - (dist / size) ** 2) ** 2
                    if spot_glow > glow:
                        glow = spot_glow
                        color_mix = mix

            # Blend colors based on spot
            t = color_mix * blend_factor + (1 - blend_factor) * 0.5
            r = int(color_primary[0] * (1 - t) + color_secondary[0] * t) * glow
            g = int(color_primary[1] * (1 - t) + color_secondary[1] * t) * glow
            b = int(color_primary[2] * (1 - t) + color_secondary[2] * t) * glow

            r = min(255, int(r))
            g = min(255, int(g))
            b = min(255, int(b))

            row.append((r, g, b, 255))
        pixels.append(row)

    return TextureData(pixels=pixels, width=width, height=height)


def generate_prismatic_glow(
    width: int = 256,
    height: int = 256,
    pattern: str = "facets",
    saturation: float = 1.0,
    brightness: float = 1.0,
    seed: int = 42,
) -> TextureData:
    """
    Generate a prismatic/rainbow glow texture.

    Args:
        width: Texture width
        height: Texture height
        pattern: "facets", "gradient", "shatter"
        saturation: Color saturation (0-1)
        brightness: Overall brightness (0-1)
        seed: Random seed
    """
    import random
    random.seed(seed)

    def hsv_to_rgb(h, s, v):
        """Convert HSV to RGB."""
        if s == 0:
            return (int(v * 255),) * 3

        h = h * 6
        i = int(h)
        f = h - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))

        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

        return (int(r * 255), int(g * 255), int(b * 255))

    pixels = []

    if pattern == "facets":
        # Create Voronoi-like facets with rainbow colors
        num_facets = 16
        facet_centers = [(random.random() * width, random.random() * height) for _ in range(num_facets)]
        facet_hues = [random.random() for _ in range(num_facets)]

        for y in range(height):
            row = []
            for x in range(width):
                # Find nearest facet
                min_dist = float('inf')
                nearest_idx = 0
                for idx, (fx, fy) in enumerate(facet_centers):
                    dist = (x - fx) ** 2 + (y - fy) ** 2
                    if dist < min_dist:
                        min_dist = dist
                        nearest_idx = idx

                hue = facet_hues[nearest_idx]
                r, g, b = hsv_to_rgb(hue, saturation, brightness)
                row.append((r, g, b, 255))
            pixels.append(row)

    elif pattern == "gradient":
        # Rainbow gradient across texture
        for y in range(height):
            row = []
            for x in range(width):
                # Diagonal rainbow
                hue = ((x + y) / (width + height)) % 1.0
                r, g, b = hsv_to_rgb(hue, saturation, brightness)
                row.append((r, g, b, 255))
            pixels.append(row)

    elif pattern == "shatter":
        # Shattered glass with prismatic colors
        num_shards = 24
        shard_centers = [(random.random() * width, random.random() * height) for _ in range(num_shards)]

        for y in range(height):
            row = []
            for x in range(width):
                # Find two nearest shards for edge detection
                distances = []
                for idx, (sx, sy) in enumerate(shard_centers):
                    dist = math.sqrt((x - sx) ** 2 + (y - sy) ** 2)
                    distances.append((dist, idx))
                distances.sort()

                # Use nearest shard for hue
                nearest_idx = distances[0][1]
                hue = (nearest_idx / num_shards) % 1.0

                # Brighten edges between shards
                edge_dist = abs(distances[0][0] - distances[1][0])
                edge_factor = max(0, 1.0 - edge_dist * 0.05)

                final_brightness = brightness * (0.7 + edge_factor * 0.3)
                r, g, b = hsv_to_rgb(hue, saturation, final_brightness)
                row.append((r, g, b, 255))
            pixels.append(row)

    else:
        # Default: solid prismatic
        for y in range(height):
            row = []
            for x in range(width):
                hue = (x / width)
                r, g, b = hsv_to_rgb(hue, saturation, brightness)
                row.append((r, g, b, 255))
            pixels.append(row)

    return TextureData(pixels=pixels, width=width, height=height)
