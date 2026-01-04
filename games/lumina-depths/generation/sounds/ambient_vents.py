#!/usr/bin/env python3
"""Generate Zone 4 ambient audio.

Output: ../../generated/sounds/ambient_vents.wav

Zone 4 (Hydrothermal Vents): Volcanic rumble, hissing, metallic.
Duration: 90 seconds.
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from audio_utils import (
    noise, sine_wave, highpass_filter, lowpass_filter, envelope,
    generate_bubbles, mix, add_reverb, write_wav, SAMPLE_RATE
)

ASSET_NAME = "ambient_vents"


def generate():
    """Generate Zone 4 ambient sound."""
    duration = 90

    # Volcanic rumble (low noise)
    rumble = noise(duration, amplitude=0.4)
    rumble = lowpass_filter(rumble, 150)
    # Modulate intensity
    for i in range(len(rumble)):
        t = i / SAMPLE_RATE
        rumble[i] *= 0.5 + 0.5 * abs(math.sin(2 * math.pi * 0.1 * t))

    # Hissing vents (periodic)
    hiss = [0.0] * int(duration * SAMPLE_RATE)
    t = 3
    while t < duration - 2:
        hiss_dur = random.uniform(0.5, 2.0)
        h = noise(hiss_dur, amplitude=0.3)
        h = highpass_filter(h, 800)
        h = lowpass_filter(h, 4000)
        h = envelope(h, 0.1, 0.1, 0.6, 0.2)

        start = int(t * SAMPLE_RATE)
        for i, s in enumerate(h):
            if start + i < len(hiss):
                hiss[start + i] += s

        t += random.uniform(5, 12)

    # Metallic pings
    pings = [0.0] * int(duration * SAMPLE_RATE)
    t = 5
    while t < duration - 1:
        freq = random.uniform(400, 1200)
        p = sine_wave(freq, 0.2, amplitude=0.2)
        # Make it metallic with inharmonic partials
        for harm in [1.5, 2.5, 3.7]:
            p = mix([p, sine_wave(freq * harm, 0.2, amplitude=0.08)])
        p = envelope(p, 0.005, 0.02, 0.1, 0.15)

        start = int(t * SAMPLE_RATE)
        for i, s in enumerate(p):
            if start + i < len(pings):
                pings[start + i] += s

        t += random.uniform(4, 10)

    # Bubble columns (distant)
    bubbles = generate_bubbles(duration, density=2)
    bubbles = lowpass_filter(bubbles, 1500)

    # Mix
    output = mix([rumble, hiss, pings, bubbles], [0.5, 0.35, 0.2, 0.15])
    output = add_reverb(output, decay=0.3, delay_ms=40)

    write_wav(f"{ASSET_NAME}.wav", output)


if __name__ == "__main__":
    generate()
