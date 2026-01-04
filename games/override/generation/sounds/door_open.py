#!/usr/bin/env python3
"""Generate door open sound effect.

Output: ../../generated/sounds/door_open.wav

Mechanical sliding door opening. Sweep from low to mid frequency.
"""
import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated" / "sounds"
ASSET_NAME = "door_open"
SAMPLE_RATE = 22050


def generate_noise(duration: float) -> np.ndarray:
    return np.random.uniform(-1, 1, int(SAMPLE_RATE * duration))


def apply_envelope(signal: np.ndarray, attack: float = 0.01, release: float = 0.1) -> np.ndarray:
    length = len(signal)
    envelope = np.ones(length)
    attack_samples = int(attack * SAMPLE_RATE)
    if attack_samples > 0 and attack_samples < length:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    release_samples = int(release * SAMPLE_RATE)
    if release_samples > 0 and release_samples < length:
        envelope[-release_samples:] = np.linspace(1, 0, release_samples)
    return signal * envelope


def save_wav(signal: np.ndarray):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    signal = np.clip(signal, -1, 1)
    signal = (signal * 32767).astype(np.int16)
    filepath = OUTPUT_DIR / f"{ASSET_NAME}.wav"
    wavfile.write(filepath, SAMPLE_RATE, signal)
    print(f"Generated: {filepath}")


def generate():
    """Generate door open sound."""
    duration = 0.4
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    freq = np.linspace(200, 400, len(t))
    signal = np.sin(2 * np.pi * freq * t)
    noise = generate_noise(duration) * 0.2
    signal = signal + noise[:len(signal)]
    signal = apply_envelope(signal, attack=0.01, release=0.1)
    save_wav(signal)


if __name__ == "__main__":
    generate()
