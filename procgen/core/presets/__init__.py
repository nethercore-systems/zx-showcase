"""
Style presets for ZX games.

Provides game-specific style configurations that parameterize
all asset generators.
"""

from .neon_synthwave import NeonSynthwavePreset
from .bioluminescent import BioluminescentPreset
from .prismatic import PrismaticPreset
from .industrial_dark import IndustrialDarkPreset

__all__ = [
    "NeonSynthwavePreset",
    "BioluminescentPreset",
    "PrismaticPreset",
    "IndustrialDarkPreset",
]
