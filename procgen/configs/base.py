"""
Base Style Token Classes - Aligned with zx-procgen semantic-asset-language

These classes extend the core base_params with additional style modifiers
and quality heuristics aligned with the plugin workflow patterns.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum
import colorsys
import random


class DetailLevel(Enum):
    """Detail level for procedural generation."""
    LOW = "low"          # Minimal detail, flat surfaces
    MEDIUM = "medium"    # Standard detail
    HIGH = "high"        # Rich detail, many features
    EXTREME = "extreme"  # Maximum detail (use sparingly)


class QualityTier(Enum):
    """Asset quality tier (from asset-quality-tiers skill)."""
    PLACEHOLDER = "placeholder"  # Colored shapes, no detail
    TEMP = "temp"                # Functional but rough
    FINAL = "final"              # Production quality
    HERO = "hero"                # Showcase quality


@dataclass
class StyleModifiers:
    """
    Style modifiers that offset base generation parameters.

    Aligned with semantic-asset-language/references/style-tokens.md
    """
    roughness_offset: float = 0.0       # Added to base roughness (-0.3 to +0.5)
    saturation_scale: float = 1.0       # Multiplied with saturation (0.5 to 1.5)
    detail_level: DetailLevel = DetailLevel.MEDIUM
    edge_hardness: float = 0.5          # 0.0 = soft organic, 1.0 = sharp geometric
    noise_octaves_offset: int = 0       # Added to noise octaves (-2 to +3)
    damage_amount: float = 0.0          # 0.0 = pristine, 1.0 = destroyed
    color_temperature: float = 0.0      # -1.0 = cool, 0.0 = neutral, 1.0 = warm


@dataclass
class ColorPaletteSpec:
    """
    Color palette specification with HSL ranges.

    Aligned with semantic-asset-language/references/color-palettes.md
    """
    hue_ranges: List[Tuple[float, float]]     # Allowed hue ranges (0-360)
    saturation_range: Tuple[float, float]     # Min-max saturation (0-1)
    lightness_range: Tuple[float, float]      # Min-max lightness (0-1)
    accent_hue_offset: float = 180.0          # Offset for accent colors
    primary_weight: float = 0.7               # Weight for primary vs accent (0-1)

    def sample(self, seed: Optional[int] = None) -> Tuple[float, float, float]:
        """Sample a color from this palette as RGB tuple (0-1)."""
        if seed is not None:
            random.seed(seed)
        hue_range = random.choice(self.hue_ranges)
        h = random.uniform(hue_range[0], hue_range[1]) / 360.0
        s = random.uniform(*self.saturation_range)
        l = random.uniform(*self.lightness_range)
        return colorsys.hls_to_rgb(h, l, s)

    def sample_pair(self, seed: Optional[int] = None) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """Sample primary and accent colors."""
        if seed is not None:
            random.seed(seed)
        primary = self.sample()
        # Offset hue for accent
        hue_range = random.choice(self.hue_ranges)
        h = (random.uniform(hue_range[0], hue_range[1]) + self.accent_hue_offset) % 360 / 360.0
        s = random.uniform(*self.saturation_range)
        l = random.uniform(*self.lightness_range)
        accent = colorsys.hls_to_rgb(h, l, s)
        return (primary, accent)


# Common palette presets
PALETTES = {
    "warm_earthy": ColorPaletteSpec(
        hue_ranges=[(15, 45)],  # Orange-brown
        saturation_range=(0.3, 0.6),
        lightness_range=(0.2, 0.5),
    ),
    "cool_metal": ColorPaletteSpec(
        hue_ranges=[(200, 240)],  # Blue-gray
        saturation_range=(0.1, 0.3),
        lightness_range=(0.4, 0.7),
    ),
    "neon": ColorPaletteSpec(
        hue_ranges=[(280, 320), (160, 200)],  # Magenta, Cyan
        saturation_range=(0.8, 1.0),
        lightness_range=(0.5, 0.7),
    ),
    "pastel": ColorPaletteSpec(
        hue_ranges=[(0, 360)],  # Any hue
        saturation_range=(0.3, 0.5),
        lightness_range=(0.7, 0.85),
    ),
    "muted": ColorPaletteSpec(
        hue_ranges=[(0, 360)],
        saturation_range=(0.1, 0.3),
        lightness_range=(0.3, 0.6),
    ),
    "vibrant": ColorPaletteSpec(
        hue_ranges=[(0, 360)],
        saturation_range=(0.7, 1.0),
        lightness_range=(0.4, 0.6),
    ),
    "industrial_dark": ColorPaletteSpec(
        hue_ranges=[(200, 220)],  # Blue-gray industrial
        saturation_range=(0.1, 0.3),
        lightness_range=(0.1, 0.4),
        accent_hue_offset=160,  # Cyan accents
    ),
    "bioluminescent": ColorPaletteSpec(
        hue_ranges=[(160, 200), (260, 300)],  # Cyan, purple
        saturation_range=(0.6, 0.9),
        lightness_range=(0.4, 0.7),
    ),
    "synthwave": ColorPaletteSpec(
        hue_ranges=[(280, 320), (180, 200)],  # Magenta, cyan
        saturation_range=(0.8, 1.0),
        lightness_range=(0.5, 0.8),
    ),
    "prismatic": ColorPaletteSpec(
        hue_ranges=[(0, 60), (180, 240), (300, 360)],  # Red, cyan, magenta
        saturation_range=(0.7, 1.0),
        lightness_range=(0.5, 0.8),
    ),
}


# Style token presets (modifiers)
STYLE_PRESETS = {
    "rustic": StyleModifiers(
        roughness_offset=0.2,
        saturation_scale=0.8,
        detail_level=DetailLevel.MEDIUM,
        edge_hardness=0.3,
        damage_amount=0.4,
        color_temperature=0.3,
    ),
    "geometric": StyleModifiers(
        roughness_offset=-0.1,
        saturation_scale=0.9,
        detail_level=DetailLevel.LOW,
        edge_hardness=1.0,
        damage_amount=0.0,
        color_temperature=0.0,
    ),
    "organic": StyleModifiers(
        roughness_offset=0.1,
        saturation_scale=1.0,
        detail_level=DetailLevel.HIGH,
        edge_hardness=0.1,
        damage_amount=0.1,
        color_temperature=0.2,
    ),
    "gothic": StyleModifiers(
        roughness_offset=0.3,
        saturation_scale=0.6,
        detail_level=DetailLevel.HIGH,
        edge_hardness=0.5,
        damage_amount=0.5,
        color_temperature=-0.3,
    ),
    "cyberpunk": StyleModifiers(
        roughness_offset=-0.1,
        saturation_scale=1.2,
        detail_level=DetailLevel.HIGH,
        edge_hardness=0.8,
        damage_amount=0.2,
        color_temperature=-0.2,
    ),
    "fantasy": StyleModifiers(
        roughness_offset=0.0,
        saturation_scale=1.1,
        detail_level=DetailLevel.MEDIUM,
        edge_hardness=0.4,
        damage_amount=0.0,
        color_temperature=0.1,
    ),
    "industrial": StyleModifiers(
        roughness_offset=0.2,
        saturation_scale=0.7,
        detail_level=DetailLevel.MEDIUM,
        edge_hardness=0.7,
        damage_amount=0.3,
        color_temperature=-0.4,
    ),
}


def apply_style_modifiers(base_roughness: float, base_saturation: float,
                          modifiers: StyleModifiers) -> Tuple[float, float]:
    """Apply style modifiers to base material parameters."""
    import numpy as np
    roughness = np.clip(base_roughness + modifiers.roughness_offset, 0.0, 1.0)
    saturation = np.clip(base_saturation * modifiers.saturation_scale, 0.0, 1.0)
    return float(roughness), float(saturation)
