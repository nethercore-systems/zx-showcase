#!/usr/bin/env python3
"""Generate whale call sound effect.

Output: ../../generated/sounds/whale.wav

Main whale call - low fundamental with harmonics and warble.
Duration: 5 seconds.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from audio_utils import sine_wave, mix, envelope, add_reverb, write_wav, SAMPLE_RATE

ASSET_NAME = "whale"


def generate():
    """Generate whale call sound."""
    duration = 5
    fundamental = 60  # Hz

    # Fundamental
    main = sine_wave(fundamental, duration, amplitude=0.5)

    # Harmonics
    h2 = sine_wave(fundamental * 2, duration, amplitude=0.25)
    h3 = sine_wave(fundamental * 3, duration, amplitude=0.12)
    h5 = sine_wave(fundamental * 5, duration, amplitude=0.06)

    output = mix([main, h2, h3, h5])

    # Slow pitch modulation (characteristic whale "warble")
    for i in range(len(output)):
        t = i / SAMPLE_RATE
        mod = 1.0 + 0.02 * math.sin(2 * math.pi * 0.5 * t)
        output[i] *= mod

    # ADSR envelope
    output = envelope(output, 0.5, 0.3, 0.6, 1.5)

    # Reverb
    output = add_reverb(output, decay=0.5, delay_ms=100)

    write_wav(f"{ASSET_NAME}.wav", output)


if __name__ == "__main__":
    generate()
