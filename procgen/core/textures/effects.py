"""
Texture effect processors.

Provides glow, emission, rim light, and post-processing effects.
"""

import math
from typing import Tuple, Optional
from ...lib.texture_buffer import TextureData
from ...lib.color_utils import lerp_color


def apply_glow(
    tex: TextureData,
    intensity: float = 1.0,
    radius: int = 10,
    threshold: float = 0.5,
    color: Optional[Tuple[int, int, int]] = None,
) -> TextureData:
    """
    Apply a glow effect to bright areas.

    Args:
        tex: Input texture
        intensity: Glow intensity (0-2)
        radius: Blur radius for glow
        threshold: Brightness threshold for glow (0-1)
        color: Optional tint color for glow
    """
    result = TextureData(tex.width, tex.height)
    threshold_val = int(threshold * 255)

    # First pass: copy original
    for y in range(tex.height):
        for x in range(tex.width):
            result.set_pixel(x, y, tex.get_pixel(x, y))

    # Second pass: add glow from bright pixels
    for y in range(tex.height):
        for x in range(tex.width):
            pixel = tex.get_pixel(x, y)
            brightness = max(pixel)

            if brightness > threshold_val:
                glow_intensity = (brightness - threshold_val) / (255 - threshold_val)
                glow_intensity *= intensity

                # Apply glow in radius
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < tex.width and 0 <= ny < tex.height:
                            dist = math.sqrt(dx * dx + dy * dy)
                            if dist <= radius:
                                falloff = 1 - (dist / radius)
                                glow_amount = glow_intensity * falloff

                                orig = result.get_pixel(nx, ny)
                                if color:
                                    glow_color = (
                                        int(color[0] * glow_amount),
                                        int(color[1] * glow_amount),
                                        int(color[2] * glow_amount),
                                    )
                                else:
                                    glow_color = (
                                        int(pixel[0] * glow_amount),
                                        int(pixel[1] * glow_amount),
                                        int(pixel[2] * glow_amount),
                                    )

                                new_color = (
                                    min(255, orig[0] + glow_color[0]),
                                    min(255, orig[1] + glow_color[1]),
                                    min(255, orig[2] + glow_color[2]),
                                )
                                result.set_pixel(nx, ny, new_color)

    return result


def apply_emission(
    tex: TextureData,
    emission_color: Tuple[int, int, int],
    strength: float = 1.0,
    mask: Optional[TextureData] = None,
) -> TextureData:
    """
    Apply emission overlay to texture.

    Args:
        tex: Input texture
        emission_color: Emission color (RGB)
        strength: Emission strength (0-2)
        mask: Optional mask texture (bright = more emission)
    """
    result = TextureData(tex.width, tex.height)

    for y in range(tex.height):
        for x in range(tex.width):
            pixel = tex.get_pixel(x, y)

            if mask:
                mask_val = max(mask.get_pixel(x, y)) / 255
            else:
                mask_val = 1.0

            emit_strength = strength * mask_val
            new_color = (
                min(255, int(pixel[0] + emission_color[0] * emit_strength)),
                min(255, int(pixel[1] + emission_color[1] * emit_strength)),
                min(255, int(pixel[2] + emission_color[2] * emit_strength)),
            )
            result.set_pixel(x, y, new_color)

    return result


def apply_rim_light(
    tex: TextureData,
    normal_map: Optional[TextureData] = None,
    light_color: Tuple[int, int, int] = (255, 255, 255),
    intensity: float = 1.0,
    power: float = 3.0,
) -> TextureData:
    """
    Apply rim lighting effect based on edge detection or normals.

    Args:
        tex: Input texture
        normal_map: Optional normal map for accurate rim lighting
        light_color: Rim light color
        intensity: Light intensity
        power: Falloff power (higher = sharper rim)
    """
    result = TextureData(tex.width, tex.height)

    for y in range(tex.height):
        for x in range(tex.width):
            pixel = tex.get_pixel(x, y)

            if normal_map:
                # Use normal map for rim calculation
                normal = normal_map.get_pixel(x, y)
                nx = (normal[0] / 255 - 0.5) * 2
                ny = (normal[1] / 255 - 0.5) * 2
                nz = normal[2] / 255

                # Rim based on view angle (assume view from front)
                rim = 1 - abs(nz)
            else:
                # Simple edge detection
                edge = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx_, ny_ = x + dx, y + dy
                        if 0 <= nx_ < tex.width and 0 <= ny_ < tex.height:
                            neighbor = tex.get_pixel(nx_, ny_)
                            diff = abs(max(pixel) - max(neighbor))
                            edge = max(edge, diff / 255)
                rim = edge

            rim = pow(rim, power) * intensity
            new_color = (
                min(255, int(pixel[0] + light_color[0] * rim)),
                min(255, int(pixel[1] + light_color[1] * rim)),
                min(255, int(pixel[2] + light_color[2] * rim)),
            )
            result.set_pixel(x, y, new_color)

    return result


def apply_scanlines(
    tex: TextureData,
    line_spacing: int = 4,
    line_opacity: float = 0.3,
    horizontal: bool = True,
) -> TextureData:
    """
    Apply CRT-style scanlines effect.

    Args:
        tex: Input texture
        line_spacing: Pixels between scanlines
        line_opacity: Darkness of scanlines (0-1)
        horizontal: True for horizontal lines, False for vertical
    """
    result = TextureData(tex.width, tex.height)
    darken = 1 - line_opacity

    for y in range(tex.height):
        for x in range(tex.width):
            pixel = tex.get_pixel(x, y)
            pos = y if horizontal else x

            if pos % line_spacing < 2:
                new_color = (
                    int(pixel[0] * darken),
                    int(pixel[1] * darken),
                    int(pixel[2] * darken),
                )
            else:
                new_color = pixel

            result.set_pixel(x, y, new_color)

    return result


def apply_chromatic_aberration(
    tex: TextureData,
    offset: int = 3,
    direction: str = "horizontal",
) -> TextureData:
    """
    Apply chromatic aberration (color fringing) effect.

    Args:
        tex: Input texture
        offset: Pixel offset for color channels
        direction: "horizontal", "vertical", or "radial"
    """
    result = TextureData(tex.width, tex.height)
    cx, cy = tex.width / 2, tex.height / 2

    for y in range(tex.height):
        for x in range(tex.width):
            if direction == "radial":
                dx = (x - cx) / max(1, cx)
                dy = (y - cy) / max(1, cy)
                off_x = int(dx * offset)
                off_y = int(dy * offset)
            elif direction == "vertical":
                off_x = 0
                off_y = offset
            else:  # horizontal
                off_x = offset
                off_y = 0

            # Get RGB from offset positions
            r_pixel = tex.get_pixel(
                max(0, min(tex.width - 1, x - off_x)),
                max(0, min(tex.height - 1, y - off_y))
            )
            g_pixel = tex.get_pixel(x, y)
            b_pixel = tex.get_pixel(
                max(0, min(tex.width - 1, x + off_x)),
                max(0, min(tex.height - 1, y + off_y))
            )

            new_color = (r_pixel[0], g_pixel[1], b_pixel[2])
            result.set_pixel(x, y, new_color)

    return result


def apply_vignette(
    tex: TextureData,
    strength: float = 0.5,
    radius: float = 0.8,
    softness: float = 0.3,
) -> TextureData:
    """
    Apply vignette (darkened corners) effect.

    Args:
        tex: Input texture
        strength: Maximum darkening amount (0-1)
        radius: Radius of bright center (0-1)
        softness: Edge softness (0-1)
    """
    result = TextureData(tex.width, tex.height)
    cx, cy = tex.width / 2, tex.height / 2
    max_dist = math.sqrt(cx * cx + cy * cy)

    for y in range(tex.height):
        for x in range(tex.width):
            pixel = tex.get_pixel(x, y)

            dist = math.sqrt((x - cx)**2 + (y - cy)**2) / max_dist
            vignette = (dist - radius) / max(0.01, softness)
            vignette = max(0, min(1, vignette)) * strength
            darken = 1 - vignette

            new_color = (
                int(pixel[0] * darken),
                int(pixel[1] * darken),
                int(pixel[2] * darken),
            )
            result.set_pixel(x, y, new_color)

    return result
