"""
SFX synthesis recipes for game sound effects.

Provides style-aware sound effect generators.
"""

from dataclasses import dataclass
from typing import Dict, Optional
from .synthesis import (
    SAMPLE_RATE,
    sine_wave, square_wave, triangle_wave, sawtooth_wave,
    noise_white, noise_pink,
    apply_adsr, apply_exponential_decay, apply_linear_fade,
    lowpass, highpass, bandpass,
    normalize, mix,
    add_reverb,
    ADSREnvelope,
)

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None


@dataclass
class SFXStyle:
    """Style parameters for SFX generation."""
    brightness: float = 0.5      # 0=dark, 1=bright
    impact_weight: float = 0.5   # 0=light, 1=heavy
    reverb_amount: float = 0.2   # 0-1
    pitch_base: float = 1.0      # Pitch multiplier


# ============================================================================
# Combat SFX
# ============================================================================

def sfx_shoot(style: SFXStyle = None) -> "np.ndarray":
    """Projectile fire sound."""
    _require_numpy()
    s = style or SFXStyle()
    base_freq = 880 * s.pitch_base * (1 + s.brightness * 0.5)

    tone1 = sine_wave(base_freq, 0.1, 0.5)
    tone2 = sine_wave(base_freq * 1.5, 0.08, 0.3)

    wave = mix(tone1, tone2[:len(tone1)])
    wave = apply_adsr(wave, ADSREnvelope(0.005, 0.02, 0.3, 0.05))

    if s.brightness > 0.5:
        wave = highpass(wave, 400)

    return wave


def sfx_hit(style: SFXStyle = None) -> "np.ndarray":
    """Impact/damage sound."""
    _require_numpy()
    s = style or SFXStyle()

    noise_part = noise_white(0.1, 0.4 * s.impact_weight)
    tone_freq = 200 * s.pitch_base / (1 + s.impact_weight * 0.5)
    tone = sine_wave(tone_freq, 0.1, 0.5)

    wave = mix(noise_part, tone)
    wave = apply_adsr(wave, ADSREnvelope(0.002, 0.03, 0.2, 0.05))
    wave = lowpass(wave, 2000)

    return wave


def sfx_death(style: SFXStyle = None) -> "np.ndarray":
    """Enemy death sound."""
    _require_numpy()
    s = style or SFXStyle()

    noise_part = noise_white(0.35, 0.4)
    tone1 = sine_wave(440 * s.pitch_base, 0.3, 0.3)
    tone2 = sine_wave(660 * s.pitch_base, 0.25, 0.2)

    wave = mix(noise_part, tone1, tone2)
    wave = apply_adsr(wave, ADSREnvelope(0.005, 0.1, 0.3, 0.15))

    if s.reverb_amount > 0:
        wave = add_reverb(wave, s.reverb_amount, 40)

    return wave


def sfx_explosion(style: SFXStyle = None) -> "np.ndarray":
    """Explosion sound."""
    _require_numpy()
    s = style or SFXStyle()
    duration = 0.5 + s.impact_weight * 0.3

    # Low rumble
    rumble = noise_white(duration, 0.6)
    rumble = lowpass(rumble, 200 + s.impact_weight * 100)

    # Initial crack
    crack = noise_white(0.05, 0.8)
    crack = apply_exponential_decay(crack, 30)

    wave = np.zeros(int(SAMPLE_RATE * duration))
    wave[:len(crack)] += crack
    wave[:len(rumble)] += rumble

    wave = apply_adsr(wave, ADSREnvelope(0.002, 0.1, 0.3, 0.3))

    if s.reverb_amount > 0:
        wave = add_reverb(wave, s.reverb_amount * 2, 100)

    return wave


# ============================================================================
# Pickup SFX
# ============================================================================

def sfx_pickup(style: SFXStyle = None) -> "np.ndarray":
    """Item pickup sound (chime)."""
    _require_numpy()
    s = style or SFXStyle()
    base = 1200 * s.pitch_base * (1 + s.brightness * 0.3)

    tone1 = sine_wave(base, 0.15, 0.5)
    tone2 = sine_wave(base * 1.5, 0.12, 0.4)
    tone3 = triangle_wave(base * 2, 0.1, 0.2)

    wave = mix(tone1, tone2, tone3)
    wave = apply_adsr(wave, ADSREnvelope(0.005, 0.02, 0.5, 0.1))

    return wave


def sfx_coin(style: SFXStyle = None) -> "np.ndarray":
    """Coin/currency pickup."""
    _require_numpy()
    s = style or SFXStyle()

    tone1 = triangle_wave(1500 * s.pitch_base, 0.12, 0.5)
    tone2 = sine_wave(2000 * s.pitch_base, 0.08, 0.3)
    tone3 = sine_wave(2500 * s.pitch_base, 0.06, 0.2)

    wave = mix(tone1, tone2, tone3)
    wave = apply_adsr(wave, ADSREnvelope(0.002, 0.02, 0.4, 0.08))

    return wave


def sfx_xp(style: SFXStyle = None) -> "np.ndarray":
    """Experience/XP gain."""
    _require_numpy()
    s = style or SFXStyle()

    tone1 = sine_wave(1200 * s.pitch_base, 0.15, 0.5)
    tone2 = sine_wave(1800 * s.pitch_base, 0.12, 0.4)
    tone3 = triangle_wave(2400 * s.pitch_base, 0.1, 0.2)

    wave = mix(tone1, tone2, tone3)
    wave = apply_adsr(wave, ADSREnvelope(0.005, 0.02, 0.5, 0.1))

    return wave


def sfx_powerup(style: SFXStyle = None) -> "np.ndarray":
    """Power-up acquisition."""
    _require_numpy()
    s = style or SFXStyle()
    duration = 0.5
    frequencies = [400, 500, 600, 800, 1000]
    frequencies = [f * s.pitch_base for f in frequencies]

    wave = np.zeros(int(SAMPLE_RATE * duration))

    for i, freq in enumerate(frequencies):
        start = int(i * SAMPLE_RATE * 0.1)
        tone = sine_wave(freq, 0.15, 0.4)
        tone = apply_adsr(tone, ADSREnvelope(0.01, 0.02, 0.5, 0.1))
        end = min(start + len(tone), len(wave))
        wave[start:end] += tone[:end - start]

    return wave


def sfx_level_up(style: SFXStyle = None) -> "np.ndarray":
    """Level up fanfare."""
    _require_numpy()
    s = style or SFXStyle()
    duration = 1.0

    freqs = [440, 554, 659, 880, 1108, 1318]
    freqs = [f * s.pitch_base for f in freqs]

    wave = np.zeros(int(SAMPLE_RATE * duration))
    for i, freq in enumerate(freqs):
        dur = duration - (freq - 440) / 2000
        amp = 0.3 - i * 0.03
        tone = sine_wave(freq, dur, amp)
        wave[:len(tone)] += tone

    wave = apply_adsr(wave, ADSREnvelope(0.05, 0.15, 0.6, 0.3))

    if s.reverb_amount > 0:
        wave = add_reverb(wave, s.reverb_amount * 1.5, 80)

    return wave


# ============================================================================
# UI SFX
# ============================================================================

def sfx_menu_select(style: SFXStyle = None) -> "np.ndarray":
    """UI selection click."""
    _require_numpy()
    s = style or SFXStyle()
    freq = 600 * s.pitch_base * (1 + s.brightness * 0.3)

    tone1 = sine_wave(freq, 0.08, 0.5)
    tone2 = sine_wave(freq * 1.33, 0.06, 0.4)

    wave = mix(tone1, tone2)
    wave = apply_adsr(wave, ADSREnvelope(0.002, 0.02, 0.4, 0.03))

    return wave


def sfx_menu_navigate(style: SFXStyle = None) -> "np.ndarray":
    """Menu navigation sound."""
    _require_numpy()
    s = style or SFXStyle()

    wave = sine_wave(500 * s.pitch_base, 0.12, 0.5)
    wave = apply_adsr(wave, ADSREnvelope(0.01, 0.03, 0.4, 0.06))

    return wave


def sfx_menu_back(style: SFXStyle = None) -> "np.ndarray":
    """Back/cancel sound."""
    _require_numpy()
    s = style or SFXStyle()

    tone1 = sine_wave(600 * s.pitch_base, 0.1, 0.5)
    tone2 = sine_wave(400 * s.pitch_base, 0.1, 0.5)

    # Crossfade
    wave = np.zeros(int(SAMPLE_RATE * 0.15))
    wave[:len(tone1)] = tone1
    blend_start = len(tone1) // 2
    blend_end = min(blend_start + len(tone2), len(wave))
    actual_blend_len = blend_end - blend_start
    if actual_blend_len > 0:
        wave[blend_start:blend_end] += tone2[:actual_blend_len] * 0.7

    wave = apply_adsr(wave, ADSREnvelope(0.01, 0.03, 0.3, 0.05))

    return wave


# ============================================================================
# Movement SFX
# ============================================================================

def sfx_dash(style: SFXStyle = None) -> "np.ndarray":
    """Dash/whoosh sound."""
    _require_numpy()
    s = style or SFXStyle()

    wave = noise_white(0.25, 0.5)
    wave = highpass(wave, 500)
    wave = lowpass(wave, 4000)
    wave = apply_adsr(wave, ADSREnvelope(0.02, 0.05, 0.2, 0.15))

    return wave


def sfx_jump(style: SFXStyle = None) -> "np.ndarray":
    """Jump sound."""
    _require_numpy()
    s = style or SFXStyle()
    duration = 0.15
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples, False)

    # Rising pitch
    freq = 200 * s.pitch_base + 400 * t / duration
    wave = 0.5 * np.sin(2 * np.pi * freq * t)
    wave = apply_adsr(wave, ADSREnvelope(0.01, 0.03, 0.4, 0.08))

    return wave


def sfx_footstep(style: SFXStyle = None) -> "np.ndarray":
    """Footstep sound."""
    _require_numpy()
    s = style or SFXStyle()

    noise = noise_white(0.08, 0.4)
    noise = lowpass(noise, 800 + s.brightness * 400)
    noise = apply_exponential_decay(noise, 20)

    return noise


# ============================================================================
# Event SFX
# ============================================================================

def sfx_boss_spawn(style: SFXStyle = None) -> "np.ndarray":
    """Boss appearance rumble."""
    _require_numpy()
    s = style or SFXStyle()
    duration = 1.5

    # Low drone
    drone = sine_wave(80 * s.pitch_base, duration, 0.5)
    drone += sine_wave(120 * s.pitch_base, duration, 0.3)

    # Noise rumble
    noise = noise_white(duration, 0.3)
    noise = lowpass(noise, 200)

    wave = drone + noise
    wave = apply_adsr(wave, ADSREnvelope(0.3, 0.3, 0.5, 0.5))

    return wave


def sfx_wave_complete(style: SFXStyle = None) -> "np.ndarray":
    """Wave/level complete fanfare."""
    _require_numpy()
    s = style or SFXStyle()
    duration = 0.8

    freqs = [523, 659, 784, 1047]  # C, E, G, C major chord
    freqs = [f * s.pitch_base for f in freqs]

    wave = np.zeros(int(SAMPLE_RATE * duration))

    for i, freq in enumerate(freqs):
        start = int(i * SAMPLE_RATE * 0.15)
        tone = sine_wave(freq, 0.25, 0.4)
        tone = apply_adsr(tone, ADSREnvelope(0.01, 0.03, 0.6, 0.15))
        end = min(start + len(tone), len(wave))
        wave[start:end] += tone[:end - start]

    if s.reverb_amount > 0:
        wave = add_reverb(wave, s.reverb_amount, 60)

    return wave


# ============================================================================
# Style Presets
# ============================================================================

NEON_DRIFT_STYLE = SFXStyle(
    brightness=0.7,
    impact_weight=0.4,
    reverb_amount=0.25,
    pitch_base=1.0
)

PRISM_SURVIVORS_STYLE = SFXStyle(
    brightness=0.8,
    impact_weight=0.5,
    reverb_amount=0.15,
    pitch_base=1.0
)

LUMINA_DEPTHS_STYLE = SFXStyle(
    brightness=0.3,
    impact_weight=0.3,
    reverb_amount=0.6,
    pitch_base=0.8
)

OVERRIDE_STYLE = SFXStyle(
    brightness=0.4,
    impact_weight=0.7,
    reverb_amount=0.3,
    pitch_base=0.9
)


def get_style_for_game(game: str) -> SFXStyle:
    """Get SFX style preset for a game."""
    styles = {
        "neon-drift": NEON_DRIFT_STYLE,
        "neon_drift": NEON_DRIFT_STYLE,
        "prism-survivors": PRISM_SURVIVORS_STYLE,
        "prism_survivors": PRISM_SURVIVORS_STYLE,
        "lumina-depths": LUMINA_DEPTHS_STYLE,
        "lumina_depths": LUMINA_DEPTHS_STYLE,
        "override": OVERRIDE_STYLE,
    }
    return styles.get(game.lower().replace(" ", "-"), SFXStyle())


def generate_game_sfx(game: str) -> Dict[str, "np.ndarray"]:
    """Generate all SFX for a game using its style preset."""
    style = get_style_for_game(game)

    return {
        "shoot": sfx_shoot(style),
        "hit": sfx_hit(style),
        "death": sfx_death(style),
        "explosion": sfx_explosion(style),
        "pickup": sfx_pickup(style),
        "coin": sfx_coin(style),
        "xp": sfx_xp(style),
        "powerup": sfx_powerup(style),
        "level_up": sfx_level_up(style),
        "menu_select": sfx_menu_select(style),
        "menu_navigate": sfx_menu_navigate(style),
        "menu_back": sfx_menu_back(style),
        "dash": sfx_dash(style),
        "jump": sfx_jump(style),
        "footstep": sfx_footstep(style),
        "boss_spawn": sfx_boss_spawn(style),
        "wave_complete": sfx_wave_complete(style),
    }


# ============================================================================
# Internal Helpers
# ============================================================================

def _require_numpy():
    """Raise ImportError if numpy is not available."""
    if not HAS_NUMPY:
        raise ImportError(
            "numpy and scipy are required for SFX synthesis. "
            "Install with: pip install numpy scipy"
        )
