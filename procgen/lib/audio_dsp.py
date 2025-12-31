"""Shared audio DSP utilities for procedural sound generation.

Provides fundamental audio processing primitives used across games:
- Wave generators (sine, noise)
- Filters (lowpass, highpass)
- Envelopes (ADSR)
- Effects (reverb, mixing)
- WAV file output
"""

import math
import random
import struct
import wave
from typing import List, Optional, Tuple

# Default sample rate for all audio generation
SAMPLE_RATE = 44100


def write_wav(
    filepath: str,
    samples: List[float],
    sample_rate: int = SAMPLE_RATE,
    normalize: bool = True,
    peak_amplitude: float = 0.9
) -> None:
    """Write samples to WAV file.

    Args:
        filepath: Output file path
        samples: Audio samples as floats (-1.0 to 1.0)
        sample_rate: Sample rate in Hz
        normalize: Whether to normalize to peak amplitude
        peak_amplitude: Target peak when normalizing (0-1)
    """
    if not samples:
        return

    # Normalize to 16-bit range
    if normalize:
        max_val = max(abs(min(samples)), abs(max(samples)))
        if max_val > 0:
            samples = [int(s / max_val * 32767 * peak_amplitude) for s in samples]
    else:
        samples = [int(max(-32767, min(32767, s * 32767))) for s in samples]

    with wave.open(filepath, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        wav.writeframes(struct.pack(f'{len(samples)}h', *samples))


# =============================================================================
# Wave Generators
# =============================================================================

def sine_wave(
    freq: float,
    duration: float,
    sample_rate: int = SAMPLE_RATE,
    amplitude: float = 1.0,
    phase: float = 0.0
) -> List[float]:
    """Generate sine wave.

    Args:
        freq: Frequency in Hz
        duration: Duration in seconds
        amplitude: Peak amplitude (0-1)
        phase: Starting phase in radians
    """
    samples = []
    for i in range(int(duration * sample_rate)):
        t = i / sample_rate
        samples.append(amplitude * math.sin(2 * math.pi * freq * t + phase))
    return samples


def noise(
    duration: float,
    sample_rate: int = SAMPLE_RATE,
    amplitude: float = 1.0,
    seed: Optional[int] = None
) -> List[float]:
    """Generate white noise.

    Args:
        duration: Duration in seconds
        amplitude: Peak amplitude
        seed: Random seed for reproducible noise
    """
    rng = random.Random(seed) if seed is not None else random
    return [amplitude * (rng.random() * 2 - 1) for _ in range(int(duration * sample_rate))]


def sawtooth_wave(
    freq: float,
    duration: float,
    sample_rate: int = SAMPLE_RATE,
    amplitude: float = 1.0
) -> List[float]:
    """Generate sawtooth wave."""
    samples = []
    period = sample_rate / freq
    for i in range(int(duration * sample_rate)):
        phase = (i % period) / period
        samples.append(amplitude * (2 * phase - 1))
    return samples


def square_wave(
    freq: float,
    duration: float,
    sample_rate: int = SAMPLE_RATE,
    amplitude: float = 1.0,
    duty_cycle: float = 0.5
) -> List[float]:
    """Generate square wave with adjustable duty cycle."""
    samples = []
    period = sample_rate / freq
    for i in range(int(duration * sample_rate)):
        phase = (i % period) / period
        samples.append(amplitude if phase < duty_cycle else -amplitude)
    return samples


def triangle_wave(
    freq: float,
    duration: float,
    sample_rate: int = SAMPLE_RATE,
    amplitude: float = 1.0
) -> List[float]:
    """Generate triangle wave."""
    samples = []
    period = sample_rate / freq
    for i in range(int(duration * sample_rate)):
        phase = (i % period) / period
        # Triangle: 0->1 for first half, 1->0 for second half
        if phase < 0.5:
            samples.append(amplitude * (4 * phase - 1))
        else:
            samples.append(amplitude * (3 - 4 * phase))
    return samples


# =============================================================================
# Filters
# =============================================================================

def lowpass_filter(
    samples: List[float],
    cutoff: float,
    sample_rate: int = SAMPLE_RATE
) -> List[float]:
    """Simple one-pole lowpass filter.

    Args:
        samples: Input samples
        cutoff: Cutoff frequency in Hz
    """
    rc = 1.0 / (2 * math.pi * cutoff)
    dt = 1.0 / sample_rate
    alpha = dt / (rc + dt)

    filtered = []
    prev = 0
    for s in samples:
        prev = prev + alpha * (s - prev)
        filtered.append(prev)
    return filtered


def highpass_filter(
    samples: List[float],
    cutoff: float,
    sample_rate: int = SAMPLE_RATE
) -> List[float]:
    """Simple one-pole highpass filter.

    Args:
        samples: Input samples
        cutoff: Cutoff frequency in Hz
    """
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


def bandpass_filter(
    samples: List[float],
    low_cutoff: float,
    high_cutoff: float,
    sample_rate: int = SAMPLE_RATE
) -> List[float]:
    """Bandpass filter (combination of lowpass and highpass)."""
    samples = highpass_filter(samples, low_cutoff, sample_rate)
    return lowpass_filter(samples, high_cutoff, sample_rate)


# =============================================================================
# Envelopes
# =============================================================================

def envelope_adsr(
    samples: List[float],
    attack: float,
    decay: float,
    sustain: float,
    release: float,
    sample_rate: int = SAMPLE_RATE
) -> List[float]:
    """Apply ADSR envelope.

    Args:
        samples: Input samples
        attack: Attack time in seconds
        decay: Decay time in seconds
        sustain: Sustain level (0-1)
        release: Release time in seconds
    """
    total = len(samples)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = max(0, total - attack_samples - decay_samples - release_samples)

    output = []
    for i, s in enumerate(samples):
        if i < attack_samples:
            env = i / attack_samples if attack_samples > 0 else 1.0
        elif i < attack_samples + decay_samples:
            progress = (i - attack_samples) / decay_samples if decay_samples > 0 else 1.0
            env = 1.0 - (1.0 - sustain) * progress
        elif i < attack_samples + decay_samples + sustain_samples:
            env = sustain
        else:
            progress = (i - attack_samples - decay_samples - sustain_samples)
            env = sustain * (1.0 - progress / release_samples) if release_samples > 0 else 0
        output.append(s * max(0, env))
    return output


def envelope_linear(
    samples: List[float],
    fade_in: float = 0.0,
    fade_out: float = 0.0,
    sample_rate: int = SAMPLE_RATE
) -> List[float]:
    """Apply simple linear fade in/out."""
    total = len(samples)
    fade_in_samples = int(fade_in * sample_rate)
    fade_out_samples = int(fade_out * sample_rate)

    output = []
    for i, s in enumerate(samples):
        env = 1.0
        if i < fade_in_samples:
            env = i / fade_in_samples if fade_in_samples > 0 else 1.0
        elif i >= total - fade_out_samples:
            remaining = total - i
            env = remaining / fade_out_samples if fade_out_samples > 0 else 0.0
        output.append(s * env)
    return output


# =============================================================================
# Effects
# =============================================================================

def reverb_comb(
    samples: List[float],
    decay: float = 0.3,
    delay_ms: float = 50,
    sample_rate: int = SAMPLE_RATE
) -> List[float]:
    """Simple comb filter reverb.

    Args:
        samples: Input samples
        decay: Feedback amount (0-1)
        delay_ms: Delay time in milliseconds
    """
    delay_samples = int(delay_ms * sample_rate / 1000)
    output = samples.copy()

    for i in range(delay_samples, len(output)):
        output[i] += output[i - delay_samples] * decay

    return output


def reverb_multi(
    samples: List[float],
    delays_ms: List[float] = [50, 100, 150],
    decays: List[float] = [0.3, 0.2, 0.1],
    sample_rate: int = SAMPLE_RATE
) -> List[float]:
    """Multi-tap reverb with multiple delay lines."""
    output = samples.copy()
    for delay_ms, decay in zip(delays_ms, decays):
        output = reverb_comb(output, decay, delay_ms, sample_rate)
    return output


# =============================================================================
# Mixing
# =============================================================================

def mix(
    samples_list: List[List[float]],
    volumes: Optional[List[float]] = None
) -> List[float]:
    """Mix multiple sample arrays.

    Args:
        samples_list: List of sample arrays to mix
        volumes: Optional per-track volume multipliers
    """
    if not samples_list:
        return []

    if volumes is None:
        volumes = [1.0] * len(samples_list)

    max_len = max(len(s) for s in samples_list)
    output = [0.0] * max_len

    for samples, vol in zip(samples_list, volumes):
        for i, s in enumerate(samples):
            output[i] += s * vol

    return output


def concat(samples_list: List[List[float]]) -> List[float]:
    """Concatenate sample arrays sequentially."""
    output = []
    for samples in samples_list:
        output.extend(samples)
    return output


def pad_to_length(
    samples: List[float],
    target_length: int,
    pad_value: float = 0.0
) -> List[float]:
    """Pad samples to target length."""
    if len(samples) >= target_length:
        return samples[:target_length]
    return samples + [pad_value] * (target_length - len(samples))


def insert_at(
    target: List[float],
    source: List[float],
    position: int,
    volume: float = 1.0
) -> List[float]:
    """Insert/mix source samples into target at given position."""
    output = target.copy()
    for i, s in enumerate(source):
        pos = position + i
        if 0 <= pos < len(output):
            output[pos] += s * volume
    return output
