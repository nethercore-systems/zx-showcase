#!/usr/bin/env python3
"""
Normal Map Parser - Interprets .normal.spec.py files and generates normal maps.

Deterministic normal map generation from declarative specs. Follows the same pattern
as sound.py for audio and animation.py for animations.

Usage:
    # From pattern spec
    python normal_parser.py pattern input.normal.spec.py output.png

    # From height image
    python normal_parser.py height height_map.png output.png [--strength 1.0]

Arguments:
    mode              - Either 'pattern' or 'height'
    input             - Spec file (.normal.spec.py) or height map image
    output            - Output path for generated normal map

Example:
    python normal_parser.py pattern .studio/normals/bricks.normal.spec.py assets/textures/bricks_normal.png
    python normal_parser.py height assets/textures/bricks_height.png assets/textures/bricks_normal.png
"""

import sys
import os
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

# Try to import scipy for Sobel filter
try:
    from scipy.ndimage import sobel
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


# =============================================================================
# SPEC LOADING
# =============================================================================

def load_spec(spec_path: str) -> Dict[str, Any]:
    """Load spec from .normal.spec.py file via exec()."""
    with open(spec_path, 'r') as f:
        code = f.read()

    namespace = {}
    exec(code, namespace)

    if 'NORMAL' not in namespace:
        raise ValueError(f"No NORMAL dict found in {spec_path}")

    return namespace['NORMAL']


# =============================================================================
# HEIGHT MAP PATTERNS
# =============================================================================

def pattern_bricks(width: int, height: int,
                   brick_width: int = 64, brick_height: int = 32,
                   mortar_width: int = 4, mortar_depth: float = 0.3,
                   brick_variation: float = 0.1, seed: int = 42) -> np.ndarray:
    """Generate brick height map."""
    np.random.seed(seed)
    result = np.ones((height, width), dtype=np.float32)

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
                result[y, x] = 1.0 - mortar_depth
            else:
                # Brick with per-brick height variation
                brick_seed = row * 1000 + col
                np.random.seed(seed + brick_seed)
                var = (np.random.rand() - 0.5) * brick_variation
                result[y, x] = 1.0 + var

    return result


def pattern_tiles(width: int, height: int,
                  tile_size: int = 64, gap_width: int = 4,
                  gap_depth: float = 0.3, seed: int = 42) -> np.ndarray:
    """Generate square tile height map."""
    np.random.seed(seed)
    result = np.ones((height, width), dtype=np.float32)

    for y in range(height):
        row = y // (tile_size + gap_width)
        y_in_row = y % (tile_size + gap_width)

        for x in range(width):
            col = x // (tile_size + gap_width)
            x_in_col = x % (tile_size + gap_width)

            # Check if in gap
            if y_in_row >= tile_size or x_in_col >= tile_size:
                result[y, x] = 1.0 - gap_depth
            else:
                # Subtle tile variation
                tile_seed = row * 1000 + col
                np.random.seed(seed + tile_seed)
                var = (np.random.rand() - 0.5) * 0.05
                result[y, x] = 1.0 + var

    return result


def pattern_hexagons(width: int, height: int,
                     hex_size: int = 32, gap_width: int = 3,
                     gap_depth: float = 0.25, seed: int = 42) -> np.ndarray:
    """Generate hexagonal tile height map."""
    np.random.seed(seed)
    result = np.ones((height, width), dtype=np.float32)

    # Hexagon geometry
    hex_height = int(hex_size * math.sqrt(3))
    row_height = int(hex_height * 0.75)

    for y in range(height):
        for x in range(width):
            # Determine which hex we're in
            row = y // row_height
            col = (x + (hex_size // 2 if row % 2 else 0)) // hex_size

            # Calculate center of this hex
            cx = col * hex_size + (hex_size // 2 if row % 2 == 0 else 0)
            cy = row * row_height + row_height // 2

            # Distance to center (approximate hex with circle)
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)

            # Hex has "radius" of about hex_size/2
            hex_radius = hex_size / 2 - gap_width

            if dist > hex_radius:
                result[y, x] = 1.0 - gap_depth
            else:
                hex_seed = row * 1000 + col
                np.random.seed(seed + hex_seed)
                var = (np.random.rand() - 0.5) * 0.05
                result[y, x] = 1.0 + var

    return result


def pattern_noise(width: int, height: int,
                  scale: float = 0.1, octaves: int = 4,
                  height_range: Tuple[float, float] = (0.0, 1.0),
                  seed: int = 42) -> np.ndarray:
    """Generate noise-based height map."""
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

    # Normalize to height range
    result = (result - result.min()) / (result.max() - result.min() + 1e-10)
    result = height_range[0] + result * (height_range[1] - height_range[0])
    return result


def pattern_scratches(width: int, height: int,
                      density: int = 50, length_range: Tuple[int, int] = (10, 40),
                      depth: float = 0.15, seed: int = 42) -> np.ndarray:
    """Generate random scratches height map."""
    np.random.seed(seed)
    result = np.ones((height, width), dtype=np.float32)

    for _ in range(density):
        # Random scratch start
        x0 = np.random.randint(0, width)
        y0 = np.random.randint(0, height)

        # Random angle and length
        angle = np.random.rand() * 2 * math.pi
        length = np.random.randint(length_range[0], length_range[1])

        # Draw scratch
        for i in range(length):
            x = int(x0 + i * math.cos(angle)) % width
            y = int(y0 + i * math.sin(angle)) % height
            result[y, x] = 1.0 - depth

            # Add some width
            if x + 1 < width:
                result[y, (x + 1) % width] = 1.0 - depth * 0.5
            if x - 1 >= 0:
                result[y, (x - 1) % width] = 1.0 - depth * 0.5

    return result


def pattern_rivets(width: int, height: int,
                   spacing: int = 32, radius: int = 4,
                   height_val: float = 0.2, seed: int = 42) -> np.ndarray:
    """Generate raised rivet/bump pattern."""
    np.random.seed(seed)
    result = np.zeros((height, width), dtype=np.float32)

    for cy in range(spacing // 2, height, spacing):
        for cx in range(spacing // 2, width, spacing):
            # Add slight randomness to position
            cx_off = cx + int((np.random.rand() - 0.5) * spacing * 0.2)
            cy_off = cy + int((np.random.rand() - 0.5) * spacing * 0.2)

            # Draw circular bump
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist <= radius:
                        x = (cx_off + dx) % width
                        y = (cy_off + dy) % height
                        # Smooth falloff
                        falloff = 1.0 - (dist / radius)
                        result[y, x] = max(result[y, x], height_val * falloff)

    return result


def pattern_weave(width: int, height: int,
                  thread_width: int = 8, gap: int = 2,
                  depth: float = 0.15) -> np.ndarray:
    """Generate woven fabric pattern."""
    result = np.ones((height, width), dtype=np.float32) * 0.5

    period = (thread_width + gap) * 2

    for y in range(height):
        for x in range(width):
            px = x % period
            py = y % period

            # Horizontal thread
            in_h_thread = (py < thread_width) or (py >= thread_width + gap and py < period - gap)
            # Vertical thread
            in_v_thread = (px < thread_width) or (px >= thread_width + gap and px < period - gap)

            # Determine over/under
            h_section = py // (thread_width + gap)
            v_section = px // (thread_width + gap)

            if in_h_thread and in_v_thread:
                if (h_section + v_section) % 2 == 0:
                    result[y, x] = 0.5 + depth  # Horizontal on top
                else:
                    result[y, x] = 0.5 - depth  # Vertical on top
            elif in_h_thread:
                result[y, x] = 0.5
            elif in_v_thread:
                result[y, x] = 0.5
            else:
                result[y, x] = 0.5 - depth * 0.5  # Gap

    return result


# =============================================================================
# HEIGHT TO NORMAL CONVERSION
# =============================================================================

def sobel_numpy(data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute Sobel gradients using numpy (fallback)."""
    # Sobel kernels
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])

    height, width = data.shape
    gx = np.zeros_like(data)
    gy = np.zeros_like(data)

    # Pad data for edge handling
    padded = np.pad(data, 1, mode='wrap')

    for y in range(height):
        for x in range(width):
            patch = padded[y:y+3, x:x+3]
            gx[y, x] = np.sum(patch * kx)
            gy[y, x] = np.sum(patch * ky)

    return gx, gy


def height_to_normal(height_map: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """Convert height map to normal map using Sobel filter.

    Returns (height, width, 3) RGB array with tangent-space normals.
    """
    height_map = height_map.astype(np.float32)

    # Compute gradients
    if HAS_SCIPY:
        gx = sobel(height_map, axis=1, mode='wrap')
        gy = sobel(height_map, axis=0, mode='wrap')
    else:
        gx, gy = sobel_numpy(height_map)

    # Scale gradients by strength
    gx *= strength
    gy *= strength

    # Compute normal vectors
    # In tangent space: X = right, Y = up, Z = out
    nx = -gx
    ny = -gy
    nz = np.ones_like(gx)

    # Normalize
    length = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx /= length
    ny /= length
    nz /= length

    # Pack to RGB [0, 255]
    # Normal range [-1, 1] -> [0, 255]
    r = ((nx + 1) * 0.5 * 255).astype(np.uint8)
    g = ((ny + 1) * 0.5 * 255).astype(np.uint8)
    b = ((nz + 1) * 0.5 * 255).astype(np.uint8)

    return np.stack([r, g, b], axis=2)


# =============================================================================
# PATTERN GENERATION
# =============================================================================

def generate_height_pattern(pattern: Dict[str, Any], width: int, height: int) -> np.ndarray:
    """Generate height map from pattern specification."""
    pattern_type = pattern.get('type', 'noise')

    if pattern_type == 'bricks':
        return pattern_bricks(
            width, height,
            brick_width=pattern.get('brick_width', pattern.get('brick_size', [64, 32])[0] if isinstance(pattern.get('brick_size'), list) else 64),
            brick_height=pattern.get('brick_height', pattern.get('brick_size', [64, 32])[1] if isinstance(pattern.get('brick_size'), list) else 32),
            mortar_width=pattern.get('mortar_width', 4),
            mortar_depth=pattern.get('mortar_depth', 0.3),
            brick_variation=pattern.get('brick_variation', 0.1),
            seed=pattern.get('seed', 42)
        )

    elif pattern_type == 'tiles':
        return pattern_tiles(
            width, height,
            tile_size=pattern.get('tile_size', 64),
            gap_width=pattern.get('gap_width', 4),
            gap_depth=pattern.get('gap_depth', 0.3),
            seed=pattern.get('seed', 42)
        )

    elif pattern_type == 'hexagons':
        return pattern_hexagons(
            width, height,
            hex_size=pattern.get('hex_size', 32),
            gap_width=pattern.get('gap_width', 3),
            gap_depth=pattern.get('gap_depth', 0.25),
            seed=pattern.get('seed', 42)
        )

    elif pattern_type == 'noise':
        return pattern_noise(
            width, height,
            scale=pattern.get('scale', 0.1),
            octaves=pattern.get('octaves', 4),
            height_range=pattern.get('height_range', (0.0, 1.0)),
            seed=pattern.get('seed', 42)
        )

    elif pattern_type == 'scratches':
        return pattern_scratches(
            width, height,
            density=pattern.get('density', 50),
            length_range=pattern.get('length_range', (10, 40)),
            depth=pattern.get('depth', 0.15),
            seed=pattern.get('seed', 42)
        )

    elif pattern_type == 'rivets':
        return pattern_rivets(
            width, height,
            spacing=pattern.get('spacing', 32),
            radius=pattern.get('radius', 4),
            height_val=pattern.get('height', 0.2),
            seed=pattern.get('seed', 42)
        )

    elif pattern_type == 'weave':
        return pattern_weave(
            width, height,
            thread_width=pattern.get('thread_width', 8),
            gap=pattern.get('gap', 2),
            depth=pattern.get('depth', 0.15)
        )

    else:
        # Default to flat
        return np.ones((height, width), dtype=np.float32) * 0.5


# =============================================================================
# NORMAL MAP GENERATION
# =============================================================================

def generate_normal(spec: Dict[str, Any]) -> np.ndarray:
    """Generate normal map from NORMAL spec.

    Returns RGB numpy array (height, width, 3).
    """
    normal = spec.get('normal', spec)

    # Get output size
    size = normal.get('size', [256, 256])
    width, height = size[0], size[1]

    # Get processing params
    processing = normal.get('processing', {})
    strength = processing.get('strength', 1.0)
    blur = processing.get('blur', 0.0)
    invert = processing.get('invert', False)

    # Generate height map based on method
    method = normal.get('method', 'from_pattern')

    if method == 'from_pattern':
        pattern = normal.get('pattern', {'type': 'noise'})
        height_map = generate_height_pattern(pattern, width, height)
    else:
        # Default to flat
        height_map = np.ones((height, width), dtype=np.float32) * 0.5

    # Apply blur if specified
    if blur > 0:
        try:
            from scipy.ndimage import gaussian_filter
            height_map = gaussian_filter(height_map, sigma=blur)
        except ImportError:
            pass  # Skip blur if scipy not available

    # Invert if specified
    if invert:
        height_map = 1.0 - height_map

    # Convert to normal map
    normal_map = height_to_normal(height_map, strength)

    return normal_map


# =============================================================================
# IMAGE I/O
# =============================================================================

def load_height_image(path: str) -> np.ndarray:
    """Load height map from image file."""
    try:
        from PIL import Image
        img = Image.open(path).convert('L')  # Convert to grayscale
        return np.array(img, dtype=np.float32) / 255.0
    except ImportError:
        raise RuntimeError("PIL/Pillow required for loading images")


def write_png(path: str, data: np.ndarray):
    """Write RGB data to PNG file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    height, width = data.shape[:2]

    try:
        from PIL import Image
        img = Image.fromarray(data, mode='RGB')
        img.save(path)
        print(f"Wrote {path} ({width}x{height})")
        return
    except ImportError:
        pass

    # Fallback: Write raw PPM
    ppm_path = path.replace('.png', '.ppm')
    with open(ppm_path, 'wb') as f:
        f.write(f'P6\n{width} {height}\n255\n'.encode())
        f.write(data.tobytes())
    print(f"Wrote {ppm_path} (PPM format - convert to PNG with: convert {ppm_path} {path})")


# =============================================================================
# MAIN
# =============================================================================

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1]
    input_path = sys.argv[2]
    output_path = sys.argv[3]

    if mode == 'pattern':
        print(f"Loading normal spec: {input_path}")
        spec = load_spec(input_path)

        print(f"Generating normal map...")
        normal = generate_normal(spec)

        write_png(output_path, normal)

    elif mode == 'height':
        print(f"Loading height map: {input_path}")
        height_map = load_height_image(input_path)

        # Parse optional strength argument
        strength = 1.0
        for i, arg in enumerate(sys.argv):
            if arg == '--strength' and i + 1 < len(sys.argv):
                strength = float(sys.argv[i + 1])

        print(f"Converting to normal map (strength={strength})...")
        normal = height_to_normal(height_map, strength)

        write_png(output_path, normal)

    else:
        print(f"Unknown mode: {mode}")
        print("Valid modes: pattern, height")
        sys.exit(1)

    print("Done!")


if __name__ == "__main__":
    main()
