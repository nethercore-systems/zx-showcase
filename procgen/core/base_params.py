"""
Universal Style Parameters for ZX Showcase Procedural Asset Generation

This module defines the core parameter system used across all three showcase games.
Game-specific configs in procgen/configs/ extend these with their own style tokens.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum


class Waveform(Enum):
    """Audio waveform types for procedural synthesis."""
    SINE = "sine"
    SQUARE = "square"
    TRIANGLE = "triangle"
    SAWTOOTH = "sawtooth"
    NOISE = "noise"


class FilterType(Enum):
    """Audio filter types."""
    LOW_PASS = "low_pass"
    HIGH_PASS = "high_pass"
    BAND_PASS = "band_pass"


class SymmetryMode(Enum):
    """Mesh symmetry modes for procedural generation."""
    NONE = "none"
    BILATERAL = "bilateral"
    RADIAL_4 = "radial_4"
    RADIAL_6 = "radial_6"
    RADIAL_8 = "radial_8"


@dataclass
class ColorPalette:
    """Color palette definition with hex colors."""
    primary: List[str]  # Main game colors
    accent: List[str]   # Highlight/effect colors
    neutral: List[str]  # Background/UI colors

    def hex_to_rgb(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to normalized RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

    def all_colors(self) -> List[str]:
        """Return all palette colors."""
        return self.primary + self.accent + self.neutral


@dataclass
class PolyBudget:
    """Polygon budget constraints for different asset types."""
    character_small: int = 500
    character_medium: int = 1000
    character_large: int = 1500
    enemy_small: int = 200
    enemy_medium: int = 500
    enemy_large: int = 1000
    enemy_boss: int = 2000
    vehicle: int = 1000
    prop_small: int = 100
    prop_medium: int = 300
    prop_large: int = 600
    environment_tile: int = 400
    projectile: int = 50


@dataclass
class TextureSettings:
    """Texture generation settings."""
    resolution: int = 256  # 64, 128, 256, 512, 1024
    roughness_range: Tuple[float, float] = (0.3, 0.8)
    metallic_range: Tuple[float, float] = (0.0, 0.3)
    normal_strength: float = 0.5
    use_emission: bool = True
    emission_strength: Tuple[float, float] = (0.5, 2.0)


@dataclass
class MaterialSettings:
    """Material/shader configuration."""
    base_roughness: float = 0.5
    base_metallic: float = 0.0
    emissive_enabled: bool = True
    emissive_strength: float = 1.0
    translucency_enabled: bool = False
    translucency_depth: float = 0.0
    fresnel_intensity: float = 0.5
    subsurface_enabled: bool = False


@dataclass
class GeometrySettings:
    """Geometry generation settings."""
    curvature_bias: float = 0.5  # 0 = angular, 1 = smooth
    symmetry_mode: SymmetryMode = SymmetryMode.BILATERAL
    detail_scale: float = 1.0
    bevel_enabled: bool = False
    bevel_width: float = 0.02


@dataclass
class AnimationSettings:
    """Procedural animation parameters."""
    idle_rotation_speed: float = 0.5  # rad/s
    pulse_frequency: float = 1.5  # Hz
    bob_amplitude: float = 0.1
    bob_frequency: float = 1.0


@dataclass
class EffectSettings:
    """Post-processing and effect settings."""
    bloom_intensity: float = 1.5
    bloom_threshold: float = 0.8
    chromatic_aberration: float = 0.0
    motion_blur: bool = False
    trail_enabled: bool = True
    trail_decay: float = 0.2  # seconds
    particle_density: str = "medium"  # low, medium, high


@dataclass
class AudioEnvelope:
    """ADSR envelope for audio synthesis."""
    attack_ms: int = 10
    decay_ms: int = 100
    sustain_level: float = 0.7
    release_ms: int = 200


@dataclass
class AudioSettings:
    """Audio synthesis parameters."""
    primary_waveform: Waveform = Waveform.SQUARE
    secondary_waveform: Optional[Waveform] = None
    detune_cents: float = 0.0
    envelope: AudioEnvelope = field(default_factory=AudioEnvelope)
    filter_type: Optional[FilterType] = None
    filter_cutoff: float = 2000.0
    filter_resonance: float = 0.3
    reverb_wet: float = 0.2
    reverb_decay: float = 1.0


@dataclass
class UniversalStyleParams:
    """
    Universal style parameters that can be configured per-game.

    This is the main configuration object that each game's style tokens
    should provide. The procedural generators read from this to produce
    appropriately styled assets.
    """

    # Identity
    game_name: str = "generic"
    style_name: str = "default"

    # Colors
    palette: ColorPalette = field(default_factory=lambda: ColorPalette(
        primary=["#FFFFFF", "#808080"],
        accent=["#FF0000", "#00FF00", "#0000FF"],
        neutral=["#000000", "#1A1A1A", "#333333"]
    ))
    saturation_range: Tuple[float, float] = (0.5, 1.0)
    value_range: Tuple[float, float] = (0.3, 1.0)
    color_temperature: float = 0.0  # -1 (cool) to 1 (warm)

    # Geometry
    poly_budget: PolyBudget = field(default_factory=PolyBudget)
    geometry: GeometrySettings = field(default_factory=GeometrySettings)

    # Textures
    textures: TextureSettings = field(default_factory=TextureSettings)

    # Materials
    materials: MaterialSettings = field(default_factory=MaterialSettings)

    # Animation
    animation: AnimationSettings = field(default_factory=AnimationSettings)

    # Effects
    effects: EffectSettings = field(default_factory=EffectSettings)

    # Audio
    audio: AudioSettings = field(default_factory=AudioSettings)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        import dataclasses
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UniversalStyleParams':
        """Create from dictionary."""
        # Handle nested dataclasses
        if 'palette' in data and isinstance(data['palette'], dict):
            data['palette'] = ColorPalette(**data['palette'])
        if 'poly_budget' in data and isinstance(data['poly_budget'], dict):
            data['poly_budget'] = PolyBudget(**data['poly_budget'])
        if 'geometry' in data and isinstance(data['geometry'], dict):
            data['geometry'] = GeometrySettings(**data['geometry'])
        if 'textures' in data and isinstance(data['textures'], dict):
            data['textures'] = TextureSettings(**data['textures'])
        if 'materials' in data and isinstance(data['materials'], dict):
            data['materials'] = MaterialSettings(**data['materials'])
        if 'animation' in data and isinstance(data['animation'], dict):
            data['animation'] = AnimationSettings(**data['animation'])
        if 'effects' in data and isinstance(data['effects'], dict):
            data['effects'] = EffectSettings(**data['effects'])
        if 'audio' in data and isinstance(data['audio'], dict):
            data['audio'] = AudioSettings(**data['audio'])
        return cls(**data)


# Convenience type alias
StyleTokens = UniversalStyleParams
