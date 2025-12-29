#!/usr/bin/env python3
"""Generate sound effects for Neon Drift using numpy synthesis.

Creates WAV files for all game SFX:
- Engine sounds (idle, rev)
- Boost, drift, brake
- Collisions (wall, barrier)
- Race events (countdown, checkpoint, finish)
- Synth samples for XM tracker
"""

import numpy as np
from pathlib import Path
import struct
import wave


def write_wav(path: Path, samples: np.ndarray, sample_rate: int = 22050):
    """Write samples to a WAV file (mono, 16-bit)."""
    # Normalize and convert to 16-bit
    samples = np.clip(samples, -1.0, 1.0)
    int_samples = (samples * 32767).astype(np.int16)

    with wave.open(str(path), 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        wav.writeframes(int_samples.tobytes())

    print(f"  Generated: {path.name} ({len(samples) / sample_rate:.2f}s)")


def generate_sine(freq: float, duration: float, sr: int = 22050) -> np.ndarray:
    """Generate a sine wave."""
    t = np.linspace(0, duration, int(sr * duration), False)
    return np.sin(2 * np.pi * freq * t)


def generate_saw(freq: float, duration: float, sr: int = 22050) -> np.ndarray:
    """Generate a sawtooth wave."""
    t = np.linspace(0, duration, int(sr * duration), False)
    return 2 * (t * freq - np.floor(0.5 + t * freq))


def generate_square(freq: float, duration: float, sr: int = 22050) -> np.ndarray:
    """Generate a square wave."""
    return np.sign(generate_sine(freq, duration, sr))


def generate_noise(duration: float, sr: int = 22050) -> np.ndarray:
    """Generate white noise."""
    return np.random.uniform(-1, 1, int(sr * duration))


def apply_envelope(samples: np.ndarray, attack: float, decay: float, sustain: float, release: float, sr: int = 22050) -> np.ndarray:
    """Apply ADSR envelope to samples."""
    total_samples = len(samples)
    attack_samples = int(attack * sr)
    decay_samples = int(decay * sr)
    release_samples = int(release * sr)
    sustain_samples = max(0, total_samples - attack_samples - decay_samples - release_samples)

    envelope = np.concatenate([
        np.linspace(0, 1, attack_samples),              # Attack
        np.linspace(1, sustain, decay_samples),         # Decay
        np.full(sustain_samples, sustain),              # Sustain
        np.linspace(sustain, 0, release_samples)        # Release
    ])

    # Pad or truncate to match samples length
    if len(envelope) < total_samples:
        envelope = np.pad(envelope, (0, total_samples - len(envelope)))
    else:
        envelope = envelope[:total_samples]

    return samples * envelope


def lowpass_filter(samples: np.ndarray, cutoff: float, sr: int = 22050) -> np.ndarray:
    """Simple lowpass filter using moving average."""
    window_size = max(1, int(sr / cutoff / 2))
    kernel = np.ones(window_size) / window_size
    return np.convolve(samples, kernel, mode='same')


# === Sound Effect Generators ===

def generate_engine_idle(path: Path):
    """Deep rumbling engine idle loop."""
    sr = 22050
    duration = 0.5  # Short loop

    # Low frequency rumble with harmonics
    base = generate_saw(55, duration, sr) * 0.5  # A1
    harm1 = generate_saw(110, duration, sr) * 0.3  # A2
    harm2 = generate_saw(165, duration, sr) * 0.1  # E3

    # Add some noise for texture
    noise = lowpass_filter(generate_noise(duration, sr), 200, sr) * 0.1

    samples = base + harm1 + harm2 + noise
    samples = lowpass_filter(samples, 400, sr)
    samples = samples / np.max(np.abs(samples)) * 0.7

    write_wav(path, samples, sr)


def generate_engine_rev(path: Path):
    """Engine rev-up sound."""
    sr = 22050
    duration = 0.3

    # Frequency sweep from idle to high
    t = np.linspace(0, duration, int(sr * duration), False)
    freq = 80 + 400 * (t / duration) ** 2  # Accelerating frequency
    phase = np.cumsum(freq) / sr
    samples = np.sin(2 * np.pi * phase)

    # Add harmonics
    samples += np.sin(4 * np.pi * phase) * 0.3
    samples += np.sin(6 * np.pi * phase) * 0.1

    samples = apply_envelope(samples, 0.02, 0.05, 0.8, 0.1, sr)
    samples = samples / np.max(np.abs(samples)) * 0.8

    write_wav(path, samples, sr)


def generate_boost(path: Path):
    """Explosive boost activation with whoosh."""
    sr = 22050
    duration = 0.5

    # Initial burst (noise + low hit)
    noise = generate_noise(0.1, sr)
    noise = lowpass_filter(noise, 800, sr)
    noise = apply_envelope(noise, 0.01, 0.05, 0.3, 0.04, sr)

    # Sub bass hit
    sub = generate_sine(40, 0.15, sr)
    sub = apply_envelope(sub, 0.01, 0.1, 0.0, 0.04, sr)

    # Whoosh (filtered noise sweep)
    whoosh = generate_noise(0.4, sr)
    t = np.linspace(0, 0.4, int(sr * 0.4), False)
    cutoff_sweep = 2000 + 4000 * t / 0.4
    # Simple filter approximation
    whoosh = lowpass_filter(whoosh, 3000, sr)
    whoosh = apply_envelope(whoosh, 0.05, 0.1, 0.5, 0.2, sr)

    # Combine with padding
    burst = np.pad(noise, (0, int(sr * duration) - len(noise))) * 0.8
    sub_pad = np.pad(sub, (0, int(sr * duration) - len(sub))) * 0.6
    whoosh_pad = np.pad(whoosh, (int(sr * 0.05), int(sr * duration) - len(whoosh) - int(sr * 0.05)))

    samples = burst + sub_pad + whoosh_pad * 0.5
    samples = samples / np.max(np.abs(samples)) * 0.9

    write_wav(path, samples, sr)


def generate_drift(path: Path):
    """Tire screech during drift."""
    sr = 22050
    duration = 0.4

    # High frequency filtered noise (tire squeal)
    noise = generate_noise(duration, sr)

    # Multiple bandpass-like filters for screech
    high = lowpass_filter(noise, 4000, sr)
    high = high - lowpass_filter(high, 1500, sr)

    # Modulate for variation
    t = np.linspace(0, duration, int(sr * duration), False)
    mod = 0.7 + 0.3 * np.sin(2 * np.pi * 8 * t)

    samples = high * mod
    samples = apply_envelope(samples, 0.02, 0.1, 0.7, 0.1, sr)
    samples = samples / np.max(np.abs(samples)) * 0.7

    write_wav(path, samples, sr)


def generate_brake(path: Path):
    """Brake squeal sound."""
    sr = 22050
    duration = 0.3

    # High pitched filtered noise
    noise = generate_noise(duration, sr)
    samples = lowpass_filter(noise, 6000, sr)
    samples = samples - lowpass_filter(samples, 2000, sr)

    samples = apply_envelope(samples, 0.05, 0.1, 0.5, 0.1, sr)
    samples = samples / np.max(np.abs(samples)) * 0.6

    write_wav(path, samples, sr)


def generate_shift(path: Path):
    """Gear shift click."""
    sr = 22050
    duration = 0.1

    # Quick burst with tone
    click = generate_noise(0.02, sr)
    click = lowpass_filter(click, 3000, sr)

    tone = generate_sine(800, 0.05, sr)
    tone = apply_envelope(tone, 0.01, 0.04, 0.0, 0.0, sr)

    click = np.pad(click, (0, int(sr * duration) - len(click)))
    tone = np.pad(tone, (int(sr * 0.02), int(sr * duration) - len(tone) - int(sr * 0.02)))

    samples = click * 0.5 + tone * 0.5
    samples = samples / np.max(np.abs(samples)) * 0.7

    write_wav(path, samples, sr)


def generate_wall_collision(path: Path):
    """Heavy wall impact sound."""
    sr = 22050
    duration = 0.4

    # Impact noise
    noise = generate_noise(0.15, sr)
    noise = lowpass_filter(noise, 1500, sr)
    noise = apply_envelope(noise, 0.01, 0.1, 0.2, 0.04, sr)

    # Low thump
    thump = generate_sine(60, 0.2, sr)
    thump = apply_envelope(thump, 0.01, 0.15, 0.0, 0.04, sr)

    # Metal debris
    debris = generate_noise(0.3, sr)
    debris = lowpass_filter(debris, 5000, sr) - lowpass_filter(debris, 1000, sr)
    debris = apply_envelope(debris, 0.05, 0.1, 0.3, 0.15, sr)

    noise = np.pad(noise, (0, int(sr * duration) - len(noise)))
    thump = np.pad(thump, (0, int(sr * duration) - len(thump)))
    debris = np.pad(debris, (int(sr * 0.05), int(sr * duration) - len(debris) - int(sr * 0.05)))

    samples = noise * 0.4 + thump * 0.4 + debris * 0.3
    samples = samples / np.max(np.abs(samples)) * 0.9

    write_wav(path, samples, sr)


def generate_barrier_collision(path: Path):
    """Lighter barrier hit sound."""
    sr = 22050
    duration = 0.25

    # Quick impact
    noise = generate_noise(0.08, sr)
    noise = lowpass_filter(noise, 2000, sr)
    noise = apply_envelope(noise, 0.01, 0.07, 0.0, 0.0, sr)

    # Ping
    ping = generate_sine(400, 0.15, sr)
    ping = apply_envelope(ping, 0.01, 0.1, 0.1, 0.04, sr)

    noise = np.pad(noise, (0, int(sr * duration) - len(noise)))
    ping = np.pad(ping, (int(sr * 0.02), int(sr * duration) - len(ping) - int(sr * 0.02)))

    samples = noise * 0.5 + ping * 0.4
    samples = samples / np.max(np.abs(samples)) * 0.7

    write_wav(path, samples, sr)


def generate_countdown(path: Path):
    """Countdown beep (3-2-1)."""
    sr = 22050
    duration = 0.15

    # Clean synth beep
    tone = generate_sine(880, duration, sr)  # A5
    tone += generate_sine(1760, duration, sr) * 0.3  # A6 harmonic

    samples = apply_envelope(tone, 0.01, 0.05, 0.6, 0.05, sr)
    samples = samples / np.max(np.abs(samples)) * 0.7

    write_wav(path, samples, sr)


def generate_checkpoint(path: Path):
    """Checkpoint pass chime."""
    sr = 22050
    duration = 0.4

    # Ascending arpeggio
    note1 = generate_sine(523, 0.1, sr)  # C5
    note2 = generate_sine(659, 0.1, sr)  # E5
    note3 = generate_sine(784, 0.2, sr)  # G5

    note1 = apply_envelope(note1, 0.01, 0.05, 0.5, 0.04, sr)
    note2 = apply_envelope(note2, 0.01, 0.05, 0.5, 0.04, sr)
    note3 = apply_envelope(note3, 0.01, 0.1, 0.3, 0.08, sr)

    samples = np.zeros(int(sr * duration))
    samples[:len(note1)] += note1
    samples[int(sr * 0.08):int(sr * 0.08) + len(note2)] += note2
    samples[int(sr * 0.16):int(sr * 0.16) + len(note3)] += note3

    samples = samples / np.max(np.abs(samples)) * 0.7

    write_wav(path, samples, sr)


def generate_finish(path: Path):
    """Race finish fanfare."""
    sr = 22050
    duration = 0.8

    # Major chord fanfare
    c = generate_saw(262, 0.6, sr) * 0.3  # C4
    e = generate_saw(330, 0.6, sr) * 0.3  # E4
    g = generate_saw(392, 0.6, sr) * 0.3  # G4
    c2 = generate_saw(523, 0.6, sr) * 0.2  # C5

    chord = c + e + g + c2
    chord = lowpass_filter(chord, 3000, sr)
    chord = apply_envelope(chord, 0.02, 0.1, 0.6, 0.28, sr)

    samples = np.zeros(int(sr * duration))
    samples[:len(chord)] = chord

    samples = samples / np.max(np.abs(samples)) * 0.8

    write_wav(path, samples, sr)


# === Synth Samples for XM Tracker ===

def generate_synth_kick(path: Path):
    """808-style kick drum."""
    sr = 22050
    duration = 0.3

    # Pitch envelope (drops quickly)
    t = np.linspace(0, duration, int(sr * duration), False)
    freq = 150 * np.exp(-15 * t) + 40

    phase = np.cumsum(freq) / sr
    samples = np.sin(2 * np.pi * phase)

    # Add click
    click = generate_noise(0.01, sr)
    click = lowpass_filter(click, 2000, sr)
    click = np.pad(click, (0, len(samples) - len(click)))

    samples = samples * 0.8 + click * 0.3
    samples = apply_envelope(samples, 0.002, 0.1, 0.3, 0.15, sr)
    samples = samples / np.max(np.abs(samples)) * 0.9

    write_wav(path, samples, sr)


def generate_synth_snare(path: Path):
    """Gated reverb snare."""
    sr = 22050
    duration = 0.25

    # Body (pitched noise)
    body = generate_noise(duration, sr)
    body = lowpass_filter(body, 3000, sr)

    # Snap (high frequency click)
    tone = generate_sine(200, 0.02, sr)
    tone = np.pad(tone, (0, int(sr * duration) - len(tone)))

    samples = body * 0.6 + tone * 0.4
    samples = apply_envelope(samples, 0.002, 0.03, 0.4, 0.15, sr)
    samples = samples / np.max(np.abs(samples)) * 0.8

    write_wav(path, samples, sr)


def generate_synth_hihat(path: Path):
    """Closed hi-hat."""
    sr = 22050
    duration = 0.05

    noise = generate_noise(duration, sr)
    samples = lowpass_filter(noise, 10000, sr) - lowpass_filter(noise, 5000, sr)
    samples = apply_envelope(samples, 0.001, 0.04, 0.0, 0.01, sr)
    samples = samples / np.max(np.abs(samples)) * 0.6

    write_wav(path, samples, sr)


def generate_synth_openhat(path: Path):
    """Open hi-hat."""
    sr = 22050
    duration = 0.3

    noise = generate_noise(duration, sr)
    samples = lowpass_filter(noise, 12000, sr) - lowpass_filter(noise, 4000, sr)
    samples = apply_envelope(samples, 0.001, 0.1, 0.5, 0.15, sr)
    samples = samples / np.max(np.abs(samples)) * 0.5

    write_wav(path, samples, sr)


def generate_synth_bass(path: Path):
    """Synth bass sample (C2)."""
    sr = 22050
    duration = 0.5

    # Detuned saws for thickness
    saw1 = generate_saw(65.41, duration, sr)
    saw2 = generate_saw(65.41 * 1.005, duration, sr)

    samples = saw1 * 0.5 + saw2 * 0.5
    samples = lowpass_filter(samples, 800, sr)
    samples = apply_envelope(samples, 0.01, 0.1, 0.7, 0.15, sr)
    samples = samples / np.max(np.abs(samples)) * 0.8

    write_wav(path, samples, sr)


def generate_synth_lead(path: Path):
    """Synth lead sample (C4)."""
    sr = 22050
    duration = 0.5

    # Bright saw with slight detune
    saw1 = generate_saw(261.63, duration, sr)
    saw2 = generate_saw(261.63 * 1.003, duration, sr)
    saw3 = generate_saw(261.63 * 0.997, duration, sr)

    samples = saw1 * 0.4 + saw2 * 0.3 + saw3 * 0.3
    samples = lowpass_filter(samples, 4000, sr)
    samples = apply_envelope(samples, 0.02, 0.1, 0.7, 0.15, sr)
    samples = samples / np.max(np.abs(samples)) * 0.7

    write_wav(path, samples, sr)


def generate_synth_pad(path: Path):
    """Warm synth pad sample (C4)."""
    sr = 22050
    duration = 1.0

    # Multiple detuned saws
    freq = 261.63
    saws = []
    for detune in [-0.02, -0.01, 0, 0.01, 0.02]:
        saws.append(generate_saw(freq * (1 + detune * 0.1), duration, sr))

    samples = sum(saws) / len(saws)
    samples = lowpass_filter(samples, 2000, sr)
    samples = apply_envelope(samples, 0.2, 0.2, 0.8, 0.3, sr)
    samples = samples / np.max(np.abs(samples)) * 0.6

    write_wav(path, samples, sr)


def generate_synth_arp(path: Path):
    """Arpeggiator pluck sample (C4)."""
    sr = 22050
    duration = 0.15

    saw = generate_saw(261.63, duration, sr)
    samples = lowpass_filter(saw, 3000, sr)
    samples = apply_envelope(samples, 0.005, 0.08, 0.2, 0.05, sr)
    samples = samples / np.max(np.abs(samples)) * 0.7

    write_wav(path, samples, sr)


def main():
    base_dir = Path(__file__).parent.parent
    audio_dir = base_dir / "assets" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    print("Generating sound effects...")

    # Game SFX
    generate_engine_idle(audio_dir / "engine_idle.wav")
    generate_engine_rev(audio_dir / "engine_rev.wav")
    generate_boost(audio_dir / "boost.wav")
    generate_drift(audio_dir / "drift.wav")
    generate_brake(audio_dir / "brake.wav")
    generate_shift(audio_dir / "shift.wav")
    generate_wall_collision(audio_dir / "wall.wav")
    generate_barrier_collision(audio_dir / "barrier.wav")
    generate_countdown(audio_dir / "countdown.wav")
    generate_checkpoint(audio_dir / "checkpoint.wav")
    generate_finish(audio_dir / "finish.wav")

    print("\nGenerating synth samples for music...")

    # Synth samples for XM tracker
    generate_synth_kick(audio_dir / "synth_kick.wav")
    generate_synth_snare(audio_dir / "synth_snare.wav")
    generate_synth_hihat(audio_dir / "synth_hihat.wav")
    generate_synth_openhat(audio_dir / "synth_openhat.wav")
    generate_synth_bass(audio_dir / "synth_bass.wav")
    generate_synth_lead(audio_dir / "synth_lead.wav")
    generate_synth_pad(audio_dir / "synth_pad.wav")
    generate_synth_arp(audio_dir / "synth_arp.wav")

    print("\nDone! Generated 19 audio files.")


if __name__ == "__main__":
    main()
