"""
ZX Showcase - Procedural Generation Library

Shared utilities for texture, mesh, and audio generation.
Aligned with zx-procgen generator-patterns skill.
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

# Pure Python mesh primitives (no Blender dependency)
from .mesh_primitives import (
    generate_ellipsoid, generate_cylinder, generate_hemisphere,
    generate_fin, merge_meshes as merge_mesh_tuples, write_obj,
)

# Pure Python audio DSP (no external dependency)
from . import audio_dsp

# Blender utilities (only available when running in Blender)
# from .bpy_utils import (
#     clear_scene, apply_modifiers, apply_transforms, auto_uv_project,
#     export_glb, export_obj as export_obj_blender, post_process,
# )

# Animation utilities (only available when running in Blender)
# from .animation_utils import (
#     keyframe_location, keyframe_rotation, keyframe_scale,
#     set_interpolation, create_bounce, create_spin, create_bob,
# )

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
    # Pure Python mesh primitives
    "generate_ellipsoid", "generate_cylinder", "generate_hemisphere",
    "generate_fin", "merge_mesh_tuples", "write_obj",
    # Audio DSP module
    "audio_dsp",
]
