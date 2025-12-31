"""
Color manipulation utilities.

Provides conversions between color spaces and blending functions.
"""

from typing import Tuple, List
import math


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color string to RGB tuple.

    Args:
        hex_color: Hex string like "#FF00FF" or "FF00FF"

    Returns:
        Tuple of (R, G, B) values 0-255
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB values to hex string.

    Args:
        r, g, b: Color components 0-255

    Returns:
        Hex string like "#FF00FF"
    """
    return f"#{r:02X}{g:02X}{b:02X}"


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """
    Convert HSV to RGB.

    Args:
        h: Hue 0-360
        s: Saturation 0-1
        v: Value 0-1

    Returns:
        Tuple of (R, G, B) values 0-255
    """
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    return (
        int((r + m) * 255),
        int((g + m) * 255),
        int((b + m) * 255)
    )


def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """
    Convert RGB to HSV.

    Args:
        r, g, b: Color components 0-255

    Returns:
        Tuple of (H, S, V) where H is 0-360, S and V are 0-1
    """
    r, g, b = r / 255, g / 255, b / 255

    max_c = max(r, g, b)
    min_c = min(r, g, b)
    diff = max_c - min_c

    # Hue
    if diff == 0:
        h = 0
    elif max_c == r:
        h = 60 * ((g - b) / diff % 6)
    elif max_c == g:
        h = 60 * ((b - r) / diff + 2)
    else:
        h = 60 * ((r - g) / diff + 4)

    # Saturation
    s = 0 if max_c == 0 else diff / max_c

    # Value
    v = max_c

    return (h, s, v)


def lerp_color(
    c1: Tuple[int, int, int],
    c2: Tuple[int, int, int],
    t: float
) -> Tuple[int, int, int]:
    """
    Linear interpolation between two colors.

    Args:
        c1: First color RGB
        c2: Second color RGB
        t: Interpolation factor 0-1

    Returns:
        Interpolated RGB color
    """
    t = max(0, min(1, t))
    return (
        int(c1[0] + t * (c2[0] - c1[0])),
        int(c1[1] + t * (c2[1] - c1[1])),
        int(c1[2] + t * (c2[2] - c1[2])),
    )


def blend_colors(
    colors: List[Tuple[int, int, int]],
    weights: List[float] = None
) -> Tuple[int, int, int]:
    """
    Blend multiple colors together.

    Args:
        colors: List of RGB colors
        weights: Optional weights (defaults to equal)

    Returns:
        Blended RGB color
    """
    if not colors:
        return (0, 0, 0)

    if weights is None:
        weights = [1.0] * len(colors)

    total_weight = sum(weights)
    if total_weight == 0:
        return colors[0]

    r = sum(c[0] * w for c, w in zip(colors, weights)) / total_weight
    g = sum(c[1] * w for c, w in zip(colors, weights)) / total_weight
    b = sum(c[2] * w for c, w in zip(colors, weights)) / total_weight

    return (int(r), int(g), int(b))


def adjust_brightness(
    color: Tuple[int, int, int],
    factor: float
) -> Tuple[int, int, int]:
    """
    Adjust color brightness.

    Args:
        color: RGB color
        factor: Brightness multiplier (>1 brighter, <1 darker)

    Returns:
        Adjusted RGB color
    """
    return (
        max(0, min(255, int(color[0] * factor))),
        max(0, min(255, int(color[1] * factor))),
        max(0, min(255, int(color[2] * factor))),
    )


def adjust_saturation(
    color: Tuple[int, int, int],
    factor: float
) -> Tuple[int, int, int]:
    """
    Adjust color saturation.

    Args:
        color: RGB color
        factor: Saturation multiplier (0=gray, 1=unchanged, >1=more saturated)

    Returns:
        Adjusted RGB color
    """
    h, s, v = rgb_to_hsv(*color)
    s = max(0, min(1, s * factor))
    return hsv_to_rgb(h, s, v)


def shift_hue(
    color: Tuple[int, int, int],
    degrees: float
) -> Tuple[int, int, int]:
    """
    Shift hue by degrees.

    Args:
        color: RGB color
        degrees: Hue shift in degrees

    Returns:
        Adjusted RGB color
    """
    h, s, v = rgb_to_hsv(*color)
    h = (h + degrees) % 360
    return hsv_to_rgb(h, s, v)


def complementary(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Get complementary (opposite) color."""
    return shift_hue(color, 180)


def triadic(color: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
    """Get triadic color scheme (3 colors 120 degrees apart)."""
    return [color, shift_hue(color, 120), shift_hue(color, 240)]


def analogous(
    color: Tuple[int, int, int],
    spread: float = 30
) -> List[Tuple[int, int, int]]:
    """Get analogous color scheme (adjacent colors)."""
    return [shift_hue(color, -spread), color, shift_hue(color, spread)]


def create_palette(
    base_color: Tuple[int, int, int],
    num_colors: int = 5,
    scheme: str = "monochromatic"
) -> List[Tuple[int, int, int]]:
    """
    Create a color palette from a base color.

    Schemes: monochromatic, complementary, triadic, analogous, split_complementary
    """
    if scheme == "monochromatic":
        # Vary lightness
        h, s, v = rgb_to_hsv(*base_color)
        return [hsv_to_rgb(h, s, max(0.2, min(1.0, 0.2 + i * 0.8 / (num_colors - 1))))
                for i in range(num_colors)]

    elif scheme == "complementary":
        comp = complementary(base_color)
        h1, s1, v1 = rgb_to_hsv(*base_color)
        h2, s2, v2 = rgb_to_hsv(*comp)
        return [
            hsv_to_rgb(h1, s1, v1 * 0.7),
            base_color,
            hsv_to_rgb(h1, s1, v1 * 1.3),
            comp,
            hsv_to_rgb(h2, s2, v2 * 0.7),
        ][:num_colors]

    elif scheme == "triadic":
        colors = triadic(base_color)
        return (colors * (num_colors // 3 + 1))[:num_colors]

    elif scheme == "analogous":
        spread = 30 * (num_colors // 2)
        return [shift_hue(base_color, -spread + i * spread * 2 / (num_colors - 1))
                for i in range(num_colors)]

    elif scheme == "split_complementary":
        comp = complementary(base_color)
        return [
            base_color,
            shift_hue(comp, -30),
            shift_hue(comp, 30),
        ] + [shift_hue(base_color, i * 15) for i in range(num_colors - 3)]

    return [base_color] * num_colors


def color_temperature(
    color: Tuple[int, int, int],
    temp: float
) -> Tuple[int, int, int]:
    """
    Adjust color temperature.

    Args:
        color: RGB color
        temp: Temperature adjustment (-1=cool/blue, 0=neutral, 1=warm/orange)

    Returns:
        Adjusted RGB color
    """
    r, g, b = color

    if temp > 0:
        # Warm - add red/orange
        r = min(255, int(r + temp * 30))
        b = max(0, int(b - temp * 20))
    else:
        # Cool - add blue
        r = max(0, int(r + temp * 20))
        b = min(255, int(b - temp * 30))

    return (r, g, b)
