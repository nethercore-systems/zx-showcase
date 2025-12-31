"""Neon Drift Audio Generation.

Sound Effects:
- Engine sounds (idle, rev)
- Racing actions (boost, drift, brake, shift)
- Collisions (wall, barrier)
- Events (countdown, checkpoint, finish)

Synth Samples (for XM tracker music):
- Drums (kick, snare, hihat, openhat)
- Instruments (bass, lead, pad, arp)
"""

import math
from pathlib import Path
from typing import List, Tuple

from procgen.lib.audio_dsp import (
    SAMPLE_RATE, write_wav,
    sine_wave, square_wave, sawtooth_wave, noise,
    lowpass_filter, highpass_filter,
    envelope_adsr, envelope_linear,
    reverb_comb, mix, insert_at, pad_to_length
)

# Neon Drift uses 22050 Hz for smaller file sizes
NEON_SAMPLE_RATE = 22050


def _resample_to_neon(samples: List[float]) -> List[float]:
    """Downsample from 44100 to 22050 Hz (simple decimation)."""
    return samples[::2]


# =============================================================================
# Engine Sounds
# =============================================================================

def generate_engine_idle(duration: float = 0.5) -> List[float]:
    """Low rumbling engine idle sound."""
    # Base frequency with harmonics
    wave = sine_wave(60, duration, amplitude=0.4)
    h2 = sine_wave(120, duration, amplitude=0.2)
    h3 = sine_wave(180, duration, amplitude=0.1)
    wave = mix([wave, h2, h3])

    # Add rough texture
    n = noise(duration, amplitude=0.05)
    wave = mix([wave, n])

    # Apply subtle pulsing
    for i in range(len(wave)):
        t = i / SAMPLE_RATE
        pulse = 0.8 + 0.2 * math.sin(2 * math.pi * 8 * t)
        wave[i] *= pulse

    wave = lowpass_filter(wave, 400)
    return _resample_to_neon(wave)


def generate_engine_rev(duration: float = 0.6) -> List[float]:
    """Engine revving up sound."""
    samples = int(duration * SAMPLE_RATE)
    wave = [0.0] * samples

    # Frequency sweep from low to high
    for i in range(samples):
        t = i / SAMPLE_RATE
        progress = (t / duration) ** 0.7
        freq = 80 + 200 * progress
        phase = 2 * math.pi * freq * t

        wave[i] = 0.4 * math.sin(phase)
        wave[i] += 0.2 * math.sin(phase * 2)  # Harmonic
        wave[i] += 0.1 * math.sin(phase * 3)  # Harmonic

    # Add texture
    n = noise(duration, amplitude=0.08)
    wave = mix([wave, n])

    wave = lowpass_filter(wave, 800)
    wave = envelope_adsr(wave, 0.05, 0.1, 0.8, 0.2)
    return _resample_to_neon(wave)


# =============================================================================
# Racing Action Sounds
# =============================================================================

def generate_boost(duration: float = 0.4) -> List[float]:
    """Boost activation - whoosh with synth accent."""
    # Whoosh noise
    whoosh = noise(duration, amplitude=0.5)
    whoosh = envelope_adsr(whoosh, 0.02, 0.1, 0.3, 0.2)

    # Synth accent (rising pitch)
    samples = int(duration * SAMPLE_RATE)
    synth = [0.0] * samples
    for i in range(samples):
        t = i / SAMPLE_RATE
        freq = 400 + 800 * (t / duration)
        synth[i] = 0.3 * math.sin(2 * math.pi * freq * t)
    synth = envelope_adsr(synth, 0.01, 0.15, 0.3, 0.15)

    return _resample_to_neon(mix([whoosh, synth]))


def generate_drift(duration: float = 0.5) -> List[float]:
    """Tire screech/drift sound."""
    # High-pitched noise for tire screech
    n = noise(duration, amplitude=0.6)

    # Modulated carrier for screech
    samples = int(duration * SAMPLE_RATE)
    carrier = [0.0] * samples
    for i in range(samples):
        t = i / SAMPLE_RATE
        freq = 2000 + 500 * math.sin(2 * math.pi * 15 * t)
        carrier[i] = 0.3 * math.sin(2 * math.pi * freq * t)

    wave = mix([n, carrier], [0.5, 0.5])
    wave = envelope_adsr(wave, 0.02, 0.1, 0.6, 0.2)
    wave = lowpass_filter(wave, 4000)
    return _resample_to_neon(wave)


def generate_brake(duration: float = 0.3) -> List[float]:
    """Brake sound - descending screech."""
    samples = int(duration * SAMPLE_RATE)
    wave = [0.0] * samples

    for i in range(samples):
        t = i / SAMPLE_RATE
        freq = 800 - 300 * (t / duration)  # Descending
        wave[i] = 0.4 * math.sin(2 * math.pi * freq * t)

    n = noise(duration, amplitude=0.2)
    wave = mix([wave, n])
    wave = envelope_adsr(wave, 0.01, 0.1, 0.4, 0.15)
    return _resample_to_neon(wave)


def generate_shift(duration: float = 0.1) -> List[float]:
    """Gear shift click."""
    # Sharp click
    click = sine_wave(1200, 0.02, amplitude=0.8)
    click2 = sine_wave(2400, 0.02, amplitude=0.4)
    click = mix([click, click2])
    click = envelope_adsr(click, 0.001, 0.01, 0.2, 0.02)

    # Mechanical thunk
    thunk = sine_wave(200, 0.08, amplitude=0.5)
    thunk_noise = noise(0.08, amplitude=0.2)
    thunk = mix([thunk, thunk_noise])
    thunk = envelope_adsr(thunk, 0.005, 0.03, 0.3, 0.04)

    # Combine
    wave = pad_to_length(click, int(duration * SAMPLE_RATE))
    wave = insert_at(wave, thunk, 0)
    return _resample_to_neon(wave)


# =============================================================================
# Collision Sounds
# =============================================================================

def generate_wall_collision(duration: float = 0.3) -> List[float]:
    """Wall collision - heavy impact."""
    # Low impact thud
    thud = sine_wave(80, duration, amplitude=0.6)
    thud2 = sine_wave(160, duration, amplitude=0.3)
    thud = mix([thud, thud2])
    thud = envelope_adsr(thud, 0.005, 0.05, 0.2, 0.2)

    # Crunch noise
    crunch = noise(0.15, amplitude=0.5)
    crunch = envelope_adsr(crunch, 0.002, 0.03, 0.3, 0.1)

    wave = pad_to_length(thud, int(duration * SAMPLE_RATE))
    wave = insert_at(wave, crunch, 0)
    wave = lowpass_filter(wave, 600)
    return _resample_to_neon(wave)


def generate_barrier_collision(duration: float = 0.25) -> List[float]:
    """Barrier scrape - lighter impact."""
    # Scrape noise
    scrape = noise(duration, amplitude=0.4)
    scrape = envelope_adsr(scrape, 0.01, 0.05, 0.5, 0.15)

    # Metallic ring
    ring = sine_wave(600, duration, amplitude=0.3)
    ring2 = sine_wave(900, duration, amplitude=0.15)
    ring = mix([ring, ring2])
    ring = envelope_adsr(ring, 0.005, 0.08, 0.2, 0.1)

    return _resample_to_neon(mix([scrape, ring]))


# =============================================================================
# Event Sounds
# =============================================================================

def generate_countdown(duration: float = 0.15) -> List[float]:
    """Countdown beep."""
    wave = sine_wave(880, duration, amplitude=0.5)
    wave2 = sine_wave(1760, duration, amplitude=0.2)
    wave = mix([wave, wave2])
    wave = envelope_adsr(wave, 0.005, 0.02, 0.6, 0.08)
    return _resample_to_neon(wave)


def generate_checkpoint(duration: float = 0.3) -> List[float]:
    """Checkpoint passed - positive chime."""
    notes = [523, 659, 784]  # C5, E5, G5
    samples = int(duration * SAMPLE_RATE)
    wave = [0.0] * samples

    for i, freq in enumerate(notes):
        start = int(i * SAMPLE_RATE * 0.08)
        note = sine_wave(freq, 0.15, amplitude=0.4)
        note = envelope_adsr(note, 0.01, 0.02, 0.5, 0.1)
        wave = insert_at(wave, note, start)

    return _resample_to_neon(wave)


def generate_finish(duration: float = 0.8) -> List[float]:
    """Race finish - triumphant chord."""
    freqs = [523, 659, 784, 1047]  # C5, E5, G5, C6
    samples = int(duration * SAMPLE_RATE)
    wave = [0.0] * samples

    for i, freq in enumerate(freqs):
        start = int(i * SAMPLE_RATE * 0.05)
        note_dur = duration - i * 0.05
        note = sine_wave(freq, note_dur, amplitude=0.3)
        # Add brassy sawtooth
        saw = sawtooth_wave(freq, note_dur, amplitude=0.1)
        note = mix([note, saw])
        note = envelope_adsr(note, 0.02, 0.1, 0.6, 0.2)
        wave = insert_at(wave, note, start)

    return _resample_to_neon(wave)


# =============================================================================
# Synth Samples (for XM tracker music)
# =============================================================================

def generate_synth_kick(duration: float = 0.3) -> List[float]:
    """Punchy kick drum with pitch drop."""
    samples = int(duration * SAMPLE_RATE)
    wave = [0.0] * samples

    for i in range(samples):
        t = i / SAMPLE_RATE
        # Pitch drop from 150Hz to 40Hz
        freq = 150 * math.exp(-20 * t) + 40
        phase = 2 * math.pi * freq * t
        envelope = math.exp(-8 * t)
        wave[i] = 0.8 * math.sin(phase) * envelope

    return _resample_to_neon(wave)


def generate_synth_snare(duration: float = 0.25) -> List[float]:
    """Snappy snare with body and noise."""
    samples = int(duration * SAMPLE_RATE)

    # Body (pitched component)
    body = [0.0] * samples
    for i in range(samples):
        t = i / SAMPLE_RATE
        body[i] = 0.4 * math.sin(2 * math.pi * 180 * t) * math.exp(-15 * t)

    # Noise (snare wires)
    n = noise(duration, amplitude=0.5)
    for i in range(len(n)):
        t = i / SAMPLE_RATE
        n[i] *= math.exp(-10 * t)

    return _resample_to_neon(mix([body, n]))


def generate_synth_hihat(duration: float = 0.08) -> List[float]:
    """Short closed hi-hat."""
    wave = noise(duration, amplitude=0.6)
    wave = envelope_adsr(wave, 0.001, 0.02, 0.3, 0.05)
    return _resample_to_neon(wave)


def generate_synth_openhat(duration: float = 0.4) -> List[float]:
    """Longer open hi-hat."""
    wave = noise(duration, amplitude=0.4)
    wave = envelope_adsr(wave, 0.001, 0.05, 0.4, 0.3)
    return _resample_to_neon(wave)


def generate_synth_bass(duration: float = 0.5) -> List[float]:
    """Synth bass - detuned saw waves."""
    freq = 55  # A1
    wave = sawtooth_wave(freq, duration, amplitude=0.4)
    wave2 = sawtooth_wave(freq * 1.003, duration, amplitude=0.3)  # Slight detune
    wave = mix([wave, wave2])
    wave = lowpass_filter(wave, 300)
    wave = envelope_adsr(wave, 0.01, 0.1, 0.7, 0.15)
    return _resample_to_neon(wave)


def generate_synth_lead(duration: float = 0.5) -> List[float]:
    """Bright lead synth."""
    freq = 440  # A4
    sq = square_wave(freq, duration, amplitude=0.3)
    saw = sawtooth_wave(freq, duration, amplitude=0.2)
    octave = sine_wave(freq * 2, duration, amplitude=0.1)
    wave = mix([sq, saw, octave])
    wave = envelope_adsr(wave, 0.01, 0.1, 0.6, 0.2)
    return _resample_to_neon(wave)


def generate_synth_pad(duration: float = 1.0) -> List[float]:
    """Soft pad sound."""
    freq = 220  # A3
    wave = sine_wave(freq, duration, amplitude=0.3)
    wave2 = sine_wave(freq * 1.002, duration, amplitude=0.25)
    wave3 = sine_wave(freq * 0.998, duration, amplitude=0.25)
    octave = sine_wave(freq * 2, duration, amplitude=0.1)
    wave = mix([wave, wave2, wave3, octave])
    wave = lowpass_filter(wave, 1000)
    wave = envelope_adsr(wave, 0.15, 0.2, 0.7, 0.3)
    return _resample_to_neon(wave)


def generate_synth_arp(duration: float = 0.15) -> List[float]:
    """Arpeggio pluck sound."""
    freq = 330  # E4
    wave = sawtooth_wave(freq, duration, amplitude=0.5)
    wave = lowpass_filter(wave, 2000)
    wave = envelope_adsr(wave, 0.002, 0.03, 0.3, 0.1)
    return _resample_to_neon(wave)


# =============================================================================
# Generation Registry
# =============================================================================

AUDIO_ASSETS: List[Tuple[str, callable, str]] = [
    # SFX
    ("engine_idle", generate_engine_idle, "Engine Idle"),
    ("engine_rev", generate_engine_rev, "Engine Rev"),
    ("boost", generate_boost, "Boost"),
    ("drift", generate_drift, "Drift"),
    ("brake", generate_brake, "Brake"),
    ("shift", generate_shift, "Gear Shift"),
    ("wall", generate_wall_collision, "Wall Collision"),
    ("barrier", generate_barrier_collision, "Barrier Collision"),
    ("countdown", generate_countdown, "Countdown Beep"),
    ("checkpoint", generate_checkpoint, "Checkpoint"),
    ("finish", generate_finish, "Race Finish"),
]

SYNTH_SAMPLES: List[Tuple[str, callable, str]] = [
    ("synth_kick", generate_synth_kick, "Kick Drum"),
    ("synth_snare", generate_synth_snare, "Snare Drum"),
    ("synth_hihat", generate_synth_hihat, "Closed Hi-Hat"),
    ("synth_openhat", generate_synth_openhat, "Open Hi-Hat"),
    ("synth_bass", generate_synth_bass, "Bass Synth"),
    ("synth_lead", generate_synth_lead, "Lead Synth"),
    ("synth_pad", generate_synth_pad, "Pad Synth"),
    ("synth_arp", generate_synth_arp, "Arp Synth"),
]


def generate_all_audio(output_dir: Path) -> int:
    """Generate all SFX audio assets."""
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    for filename, generator, description in AUDIO_ASSETS:
        print(f"Generating {description}...")
        samples = generator()
        output_path = output_dir / f"{filename}.wav"
        write_wav(str(output_path), samples, sample_rate=NEON_SAMPLE_RATE)
        print(f"  -> {output_path.name}")
        count += 1

    return count


def generate_all_synth_samples(output_dir: Path) -> int:
    """Generate all synth samples for XM music."""
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    for filename, generator, description in SYNTH_SAMPLES:
        print(f"Generating {description}...")
        samples = generator()
        output_path = output_dir / f"{filename}.wav"
        write_wav(str(output_path), samples, sample_rate=NEON_SAMPLE_RATE)
        print(f"  -> {output_path.name}")
        count += 1

    return count


__all__ = [
    "generate_all_audio",
    "generate_all_synth_samples",
    "AUDIO_ASSETS",
    "SYNTH_SAMPLES",
]
