"""
Neon Drift - Synthwave style preset.

Aesthetic: Neon glows, synthwave colors, speed lines, chrome surfaces.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class NeonSynthwavePreset:
    """Style preset for Neon Drift synthwave aesthetic."""

    # === Identity ===
    name: str = "neon_synthwave"
    game: str = "Neon Drift"

    # === Color Palette ===
    # Primary neon colors
    primary_colors: List[str] = None
    # Secondary/accent colors
    accent_colors: List[str] = None
    # Background/dark colors
    background_colors: List[str] = None

    # Color properties
    saturation_range: Tuple[float, float] = (0.7, 1.0)
    color_temperature: float = -0.2  # Slightly cool (blue-shifted)
    contrast: float = 0.8

    # === Geometry ===
    poly_budgets: dict = None
    curvature_bias: float = 0.6  # More rounded/streamlined
    symmetry_mode: str = "bilateral"
    edge_sharpness: float = 0.7

    # === Materials ===
    emissive_enabled: bool = True
    emissive_strength: Tuple[float, float] = (0.5, 2.5)
    roughness_range: Tuple[float, float] = (0.1, 0.4)  # More reflective
    metallic_range: Tuple[float, float] = (0.5, 0.9)  # Chrome-like

    # === Effects ===
    bloom_intensity: float = 2.0
    trail_decay: float = 0.15
    chromatic_aberration: float = 0.3
    scanlines: bool = True
    scanline_opacity: float = 0.15

    # === Audio ===
    tempo_range: Tuple[int, int] = (128, 145)
    preferred_keys: List[str] = None
    preferred_scales: List[str] = None
    preferred_progressions: List[str] = None
    reverb_amount: float = 0.25
    brightness: float = 0.7

    def __post_init__(self):
        if self.primary_colors is None:
            self.primary_colors = [
                "#FF00FF",  # Magenta
                "#00FFFF",  # Cyan
                "#FF1493",  # Deep pink
                "#00FF88",  # Neon green
            ]
        if self.accent_colors is None:
            self.accent_colors = [
                "#FFD700",  # Gold
                "#FF4500",  # Orange-red
                "#8A2BE2",  # Blue violet
            ]
        if self.background_colors is None:
            self.background_colors = [
                "#0D0221",  # Deep purple-black
                "#1A0533",  # Dark purple
                "#0F0F23",  # Midnight blue
            ]
        if self.poly_budgets is None:
            self.poly_budgets = {
                "vehicle": 1000,
                "prop_small": 150,
                "prop_large": 500,
                "building": 800,
                "effect": 100,
            }
        if self.preferred_keys is None:
            self.preferred_keys = ["Am", "Em", "Dm", "Fm"]
        if self.preferred_scales is None:
            self.preferred_scales = ["minor", "dorian", "phrygian"]
        if self.preferred_progressions is None:
            self.preferred_progressions = ["synthwave", "tense", "dark"]

    def get_texture_params(self) -> dict:
        """Get parameters for texture generation."""
        return {
            "palette": self.primary_colors + self.accent_colors,
            "saturation": self.saturation_range,
            "contrast": self.contrast,
            "emissive": self.emissive_enabled,
            "bloom": self.bloom_intensity,
        }

    def get_mesh_params(self) -> dict:
        """Get parameters for mesh generation."""
        return {
            "poly_budgets": self.poly_budgets,
            "curvature": self.curvature_bias,
            "symmetry": self.symmetry_mode,
            "edge_sharpness": self.edge_sharpness,
        }

    def get_audio_params(self) -> dict:
        """Get parameters for audio generation."""
        return {
            "tempo_range": self.tempo_range,
            "keys": self.preferred_keys,
            "scales": self.preferred_scales,
            "progressions": self.preferred_progressions,
            "reverb": self.reverb_amount,
            "brightness": self.brightness,
        }

    def get_sfx_style(self):
        """Get SFX style parameters."""
        from ...lib.sfx import SFXStyle
        return SFXStyle(
            brightness=self.brightness,
            impact_weight=0.4,
            reverb_amount=self.reverb_amount,
            pitch_base=1.0,
        )
