"""
ZX Showcase Procedural Asset Generation System.

This package provides a comprehensive procedural generation pipeline
for ZX console games, organized as:

- lib/: Shared utility library (synthesis, XM writer, mesh utils, etc.)
- core/: Reusable asset generators (textures, meshes, audio, presets)
- configs/: Game-specific style configurations
- games/: Game-specific generator scripts (in games/<game>/scripts/)

Usage:
    # Import from library
    from procgen.lib.synthesis import sine_wave, apply_adsr
    from procgen.lib.xm_writer import XmModule, PatternBuilder

    # Import from core generators
    from procgen.core.meshes import create_box, create_humanoid_mesh
    from procgen.core.textures import generate_grid_pattern

    # Import presets
    from procgen.core.presets import NeonSynthwavePreset
"""

__version__ = "2.0.0"

# Re-export commonly used items
from .core.base_params import UniversalStyleParams

__all__ = [
    "UniversalStyleParams",
]
