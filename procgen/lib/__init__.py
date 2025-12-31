"""
ZX Showcase - Procedural Generation Library

Shared utilities for texture, mesh, and audio generation.
"""

from .texture_buffer import TextureData, create_texture, draw_line, draw_rect, draw_circle
from .mesh_utils import MeshData, merge_meshes, translate, scale, rotate, apply_noise
from .noise import perlin_2d, voronoi_2d, cellular_2d, fbm_2d
from .color_utils import hex_to_rgb, rgb_to_hex, hsv_to_rgb, rgb_to_hsv, lerp_color
from .export import export_obj, export_ppm, export_wav
from .synthesis import (
    SAMPLE_RATE,
    sine_wave, square_wave, triangle_wave, sawtooth_wave,
    noise_white, noise_pink,
    apply_adsr, apply_exponential_decay,
    lowpass, highpass, bandpass,
    normalize, mix, to_pcm16, save_wav,
)

__all__ = [
    # Texture
    "TextureData", "create_texture", "draw_line", "draw_rect", "draw_circle",
    # Mesh
    "MeshData", "merge_meshes", "translate", "scale", "rotate", "apply_noise",
    # Noise
    "perlin_2d", "voronoi_2d", "cellular_2d", "fbm_2d",
    # Color
    "hex_to_rgb", "rgb_to_hex", "hsv_to_rgb", "rgb_to_hsv", "lerp_color",
    # Export
    "export_obj", "export_ppm", "export_wav",
    # Synthesis
    "SAMPLE_RATE",
    "sine_wave", "square_wave", "triangle_wave", "sawtooth_wave",
    "noise_white", "noise_pink",
    "apply_adsr", "apply_exponential_decay",
    "lowpass", "highpass", "bandpass",
    "normalize", "mix", "to_pcm16", "save_wav",
]
