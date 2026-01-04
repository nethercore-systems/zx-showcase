"""Shared audio synthesis utilities for Lumina Depths.

Pure Python audio generation using wave module.
"""
import math
import random
import struct
import wave
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated" / "sounds"
SAMPLE_RATE = 44100


def write_wav(filename, samples, sample_rate=SAMPLE_RATE):
    """Write samples to WAV file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / filename

    # Normalize to 16-bit range
    max_val = max(abs(min(samples)), abs(max(samples))) if samples else 1
    if max_val > 0:
        samples = [int(s / max_val * 32767 * 0.9) for s in samples]

    with wave.open(str(filepath), 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(struct.pack(f'{len(samples)}h', *samples))

    print(f"Generated: {filepath}")
    print(f"  Duration: {len(samples) / sample_rate:.1f}s")
    return filepath


def sine_wave(freq, duration, sample_rate=SAMPLE_RATE, amplitude=1.0):
    """Generate sine wave."""
    samples = []
    for i in range(int(duration * sample_rate)):
        t = i / sample_rate
        samples.append(amplitude * math.sin(2 * math.pi * freq * t))
    return samples


def noise(duration, sample_rate=SAMPLE_RATE, amplitude=1.0):
    """Generate white noise."""
    return [amplitude * (random.random() * 2 - 1) for _ in range(int(duration * sample_rate))]


def lowpass_filter(samples, cutoff, sample_rate=SAMPLE_RATE):
    """Simple one-pole lowpass filter."""
    rc = 1.0 / (2 * math.pi * cutoff)
    dt = 1.0 / sample_rate
    alpha = dt / (rc + dt)

    filtered = []
    prev = 0
    for s in samples:
        prev = prev + alpha * (s - prev)
        filtered.append(prev)
    return filtered


def highpass_filter(samples, cutoff, sample_rate=SAMPLE_RATE):
    """Simple one-pole highpass filter."""
    rc = 1.0 / (2 * math.pi * cutoff)
    dt = 1.0 / sample_rate
    alpha = rc / (rc + dt)

    filtered = []
    prev_in = 0
    prev_out = 0
    for s in samples:
        prev_out = alpha * (prev_out + s - prev_in)
        prev_in = s
        filtered.append(prev_out)
    return filtered


def add_reverb(samples, decay=0.3, delay_ms=50, sample_rate=SAMPLE_RATE):
    """Simple comb filter reverb."""
    delay_samples = int(delay_ms * sample_rate / 1000)
    output = samples.copy()

    for i in range(delay_samples, len(output)):
        output[i] += output[i - delay_samples] * decay

    return output


def envelope(samples, attack, decay, sustain, release, sample_rate=SAMPLE_RATE):
    """Apply ADSR envelope."""
    total = len(samples)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = total - attack_samples - decay_samples - release_samples

    output = []
    for i, s in enumerate(samples):
        if i < attack_samples:
            env = i / attack_samples
        elif i < attack_samples + decay_samples:
            env = 1.0 - (1.0 - sustain) * (i - attack_samples) / decay_samples
        elif i < attack_samples + decay_samples + sustain_samples:
            env = sustain
        else:
            env = sustain * (1.0 - (i - attack_samples - decay_samples - sustain_samples) / release_samples)
        output.append(s * max(0, env))
    return output


def mix(samples_list, volumes=None):
    """Mix multiple sample arrays."""
    if volumes is None:
        volumes = [1.0] * len(samples_list)

    max_len = max(len(s) for s in samples_list)
    output = [0.0] * max_len

    for samples, vol in zip(samples_list, volumes):
        for i, s in enumerate(samples):
            output[i] += s * vol

    return output


def generate_bubbles(duration, density=5, sample_rate=SAMPLE_RATE):
    """Generate bubble sounds."""
    samples = [0.0] * int(duration * sample_rate)

    num_bubbles = int(duration * density)
    for _ in range(num_bubbles):
        start = random.randint(0, len(samples) - int(0.2 * sample_rate))
        freq = random.uniform(800, 2500)
        bubble_dur = random.uniform(0.02, 0.1)
        amp = random.uniform(0.1, 0.4)

        bubble = sine_wave(freq, bubble_dur, amplitude=amp)
        bubble = envelope(bubble, 0.005, 0.01, 0.3, bubble_dur * 0.6)

        for i in range(len(bubble)):
            t = i / sample_rate
            sweep = 1 + t * 2
            bubble[i] *= math.sin(2 * math.pi * freq * sweep * t) / (amp + 0.1)

        for i, b in enumerate(bubble):
            if start + i < len(samples):
                samples[start + i] += b

    return samples
