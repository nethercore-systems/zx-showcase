#!/usr/bin/env python3
"""
Texture Parser - Interprets .texture.spec.py files and generates textures.

Deterministic texture generation from declarative specs. Follows the same pattern
as sound.py for audio and animation.py for animations.

Usage:
    python texture_parser.py input.texture.spec.py output.png

Arguments:
    input.texture.spec.py - Path to texture spec file (contains TEXTURE dict)
    output.png            - Output path for generated texture

Example:
    python texture_parser.py .studio/textures/wood.texture.spec.py assets/textures/wood.png
"""

import sys
import os
import math
import struct
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

# Optional: Try to import noise library for better quality
try:
    import pyfastnoiselite as fnl
    HAS_FAST_NOISE = True
except ImportError:
    HAS_FAST_NOISE = False


# =============================================================================
# SPEC LOADING
# =============================================================================

def load_spec(spec_path: str) -> Dict[str, Any]:
    """Load spec from .texture.spec.py file via exec()."""
    with open(spec_path, 'r') as f:
        code = f.read()

    namespace = {}
    exec(code, namespace)

    if 'TEXTURE' not in namespace:
        raise ValueError(f"No TEXTURE dict found in {spec_path}")

    return namespace['TEXTURE']


# =============================================================================
# NOISE GENERATORS
# =============================================================================

def perlin_noise(width: int, height: int, scale: float = 0.1,
                 octaves: int = 4, seed: int = 42) -> np.ndarray:
    """Generate Perlin-like noise using value noise fallback."""
    if HAS_FAST_NOISE:
        noise = fnl.FastNoiseLite(seed)
        noise.noise_type = fnl.NoiseType.NoiseType_Perlin
        noise.fractal_type = fnl.FractalType.FractalType_FBm
        noise.fractal_octaves = octaves
        noise.frequency = scale

        result = np.zeros((height, width), dtype=np.float32)
        for y in range(height):
            for x in range(width):
                result[y, x] = noise.get_noise(x, y)
        # Normalize to 0-1
        result = (result + 1) / 2
        return result

    # Fallback: Value noise with multiple octaves
    np.random.seed(seed)
    result = np.zeros((height, width), dtype=np.float32)

    for octave in range(octaves):
        freq = scale * (2 ** octave)
        amp = 1.0 / (2 ** octave)

        # Generate random values at grid points
        grid_w = max(2, int(width * freq) + 2)
        grid_h = max(2, int(height * freq) + 2)
        grid = np.random.rand(grid_h, grid_w)

        # Interpolate
        for y in range(height):
            for x in range(width):
                fx = x * freq
                fy = y * freq
                gx = int(fx) % (grid_w - 1)
                gy = int(fy) % (grid_h - 1)
                tx = fx - int(fx)
                ty = fy - int(fy)

                # Bilinear interpolation
                v00 = grid[gy, gx]
                v10 = grid[gy, gx + 1]
                v01 = grid[gy + 1, gx]
                v11 = grid[gy + 1, gx + 1]

                v0 = v00 * (1 - tx) + v10 * tx
                v1 = v01 * (1 - tx) + v11 * tx
                result[y, x] += (v0 * (1 - ty) + v1 * ty) * amp

    # Normalize to 0-1
    result = (result - result.min()) / (result.max() - result.min() + 1e-10)
    return result


def simplex_noise(width: int, height: int, scale: float = 0.1,
                  octaves: int = 4, seed: int = 42) -> np.ndarray:
    """Generate Simplex-like noise."""
    if HAS_FAST_NOISE:
        noise = fnl.FastNoiseLite(seed)
        noise.noise_type = fnl.NoiseType.NoiseType_OpenSimplex2
        noise.fractal_type = fnl.FractalType.FractalType_FBm
        noise.fractal_octaves = octaves
        noise.frequency = scale

        result = np.zeros((height, width), dtype=np.float32)
        for y in range(height):
            for x in range(width):
                result[y, x] = noise.get_noise(x, y)
        result = (result + 1) / 2
        return result

    # Fallback to perlin-like noise
    return perlin_noise(width, height, scale, octaves, seed)


def voronoi_noise(width: int, height: int, scale: float = 0.05,
                  jitter: float = 1.0, seed: int = 42) -> np.ndarray:
    """Generate Voronoi/cellular noise."""
    if HAS_FAST_NOISE:
        noise = fnl.FastNoiseLite(seed)
        noise.noise_type = fnl.NoiseType.NoiseType_Cellular
        noise.cellular_distance_function = fnl.CellularDistanceFunction.CellularDistanceFunction_Euclidean
        noise.cellular_return_type = fnl.CellularReturnType.CellularReturnType_Distance
        noise.frequency = scale
        noise.cellular_jitter = jitter

        result = np.zeros((height, width), dtype=np.float32)
        for y in range(height):
            for x in range(width):
                result[y, x] = noise.get_noise(x, y)
        result = (result + 1) / 2
        return result

    # Fallback: Simple Voronoi
    np.random.seed(seed)
    cell_size = max(8, int(1 / scale))
    num_cells_x = (width // cell_size) + 2
    num_cells_y = (height // cell_size) + 2

    # Generate cell centers
    centers = []
    for cy in range(num_cells_y):
        for cx in range(num_cells_x):
            px = (cx + 0.5 + (np.random.rand() - 0.5) * jitter) * cell_size
            py = (cy + 0.5 + (np.random.rand() - 0.5) * jitter) * cell_size
            centers.append((px, py))

    result = np.zeros((height, width), dtype=np.float32)
    for y in range(height):
        for x in range(width):
            min_dist = float('inf')
            for px, py in centers:
                dist = math.sqrt((x - px) ** 2 + (y - py) ** 2)
                min_dist = min(min_dist, dist)
            result[y, x] = min_dist

    # Normalize
    result = (result - result.min()) / (result.max() - result.min() + 1e-10)
    return result


# =============================================================================
# PATTERN GENERATORS
# =============================================================================

def solid_fill(width: int, height: int, color: float = 1.0) -> np.ndarray:
    """Generate solid color fill."""
    return np.full((height, width), color, dtype=np.float32)


def gradient_linear(width: int, height: int, direction: str = 'vertical',
                    start: float = 0.0, end: float = 1.0) -> np.ndarray:
    """Generate linear gradient."""
    result = np.zeros((height, width), dtype=np.float32)

    if direction == 'vertical':
        for y in range(height):
            result[y, :] = start + (end - start) * (y / (height - 1))
    elif direction == 'horizontal':
        for x in range(width):
            result[:, x] = start + (end - start) * (x / (width - 1))
    elif direction == 'diagonal':
        for y in range(height):
            for x in range(width):
                t = ((x + y) / (width + height - 2))
                result[y, x] = start + (end - start) * t

    return result


def gradient_radial(width: int, height: int, center: Tuple[float, float] = (0.5, 0.5),
                    inner: float = 1.0, outer: float = 0.0) -> np.ndarray:
    """Generate radial gradient."""
    result = np.zeros((height, width), dtype=np.float32)
    cx, cy = center[0] * width, center[1] * height
    max_dist = math.sqrt((width / 2) ** 2 + (height / 2) ** 2)

    for y in range(height):
        for x in range(width):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            t = min(1.0, dist / max_dist)
            result[y, x] = inner + (outer - inner) * t

    return result


def checkerboard(width: int, height: int, tile_size: int = 32,
                 color1: float = 0.0, color2: float = 1.0) -> np.ndarray:
    """Generate checkerboard pattern."""
    result = np.zeros((height, width), dtype=np.float32)

    for y in range(height):
        for x in range(width):
            tx = x // tile_size
            ty = y // tile_size
            if (tx + ty) % 2 == 0:
                result[y, x] = color1
            else:
                result[y, x] = color2

    return result


def stripes(width: int, height: int, direction: str = 'vertical',
            stripe_width: int = 16, color1: float = 0.0, color2: float = 1.0) -> np.ndarray:
    """Generate stripe pattern."""
    result = np.zeros((height, width), dtype=np.float32)

    for y in range(height):
        for x in range(width):
            if direction == 'vertical':
                stripe_idx = x // stripe_width
            else:
                stripe_idx = y // stripe_width

            if stripe_idx % 2 == 0:
                result[y, x] = color1
            else:
                result[y, x] = color2

    return result


def wood_grain(width: int, height: int, ring_count: int = 8,
               distortion: float = 0.3, seed: int = 42) -> np.ndarray:
    """Generate wood grain pattern with concentric rings."""
    np.random.seed(seed)
    result = np.zeros((height, width), dtype=np.float32)

    # Generate distortion noise
    distortion_noise = perlin_noise(width, height, 0.02, 3, seed)

    cx, cy = width / 2, height / 2
    ring_spacing = min(width, height) / (2 * ring_count)

    for y in range(height):
        for x in range(width):
            # Distance from center with distortion
            dx = x - cx + (distortion_noise[y, x] - 0.5) * distortion * ring_spacing
            dy = y - cy + (distortion_noise[y, x] - 0.5) * distortion * ring_spacing
            dist = math.sqrt(dx * dx + dy * dy)

            # Create ring pattern
            ring_val = (dist / ring_spacing) % 1.0
            # Softer transition
            result[y, x] = 0.5 + 0.5 * math.sin(ring_val * 2 * math.pi)

    return result


def brick_pattern(width: int, height: int, brick_width: int = 64, brick_height: int = 32,
                  mortar_width: int = 4, mortar_color: float = 0.3,
                  brick_color: float = 0.7, variation: float = 0.1,
                  seed: int = 42) -> np.ndarray:
    """Generate brick pattern."""
    np.random.seed(seed)
    result = np.zeros((height, width), dtype=np.float32)

    for y in range(height):
        row = y // (brick_height + mortar_width)
        y_in_row = y % (brick_height + mortar_width)

        for x in range(width):
            # Offset every other row
            x_offset = (brick_width // 2) if row % 2 else 0
            col = (x + x_offset) // (brick_width + mortar_width)
            x_in_col = (x + x_offset) % (brick_width + mortar_width)

            # Check if in mortar
            if y_in_row >= brick_height or x_in_col >= brick_width:
                result[y, x] = mortar_color
            else:
                # Brick with per-brick variation
                brick_seed = row * 1000 + col
                np.random.seed(seed + brick_seed)
                var = (np.random.rand() - 0.5) * variation
                result[y, x] = brick_color + var

    return result


# =============================================================================
# BLEND MODES
# =============================================================================

def blend_normal(base: np.ndarray, layer: np.ndarray, opacity: float = 1.0) -> np.ndarray:
    """Normal blend mode."""
    return base * (1 - opacity) + layer * opacity


def blend_multiply(base: np.ndarray, layer: np.ndarray, opacity: float = 1.0) -> np.ndarray:
    """Multiply blend mode."""
    blended = base * layer
    return base * (1 - opacity) + blended * opacity


def blend_add(base: np.ndarray, layer: np.ndarray, opacity: float = 1.0) -> np.ndarray:
    """Add blend mode."""
    blended = np.clip(base + layer, 0, 1)
    return base * (1 - opacity) + blended * opacity


def blend_screen(base: np.ndarray, layer: np.ndarray, opacity: float = 1.0) -> np.ndarray:
    """Screen blend mode."""
    blended = 1 - (1 - base) * (1 - layer)
    return base * (1 - opacity) + blended * opacity


def blend_overlay(base: np.ndarray, layer: np.ndarray, opacity: float = 1.0) -> np.ndarray:
    """Overlay blend mode."""
    blended = np.where(
        base < 0.5,
        2 * base * layer,
        1 - 2 * (1 - base) * (1 - layer)
    )
    return base * (1 - opacity) + blended * opacity


def blend_soft_light(base: np.ndarray, layer: np.ndarray, opacity: float = 1.0) -> np.ndarray:
    """Soft light blend mode."""
    blended = np.where(
        layer < 0.5,
        base - (1 - 2 * layer) * base * (1 - base),
        base + (2 * layer - 1) * (np.sqrt(base) - base)
    )
    return base * (1 - opacity) + blended * opacity


BLEND_MODES = {
    'normal': blend_normal,
    'multiply': blend_multiply,
    'add': blend_add,
    'screen': blend_screen,
    'overlay': blend_overlay,
    'soft_light': blend_soft_light,
}


# =============================================================================
# LAYER GENERATION
# =============================================================================

def generate_layer(layer: Dict[str, Any], width: int, height: int) -> np.ndarray:
    """Generate a single layer from spec."""
    layer_type = layer.get('type', 'solid')

    if layer_type == 'solid':
        color = layer.get('color', 1.0)
        if isinstance(color, str):
            color = hex_to_gray(color)
        return solid_fill(width, height, color)

    elif layer_type == 'noise':
        noise_type = layer.get('noise_type', 'perlin')
        scale = layer.get('scale', 0.1)
        octaves = layer.get('octaves', 4)
        seed = layer.get('seed', 42)

        if noise_type == 'perlin':
            return perlin_noise(width, height, scale, octaves, seed)
        elif noise_type == 'simplex':
            return simplex_noise(width, height, scale, octaves, seed)
        elif noise_type == 'voronoi':
            jitter = layer.get('jitter', 1.0)
            return voronoi_noise(width, height, scale, jitter, seed)
        else:
            return perlin_noise(width, height, scale, octaves, seed)

    elif layer_type == 'gradient':
        direction = layer.get('direction', 'vertical')
        if direction == 'radial':
            center = layer.get('center', (0.5, 0.5))
            inner = layer.get('inner', 1.0)
            outer = layer.get('outer', 0.0)
            return gradient_radial(width, height, center, inner, outer)
        else:
            start = layer.get('start', 0.0)
            end = layer.get('end', 1.0)
            return gradient_linear(width, height, direction, start, end)

    elif layer_type == 'checkerboard':
        tile_size = layer.get('tile_size', 32)
        color1 = layer.get('color1', 0.0)
        color2 = layer.get('color2', 1.0)
        return checkerboard(width, height, tile_size, color1, color2)

    elif layer_type == 'stripes':
        direction = layer.get('direction', 'vertical')
        stripe_width = layer.get('stripe_width', 16)
        color1 = layer.get('color1', 0.0)
        color2 = layer.get('color2', 1.0)
        return stripes(width, height, direction, stripe_width, color1, color2)

    elif layer_type == 'wood_grain':
        ring_count = layer.get('ring_count', 8)
        distortion = layer.get('distortion', 0.3)
        seed = layer.get('seed', 42)
        return wood_grain(width, height, ring_count, distortion, seed)

    elif layer_type == 'brick':
        return brick_pattern(
            width, height,
            brick_width=layer.get('brick_width', 64),
            brick_height=layer.get('brick_height', 32),
            mortar_width=layer.get('mortar_width', 4),
            mortar_color=layer.get('mortar_color', 0.3),
            brick_color=layer.get('brick_color', 0.7),
            variation=layer.get('variation', 0.1),
            seed=layer.get('seed', 42)
        )

    else:
        # Default to solid white
        return solid_fill(width, height, 1.0)


# =============================================================================
# COLOR UTILITIES
# =============================================================================

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def hex_to_gray(hex_color: str) -> float:
    """Convert hex color to grayscale 0-1."""
    r, g, b = hex_to_rgb(hex_color)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0


def apply_palette(grayscale: np.ndarray, palette: List[str]) -> np.ndarray:
    """Apply color palette to grayscale image.

    Returns (height, width, 3) RGB array.
    """
    height, width = grayscale.shape
    result = np.zeros((height, width, 3), dtype=np.uint8)

    if not palette:
        # Convert grayscale to RGB
        gray_uint8 = (grayscale * 255).astype(np.uint8)
        result[:, :, 0] = gray_uint8
        result[:, :, 1] = gray_uint8
        result[:, :, 2] = gray_uint8
        return result

    # Convert palette to RGB
    palette_rgb = [hex_to_rgb(c) for c in palette]
    num_colors = len(palette_rgb)

    for y in range(height):
        for x in range(width):
            # Map grayscale value to palette index
            val = grayscale[y, x]
            idx = min(int(val * num_colors), num_colors - 1)
            r, g, b = palette_rgb[idx]
            result[y, x, 0] = r
            result[y, x, 1] = g
            result[y, x, 2] = b

    return result


def apply_color_ramp(grayscale: np.ndarray, colors: List[str]) -> np.ndarray:
    """Apply smooth color ramp to grayscale image."""
    height, width = grayscale.shape
    result = np.zeros((height, width, 3), dtype=np.uint8)

    if not colors or len(colors) < 2:
        gray_uint8 = (grayscale * 255).astype(np.uint8)
        result[:, :, 0] = gray_uint8
        result[:, :, 1] = gray_uint8
        result[:, :, 2] = gray_uint8
        return result

    # Convert colors to RGB
    colors_rgb = [hex_to_rgb(c) for c in colors]
    num_colors = len(colors_rgb)

    for y in range(height):
        for x in range(width):
            val = grayscale[y, x]
            # Find which segment we're in
            segment_size = 1.0 / (num_colors - 1)
            segment = int(val / segment_size)
            segment = min(segment, num_colors - 2)

            # Interpolate within segment
            t = (val - segment * segment_size) / segment_size
            r1, g1, b1 = colors_rgb[segment]
            r2, g2, b2 = colors_rgb[segment + 1]

            result[y, x, 0] = int(r1 + (r2 - r1) * t)
            result[y, x, 1] = int(g1 + (g2 - g1) * t)
            result[y, x, 2] = int(b1 + (b2 - b1) * t)

    return result


# =============================================================================
# TEXTURE GENERATION
# =============================================================================

def generate_texture(spec: Dict[str, Any]) -> np.ndarray:
    """Generate texture from TEXTURE spec.

    Returns RGB numpy array (height, width, 3).
    """
    texture = spec.get('texture', spec)

    # Get output size
    output = texture.get('output', {})
    size = output.get('size', texture.get('size', [256, 256]))
    width, height = size[0], size[1]

    # Get layers
    layers = texture.get('layers', [])
    if not layers:
        # Default single noise layer
        layers = [{'type': 'noise', 'noise_type': 'perlin'}]

    # Generate and composite layers
    result = np.zeros((height, width), dtype=np.float32)

    for layer in layers:
        layer_data = generate_layer(layer, width, height)

        # Get blend mode and opacity
        blend_mode = layer.get('blend', 'normal')
        opacity = layer.get('opacity', 1.0)

        # Apply blend
        blend_func = BLEND_MODES.get(blend_mode, blend_normal)
        result = blend_func(result, layer_data, opacity)

    # Clamp result
    result = np.clip(result, 0, 1)

    # Apply palette or color ramp if specified
    palette = texture.get('palette', [])
    color_ramp = texture.get('color_ramp', [])

    if color_ramp:
        rgb_result = apply_color_ramp(result, color_ramp)
    elif palette:
        rgb_result = apply_palette(result, palette)
    else:
        # Convert to grayscale RGB
        gray_uint8 = (result * 255).astype(np.uint8)
        rgb_result = np.stack([gray_uint8, gray_uint8, gray_uint8], axis=2)

    return rgb_result


# =============================================================================
# PNG OUTPUT
# =============================================================================

def write_png(path: str, data: np.ndarray):
    """Write RGB data to PNG file (minimal implementation without PIL)."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    height, width = data.shape[:2]
    channels = data.shape[2] if len(data.shape) > 2 else 1

    # Try PIL first
    try:
        from PIL import Image
        if channels == 3:
            img = Image.fromarray(data, mode='RGB')
        elif channels == 4:
            img = Image.fromarray(data, mode='RGBA')
        else:
            img = Image.fromarray(data, mode='L')
        img.save(path)
        print(f"Wrote {path} ({width}x{height}, {channels} channels)")
        return
    except ImportError:
        pass

    # Fallback: Write raw PPM (can be converted to PNG externally)
    ppm_path = path.replace('.png', '.ppm')
    with open(ppm_path, 'wb') as f:
        f.write(f'P6\n{width} {height}\n255\n'.encode())
        if channels == 3:
            f.write(data.tobytes())
        else:
            # Convert grayscale to RGB
            rgb = np.stack([data, data, data], axis=2)
            f.write(rgb.tobytes())

    print(f"Wrote {ppm_path} (PPM format - convert to PNG with: convert {ppm_path} {path})")


# =============================================================================
# MAIN
# =============================================================================

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    spec_path = sys.argv[1]
    output_path = sys.argv[2]

    print(f"Loading texture spec: {spec_path}")
    spec = load_spec(spec_path)

    print(f"Generating texture...")
    texture = generate_texture(spec)

    write_png(output_path, texture)
    print("Done!")


if __name__ == "__main__":
    main()
