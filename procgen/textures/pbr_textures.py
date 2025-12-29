"""
PBR texture generators for ZX console.

Generates albedo, emission, roughness, and normal maps.
"""

import math
from typing import Tuple, Optional
from .noise_patterns import TextureData, generate_perlin, generate_voronoi
from procgen.core import UniversalStyleParams


def generate_albedo(
    style: UniversalStyleParams,
    width: int = 256,
    height: int = 256,
    base_color: Optional[Tuple[int, int, int]] = None,
    pattern: str = "solid",
    seed: int = 42,
) -> TextureData:
    """
    Generate an albedo (base color) texture.

    Args:
        style: Style tokens for color palette
        width: Texture width
        height: Texture height
        base_color: Override color (or use palette)
        pattern: "solid", "noisy", "gradient", "metallic"
        seed: Random seed
    """
    # Get base color from style or override
    if base_color is None:
        # Use first primary color from palette
        hex_color = style.palette.primary[0] if style.palette.primary else "#808080"
        base_color = hex_to_rgb(hex_color)

    pixels = []

    if pattern == "solid":
        # Solid color
        for y in range(height):
            row = [(base_color[0], base_color[1], base_color[2], 255) for _ in range(width)]
            pixels.append(row)

    elif pattern == "noisy":
        # Add noise variation
        noise = generate_perlin(width, height, scale=8, seed=seed)

        for y in range(height):
            row = []
            for x in range(width):
                # Get noise value (grayscale)
                noise_val = noise.pixels[y][x][0] / 255.0
                # Apply subtle variation
                variation = 0.1 * (noise_val - 0.5)

                r = int(base_color[0] * (1 + variation))
                g = int(base_color[1] * (1 + variation))
                b = int(base_color[2] * (1 + variation))

                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))

                row.append((r, g, b, 255))
            pixels.append(row)

    elif pattern == "gradient":
        # Vertical gradient
        accent_hex = style.palette.accent[0] if style.palette.accent else "#FFFFFF"
        accent_color = hex_to_rgb(accent_hex)

        for y in range(height):
            t = y / height
            row = []
            for x in range(width):
                r = int(base_color[0] * (1 - t) + accent_color[0] * t)
                g = int(base_color[1] * (1 - t) + accent_color[1] * t)
                b = int(base_color[2] * (1 - t) + accent_color[2] * t)
                row.append((r, g, b, 255))
            pixels.append(row)

    elif pattern == "metallic":
        # Metallic with subtle brushed effect
        for y in range(height):
            row = []
            for x in range(width):
                # Horizontal brushed streaks
                streak = math.sin((x + y * 0.1) * 0.5) * 0.1

                r = int(base_color[0] * (0.9 + streak))
                g = int(base_color[1] * (0.9 + streak))
                b = int(base_color[2] * (0.9 + streak))

                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))

                row.append((r, g, b, 255))
            pixels.append(row)

    else:
        # Fallback to solid
        for y in range(height):
            row = [(base_color[0], base_color[1], base_color[2], 255) for _ in range(width)]
            pixels.append(row)

    return TextureData(pixels=pixels, width=width, height=height)


def generate_emission(
    style: UniversalStyleParams,
    width: int = 256,
    height: int = 256,
    emission_color: Optional[Tuple[int, int, int]] = None,
    pattern: str = "glow",
    strength: float = 1.0,
    seed: int = 42,
) -> TextureData:
    """
    Generate an emission texture.

    Args:
        style: Style tokens
        width: Texture width
        height: Texture height
        emission_color: Override color
        pattern: "glow", "strips", "spots", "outline"
        strength: Emission intensity (0-1)
        seed: Random seed
    """
    if emission_color is None:
        hex_color = style.palette.primary[0] if style.palette.primary else "#00FFFF"
        emission_color = hex_to_rgb(hex_color)

    pixels = []

    if pattern == "glow":
        # Central glow
        cx, cy = width / 2, height / 2
        max_dist = math.sqrt(cx ** 2 + cy ** 2)

        for y in range(height):
            row = []
            for x in range(width):
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                glow = max(0, 1 - dist / max_dist)
                glow = glow ** 2 * strength

                r = int(emission_color[0] * glow)
                g = int(emission_color[1] * glow)
                b = int(emission_color[2] * glow)

                row.append((r, g, b, 255))
            pixels.append(row)

    elif pattern == "strips":
        # Horizontal emissive strips
        strip_spacing = height // 6

        for y in range(height):
            row = []
            for x in range(width):
                strip_dist = min(y % strip_spacing, strip_spacing - y % strip_spacing)
                strip_width = 4
                if strip_dist < strip_width:
                    glow = (1 - strip_dist / strip_width) * strength
                else:
                    glow = 0

                r = int(emission_color[0] * glow)
                g = int(emission_color[1] * glow)
                b = int(emission_color[2] * glow)

                row.append((r, g, b, 255))
            pixels.append(row)

    elif pattern == "spots":
        # Random emissive spots
        import random
        random.seed(seed)

        spots = [(random.random() * width, random.random() * height, 10 + random.random() * 20)
                 for _ in range(8)]

        for y in range(height):
            row = []
            for x in range(width):
                glow = 0
                for sx, sy, sr in spots:
                    dist = math.sqrt((x - sx) ** 2 + (y - sy) ** 2)
                    if dist < sr:
                        spot_glow = (1 - dist / sr) ** 2
                        glow = max(glow, spot_glow)

                glow *= strength

                r = int(emission_color[0] * glow)
                g = int(emission_color[1] * glow)
                b = int(emission_color[2] * glow)

                row.append((r, g, b, 255))
            pixels.append(row)

    elif pattern == "outline":
        # Edge glow
        border_width = min(width, height) * 0.1

        for y in range(height):
            row = []
            for x in range(width):
                edge_dist = min(x, y, width - x - 1, height - y - 1)

                if edge_dist < border_width:
                    glow = (1 - edge_dist / border_width) * strength
                else:
                    glow = 0

                r = int(emission_color[0] * glow)
                g = int(emission_color[1] * glow)
                b = int(emission_color[2] * glow)

                row.append((r, g, b, 255))
            pixels.append(row)

    else:
        # No emission
        for y in range(height):
            row = [(0, 0, 0, 255) for _ in range(width)]
            pixels.append(row)

    return TextureData(pixels=pixels, width=width, height=height)


def generate_roughness(
    style: UniversalStyleParams,
    width: int = 256,
    height: int = 256,
    base_roughness: float = 0.5,
    pattern: str = "uniform",
    seed: int = 42,
) -> TextureData:
    """
    Generate a roughness map (grayscale).

    Args:
        style: Style tokens
        width: Texture width
        height: Texture height
        base_roughness: Base roughness value (0=smooth, 1=rough)
        pattern: "uniform", "noisy", "scratched"
        seed: Random seed
    """
    if base_roughness is None:
        # Use style default
        base_roughness = style.materials.base_roughness

    pixels = []

    if pattern == "uniform":
        gray = int(base_roughness * 255)
        for y in range(height):
            row = [(gray, gray, gray, 255) for _ in range(width)]
            pixels.append(row)

    elif pattern == "noisy":
        noise = generate_perlin(width, height, scale=4, seed=seed)

        for y in range(height):
            row = []
            for x in range(width):
                noise_val = noise.pixels[y][x][0] / 255.0
                roughness = base_roughness + (noise_val - 0.5) * 0.3
                roughness = max(0, min(1, roughness))
                gray = int(roughness * 255)
                row.append((gray, gray, gray, 255))
            pixels.append(row)

    elif pattern == "scratched":
        import random
        random.seed(seed)

        # Start with base
        for y in range(height):
            row = []
            for x in range(width):
                gray = int(base_roughness * 255)
                row.append((gray, gray, gray, 255))
            pixels.append(row)

        # Add scratches
        for _ in range(20):
            x1, y1 = random.randint(0, width - 1), random.randint(0, height - 1)
            angle = random.random() * math.pi
            length = random.randint(20, 60)

            for i in range(length):
                x = int(x1 + math.cos(angle) * i)
                y = int(y1 + math.sin(angle) * i)

                if 0 <= x < width and 0 <= y < height:
                    scratch_roughness = base_roughness + 0.3
                    scratch_roughness = min(1, scratch_roughness)
                    gray = int(scratch_roughness * 255)
                    pixels[y][x] = (gray, gray, gray, 255)

    else:
        # Fallback
        gray = int(base_roughness * 255)
        for y in range(height):
            row = [(gray, gray, gray, 255) for _ in range(width)]
            pixels.append(row)

    return TextureData(pixels=pixels, width=width, height=height)


def generate_normal_map(
    width: int = 256,
    height: int = 256,
    pattern: str = "flat",
    strength: float = 0.3,
    seed: int = 42,
) -> TextureData:
    """
    Generate a normal map.

    Args:
        width: Texture width
        height: Texture height
        pattern: "flat", "noisy", "faceted"
        strength: Normal strength (0-1)
        seed: Random seed
    """
    pixels = []

    if pattern == "flat":
        # Flat normal pointing up (128, 128, 255)
        for y in range(height):
            row = [(128, 128, 255, 255) for _ in range(width)]
            pixels.append(row)

    elif pattern == "noisy":
        # Generate height field from noise
        noise = generate_perlin(width, height, scale=4, seed=seed)

        for y in range(height):
            row = []
            for x in range(width):
                # Calculate gradient
                x1 = noise.pixels[y][(x - 1) % width][0] / 255.0
                x2 = noise.pixels[y][(x + 1) % width][0] / 255.0
                y1 = noise.pixels[(y - 1) % height][x][0] / 255.0
                y2 = noise.pixels[(y + 1) % height][x][0] / 255.0

                dx = (x2 - x1) * strength
                dy = (y2 - y1) * strength

                # Normal from gradient
                nx = -dx
                ny = -dy
                nz = 1.0

                # Normalize
                length = math.sqrt(nx * nx + ny * ny + nz * nz)
                if length > 0:
                    nx /= length
                    ny /= length
                    nz /= length

                # Convert to 0-255 range
                r = int((nx * 0.5 + 0.5) * 255)
                g = int((ny * 0.5 + 0.5) * 255)
                b = int((nz * 0.5 + 0.5) * 255)

                row.append((r, g, b, 255))
            pixels.append(row)

    elif pattern == "faceted":
        # Faceted/crystalline normals
        voronoi = generate_voronoi(width, height, num_points=16, seed=seed)

        for y in range(height):
            row = []
            for x in range(width):
                # Use Voronoi distance for facet detection
                val = voronoi.pixels[y][x][0] / 255.0

                # Create slight normal variation per facet
                angle = val * math.pi * 2
                nx = math.cos(angle) * strength * 0.5
                ny = math.sin(angle) * strength * 0.5
                nz = math.sqrt(max(0, 1 - nx * nx - ny * ny))

                r = int((nx * 0.5 + 0.5) * 255)
                g = int((ny * 0.5 + 0.5) * 255)
                b = int((nz * 0.5 + 0.5) * 255)

                row.append((r, g, b, 255))
            pixels.append(row)

    else:
        # Fallback: flat
        for y in range(height):
            row = [(128, 128, 255, 255) for _ in range(width)]
            pixels.append(row)

    return TextureData(pixels=pixels, width=width, height=height)


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
