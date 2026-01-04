#!/usr/bin/env python3
"""Generate Zone 2 ambient audio.

Output: ../../generated/sounds/ambient_twilight.wav

Zone 2 (Twilight Realm): Mysterious, whale echoes, darker.
Duration: 90 seconds.
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from audio_utils import (
    noise, sine_wave, highpass_filter, lowpass_filter, envelope,
    mix, add_reverb, write_wav, SAMPLE_RATE
)

ASSET_NAME = "ambient_twilight"


def generate():
    """Generate Zone 2 ambient sound."""
    duration = 90

    # Darker base (more lowpass)
    base = noise(duration, amplitude=0.25)
    base = lowpass_filter(base, 2000)
    base = highpass_filter(base, 50)

    # Pressure drone (low sine)
    drone = sine_wave(55, duration, amplitude=0.3)
    # Add slow modulation
    for i in range(len(drone)):
        t = i / SAMPLE_RATE
        drone[i] *= 0.7 + 0.3 * math.sin(2 * math.pi * 0.05 * t)

    # Distant whale echoes (every 20-30s)
    whales = [0.0] * int(duration * SAMPLE_RATE)
    t = 15
    while t < duration - 5:
        whale_dur = random.uniform(1.5, 3.0)
        whale_freq = random.uniform(80, 150)
        whale = sine_wave(whale_freq, whale_dur, amplitude=0.15)

        for harm in [2, 3, 5]:
            harm_wave = sine_wave(whale_freq * harm, whale_dur, amplitude=0.05 / harm)
            whale = mix([whale, harm_wave])

        whale = envelope(whale, 0.3, 0.2, 0.4, whale_dur * 0.4)
        whale = lowpass_filter(whale, 800)
        whale = add_reverb(whale, decay=0.5, delay_ms=100)

        start = int(t * SAMPLE_RATE)
        for i, w in enumerate(whale):
            if start + i < len(whales):
                whales[start + i] += w

        t += random.uniform(18, 28)

    # Marine snow tinkle
    snow = noise(duration, amplitude=0.05)
    snow = highpass_filter(snow, 3000)
    snow = lowpass_filter(snow, 8000)

    # Mix with heavy reverb
    output = mix([base, drone, whales, snow], [0.35, 0.4, 0.5, 0.15])
    output = add_reverb(output, decay=0.4, delay_ms=80)

    write_wav(f"{ASSET_NAME}.wav", output)


if __name__ == "__main__":
    generate()
