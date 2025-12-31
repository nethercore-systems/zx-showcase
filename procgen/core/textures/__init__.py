"""
Core texture generators for ZX games.

Provides reusable texture patterns, gradients, noise textures, and effects
that can be customized with style tokens.
"""

from .patterns import (
    generate_grid_pattern,
    generate_hexagon_pattern,
    generate_checkerboard,
    generate_dots,
    generate_stripes,
    generate_bricks,
)

from .gradients import (
    generate_linear_gradient,
    generate_radial_gradient,
    generate_angular_gradient,
    generate_diamond_gradient,
)

from .noise_textures import (
    generate_perlin_texture,
    generate_voronoi_texture,
    generate_cellular_texture,
    generate_fbm_texture,
    generate_marble_texture,
    generate_wood_texture,
)

from .effects import (
    apply_glow,
    apply_emission,
    apply_rim_light,
    apply_scanlines,
    apply_chromatic_aberration,
    apply_vignette,
)

__all__ = [
    # Patterns
    "generate_grid_pattern",
    "generate_hexagon_pattern",
    "generate_checkerboard",
    "generate_dots",
    "generate_stripes",
    "generate_bricks",
    # Gradients
    "generate_linear_gradient",
    "generate_radial_gradient",
    "generate_angular_gradient",
    "generate_diamond_gradient",
    # Noise
    "generate_perlin_texture",
    "generate_voronoi_texture",
    "generate_cellular_texture",
    "generate_fbm_texture",
    "generate_marble_texture",
    "generate_wood_texture",
    # Effects
    "apply_glow",
    "apply_emission",
    "apply_rim_light",
    "apply_scanlines",
    "apply_chromatic_aberration",
    "apply_vignette",
]
