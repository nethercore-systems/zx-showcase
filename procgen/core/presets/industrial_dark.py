"""
Override - Industrial Dark style preset.

Aesthetic: Dark sci-fi industrial, high contrast, muted grays/blues,
oppressive facility environments.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class IndustrialDarkPreset:
    """Style preset for Override industrial sci-fi aesthetic."""

    # === Identity ===
    name: str = "industrial_dark"
    game: str = "Override"

    # === Color Palette ===
    primary_colors: List[str] = None
    accent_colors: List[str] = None  # Warning/danger colors
    background_colors: List[str] = None

    # Color properties
    saturation_range: Tuple[float, float] = (0.1, 0.5)  # Muted
    color_temperature: float = -0.3  # Cold, industrial
    contrast: float = 0.85  # High contrast for visibility

    # === Geometry ===
    poly_budgets: dict = None
    curvature_bias: float = 0.3  # Angular, industrial
    symmetry_mode: str = "bilateral"
    edge_sharpness: float = 0.8  # Hard edges

    # === Materials ===
    emissive_enabled: bool = True
    emissive_strength: Tuple[float, float] = (0.3, 1.2)  # Subtle glow
    roughness_range: Tuple[float, float] = (0.4, 0.9)  # Worn surfaces
    metallic_range: Tuple[float, float] = (0.6, 0.95)  # Lots of metal

    # Industrial-specific
    wear_amount: float = 0.4  # Surface wear/damage
    grime_amount: float = 0.3  # Dirt and oil

    # === Effects ===
    bloom_intensity: float = 0.8  # Subtle bloom
    fog_density: float = 0.2  # Atmospheric haze
    grain_intensity: float = 0.1  # Film grain

    # === Audio ===
    tempo_range: Tuple[int, int] = (90, 130)
    preferred_keys: List[str] = None
    preferred_scales: List[str] = None
    preferred_progressions: List[str] = None
    reverb_amount: float = 0.3
    brightness: float = 0.4  # Dark, muted

    def __post_init__(self):
        if self.primary_colors is None:
            self.primary_colors = [
                "#3A3A4A",  # Steel gray
                "#2A2A3A",  # Dark gray-blue
                "#4A4A5A",  # Medium gray
                "#5A5A6A",  # Light gray
            ]
        if self.accent_colors is None:
            self.accent_colors = [
                "#FF3333",  # Warning red
                "#FFAA00",  # Caution orange
                "#00CCFF",  # Tech blue
                "#33FF33",  # Terminal green
            ]
        if self.background_colors is None:
            self.background_colors = [
                "#0A0A0F",  # Near black
                "#15151A",  # Dark charcoal
                "#1A1A22",  # Charcoal blue
            ]
        if self.poly_budgets is None:
            self.poly_budgets = {
                "runner": 600,
                "drone": 400,
                "tile_floor": 100,
                "tile_wall": 150,
                "door": 200,
                "trap": 250,
                "prop": 150,
            }
        if self.preferred_keys is None:
            self.preferred_keys = ["Dm", "Cm", "Am", "Em"]
        if self.preferred_scales is None:
            self.preferred_scales = ["minor", "locrian", "phrygian"]
        if self.preferred_progressions is None:
            self.preferred_progressions = ["tense", "dark", "mysterious"]

    def get_texture_params(self) -> dict:
        """Get parameters for texture generation."""
        return {
            "palette": self.primary_colors + self.accent_colors,
            "saturation": self.saturation_range,
            "contrast": self.contrast,
            "emissive": self.emissive_enabled,
            "bloom": self.bloom_intensity,
            "wear": self.wear_amount,
            "grime": self.grime_amount,
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
            impact_weight=0.7,  # Heavy industrial impacts
            reverb_amount=self.reverb_amount,
            pitch_base=0.9,  # Slightly lower
        )
