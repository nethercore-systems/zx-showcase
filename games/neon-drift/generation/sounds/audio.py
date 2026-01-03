#!/usr/bin/env python3
"""
Neon Drift - Audio Asset Generator

Generates all SFX using numpy/scipy synthesis.
Run with: python generate_neon_drift_audio.py

Output:
    games/neon-drift/assets/audio/*.wav
"""

import numpy as np
from pathlib import Path
from scipy.io import wavfile

# Audio parameters
SAMPLE_RATE = 22050


def generate_sine(freq: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
    """Generate a sine wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return amplitude * np.sin(2 * np.pi * freq * t)


def generate_square(freq: float, duration: float, amplitude: float = 0.3) -> np.ndarray:
    """Generate a square wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return amplitude * np.sign(np.sin(2 * np.pi * freq * t))


def generate_saw(freq: float, duration: float, amplitude: float = 0.3) -> np.ndarray:
    """Generate a sawtooth wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return amplitude * (2 * (freq * t % 1) - 1)


def generate_noise(duration: float, amplitude: float = 0.3) -> np.ndarray:
    """Generate white noise."""
    samples = int(SAMPLE_RATE * duration)
    return amplitude * (np.random.random(samples) * 2 - 1)


def apply_envelope(wave: np.ndarray, attack: float, decay: float, sustain: float, release: float) -> np.ndarray:
    """Apply ADSR envelope."""
    total = len(wave)
    a_samples = int(attack * SAMPLE_RATE)
    d_samples = int(decay * SAMPLE_RATE)
    r_samples = int(release * SAMPLE_RATE)
    s_samples = max(0, total - a_samples - d_samples - r_samples)

    envelope = np.zeros(total)

    # Attack
    if a_samples > 0:
        envelope[:a_samples] = np.linspace(0, 1, a_samples)

    # Decay
    d_start = a_samples
    d_end = d_start + d_samples
    if d_samples > 0 and d_end <= total:
        envelope[d_start:d_end] = np.linspace(1, sustain, d_samples)

    # Sustain
    s_start = d_end
    s_end = s_start + s_samples
    if s_samples > 0 and s_end <= total:
        envelope[s_start:s_end] = sustain

    # Release
    r_start = s_end
    if r_samples > 0 and r_start < total:
        envelope[r_start:] = np.linspace(sustain, 0, total - r_start)

    return wave * envelope


def lowpass_filter(wave: np.ndarray, cutoff: float) -> np.ndarray:
    """Simple lowpass filter using rolling average."""
    window_size = max(1, int(SAMPLE_RATE / cutoff / 4))
    return np.convolve(wave, np.ones(window_size)/window_size, mode='same')


def save_wav(filename: str, wave: np.ndarray, output_dir: Path):
    """Save wave to WAV file."""
    # Normalize and convert to 16-bit
    if np.max(np.abs(wave)) > 0:
        wave = wave / np.max(np.abs(wave))
    wave_int = (wave * 32767).astype(np.int16)
    wavfile.write(output_dir / filename, SAMPLE_RATE, wave_int)
    print(f"  {filename}")


# =============================================================================
# SFX GENERATORS
# =============================================================================

def generate_engine_idle() -> np.ndarray:
    """Low rumbling engine idle sound."""
    duration = 0.5

    # Base frequency with harmonics
    wave = generate_sine(60, duration, 0.4)
    wave += generate_sine(120, duration, 0.2)
    wave += generate_sine(180, duration, 0.1)

    # Add some rough texture
    wave += generate_noise(duration, 0.05)

    # Apply subtle pulsing
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    pulse = 0.8 + 0.2 * np.sin(2 * np.pi * 8 * t)
    wave *= pulse

    return lowpass_filter(wave, 400)


def generate_engine_rev() -> np.ndarray:
    """Engine revving up sound."""
    duration = 0.6

    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Frequency sweep from low to high
    freq_sweep = 80 + 200 * (t / duration) ** 0.7
    wave = 0.4 * np.sin(2 * np.pi * np.cumsum(freq_sweep) / SAMPLE_RATE)

    # Harmonics
    wave += 0.2 * np.sin(2 * np.pi * np.cumsum(freq_sweep * 2) / SAMPLE_RATE)
    wave += 0.1 * np.sin(2 * np.pi * np.cumsum(freq_sweep * 3) / SAMPLE_RATE)

    # Add texture
    wave += generate_noise(duration, 0.08)

    return apply_envelope(lowpass_filter(wave, 800), 0.05, 0.1, 0.8, 0.2)


def generate_boost() -> np.ndarray:
    """Boost activation - whoosh with synth accent."""
    duration = 0.4

    # Woosh noise
    noise = generate_noise(duration, 0.5)
    noise = apply_envelope(noise, 0.02, 0.1, 0.3, 0.2)

    # Synth accent (rising pitch)
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq_sweep = 400 + 800 * (t / duration)
    synth = 0.3 * np.sin(2 * np.pi * np.cumsum(freq_sweep) / SAMPLE_RATE)
    synth = apply_envelope(synth, 0.01, 0.15, 0.3, 0.15)

    return noise + synth


def generate_drift() -> np.ndarray:
    """Tire screech/drift sound."""
    duration = 0.5

    # High-pitched noise for tire screech
    noise = generate_noise(duration, 0.6)

    # Bandpass around tire screech frequencies
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq_mod = 2000 + 500 * np.sin(2 * np.pi * 15 * t)
    carrier = 0.3 * np.sin(2 * np.pi * np.cumsum(freq_mod) / SAMPLE_RATE)

    wave = noise * 0.5 + carrier * 0.5
    wave = apply_envelope(wave, 0.02, 0.1, 0.6, 0.2)

    return lowpass_filter(wave, 4000)


def generate_brake() -> np.ndarray:
    """Brake sound - lower screech."""
    duration = 0.3

    # Lower frequency screech
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq = 800 - 300 * (t / duration)  # Descending
    wave = 0.4 * np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE)
    wave += generate_noise(duration, 0.2)

    return apply_envelope(wave, 0.01, 0.1, 0.4, 0.15)


def generate_shift() -> np.ndarray:
    """Gear shift click."""
    duration = 0.1

    # Sharp click
    click1 = generate_sine(1200, 0.02, 0.8)
    click2 = generate_sine(2400, 0.02, 0.4)
    click = click1 + click2
    click = apply_envelope(click, 0.001, 0.01, 0.2, 0.02)

    # Mechanical thunk
    thunk = generate_sine(200, 0.08, 0.5)
    thunk_noise = generate_noise(0.08, 0.2)
    thunk = thunk + thunk_noise
    thunk = apply_envelope(thunk, 0.005, 0.03, 0.3, 0.04)

    # Combine
    wave = np.zeros(int(SAMPLE_RATE * duration))
    wave[:len(click)] += click
    wave[:len(thunk)] += thunk

    return wave


def generate_wall() -> np.ndarray:
    """Wall collision - heavy impact."""
    duration = 0.3

    # Low impact thud
    thud = generate_sine(80, duration, 0.6) + generate_sine(160, duration, 0.3)
    thud = apply_envelope(thud, 0.005, 0.05, 0.2, 0.2)

    # Crunch noise
    noise = generate_noise(0.15, 0.5)
    noise = apply_envelope(noise, 0.002, 0.03, 0.3, 0.1)

    wave = np.zeros(int(SAMPLE_RATE * duration))
    wave[:len(thud)] += thud
    wave[:len(noise)] += noise

    return lowpass_filter(wave, 600)


def generate_barrier() -> np.ndarray:
    """Barrier scrape - lighter impact."""
    duration = 0.25

    # Scrape noise
    noise = generate_noise(duration, 0.4)
    noise = apply_envelope(noise, 0.01, 0.05, 0.5, 0.15)

    # Metallic ring
    ring = generate_sine(600, duration, 0.3) + generate_sine(900, duration, 0.15)
    ring = apply_envelope(ring, 0.005, 0.08, 0.2, 0.1)

    return noise + ring


def generate_countdown() -> np.ndarray:
    """Countdown beep."""
    duration = 0.15

    # Clean beep
    wave = generate_sine(880, duration, 0.5) + generate_sine(1760, duration, 0.2)
    return apply_envelope(wave, 0.005, 0.02, 0.6, 0.08)


def generate_checkpoint() -> np.ndarray:
    """Checkpoint passed - positive chime."""
    duration = 0.3

    # Rising arpeggio
    notes = [523, 659, 784]  # C5, E5, G5
    wave = np.zeros(int(SAMPLE_RATE * duration))

    for i, freq in enumerate(notes):
        start = int(i * SAMPLE_RATE * 0.08)
        note = generate_sine(freq, 0.15, 0.4)
        note = apply_envelope(note, 0.01, 0.02, 0.5, 0.1)
        end = min(start + len(note), len(wave))
        wave[start:end] += note[:end - start]

    return wave


def generate_finish() -> np.ndarray:
    """Race finish - triumphant chord."""
    duration = 0.8

    # Major chord with fanfare feel
    freqs = [523, 659, 784, 1047]  # C5, E5, G5, C6
    wave = np.zeros(int(SAMPLE_RATE * duration))

    for i, freq in enumerate(freqs):
        start = int(i * SAMPLE_RATE * 0.05)
        note = generate_sine(freq, duration - i * 0.05, 0.3)
        note += generate_saw(freq, duration - i * 0.05, 0.1)  # Brassy
        note = apply_envelope(note, 0.02, 0.1, 0.6, 0.2)
        end = min(start + len(note), len(wave))
        wave[start:end] += note[:end - start]

    return wave


# =============================================================================
# SYNTH SAMPLES (for XM music)
# =============================================================================

def generate_synth_kick() -> np.ndarray:
    """Punchy kick drum."""
    duration = 0.3
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Pitch drop from 150Hz to 40Hz
    freq = 150 * np.exp(-20 * t) + 40
    wave = 0.8 * np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE)

    # Sharp attack, quick decay
    envelope = np.exp(-8 * t)
    return wave * envelope


def generate_synth_snare() -> np.ndarray:
    """Snappy snare with body and noise."""
    duration = 0.25
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Body (pitched component)
    body = 0.4 * np.sin(2 * np.pi * 180 * t)
    body *= np.exp(-15 * t)

    # Noise (snare wires)
    noise = generate_noise(duration, 0.5)
    noise *= np.exp(-10 * t)

    return body + noise


def generate_synth_hihat() -> np.ndarray:
    """Short closed hi-hat."""
    duration = 0.08
    noise = generate_noise(duration, 0.6)
    return apply_envelope(noise, 0.001, 0.02, 0.3, 0.05)


def generate_synth_openhat() -> np.ndarray:
    """Longer open hi-hat."""
    duration = 0.4
    noise = generate_noise(duration, 0.4)
    return apply_envelope(noise, 0.001, 0.05, 0.4, 0.3)


def generate_synth_bass() -> np.ndarray:
    """Synth bass - single cycle saw for XM."""
    duration = 0.5
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Detuned saw waves
    freq = 55  # A1
    wave = generate_saw(freq, duration, 0.4)
    wave += generate_saw(freq * 1.003, duration, 0.3)  # Slight detune

    # Low-pass
    wave = lowpass_filter(wave, 300)
    return apply_envelope(wave, 0.01, 0.1, 0.7, 0.15)


def generate_synth_lead() -> np.ndarray:
    """Bright lead synth."""
    duration = 0.5
    freq = 440  # A4

    # Square + saw blend
    wave = generate_square(freq, duration, 0.3)
    wave += generate_saw(freq, duration, 0.2)
    wave += generate_sine(freq * 2, duration, 0.1)  # Octave harmonic

    return apply_envelope(wave, 0.01, 0.1, 0.6, 0.2)


def generate_synth_pad() -> np.ndarray:
    """Soft pad sound."""
    duration = 1.0
    freq = 220  # A3

    # Multiple detuned sines
    wave = generate_sine(freq, duration, 0.3)
    wave += generate_sine(freq * 1.002, duration, 0.25)
    wave += generate_sine(freq * 0.998, duration, 0.25)
    wave += generate_sine(freq * 2, duration, 0.1)

    wave = lowpass_filter(wave, 1000)
    return apply_envelope(wave, 0.15, 0.2, 0.7, 0.3)


def generate_synth_arp() -> np.ndarray:
    """Arpeggio pluck sound."""
    duration = 0.15
    freq = 330  # E4

    wave = generate_saw(freq, duration, 0.5)
    wave = lowpass_filter(wave, 2000)
    return apply_envelope(wave, 0.002, 0.03, 0.3, 0.1)


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n" + "=" * 60)
    print("  NEON DRIFT - AUDIO GENERATION")
    print("=" * 60)

    output_dir = Path(__file__).parent.parent.parent / "generated" / "sounds"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nOutput: {output_dir}")
    print("\n--- SOUND EFFECTS ---")

    sfx_generators = [
        ("engine_idle.wav", generate_engine_idle),
        ("engine_rev.wav", generate_engine_rev),
        ("boost.wav", generate_boost),
        ("drift.wav", generate_drift),
        ("brake.wav", generate_brake),
        ("shift.wav", generate_shift),
        ("wall.wav", generate_wall),
        ("barrier.wav", generate_barrier),
        ("countdown.wav", generate_countdown),
        ("checkpoint.wav", generate_checkpoint),
        ("finish.wav", generate_finish),
    ]

    for filename, generator in sfx_generators:
        wave = generator()
        save_wav(filename, wave, output_dir)

    print("\n--- SYNTH SAMPLES (for XM music) ---")

    synth_generators = [
        ("synth_kick.wav", generate_synth_kick),
        ("synth_snare.wav", generate_synth_snare),
        ("synth_hihat.wav", generate_synth_hihat),
        ("synth_openhat.wav", generate_synth_openhat),
        ("synth_bass.wav", generate_synth_bass),
        ("synth_lead.wav", generate_synth_lead),
        ("synth_pad.wav", generate_synth_pad),
        ("synth_arp.wav", generate_synth_arp),
    ]

    for filename, generator in synth_generators:
        wave = generator()
        save_wav(filename, wave, output_dir)

    print("\n" + "=" * 60)
    print(f"  Generated {len(sfx_generators)} SFX + {len(synth_generators)} synth samples")
    print("=" * 60)


if __name__ == "__main__":
    main()
