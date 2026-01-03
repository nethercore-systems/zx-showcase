#!/usr/bin/env python3
"""Generate audio for Override.

SFX:
- footstep, footstep_sprint
- door_open, door_close, door_locked
- trap_spike, trap_gas, trap_laser
- core_pickup, drone_hover, drone_spawn
- runner_death, alarm, extraction_open
- lights_off, timer_warning

All using numpy/scipy synthesis.
"""

import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path


def generate_tone(freq: float, duration: float, sample_rate: int = 22050) -> np.ndarray:
    """Generate a simple sine wave tone."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    return np.sin(2 * np.pi * freq * t)


def generate_noise(duration: float, sample_rate: int = 22050) -> np.ndarray:
    """Generate white noise."""
    return np.random.uniform(-1, 1, int(sample_rate * duration))


def apply_envelope(signal: np.ndarray, attack: float = 0.01, release: float = 0.1, sample_rate: int = 22050) -> np.ndarray:
    """Apply ADSR envelope to signal."""
    length = len(signal)
    envelope = np.ones(length)

    # Attack
    attack_samples = int(attack * sample_rate)
    if attack_samples > 0 and attack_samples < length:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Release
    release_samples = int(release * sample_rate)
    if release_samples > 0 and release_samples < length:
        envelope[-release_samples:] = np.linspace(1, 0, release_samples)

    return signal * envelope


def save_wav(filename: str, signal: np.ndarray, sample_rate: int = 22050):
    """Save signal as WAV file."""
    output_dir = Path(__file__).parent.parent.parent / "generated" / "sounds"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Normalize and convert to int16
    signal = np.clip(signal, -1, 1)
    signal = (signal * 32767).astype(np.int16)

    filepath = output_dir / filename
    wavfile.write(filepath, sample_rate, signal)
    print(f"  OK {filename}")


def generate_footstep():
    """Low thud for footstep."""
    tone = generate_tone(80, 0.1)
    noise = generate_noise(0.05) * 0.3
    signal = tone[:len(noise)] + noise
    signal = apply_envelope(signal, attack=0.001, release=0.08)
    save_wav("footstep.wav", signal)


def generate_footstep_sprint():
    """Faster, sharper footstep."""
    tone = generate_tone(100, 0.08)
    noise = generate_noise(0.04) * 0.4
    signal = tone[:len(noise)] + noise
    signal = apply_envelope(signal, attack=0.001, release=0.05)
    save_wav("footstep_sprint.wav", signal)


def generate_door_open():
    """Mechanical sliding door open."""
    # Sweep from low to mid
    duration = 0.4
    t = np.linspace(0, duration, int(22050 * duration))
    freq = np.linspace(200, 400, len(t))
    signal = np.sin(2 * np.pi * freq * t)
    noise = generate_noise(duration) * 0.2
    signal = signal + noise[:len(signal)]
    signal = apply_envelope(signal, attack=0.01, release=0.1)
    save_wav("door_open.wav", signal)


def generate_door_close():
    """Mechanical sliding door close."""
    # Sweep from mid to low
    duration = 0.4
    t = np.linspace(0, duration, int(22050 * duration))
    freq = np.linspace(400, 200, len(t))
    signal = np.sin(2 * np.pi * freq * t)
    noise = generate_noise(duration) * 0.2
    signal = signal + noise[:len(signal)]
    signal = apply_envelope(signal, attack=0.01, release=0.1)
    save_wav("door_close.wav", signal)


def generate_door_locked():
    """Denied - harsh buzz."""
    tone1 = generate_tone(100, 0.2)
    tone2 = generate_tone(150, 0.2)
    signal = (tone1 + tone2) * 0.5
    signal = apply_envelope(signal, attack=0.01, release=0.05)
    save_wav("door_locked.wav", signal)


def generate_trap_spike():
    """Sharp metallic stab."""
    tone = generate_tone(800, 0.15)
    noise = generate_noise(0.15) * 0.5
    signal = tone + noise
    signal = apply_envelope(signal, attack=0.001, release=0.1)
    save_wav("trap_spike.wav", signal)


def generate_drone_hover():
    """Constant mechanical hum."""
    tone1 = generate_tone(120, 0.5)
    tone2 = generate_tone(180, 0.5)
    signal = (tone1 + tone2) * 0.5
    signal = apply_envelope(signal, attack=0.05, release=0.05)
    save_wav("drone_hover.wav", signal)


def generate_alarm():
    """Warning siren."""
    duration = 1.0
    t = np.linspace(0, duration, int(22050 * duration))
    # Oscillating frequency
    freq = 400 + 200 * np.sin(2 * np.pi * 2 * t)
    signal = np.sin(2 * np.pi * freq * t)
    signal = apply_envelope(signal, attack=0.05, release=0.05)
    save_wav("alarm.wav", signal)


def generate_core_pickup():
    """Positive chime."""
    tone1 = generate_tone(800, 0.3)
    tone2 = generate_tone(1000, 0.3)
    tone3 = generate_tone(1200, 0.3)
    signal = (tone1 + tone2 + tone3) / 3
    signal = apply_envelope(signal, attack=0.01, release=0.2)
    save_wav("core_pickup.wav", signal)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("OVERRIDE - Audio Generation")
    print("="*60 + "\n")

    print("Footsteps:")
    generate_footstep()
    generate_footstep_sprint()

    print("\nDoors:")
    generate_door_open()
    generate_door_close()
    generate_door_locked()

    print("\nTraps:")
    generate_trap_spike()

    print("\nDrone:")
    generate_drone_hover()

    print("\nGameplay:")
    generate_core_pickup()
    generate_alarm()

    print("\n" + "="*60)
    print("All audio generated successfully!")
    print("="*60)
