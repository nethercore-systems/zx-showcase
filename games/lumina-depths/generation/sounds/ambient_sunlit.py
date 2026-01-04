#!/usr/bin/env python3
"""Generate Zone 1 ambient audio.

Output: ../../generated/sounds/ambient_sunlit.wav

Zone 1 (Sunlit Waters): Bright, active, bubbles, fish activity.
Duration: 60 seconds.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from audio_utils import (
    noise, highpass_filter, lowpass_filter, envelope,
    generate_bubbles, mix, add_reverb, write_wav, SAMPLE_RATE
)

ASSET_NAME = "ambient_sunlit"


def generate():
    """Generate Zone 1 ambient sound."""
    duration = 60

    # Base water movement (bright filtered noise)
    base = noise(duration, amplitude=0.3)
    base = highpass_filter(base, 200)
    base = lowpass_filter(base, 6000)

    # Bubbles
    bubbles = generate_bubbles(duration, density=8)
    bubbles = lowpass_filter(bubbles, 4000)

    # Occasional fish swishes (short noise bursts)
    fish = [0.0] * int(duration * SAMPLE_RATE)
    for _ in range(int(duration / 3)):
        start = random.randint(0, len(fish) - int(0.3 * SAMPLE_RATE))
        swish = noise(0.15, amplitude=0.2)
        swish = highpass_filter(swish, 1000)
        swish = lowpass_filter(swish, 5000)
        swish = envelope(swish, 0.01, 0.02, 0.3, 0.1)
        for i, s in enumerate(swish):
            if start + i < len(fish):
                fish[start + i] += s

    # Mix
    output = mix([base, bubbles, fish], [0.4, 0.5, 0.3])
    output = add_reverb(output, decay=0.2, delay_ms=30)

    write_wav(f"{ASSET_NAME}.wav", output)


if __name__ == "__main__":
    generate()
