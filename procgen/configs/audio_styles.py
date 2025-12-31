"""
Audio style configurations for ZX games.

Provides comprehensive audio styling for each game including
tempo, instrumentation, and composition preferences.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict


@dataclass
class AudioStyleConfig:
    """Complete audio style configuration for a game."""

    # === Tempo & Rhythm ===
    tempo_range: Tuple[int, int]
    default_speed: int = 6  # XM speed (lower = faster)
    time_signature: Tuple[int, int] = (4, 4)
    swing_amount: float = 0.0  # 0-1

    # === Harmony ===
    preferred_keys: List[str] = None
    preferred_scales: List[str] = None
    preferred_progressions: List[str] = None

    # === Instrumentation ===
    instrument_kit: str = "default"
    use_drums: bool = True
    use_bass: bool = True
    use_lead: bool = True
    use_pad: bool = True
    use_arp: bool = True

    # === Effects & Processing ===
    reverb_amount: float = 0.3
    use_vibrato: bool = True
    use_arpeggios: bool = True
    use_portamento: bool = False
    filter_envelope: bool = True

    # === Dynamics ===
    volume_range: Tuple[int, int] = (32, 64)  # XM volume 0-64
    crescendo_enabled: bool = True
    staccato_amount: float = 0.0  # 0-1

    def __post_init__(self):
        if self.preferred_keys is None:
            self.preferred_keys = ["Am", "Em"]
        if self.preferred_scales is None:
            self.preferred_scales = ["minor"]
        if self.preferred_progressions is None:
            self.preferred_progressions = ["epic"]


# ============================================================================
# Game-Specific Audio Styles
# ============================================================================

NEON_DRIFT_AUDIO = AudioStyleConfig(
    tempo_range=(128, 145),
    default_speed=6,
    preferred_keys=["Am", "Em", "Dm", "Fm"],
    preferred_scales=["minor", "dorian", "phrygian"],
    preferred_progressions=["synthwave", "tense", "dark"],
    instrument_kit="neon_drift",
    use_drums=True,
    use_bass=True,
    use_lead=True,
    use_pad=True,
    use_arp=True,
    reverb_amount=0.25,
    use_vibrato=True,
    use_arpeggios=True,
    use_portamento=True,
    filter_envelope=True,
    volume_range=(40, 60),
)

LUMINA_DEPTHS_AUDIO = AudioStyleConfig(
    tempo_range=(60, 90),
    default_speed=8,  # Slower
    preferred_keys=["Em", "Am", "Dm", "Bm"],
    preferred_scales=["aeolian", "dorian", "pentatonic_minor"],
    preferred_progressions=["ambient", "mysterious", "peaceful"],
    instrument_kit="lumina_depths",
    use_drums=False,  # No drums for ambient
    use_bass=True,
    use_lead=True,
    use_pad=True,
    use_arp=True,
    reverb_amount=0.6,  # Lots of reverb
    use_vibrato=True,
    use_arpeggios=True,
    use_portamento=True,
    filter_envelope=True,
    volume_range=(24, 48),  # Quieter dynamics
    crescendo_enabled=True,
)

PRISM_SURVIVORS_AUDIO = AudioStyleConfig(
    tempo_range=(140, 170),
    default_speed=5,  # Faster
    preferred_keys=["Em", "Am", "Cm", "Dm"],
    preferred_scales=["minor", "harmonic_minor", "phrygian"],
    preferred_progressions=["epic", "tense", "uplifting"],
    instrument_kit="prism_survivors",
    use_drums=True,
    use_bass=True,
    use_lead=True,
    use_pad=True,
    use_arp=True,
    reverb_amount=0.15,
    use_vibrato=True,
    use_arpeggios=True,
    use_portamento=False,
    filter_envelope=True,
    volume_range=(48, 64),  # Louder, more aggressive
)

OVERRIDE_AUDIO = AudioStyleConfig(
    tempo_range=(90, 130),
    default_speed=6,
    preferred_keys=["Dm", "Cm", "Am", "Em"],
    preferred_scales=["minor", "locrian", "phrygian"],
    preferred_progressions=["tense", "dark", "mysterious"],
    instrument_kit="override",
    use_drums=True,
    use_bass=True,
    use_lead=True,
    use_pad=True,
    use_arp=False,  # Less melodic
    reverb_amount=0.3,
    use_vibrato=False,
    use_arpeggios=False,
    use_portamento=False,
    filter_envelope=True,
    volume_range=(32, 56),
    staccato_amount=0.3,  # Punchy, rhythmic
)


# ============================================================================
# Context-Specific Styles
# ============================================================================

@dataclass
class ContextAudioStyle:
    """Audio style for specific game contexts/scenes."""
    base_style: AudioStyleConfig
    tempo_modifier: float = 1.0  # Multiply base tempo
    intensity: float = 0.5  # 0=calm, 1=intense
    tension: float = 0.5  # 0=relaxed, 1=tense


MENU_STYLE = ContextAudioStyle(
    base_style=AudioStyleConfig(
        tempo_range=(80, 100),
        default_speed=7,
        preferred_keys=["Am", "Em"],
        preferred_scales=["minor", "dorian"],
        preferred_progressions=["peaceful", "ambient"],
        use_drums=False,
        reverb_amount=0.4,
        volume_range=(24, 40),
    ),
    tempo_modifier=0.8,
    intensity=0.2,
    tension=0.2,
)

COMBAT_STYLE = ContextAudioStyle(
    base_style=AudioStyleConfig(
        tempo_range=(140, 180),
        default_speed=5,
        preferred_keys=["Em", "Am", "Cm"],
        preferred_scales=["minor", "harmonic_minor"],
        preferred_progressions=["epic", "tense"],
        use_drums=True,
        reverb_amount=0.15,
        volume_range=(48, 64),
    ),
    tempo_modifier=1.2,
    intensity=0.9,
    tension=0.8,
)

BOSS_STYLE = ContextAudioStyle(
    base_style=AudioStyleConfig(
        tempo_range=(150, 190),
        default_speed=4,
        preferred_keys=["Cm", "Dm", "Fm"],
        preferred_scales=["harmonic_minor", "phrygian"],
        preferred_progressions=["epic", "dark"],
        use_drums=True,
        reverb_amount=0.2,
        volume_range=(56, 64),
    ),
    tempo_modifier=1.3,
    intensity=1.0,
    tension=1.0,
)

VICTORY_STYLE = ContextAudioStyle(
    base_style=AudioStyleConfig(
        tempo_range=(100, 130),
        default_speed=6,
        preferred_keys=["C", "G", "D"],
        preferred_scales=["major", "lydian"],
        preferred_progressions=["triumphant", "uplifting"],
        use_drums=True,
        reverb_amount=0.3,
        volume_range=(40, 56),
    ),
    tempo_modifier=1.0,
    intensity=0.7,
    tension=0.1,
)

DEFEAT_STYLE = ContextAudioStyle(
    base_style=AudioStyleConfig(
        tempo_range=(60, 80),
        default_speed=8,
        preferred_keys=["Dm", "Am", "Em"],
        preferred_scales=["minor", "aeolian"],
        preferred_progressions=["melancholic", "mysterious"],
        use_drums=False,
        reverb_amount=0.5,
        volume_range=(20, 36),
    ),
    tempo_modifier=0.7,
    intensity=0.2,
    tension=0.3,
)


# ============================================================================
# Style Lookup Functions
# ============================================================================

def get_audio_style(game: str) -> AudioStyleConfig:
    """Get audio style config for a game."""
    styles = {
        "neon-drift": NEON_DRIFT_AUDIO,
        "neon_drift": NEON_DRIFT_AUDIO,
        "lumina-depths": LUMINA_DEPTHS_AUDIO,
        "lumina_depths": LUMINA_DEPTHS_AUDIO,
        "prism-survivors": PRISM_SURVIVORS_AUDIO,
        "prism_survivors": PRISM_SURVIVORS_AUDIO,
        "override": OVERRIDE_AUDIO,
    }
    return styles.get(game.lower(), NEON_DRIFT_AUDIO)


def get_context_style(context: str) -> ContextAudioStyle:
    """Get audio style for a game context."""
    contexts = {
        "menu": MENU_STYLE,
        "combat": COMBAT_STYLE,
        "boss": BOSS_STYLE,
        "victory": VICTORY_STYLE,
        "defeat": DEFEAT_STYLE,
    }
    return contexts.get(context.lower(), COMBAT_STYLE)
