"""
UI sound effect generators.

Provides menu clicks, hovers, confirms, and other interface sounds.
"""

from typing import Optional
from dataclasses import dataclass

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None


@dataclass
class UIStyleParams:
    """Style parameters for UI sounds."""
    brightness: float = 0.5      # 0=dark/muted, 1=bright/crisp
    pitch_base: float = 1.0      # Base pitch multiplier
    reverb_amount: float = 0.1   # 0-1 reverb
    snap: float = 0.5            # 0=soft, 1=snappy attack


def _require_numpy():
    if not HAS_NUMPY:
        raise ImportError("numpy is required for audio synthesis")


def generate_menu_click(
    style: UIStyleParams = None,
    variant: int = 0,
) -> "np.ndarray":
    """
    Generate menu click/select sound.

    Args:
        style: UI style parameters
        variant: Sound variant (0-2)
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, triangle_wave, apply_adsr, ADSREnvelope, highpass
    )

    s = style or UIStyleParams()
    base_freq = 600 * s.pitch_base * (1 + s.brightness * 0.3)

    if variant == 0:
        # Simple click
        wave = sine_wave(base_freq, 0.08, 0.5)
        wave += sine_wave(base_freq * 1.5, 0.06, 0.3)
    elif variant == 1:
        # Two-tone click
        wave = sine_wave(base_freq, 0.04, 0.5)
        wave2 = sine_wave(base_freq * 1.2, 0.04, 0.4)
        # Offset second tone
        result = np.zeros(len(wave) + len(wave2) // 2)
        result[:len(wave)] = wave
        result[len(wave2) // 2:len(wave2) // 2 + len(wave2)] += wave2
        wave = result
    else:
        # Triangle click (softer)
        wave = triangle_wave(base_freq * 0.8, 0.1, 0.5)

    attack = 0.002 + (1 - s.snap) * 0.01
    wave = apply_adsr(wave, ADSREnvelope(attack, 0.02, 0.3, 0.04))

    if s.brightness > 0.5:
        wave = highpass(wave, 300)

    return wave


def generate_menu_hover(
    style: UIStyleParams = None,
) -> "np.ndarray":
    """
    Generate menu hover/focus sound.

    Args:
        style: UI style parameters
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, apply_adsr, ADSREnvelope, lowpass
    )

    s = style or UIStyleParams()
    freq = 400 * s.pitch_base

    wave = sine_wave(freq, 0.06, 0.3)
    wave = apply_adsr(wave, ADSREnvelope(0.005, 0.02, 0.2, 0.03))
    wave = lowpass(wave, 2000 + s.brightness * 2000)

    return wave


def generate_menu_confirm(
    style: UIStyleParams = None,
) -> "np.ndarray":
    """
    Generate menu confirm/accept sound.

    Args:
        style: UI style parameters
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, apply_adsr, ADSREnvelope, SAMPLE_RATE, add_reverb
    )

    s = style or UIStyleParams()
    base = 500 * s.pitch_base

    # Rising two-tone confirmation
    duration = 0.2
    wave = np.zeros(int(SAMPLE_RATE * duration))

    tone1 = sine_wave(base, 0.1, 0.5)
    tone1 = apply_adsr(tone1, ADSREnvelope(0.005, 0.02, 0.5, 0.05))
    wave[:len(tone1)] = tone1

    tone2 = sine_wave(base * 1.25, 0.12, 0.5)  # Major third
    tone2 = apply_adsr(tone2, ADSREnvelope(0.005, 0.02, 0.5, 0.07))
    start = int(SAMPLE_RATE * 0.06)
    wave[start:start + len(tone2)] += tone2

    if s.reverb_amount > 0:
        wave = add_reverb(wave, s.reverb_amount * 0.5, 30)

    return wave


def generate_menu_cancel(
    style: UIStyleParams = None,
) -> "np.ndarray":
    """
    Generate menu cancel/back sound.

    Args:
        style: UI style parameters
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, apply_adsr, ADSREnvelope, SAMPLE_RATE
    )

    s = style or UIStyleParams()
    base = 500 * s.pitch_base

    # Descending two-tone cancel
    duration = 0.15
    wave = np.zeros(int(SAMPLE_RATE * duration))

    tone1 = sine_wave(base, 0.08, 0.5)
    tone1 = apply_adsr(tone1, ADSREnvelope(0.005, 0.02, 0.3, 0.04))
    wave[:len(tone1)] = tone1

    tone2 = sine_wave(base * 0.8, 0.1, 0.5)  # Lower pitch
    tone2 = apply_adsr(tone2, ADSREnvelope(0.005, 0.02, 0.3, 0.06))
    start = int(SAMPLE_RATE * 0.04)
    wave[start:start + len(tone2)] += tone2

    return wave


def generate_menu_error(
    style: UIStyleParams = None,
) -> "np.ndarray":
    """
    Generate menu error/invalid sound.

    Args:
        style: UI style parameters
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, square_wave, apply_adsr, ADSREnvelope, lowpass, mix
    )

    s = style or UIStyleParams()
    base = 200 * s.pitch_base

    # Buzzy error tone
    tone1 = square_wave(base, 0.15, 0.3)
    tone2 = square_wave(base * 1.05, 0.15, 0.2)  # Slight detune for buzz

    wave = mix(tone1, tone2)
    wave = lowpass(wave, 1500)
    wave = apply_adsr(wave, ADSREnvelope(0.002, 0.05, 0.3, 0.08))

    return wave


def generate_notification(
    style: UIStyleParams = None,
    notification_type: str = "info",
) -> "np.ndarray":
    """
    Generate notification sound.

    Args:
        style: UI style parameters
        notification_type: "info", "success", "warning", "alert"
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, triangle_wave, apply_adsr, ADSREnvelope,
        SAMPLE_RATE, add_reverb
    )

    s = style or UIStyleParams()

    if notification_type == "info":
        # Gentle two-tone
        base = 800 * s.pitch_base
        wave = sine_wave(base, 0.15, 0.4)
        wave2 = sine_wave(base * 1.5, 0.12, 0.3)
        result = np.zeros(int(SAMPLE_RATE * 0.2))
        result[:len(wave)] = wave
        result[int(SAMPLE_RATE * 0.05):int(SAMPLE_RATE * 0.05) + len(wave2)] += wave2
        wave = result

    elif notification_type == "success":
        # Ascending arpeggio
        base = 600 * s.pitch_base
        freqs = [base, base * 1.25, base * 1.5]  # Major chord
        result = np.zeros(int(SAMPLE_RATE * 0.4))

        for i, freq in enumerate(freqs):
            tone = triangle_wave(freq, 0.15, 0.4)
            tone = apply_adsr(tone, ADSREnvelope(0.01, 0.03, 0.5, 0.1))
            start = int(SAMPLE_RATE * 0.08 * i)
            result[start:start + len(tone)] += tone

        wave = result

    elif notification_type == "warning":
        # Attention-getting pulse
        base = 500 * s.pitch_base
        result = np.zeros(int(SAMPLE_RATE * 0.4))

        for i in range(2):
            tone = sine_wave(base, 0.1, 0.5)
            tone = apply_adsr(tone, ADSREnvelope(0.005, 0.03, 0.4, 0.05))
            start = int(SAMPLE_RATE * 0.15 * i)
            result[start:start + len(tone)] += tone

        wave = result

    else:  # alert
        # Urgent repeated tone
        base = 700 * s.pitch_base
        result = np.zeros(int(SAMPLE_RATE * 0.5))

        for i in range(3):
            tone = sine_wave(base, 0.08, 0.5)
            tone = apply_adsr(tone, ADSREnvelope(0.002, 0.02, 0.3, 0.03))
            start = int(SAMPLE_RATE * 0.12 * i)
            result[start:start + len(tone)] += tone

        wave = result

    wave = apply_adsr(wave, ADSREnvelope(0.01, 0.05, 0.7, 0.15))

    if s.reverb_amount > 0:
        wave = add_reverb(wave, s.reverb_amount, 40)

    return wave
