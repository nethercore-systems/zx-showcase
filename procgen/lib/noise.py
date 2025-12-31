"""
Noise generation algorithms for procedural content.

Provides Perlin, Voronoi, and other noise functions.
"""

import math
import random
from typing import Tuple, List, Optional


def perlin_2d(
    x: float,
    y: float,
    seed: int = 42,
    scale: float = 1.0,
) -> float:
    """
    Generate 2D Perlin noise at a point.

    Returns value in range [-1, 1].
    """
    # Scale input
    x = x * scale
    y = y * scale

    # Get permutation table for this seed
    perm = _get_permutation(seed)

    def fade(t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(t, a, b):
        return a + t * (b - a)

    def grad(hash_val, x, y):
        h = hash_val & 3
        u = x if h < 2 else y
        v = y if h < 2 else x
        return (u if h & 1 == 0 else -u) + (v if h & 2 == 0 else -v)

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


def voronoi_2d(
    x: float,
    y: float,
    seed: int = 42,
    num_points: int = 32,
    width: float = 256,
    height: float = 256,
) -> float:
    """
    Generate 2D Voronoi noise at a point.

    Returns normalized distance to nearest cell center [0, 1].
    """
    rng = random.Random(seed)
    points = [(rng.random() * width, rng.random() * height) for _ in range(num_points)]

    min_dist = float('inf')
    for px, py in points:
        dist = math.sqrt((x - px) ** 2 + (y - py) ** 2)
        if dist < min_dist:
            min_dist = dist

    max_possible = math.sqrt(width ** 2 + height ** 2) / math.sqrt(num_points)
    return min(1.0, min_dist / max_possible)


def cellular_2d(
    x: float,
    y: float,
    cell_size: float = 32,
    border_width: float = 2,
) -> float:
    """
    Generate cellular/grid pattern at a point.

    Returns 1.0 on border, 0.0 in cell interior.
    """
    x_mod = x % cell_size
    y_mod = y % cell_size

    on_border = (
        x_mod < border_width or
        x_mod >= cell_size - border_width or
        y_mod < border_width or
        y_mod >= cell_size - border_width
    )

    return 1.0 if on_border else 0.0


def fbm_2d(
    x: float,
    y: float,
    seed: int = 42,
    octaves: int = 4,
    lacunarity: float = 2.0,
    persistence: float = 0.5,
) -> float:
    """
    Fractal Brownian Motion - layered Perlin noise.

    Returns value in range approximately [-1, 1].
    """
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_amplitude = 0.0

    for _ in range(octaves):
        value += amplitude * perlin_2d(x * frequency, y * frequency, seed)
        max_amplitude += amplitude
        amplitude *= persistence
        frequency *= lacunarity

    return value / max_amplitude if max_amplitude > 0 else 0


def worley_2d(
    x: float,
    y: float,
    seed: int = 42,
    cell_size: float = 32,
    distance_func: str = "euclidean",
) -> Tuple[float, float]:
    """
    Generate Worley/cellular noise at a point.

    Returns (F1, F2) - distances to nearest and second nearest points.
    """
    rng = random.Random(seed)

    # Determine which cell we're in
    cell_x = int(x / cell_size)
    cell_y = int(y / cell_size)

    min_dist1 = float('inf')
    min_dist2 = float('inf')

    # Check 3x3 neighborhood of cells
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            cx = cell_x + dx
            cy = cell_y + dy

            # Deterministic point in this cell
            rng.seed(seed + cx * 374761393 + cy * 668265263)
            px = (cx + rng.random()) * cell_size
            py = (cy + rng.random()) * cell_size

            # Calculate distance
            if distance_func == "manhattan":
                dist = abs(x - px) + abs(y - py)
            elif distance_func == "chebyshev":
                dist = max(abs(x - px), abs(y - py))
            else:  # euclidean
                dist = math.sqrt((x - px) ** 2 + (y - py) ** 2)

            if dist < min_dist1:
                min_dist2 = min_dist1
                min_dist1 = dist
            elif dist < min_dist2:
                min_dist2 = dist

    return (min_dist1 / cell_size, min_dist2 / cell_size)


def turbulence_2d(
    x: float,
    y: float,
    seed: int = 42,
    octaves: int = 4,
) -> float:
    """
    Turbulence - absolute value FBM for more chaotic patterns.

    Returns value in range [0, 1].
    """
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_amplitude = 0.0

    for _ in range(octaves):
        value += amplitude * abs(perlin_2d(x * frequency, y * frequency, seed))
        max_amplitude += amplitude
        amplitude *= 0.5
        frequency *= 2.0

    return value / max_amplitude if max_amplitude > 0 else 0


def ridged_2d(
    x: float,
    y: float,
    seed: int = 42,
    octaves: int = 4,
    offset: float = 1.0,
) -> float:
    """
    Ridged multifractal noise - creates sharp ridges.

    Returns value in range [0, 1].
    """
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    weight = 1.0
    max_amplitude = 0.0

    for _ in range(octaves):
        signal = perlin_2d(x * frequency, y * frequency, seed)
        signal = offset - abs(signal)
        signal *= signal
        signal *= weight
        weight = max(0, min(1, signal * 2))

        value += amplitude * signal
        max_amplitude += amplitude
        amplitude *= 0.5
        frequency *= 2.0

    return value / max_amplitude if max_amplitude > 0 else 0


# ============================================================================
# Internal Helpers
# ============================================================================

_PERM_CACHE = {}


def _get_permutation(seed: int) -> List[int]:
    """Get cached permutation table for seed."""
    if seed not in _PERM_CACHE:
        rng = random.Random(seed)
        perm = list(range(256))
        rng.shuffle(perm)
        _PERM_CACHE[seed] = perm + perm  # Double for wrapping
    return _PERM_CACHE[seed]
