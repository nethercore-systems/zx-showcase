#!/usr/bin/env python3
"""Generate sprint footstep sound effect.

Output: ../../generated/sounds/footstep_sprint.wav

Faster, sharper footstep for sprinting.
"""
import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated" / "sounds"
ASSET_NAME = "footstep_sprint"
SAMPLE_RATE = 22050


def generate_tone(freq: float, duration: float) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    return np.sin(2 * np.pi * freq * t)


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
    """Generate sprint footstep sound."""
    tone = generate_tone(100, 0.08)
    noise = generate_noise(0.04) * 0.4
    signal = tone[:len(noise)] + noise
    signal = apply_envelope(signal, attack=0.001, release=0.05)
    save_wav(signal)


if __name__ == "__main__":
    generate()
