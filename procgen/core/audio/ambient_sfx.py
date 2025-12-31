"""
Ambient sound effect generators.

Provides drones, environmental sounds, and atmospheric textures.
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
class AmbientStyleParams:
    """Style parameters for ambient sounds."""
    warmth: float = 0.5        # 0=cold/synthetic, 1=warm/organic
    movement: float = 0.3      # 0=static, 1=evolving
    density: float = 0.5       # 0=sparse, 1=dense
    pitch_base: float = 1.0


def _require_numpy():
    if not HAS_NUMPY:
        raise ImportError("numpy is required for audio synthesis")


def generate_hum(
    style: AmbientStyleParams = None,
    duration: float = 2.0,
    frequency: float = 60.0,
) -> "np.ndarray":
    """
    Generate electrical/mechanical hum.

    Args:
        style: Ambient style parameters
        duration: Sound duration in seconds
        frequency: Base frequency (60 or 50 Hz typical)
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, apply_adsr, ADSREnvelope, lowpass, SAMPLE_RATE
    )

    s = style or AmbientStyleParams()
    freq = frequency * s.pitch_base

    # Fundamental + harmonics
    wave = sine_wave(freq, duration, 0.4)
    wave += sine_wave(freq * 2, duration, 0.2)
    wave += sine_wave(freq * 3, duration, 0.1)

    # Add slight warble for movement
    if s.movement > 0:
        samples = int(SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, False)
        modulation = 1 + 0.03 * s.movement * np.sin(2 * np.pi * 0.5 * t)
        wave = wave * modulation

    wave = lowpass(wave, 500 + s.warmth * 500)
    wave = apply_adsr(wave, ADSREnvelope(0.1, 0.2, 0.8, 0.2))

    return wave


def generate_drone(
    style: AmbientStyleParams = None,
    duration: float = 4.0,
    base_freq: float = 55.0,
    layers: int = 3,
) -> "np.ndarray":
    """
    Generate atmospheric drone.

    Args:
        style: Ambient style parameters
        duration: Sound duration
        base_freq: Base frequency (A1 = 55 Hz typical)
        layers: Number of harmonic layers
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, sawtooth_wave, apply_adsr, ADSREnvelope,
        lowpass, add_chorus, SAMPLE_RATE
    )

    s = style or AmbientStyleParams()
    samples = int(SAMPLE_RATE * duration)
    wave = np.zeros(samples)

    freq = base_freq * s.pitch_base

    # Layer detuned oscillators
    detune_cents = [0, -8, 8, -15, 15]
    for i in range(min(layers, len(detune_cents))):
        detune = 2 ** (detune_cents[i] / 1200)
        layer_freq = freq * detune

        if s.warmth > 0.5:
            # Warm sine layers
            layer = sine_wave(layer_freq, duration, 0.3 / (i + 1))
        else:
            # Colder sawtooth layers
            layer = sawtooth_wave(layer_freq, duration, 0.2 / (i + 1))

        wave[:len(layer)] += layer

    # Add octave
    octave = sine_wave(freq * 2, duration, 0.15)
    wave[:len(octave)] += octave

    # Filter and shape
    cutoff = 400 + s.warmth * 600
    wave = lowpass(wave, cutoff)

    if s.movement > 0.3:
        wave = add_chorus(wave, depth_ms=8 * s.movement, rate_hz=0.3, mix=0.4)

    wave = apply_adsr(wave, ADSREnvelope(0.3, 0.5, 0.7, 0.5))

    return wave


def generate_wind(
    style: AmbientStyleParams = None,
    duration: float = 3.0,
    intensity: float = 0.5,
) -> "np.ndarray":
    """
    Generate wind sound.

    Args:
        style: Ambient style parameters
        duration: Sound duration
        intensity: Wind intensity (0=breeze, 1=gale)
    """
    _require_numpy()
    from ...lib.synthesis import (
        noise_white, noise_pink, apply_adsr, ADSREnvelope,
        lowpass, highpass, SAMPLE_RATE
    )

    s = style or AmbientStyleParams()
    samples = int(SAMPLE_RATE * duration)

    # Pink noise is good for wind
    wave = noise_pink(duration, 0.4 + intensity * 0.3)

    # Modulate for gusts
    if s.movement > 0.2:
        t = np.linspace(0, duration, samples, False)
        # Multiple overlapping gusts
        gust1 = 0.5 + 0.5 * np.sin(2 * np.pi * 0.15 * t)
        gust2 = 0.5 + 0.5 * np.sin(2 * np.pi * 0.23 * t + 1.5)
        gust3 = 0.5 + 0.5 * np.sin(2 * np.pi * 0.08 * t + 0.7)
        modulation = (gust1 + gust2 + gust3) / 3
        modulation = 0.3 + 0.7 * modulation * s.movement
        wave = wave * modulation

    # Filter based on intensity
    low_cut = 100 + intensity * 200
    high_cut = 2000 + intensity * 3000
    wave = highpass(wave, low_cut)
    wave = lowpass(wave, high_cut)

    wave = apply_adsr(wave, ADSREnvelope(0.2, 0.3, 0.8, 0.3))

    return wave


def generate_water(
    style: AmbientStyleParams = None,
    duration: float = 3.0,
    water_type: str = "stream",
) -> "np.ndarray":
    """
    Generate water sound.

    Args:
        style: Ambient style parameters
        duration: Sound duration
        water_type: "stream", "rain", "underwater", "drip"
    """
    _require_numpy()
    from ...lib.synthesis import (
        noise_white, noise_pink, sine_wave, apply_adsr, ADSREnvelope,
        lowpass, highpass, bandpass, SAMPLE_RATE
    )

    s = style or AmbientStyleParams()
    samples = int(SAMPLE_RATE * duration)

    if water_type == "stream":
        # Continuous flowing
        wave = noise_white(duration, 0.4)
        wave = lowpass(wave, 3000)
        wave = highpass(wave, 200)

        # Modulate for flow variation
        t = np.linspace(0, duration, samples, False)
        flow = 0.7 + 0.3 * np.sin(2 * np.pi * 0.5 * t)
        wave = wave * flow

    elif water_type == "rain":
        # Patter of drops
        wave = np.zeros(samples)

        # Base wash
        wash = noise_pink(duration, 0.25)
        wash = lowpass(wash, 4000)
        wave[:len(wash)] = wash

        # Individual drops
        drop_count = int(s.density * 50 * duration)
        for _ in range(drop_count):
            t = np.random.random() * duration
            start = int(t * SAMPLE_RATE)

            drop = noise_white(0.02, 0.3 * np.random.random())
            drop = highpass(drop, 2000)
            drop = apply_adsr(drop, ADSREnvelope(0.001, 0.005, 0.1, 0.01))

            end = min(start + len(drop), len(wave))
            wave[start:end] += drop[:end - start]

    elif water_type == "underwater":
        # Muffled, submerged
        wave = noise_pink(duration, 0.4)
        wave = lowpass(wave, 400 + s.warmth * 200)

        # Add bubbles
        if s.movement > 0.2:
            bubble_count = int(s.movement * 10 * duration)
            for _ in range(bubble_count):
                t_start = np.random.random() * duration
                start = int(t_start * SAMPLE_RATE)
                freq = 300 + np.random.random() * 500

                bubble = sine_wave(freq, 0.1, 0.2)
                bubble = apply_adsr(bubble, ADSREnvelope(0.01, 0.03, 0.3, 0.05))

                end = min(start + len(bubble), len(wave))
                wave[start:end] += bubble[:end - start]

    else:  # drip
        # Periodic drips
        wave = np.zeros(samples)
        drip_interval = 0.5 + (1 - s.density) * 0.5

        t = 0
        while t < duration:
            start = int(t * SAMPLE_RATE)
            freq = 800 + np.random.random() * 400

            drip = sine_wave(freq, 0.08, 0.4)
            drip = apply_adsr(drip, ADSREnvelope(0.001, 0.02, 0.2, 0.05))

            end = min(start + len(drip), len(wave))
            wave[start:end] += drip[:end - start]

            t += drip_interval * (0.8 + np.random.random() * 0.4)

    wave = apply_adsr(wave, ADSREnvelope(0.15, 0.2, 0.8, 0.2))

    return wave


def generate_machinery(
    style: AmbientStyleParams = None,
    duration: float = 3.0,
    machine_type: str = "engine",
) -> "np.ndarray":
    """
    Generate machinery sound.

    Args:
        style: Ambient style parameters
        duration: Sound duration
        machine_type: "engine", "motor", "servo", "factory"
    """
    _require_numpy()
    from ...lib.synthesis import (
        sine_wave, square_wave, noise_white, apply_adsr, ADSREnvelope,
        lowpass, SAMPLE_RATE
    )

    s = style or AmbientStyleParams()
    samples = int(SAMPLE_RATE * duration)

    if machine_type == "engine":
        # Low rumble with rhythm
        freq = 40 * s.pitch_base
        t = np.linspace(0, duration, samples, False)

        # Engine pulse
        pulse_rate = 15  # Hz
        pulse = 0.7 + 0.3 * np.sin(2 * np.pi * pulse_rate * t)

        wave = sine_wave(freq, duration, 0.5) * pulse
        wave += sine_wave(freq * 2, duration, 0.25) * pulse
        wave += noise_white(duration, 0.15)[:samples]

        wave = lowpass(wave, 300)

    elif machine_type == "motor":
        # Higher pitched whine
        freq = 200 * s.pitch_base
        wave = sine_wave(freq, duration, 0.4)
        wave += sine_wave(freq * 1.5, duration, 0.2)

        # Add wobble
        t = np.linspace(0, duration, samples, False)
        wobble = 1 + 0.05 * s.movement * np.sin(2 * np.pi * 3 * t)
        wave = wave * wobble

    elif machine_type == "servo":
        # Intermittent mechanical
        wave = np.zeros(samples)
        interval = 0.4 + (1 - s.movement) * 0.4

        t = 0
        while t < duration:
            start = int(t * SAMPLE_RATE)
            freq = 300 + np.random.random() * 200

            servo = square_wave(freq, 0.15, 0.3)
            servo = lowpass(servo, 1500)
            servo = apply_adsr(servo, ADSREnvelope(0.01, 0.02, 0.3, 0.05))

            end = min(start + len(servo), len(wave))
            wave[start:end] += servo[:end - start]

            t += interval * (0.8 + np.random.random() * 0.4)

    else:  # factory
        # Dense mechanical ambient
        wave = noise_white(duration, 0.3)
        wave = lowpass(wave, 2000)

        # Add rhythmic elements
        t = np.linspace(0, duration, samples, False)
        rhythm = 0.7 + 0.3 * np.sin(2 * np.pi * 2 * t)
        wave = wave * rhythm

        # Tonal element
        tone = sine_wave(80 * s.pitch_base, duration, 0.3)
        wave[:len(tone)] += tone

    wave = apply_adsr(wave, ADSREnvelope(0.2, 0.3, 0.8, 0.3))

    return wave
