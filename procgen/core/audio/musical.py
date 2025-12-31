"""
Musical sample generators.

Provides synthesized instrument samples for tracker music.
"""

from typing import Dict, Optional
from dataclasses import dataclass

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None


@dataclass
class MusicalStyleParams:
    """Style parameters for musical samples."""
    brightness: float = 0.5    # 0=dark, 1=bright
    warmth: float = 0.5        # 0=cold/digital, 1=warm/analog
    attack: float = 0.5        # 0=slow, 1=fast attack
    release: float = 0.5       # 0=short, 1=long decay


def _require_numpy():
    if not HAS_NUMPY:
        raise ImportError("numpy is required for audio synthesis")


def generate_bass_sample(
    style: MusicalStyleParams = None,
    bass_type: str = "synth",
    base_freq: float = 55.0,
) -> "np.ndarray":
    """
    Generate bass instrument sample.

    Args:
        style: Musical style parameters
        bass_type: "synth", "sub", "pluck", "fm"
        base_freq: Base frequency (A1 = 55 Hz)
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, sawtooth_wave, square_wave, apply_adsr, ADSREnvelope,
        lowpass, fm_wave
    )

    s = style or MusicalStyleParams()
    duration = 0.5 + s.release * 0.5

    if bass_type == "synth":
        # Classic synth bass
        wave = sawtooth_wave(base_freq, duration, 0.4)
        wave += sawtooth_wave(base_freq * 1.005, duration, 0.3)  # Slight detune

        cutoff = 300 + s.brightness * 400
        wave = lowpass(wave, cutoff)

        attack = 0.01 + (1 - s.attack) * 0.03
        wave = apply_adsr(wave, ADSREnvelope(attack, 0.1, 0.7, 0.1 + s.release * 0.2))

    elif bass_type == "sub":
        # Deep sub bass
        wave = sine_wave(base_freq, duration, 0.6)
        wave += sine_wave(base_freq * 2, duration, 0.2 * s.brightness)

        wave = apply_adsr(wave, ADSREnvelope(0.02, 0.1, 0.8, 0.15))

    elif bass_type == "pluck":
        # Plucked bass
        wave = sawtooth_wave(base_freq, duration, 0.5)
        wave = lowpass(wave, 800 + s.brightness * 500)

        attack = 0.002 + (1 - s.attack) * 0.01
        wave = apply_adsr(wave, ADSREnvelope(attack, 0.08, 0.4, 0.1))

    else:  # fm
        # FM bass
        wave = fm_wave(
            carrier_freq=base_freq,
            mod_freq=base_freq * 2,
            mod_index=2 + s.brightness * 2,
            duration=duration,
            amplitude=0.5
        )
        wave = lowpass(wave, 600)
        wave = apply_adsr(wave, ADSREnvelope(0.01, 0.1, 0.6, 0.15))

    return wave


def generate_lead_sample(
    style: MusicalStyleParams = None,
    lead_type: str = "square",
    base_freq: float = 440.0,
) -> "np.ndarray":
    """
    Generate lead synth sample.

    Args:
        style: Musical style parameters
        lead_type: "square", "saw", "pwm", "supersaw"
        base_freq: Base frequency (A4 = 440 Hz)
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, sawtooth_wave, square_wave, apply_adsr, ADSREnvelope,
        lowpass, SAMPLE_RATE
    )

    s = style or MusicalStyleParams()
    duration = 0.5

    if lead_type == "square":
        wave = square_wave(base_freq, duration, 0.4)
        wave += sine_wave(base_freq * 2, duration, 0.15 * s.brightness)

        cutoff = 2000 + s.brightness * 3000
        wave = lowpass(wave, cutoff)

    elif lead_type == "saw":
        wave = sawtooth_wave(base_freq, duration, 0.4)

        cutoff = 3000 + s.brightness * 4000
        wave = lowpass(wave, cutoff)

    elif lead_type == "pwm":
        # Pulse width modulated
        samples = int(SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, False)

        # Modulate duty cycle
        duty = 0.3 + 0.2 * np.sin(2 * np.pi * 3 * t)
        wave = np.sign(np.sin(2 * np.pi * base_freq * t) - (1 - 2 * duty)) * 0.4

        wave = lowpass(wave, 2500 + s.brightness * 2000)

    else:  # supersaw
        # Multiple detuned saws
        wave = np.zeros(int(SAMPLE_RATE * duration))
        detunes = [-15, -7, 0, 7, 15]  # cents

        for detune in detunes:
            ratio = 2 ** (detune / 1200)
            layer = sawtooth_wave(base_freq * ratio, duration, 0.2)
            wave[:len(layer)] += layer

        wave = lowpass(wave, 4000 + s.brightness * 3000)

    attack = 0.005 + (1 - s.attack) * 0.02
    wave = apply_adsr(wave, ADSREnvelope(attack, 0.1, 0.6, 0.1 + s.release * 0.15))

    return wave


def generate_pad_sample(
    style: MusicalStyleParams = None,
    pad_type: str = "warm",
    base_freq: float = 220.0,
) -> "np.ndarray":
    """
    Generate pad/atmosphere sample.

    Args:
        style: Musical style parameters
        pad_type: "warm", "strings", "choir", "glass"
        base_freq: Base frequency
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, sawtooth_wave, triangle_wave, apply_adsr, ADSREnvelope,
        lowpass, add_chorus, SAMPLE_RATE
    )

    s = style or MusicalStyleParams()
    duration = 1.0

    if pad_type == "warm":
        # Warm analog pad
        wave = sine_wave(base_freq, duration, 0.3)
        wave += sine_wave(base_freq * 2, duration, 0.15)
        wave += sine_wave(base_freq * 3, duration, 0.08)

        # Slight detuned layer
        wave += sine_wave(base_freq * 1.003, duration, 0.2)

        wave = lowpass(wave, 1000 + s.warmth * 500)
        wave = add_chorus(wave, depth_ms=6, rate_hz=0.5, mix=0.4)

    elif pad_type == "strings":
        # String ensemble
        wave = np.zeros(int(SAMPLE_RATE * duration))

        for i in range(4):
            detune = (i - 1.5) * 5  # cents
            ratio = 2 ** (detune / 1200)
            layer = sawtooth_wave(base_freq * ratio, duration, 0.2)
            wave[:len(layer)] += layer

        wave = lowpass(wave, 3000 + s.brightness * 2000)
        wave = add_chorus(wave, depth_ms=8, rate_hz=0.3, mix=0.3)

    elif pad_type == "choir":
        # Vocal-ish pad
        wave = sine_wave(base_freq, duration, 0.4)
        wave += sine_wave(base_freq * 2, duration, 0.3)
        wave += sine_wave(base_freq * 3, duration, 0.15)
        wave += sine_wave(base_freq * 4, duration, 0.08)

        # Add formant-like filtering
        wave = lowpass(wave, 2000)

    else:  # glass
        # Crystalline pad
        wave = triangle_wave(base_freq, duration, 0.3)
        wave += sine_wave(base_freq * 2, duration, 0.25)
        wave += sine_wave(base_freq * 4, duration, 0.15)

        wave = add_chorus(wave, depth_ms=4, rate_hz=0.8, mix=0.5)

    attack = 0.1 + (1 - s.attack) * 0.3
    release = 0.2 + s.release * 0.3
    wave = apply_adsr(wave, ADSREnvelope(attack, 0.2, 0.7, release))

    return wave


def generate_arp_sample(
    style: MusicalStyleParams = None,
    arp_type: str = "pluck",
    base_freq: float = 440.0,
) -> "np.ndarray":
    """
    Generate arpeggio/pluck sample.

    Args:
        style: Musical style parameters
        arp_type: "pluck", "bell", "stab", "chip"
        base_freq: Base frequency
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, triangle_wave, sawtooth_wave, square_wave,
        apply_adsr, ADSREnvelope, lowpass, fm_wave
    )

    s = style or MusicalStyleParams()
    duration = 0.2

    if arp_type == "pluck":
        wave = sawtooth_wave(base_freq, duration, 0.5)
        wave = lowpass(wave, 2000 + s.brightness * 2000)
        wave = apply_adsr(wave, ADSREnvelope(0.002, 0.03, 0.3, 0.1))

    elif arp_type == "bell":
        wave = fm_wave(
            carrier_freq=base_freq,
            mod_freq=base_freq * 1.4,
            mod_index=3 + s.brightness * 2,
            duration=duration,
            amplitude=0.4
        )
        wave = apply_adsr(wave, ADSREnvelope(0.001, 0.15, 0.3, 0.15))

    elif arp_type == "stab":
        wave = sawtooth_wave(base_freq, duration, 0.4)
        wave += sawtooth_wave(base_freq * 1.01, duration, 0.3)

        wave = lowpass(wave, 3000 + s.brightness * 2000)
        wave = apply_adsr(wave, ADSREnvelope(0.001, 0.04, 0.2, 0.05))

    else:  # chip
        # 8-bit style
        wave = square_wave(base_freq, duration, 0.4)
        wave = apply_adsr(wave, ADSREnvelope(0.001, 0.02, 0.4, 0.08))

    return wave


def generate_drum_kit(
    style: MusicalStyleParams = None,
) -> Dict[str, "np.ndarray"]:
    """
    Generate a complete drum kit.

    Args:
        style: Musical style parameters

    Returns:
        Dict with keys: kick, snare, hihat, openhat, clap, tom
    """
    _require_numpy()
    from ...lib.instruments import (
        synth_kick, synth_snare, synth_hihat, synth_clap, synth_tom
    )

    s = style or MusicalStyleParams()

    # Adjust parameters based on style
    kick_pitch = 150 if s.brightness > 0.5 else 120
    snare_noise = 0.4 + s.brightness * 0.2
    decay_mult = 0.8 + s.warmth * 0.4

    return {
        "kick": synth_kick(
            pitch_start=kick_pitch,
            pitch_end=40,
            decay_rate=8 / decay_mult
        ),
        "snare": synth_snare(
            body_freq=180,
            noise_amount=snare_noise
        ),
        "hihat": synth_hihat(closed=True),
        "openhat": synth_hihat(closed=False),
        "clap": synth_clap(),
        "tom": synth_tom(pitch=100),
    }
