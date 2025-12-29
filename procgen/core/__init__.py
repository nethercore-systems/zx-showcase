"""
ZX Showcase - Procedural Asset Generation Core

This module provides the universal style parameter system and base
utilities for procedural asset generation across all ZX showcase games.
"""

from .base_params import (
    UniversalStyleParams,
    StyleTokens,
    ColorPalette,
    PolyBudget,
    GeometrySettings,
    TextureSettings,
    MaterialSettings,
    AnimationSettings,
    EffectSettings,
    AudioSettings,
    AudioEnvelope,
    Waveform,
    FilterType,
    SymmetryMode,
)


__all__ = [
    "UniversalStyleParams",
    "StyleTokens",
    "ColorPalette",
    "PolyBudget",
    "GeometrySettings",
    "TextureSettings",
    "MaterialSettings",
    "AnimationSettings",
    "EffectSettings",
    "AudioSettings",
    "AudioEnvelope",
    "Waveform",
    "FilterType",
    "SymmetryMode",
]
