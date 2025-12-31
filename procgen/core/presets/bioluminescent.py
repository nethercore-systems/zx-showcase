"""
Lumina Depths - Bioluminescent style preset.

Aesthetic: Underwater bioluminescence, alien beauty, ethereal glow.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class BioluminescentPreset:
    """Style preset for Lumina Depths underwater aesthetic."""

    # === Identity ===
    name: str = "bioluminescent"
    game: str = "Lumina Depths"

    # === Color Palette ===
    primary_colors: List[str] = None
    accent_colors: List[str] = None
    background_colors: List[str] = None

    # Color properties
    saturation_range: Tuple[float, float] = (0.4, 0.8)
    color_temperature: float = -0.4  # Cool, underwater feel
    contrast: float = 0.5  # Lower contrast for murky depths

    # === Geometry ===
    poly_budgets: dict = None
    curvature_bias: float = 0.9  # Very organic/smooth
    symmetry_mode: str = "radial"  # Sea creatures often radial
    edge_sharpness: float = 0.2  # Soft edges

    # === Materials ===
    emissive_enabled: bool = True
    emissive_strength: Tuple[float, float] = (0.3, 1.5)
    roughness_range: Tuple[float, float] = (0.4, 0.8)  # Organic surfaces
    metallic_range: Tuple[float, float] = (0.0, 0.2)  # Non-metallic

    # Underwater-specific
    subsurface_scattering: float = 0.6
    transparency: float = 0.3

    # === Effects ===
    bloom_intensity: float = 1.5
    fog_density: float = 0.4
    caustics: bool = True
    particle_density: float = 0.3  # Floating particles

    # === Audio ===
    tempo_range: Tuple[int, int] = (60, 90)
    preferred_keys: List[str] = None
    preferred_scales: List[str] = None
    preferred_progressions: List[str] = None
    reverb_amount: float = 0.6  # Underwater reverb
    brightness: float = 0.3  # Muted, underwater

    def __post_init__(self):
        if self.primary_colors is None:
            self.primary_colors = [
                "#00CED1",  # Dark turquoise
                "#7B68EE",  # Medium slate blue
                "#00FA9A",  # Medium spring green
                "#4169E1",  # Royal blue
            ]
        if self.accent_colors is None:
            self.accent_colors = [
                "#FF69B4",  # Hot pink (bioluminescence)
                "#FFD700",  # Gold accents
                "#FF6347",  # Tomato (warning creatures)
            ]
        if self.background_colors is None:
            self.background_colors = [
                "#001133",  # Deep ocean blue
                "#000022",  # Almost black
                "#0A1929",  # Dark navy
            ]
        if self.poly_budgets is None:
            self.poly_budgets = {
                "creature_small": 400,
                "creature_large": 1200,
                "coral": 300,
                "plant": 200,
                "environment": 600,
            }
        if self.preferred_keys is None:
            self.preferred_keys = ["Em", "Am", "Dm", "Bm"]
        if self.preferred_scales is None:
            self.preferred_scales = ["aeolian", "dorian", "pentatonic_minor"]
        if self.preferred_progressions is None:
            self.preferred_progressions = ["ambient", "mysterious", "peaceful"]

    def get_texture_params(self) -> dict:
        """Get parameters for texture generation."""
        return {
            "palette": self.primary_colors + self.accent_colors,
            "saturation": self.saturation_range,
            "contrast": self.contrast,
            "emissive": self.emissive_enabled,
            "bloom": self.bloom_intensity,
            "subsurface": self.subsurface_scattering,
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
            impact_weight=0.3,  # Light, underwater impacts
            reverb_amount=self.reverb_amount,
            pitch_base=0.8,  # Lower pitch underwater
        )
