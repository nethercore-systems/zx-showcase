#!/usr/bin/env python3
"""Generate Zone 3 ambient audio.

Output: ../../generated/sounds/ambient_midnight.wav

Zone 3 (Midnight Abyss): Sub-bass pressure, isolation, bioluminescent pings.
Duration: 120 seconds.
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from audio_utils import (
    noise, sine_wave, lowpass_filter, envelope,
    mix, add_reverb, write_wav, SAMPLE_RATE
)

ASSET_NAME = "ambient_midnight"


def generate():
    """Generate Zone 3 ambient sound."""
    duration = 120

    # Sub-bass pressure drone
    drone = sine_wave(35, duration, amplitude=0.4)
    # Very slow modulation
    for i in range(len(drone)):
        t = i / SAMPLE_RATE
        drone[i] *= 0.6 + 0.4 * math.sin(2 * math.pi * 0.02 * t)

    # Near-silence base (very quiet)
    base = noise(duration, amplitude=0.05)
    base = lowpass_filter(base, 500)

    # Rare bioluminescent pings
    pings = [0.0] * int(duration * SAMPLE_RATE)
    t = 10
    while t < duration - 3:
        ping_freq = random.uniform(1500, 3000)
        ping_dur = random.uniform(0.5, 1.5)
        ping = sine_wave(ping_freq, ping_dur, amplitude=0.15)
        ping = envelope(ping, 0.01, 0.05, 0.2, ping_dur * 0.7)
        ping = add_reverb(ping, decay=0.6, delay_ms=150)

        start = int(t * SAMPLE_RATE)
        for i, p in enumerate(ping):
            if start + i < len(pings):
                pings[start + i] += p

        t += random.uniform(15, 35)  # Rare

    # Mix
    output = mix([drone, base, pings], [0.6, 0.2, 0.25])
    output = lowpass_filter(output, 2000)  # Heavy filtering
    output = add_reverb(output, decay=0.6, delay_ms=200)  # Massive reverb

    write_wav(f"{ASSET_NAME}.wav", output)


if __name__ == "__main__":
    generate()
