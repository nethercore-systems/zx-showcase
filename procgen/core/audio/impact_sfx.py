"""
Impact sound effect generators.

Provides hits, explosions, and collision sounds.
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
class ImpactStyleParams:
    """Style parameters for impact sounds."""
    weight: float = 0.5        # 0=light, 1=heavy
    brightness: float = 0.5    # 0=muted, 1=bright
    reverb_amount: float = 0.2
    pitch_base: float = 1.0


def _require_numpy():
    if not HAS_NUMPY:
        raise ImportError("numpy is required for audio synthesis")


def generate_hit(
    style: ImpactStyleParams = None,
    hit_type: str = "punch",
) -> "np.ndarray":
    """
    Generate hit/impact sound.

    Args:
        style: Impact style parameters
        hit_type: "punch", "slap", "thud", "slash"
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, noise_white, apply_adsr, apply_exponential_decay,
        ADSREnvelope, lowpass, highpass, mix, SAMPLE_RATE
    )

    s = style or ImpactStyleParams()

    if hit_type == "punch":
        # Body thump with some high-end crack
        body_freq = 100 * s.pitch_base / (1 + s.weight * 0.5)
        body = sine_wave(body_freq, 0.15, 0.6)
        body = apply_exponential_decay(body, 15 - s.weight * 5)

        crack = noise_white(0.03, 0.4 * s.brightness)
        crack = highpass(crack, 2000)
        crack = apply_exponential_decay(crack, 50)

        wave = np.zeros(len(body))
        wave[:len(body)] = body
        wave[:len(crack)] += crack

    elif hit_type == "slap":
        # Quick snap with high frequencies
        noise = noise_white(0.08, 0.5)
        noise = bandpass_filter(noise, 500, 4000)
        wave = apply_adsr(noise, ADSREnvelope(0.001, 0.02, 0.2, 0.04))

    elif hit_type == "thud":
        # Deep impact
        freq = 60 * s.pitch_base
        wave = sine_wave(freq, 0.25, 0.7)
        wave += noise_white(0.1, 0.2)[:len(wave)]
        wave = lowpass(wave, 300)
        wave = apply_exponential_decay(wave, 8)

    else:  # slash
        # Sharp cutting sound
        noise = noise_white(0.12, 0.5)
        noise = highpass(noise, 1500 + s.brightness * 2000)
        wave = apply_adsr(noise, ADSREnvelope(0.001, 0.03, 0.2, 0.08))

    return wave


def bandpass_filter(wave, low, high):
    """Simple bandpass by combining lowpass and highpass."""
    from ...lib.synthesis import lowpass, highpass
    wave = highpass(wave, low)
    wave = lowpass(wave, high)
    return wave


def generate_explosion(
    style: ImpactStyleParams = None,
    size: str = "medium",
) -> "np.ndarray":
    """
    Generate explosion sound.

    Args:
        style: Impact style parameters
        size: "small", "medium", "large", "massive"
    """
    _require_numpy()
    from ...lib.synthesis import (
        noise_white, apply_adsr, apply_exponential_decay,
        ADSREnvelope, lowpass, highpass, SAMPLE_RATE, add_reverb
    )

    s = style or ImpactStyleParams()

    size_params = {
        "small": (0.3, 300, 20, 0.4),
        "medium": (0.5, 200, 12, 0.6),
        "large": (0.8, 100, 8, 0.8),
        "massive": (1.2, 60, 5, 1.0),
    }
    duration, cutoff, decay, amp = size_params.get(size, size_params["medium"])
    duration *= (1 + s.weight * 0.3)

    # Low rumble
    rumble = noise_white(duration, amp * 0.7)
    rumble = lowpass(rumble, cutoff + s.weight * 50)
    rumble = apply_exponential_decay(rumble, decay)

    # Initial crack
    crack = noise_white(0.05, amp)
    crack = apply_exponential_decay(crack, 40)

    wave = np.zeros(int(SAMPLE_RATE * duration))
    wave[:len(crack)] = crack
    wave[:len(rumble)] += rumble

    wave = apply_adsr(wave, ADSREnvelope(0.002, 0.1, 0.3, duration * 0.4))

    if s.reverb_amount > 0:
        wave = add_reverb(wave, s.reverb_amount * 1.5, 80)

    return wave


def generate_impact(
    style: ImpactStyleParams = None,
    material: str = "metal",
) -> "np.ndarray":
    """
    Generate material impact sound.

    Args:
        style: Impact style parameters
        material: "metal", "wood", "stone", "flesh"
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, noise_white, apply_adsr, apply_exponential_decay,
        ADSREnvelope, lowpass, highpass, mix, SAMPLE_RATE
    )

    s = style or ImpactStyleParams()

    if material == "metal":
        # Metallic ring
        freqs = [800, 1200, 1800, 2400]
        freqs = [f * s.pitch_base for f in freqs]
        duration = 0.4
        wave = np.zeros(int(SAMPLE_RATE * duration))

        for i, freq in enumerate(freqs):
            tone = sine_wave(freq, duration, 0.25 / (i + 1))
            tone = apply_exponential_decay(tone, 6 + i * 2)
            wave[:len(tone)] += tone

        # Add initial transient
        transient = noise_white(0.01, 0.5)
        wave[:len(transient)] += transient

    elif material == "wood":
        # Hollow thunk
        freq = 200 * s.pitch_base
        tone = sine_wave(freq, 0.15, 0.5)
        tone2 = sine_wave(freq * 2.3, 0.1, 0.2)

        wave = mix(tone, tone2[:len(tone)])
        wave = apply_exponential_decay(wave, 15)

        # Wood crack
        crack = noise_white(0.02, 0.3)
        crack = bandpass_filter(crack, 500, 2000)
        wave[:len(crack)] += crack

    elif material == "stone":
        # Heavy crunch
        noise = noise_white(0.2, 0.6)
        noise = lowpass(noise, 800)

        tone = sine_wave(80 * s.pitch_base, 0.15, 0.4)

        wave = mix(noise, tone)
        wave = apply_exponential_decay(wave, 10)

    else:  # flesh
        # Muffled impact
        noise = noise_white(0.1, 0.5)
        noise = lowpass(noise, 600)

        tone = sine_wave(100 * s.pitch_base, 0.1, 0.4)

        wave = mix(noise, tone)
        wave = apply_adsr(wave, ADSREnvelope(0.002, 0.03, 0.2, 0.05))

    return wave


def generate_crunch(
    style: ImpactStyleParams = None,
    intensity: float = 0.5,
) -> "np.ndarray":
    """
    Generate crunch/crush sound.

    Args:
        style: Impact style parameters
        intensity: 0-1 intensity
    """
    _require_numpy()
    from ...lib.synthesis import (
        noise_white, apply_adsr, apply_exponential_decay,
        ADSREnvelope, lowpass, SAMPLE_RATE
    )

    s = style or ImpactStyleParams()
    duration = 0.15 + intensity * 0.15

    wave = noise_white(duration, 0.5 + intensity * 0.3)
    wave = lowpass(wave, 1500 + s.brightness * 2000)

    # Add some grittiness
    for i in range(3):
        t = np.random.random() * duration * 0.8
        start = int(t * SAMPLE_RATE)
        burst = noise_white(0.02, 0.4)
        end = min(start + len(burst), len(wave))
        wave[start:end] += burst[:end - start]

    wave = apply_adsr(wave, ADSREnvelope(0.001, 0.03, 0.3, 0.08))

    return wave


def generate_shatter(
    style: ImpactStyleParams = None,
    material: str = "glass",
) -> "np.ndarray":
    """
    Generate shatter/break sound.

    Args:
        style: Impact style parameters
        material: "glass", "ice", "crystal"
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, noise_white, apply_adsr, apply_exponential_decay,
        ADSREnvelope, highpass, lowpass, SAMPLE_RATE, add_reverb
    )

    s = style or ImpactStyleParams()
    duration = 0.4

    if material == "glass":
        # High-pitched shards
        wave = noise_white(duration, 0.5)
        wave = highpass(wave, 3000 + s.brightness * 2000)

        # Add tinkling
        for i in range(5):
            freq = 2000 + np.random.random() * 4000
            tone = sine_wave(freq, 0.1 + np.random.random() * 0.1, 0.2)
            tone = apply_exponential_decay(tone, 20)
            start = int(np.random.random() * 0.2 * SAMPLE_RATE)
            end = min(start + len(tone), len(wave))
            wave[start:end] += tone[:end - start]

    elif material == "ice":
        # Cracking ice
        wave = noise_white(duration, 0.5)
        wave = highpass(wave, 2000)

        # Lower crack
        crack = noise_white(0.1, 0.4)
        crack = lowpass(crack, 1500)
        wave[:len(crack)] += crack

    else:  # crystal
        # Resonant shatter
        wave = np.zeros(int(SAMPLE_RATE * duration))
        base_freqs = [1200, 1800, 2400, 3200]

        for freq in base_freqs:
            freq *= s.pitch_base * (0.9 + np.random.random() * 0.2)
            tone = sine_wave(freq, 0.25, 0.2)
            tone = apply_exponential_decay(tone, 10)
            start = int(np.random.random() * 0.1 * SAMPLE_RATE)
            end = min(start + len(tone), len(wave))
            wave[start:end] += tone[:end - start]

        # Add noise
        noise = noise_white(duration * 0.7, 0.3)
        noise = highpass(noise, 2500)
        wave[:len(noise)] += noise

    wave = apply_adsr(wave, ADSREnvelope(0.001, 0.05, 0.2, 0.2))

    if s.reverb_amount > 0:
        wave = add_reverb(wave, s.reverb_amount, 50)

    return wave
