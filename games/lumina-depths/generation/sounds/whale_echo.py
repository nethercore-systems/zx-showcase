#!/usr/bin/env python3
"""Generate distant whale echo sound effect.

Output: ../../generated/sounds/whale_echo.wav

Distant whale call with heavy reverb and filtering.
Duration: 8 seconds.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from audio_utils import (
    sine_wave, mix, envelope, add_reverb, lowpass_filter,
    write_wav, SAMPLE_RATE
)

ASSET_NAME = "whale_echo"


def generate():
    """Generate distant whale echo sound."""
    duration = 8
    fundamental = 80  # Slightly higher (different whale)

    # Base call
    main = sine_wave(fundamental, duration * 0.6, amplitude=0.3)

    # Harmonics (fewer, more filtered)
    h2 = sine_wave(fundamental * 2, duration * 0.6, amplitude=0.15)
    h3 = sine_wave(fundamental * 3, duration * 0.6, amplitude=0.05)

    call = mix([main, h2, h3])
    call = envelope(call, 0.8, 0.5, 0.4, 1.0)

    # Heavy lowpass (distant)
    call = lowpass_filter(call, 600)

    # Pad to full duration
    call = call + [0.0] * (int(duration * SAMPLE_RATE) - len(call))

    # Multiple reverb passes for cathedral effect
    call = add_reverb(call, decay=0.6, delay_ms=150)
    call = add_reverb(call, decay=0.4, delay_ms=300)
    call = add_reverb(call, decay=0.3, delay_ms=500)

    write_wav(f"{ASSET_NAME}.wav", call)


if __name__ == "__main__":
    generate()
