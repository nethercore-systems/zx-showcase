"""
Prism Survivors - Prismatic crystal style preset.

Aesthetic: Crystalline chaos, prismatic violence, shattered beauty.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class PrismaticPreset:
    """Style preset for Prism Survivors crystal aesthetic."""

    # === Identity ===
    name: str = "prismatic"
    game: str = "Prism Survivors"

    # === Color Palette ===
    primary_colors: List[str] = None
    accent_colors: List[str] = None
    background_colors: List[str] = None

    # Color properties
    saturation_range: Tuple[float, float] = (0.8, 1.0)
    color_temperature: float = 0.0  # Neutral, full spectrum
    contrast: float = 0.9  # High contrast for visibility

    # === Geometry ===
    poly_budgets: dict = None
    curvature_bias: float = 0.2  # Angular, faceted
    symmetry_mode: str = "radial"  # Crystal symmetry
    edge_sharpness: float = 0.95  # Sharp crystal edges

    # === Materials ===
    emissive_enabled: bool = True
    emissive_strength: Tuple[float, float] = (0.8, 3.0)
    roughness_range: Tuple[float, float] = (0.0, 0.2)  # Very smooth crystals
    metallic_range: Tuple[float, float] = (0.0, 0.1)  # Non-metallic

    # Crystal-specific
    refraction_index: float = 1.5
    dispersion: float = 0.4  # Rainbow effect

    # === Effects ===
    bloom_intensity: float = 2.5
    chromatic_dispersion: bool = True
    particle_density: float = 0.5  # Crystal shards flying

    # === Audio ===
    tempo_range: Tuple[int, int] = (140, 170)  # Fast-paced action
    preferred_keys: List[str] = None
    preferred_scales: List[str] = None
    preferred_progressions: List[str] = None
    reverb_amount: float = 0.15
    brightness: float = 0.8  # Bright, crystalline

    def __post_init__(self):
        if self.primary_colors is None:
            self.primary_colors = [
                "#FF0000",  # Red
                "#FF7F00",  # Orange
                "#FFFF00",  # Yellow
                "#00FF00",  # Green
                "#0000FF",  # Blue
                "#8B00FF",  # Violet
            ]
        if self.accent_colors is None:
            self.accent_colors = [
                "#FFFFFF",  # Pure white
                "#FFD700",  # Gold
                "#FF1493",  # Deep pink
            ]
        if self.background_colors is None:
            self.background_colors = [
                "#0A0A0A",  # Near black
                "#1A0A2E",  # Deep purple
                "#0A1A2E",  # Deep blue
            ]
        if self.poly_budgets is None:
            self.poly_budgets = {
                "hero": 800,
                "enemy_small": 200,
                "enemy_medium": 400,
                "enemy_large": 800,
                "projectile": 50,
                "pickup": 100,
            }
        if self.preferred_keys is None:
            self.preferred_keys = ["Em", "Am", "Cm", "Dm"]
        if self.preferred_scales is None:
            self.preferred_scales = ["minor", "harmonic_minor", "phrygian"]
        if self.preferred_progressions is None:
            self.preferred_progressions = ["epic", "tense", "uplifting"]

    def get_texture_params(self) -> dict:
        """Get parameters for texture generation."""
        return {
            "palette": self.primary_colors + self.accent_colors,
            "saturation": self.saturation_range,
            "contrast": self.contrast,
            "emissive": self.emissive_enabled,
            "bloom": self.bloom_intensity,
            "dispersion": self.dispersion,
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
            impact_weight=0.5,
            reverb_amount=self.reverb_amount,
            pitch_base=1.0,
        )
