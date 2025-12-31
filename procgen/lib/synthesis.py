"""
Audio synthesis utilities for procedural sound generation.

Provides waveform generators, envelopes, and filters.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import math

try:
    import numpy as np
    from scipy.signal import butter, filtfilt, lfilter
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None


SAMPLE_RATE = 22050  # ZX standard sample rate


@dataclass
class ADSREnvelope:
    """ADSR envelope parameters (in seconds)."""
    attack: float = 0.01
    decay: float = 0.1
    sustain: float = 0.7  # Sustain level 0-1
    release: float = 0.2


# ============================================================================
# Waveform Generators
# ============================================================================

def sine_wave(freq: float, duration: float, amplitude: float = 0.5) -> "np.ndarray":
    """Generate a sine wave."""
    _require_numpy()
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return amplitude * np.sin(2 * np.pi * freq * t)


def square_wave(
    freq: float,
    duration: float,
    amplitude: float = 0.3,
    duty: float = 0.5
) -> "np.ndarray":
    """Generate a square/pulse wave with adjustable duty cycle."""
    _require_numpy()
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return amplitude * np.sign(np.sin(2 * np.pi * freq * t) - (1 - 2 * duty))


def triangle_wave(freq: float, duration: float, amplitude: float = 0.5) -> "np.ndarray":
    """Generate a triangle wave."""
    _require_numpy()
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return amplitude * (2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1)


def sawtooth_wave(freq: float, duration: float, amplitude: float = 0.3) -> "np.ndarray":
    """Generate a sawtooth wave."""
    _require_numpy()
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return amplitude * (2 * (t * freq - np.floor(t * freq + 0.5)))


def noise_white(duration: float, amplitude: float = 0.3) -> "np.ndarray":
    """Generate white noise."""
    _require_numpy()
    samples = int(SAMPLE_RATE * duration)
    return amplitude * (np.random.random(samples) * 2 - 1)


def noise_pink(duration: float, amplitude: float = 0.3) -> "np.ndarray":
    """Generate pink noise (1/f noise)."""
    _require_numpy()
    samples = int(SAMPLE_RATE * duration)
    white = np.random.random(samples) * 2 - 1

    # Pink noise filter coefficients
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]

    pink = lfilter(b, a, white)
    max_val = np.max(np.abs(pink))
    if max_val > 0:
        pink = pink / max_val
    return amplitude * pink


def noise_brown(duration: float, amplitude: float = 0.3) -> "np.ndarray":
    """Generate brown/Brownian noise."""
    _require_numpy()
    samples = int(SAMPLE_RATE * duration)
    white = np.random.random(samples) * 2 - 1
    brown = np.cumsum(white)
    brown = brown - np.mean(brown)
    max_val = np.max(np.abs(brown))
    if max_val > 0:
        brown = brown / max_val
    return amplitude * brown


# ============================================================================
# FM Synthesis
# ============================================================================

def fm_wave(
    carrier_freq: float,
    mod_freq: float,
    mod_index: float,
    duration: float,
    amplitude: float = 0.5
) -> "np.ndarray":
    """
    Generate FM synthesis wave.

    Args:
        carrier_freq: Carrier oscillator frequency (Hz)
        mod_freq: Modulator frequency (Hz)
        mod_index: Modulation index (depth)
        duration: Duration in seconds
        amplitude: Output amplitude
    """
    _require_numpy()
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    modulator = mod_index * np.sin(2 * np.pi * mod_freq * t)
    return amplitude * np.sin(2 * np.pi * carrier_freq * t + modulator)


# ============================================================================
# Envelopes
# ============================================================================

def apply_adsr(wave: "np.ndarray", env: ADSREnvelope) -> "np.ndarray":
    """Apply ADSR envelope to waveform."""
    _require_numpy()
    total_samples = len(wave)
    attack_samples = int(env.attack * SAMPLE_RATE)
    decay_samples = int(env.decay * SAMPLE_RATE)
    release_samples = int(env.release * SAMPLE_RATE)
    sustain_samples = max(0, total_samples - attack_samples - decay_samples - release_samples)

    envelope = np.zeros(total_samples)
    pos = 0

    # Attack: 0 -> 1
    if attack_samples > 0 and pos + attack_samples <= total_samples:
        envelope[pos:pos + attack_samples] = np.linspace(0, 1, attack_samples)
        pos += attack_samples

    # Decay: 1 -> sustain
    if decay_samples > 0 and pos + decay_samples <= total_samples:
        envelope[pos:pos + decay_samples] = np.linspace(1, env.sustain, decay_samples)
        pos += decay_samples

    # Sustain
    if sustain_samples > 0 and pos + sustain_samples <= total_samples:
        envelope[pos:pos + sustain_samples] = env.sustain
        pos += sustain_samples

    # Release: sustain -> 0
    if release_samples > 0 and pos < total_samples:
        remaining = total_samples - pos
        envelope[pos:] = np.linspace(env.sustain, 0, remaining)

    return wave * envelope


def apply_exponential_decay(wave: "np.ndarray", decay_rate: float) -> "np.ndarray":
    """Apply exponential decay envelope."""
    _require_numpy()
    t = np.linspace(0, len(wave) / SAMPLE_RATE, len(wave), False)
    return wave * np.exp(-decay_rate * t)


def apply_linear_fade(
    wave: "np.ndarray",
    fade_in: float = 0,
    fade_out: float = 0
) -> "np.ndarray":
    """Apply linear fade in/out."""
    _require_numpy()
    result = wave.copy()

    if fade_in > 0:
        fade_samples = int(fade_in * SAMPLE_RATE)
        fade_samples = min(fade_samples, len(result))
        result[:fade_samples] *= np.linspace(0, 1, fade_samples)

    if fade_out > 0:
        fade_samples = int(fade_out * SAMPLE_RATE)
        fade_samples = min(fade_samples, len(result))
        result[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    return result


# ============================================================================
# Filters
# ============================================================================

def lowpass(wave: "np.ndarray", cutoff: float, order: int = 2) -> "np.ndarray":
    """Apply Butterworth lowpass filter."""
    _require_numpy()
    nyquist = SAMPLE_RATE / 2
    normalized_cutoff = min(cutoff / nyquist, 0.99)
    b, a = butter(order, normalized_cutoff, btype='low')
    return filtfilt(b, a, wave)


def highpass(wave: "np.ndarray", cutoff: float, order: int = 2) -> "np.ndarray":
    """Apply Butterworth highpass filter."""
    _require_numpy()
    nyquist = SAMPLE_RATE / 2
    normalized_cutoff = min(cutoff / nyquist, 0.99)
    b, a = butter(order, normalized_cutoff, btype='high')
    return filtfilt(b, a, wave)


def bandpass(
    wave: "np.ndarray",
    low_cutoff: float,
    high_cutoff: float,
    order: int = 2
) -> "np.ndarray":
    """Apply bandpass filter."""
    _require_numpy()
    nyquist = SAMPLE_RATE / 2
    low = min(low_cutoff / nyquist, 0.99)
    high = min(high_cutoff / nyquist, 0.99)
    if low >= high:
        return wave
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, wave)


# ============================================================================
# Utilities
# ============================================================================

def normalize(wave: "np.ndarray", peak: float = 0.9) -> "np.ndarray":
    """Normalize waveform to peak amplitude."""
    _require_numpy()
    max_val = np.max(np.abs(wave))
    if max_val > 0:
        return wave * (peak / max_val)
    return wave


def mix(*waves, volumes: Optional[List[float]] = None) -> "np.ndarray":
    """Mix multiple waveforms together."""
    _require_numpy()
    if not waves:
        return np.array([])

    max_len = max(len(w) for w in waves)
    result = np.zeros(max_len)
    vols = volumes or [1.0] * len(waves)

    for wave, vol in zip(waves, vols):
        result[:len(wave)] += wave * vol

    return result


def concat(*waves) -> "np.ndarray":
    """Concatenate waveforms end to end."""
    _require_numpy()
    if not waves:
        return np.array([])
    return np.concatenate(waves)


def pitch_shift(wave: "np.ndarray", semitones: float) -> "np.ndarray":
    """
    Simple pitch shift by resampling.

    Note: This also changes duration. For time-preserving pitch shift,
    use a more sophisticated algorithm.
    """
    _require_numpy()
    factor = 2 ** (semitones / 12)
    new_len = int(len(wave) / factor)
    indices = np.linspace(0, len(wave) - 1, new_len)
    return np.interp(indices, np.arange(len(wave)), wave)


def to_pcm16(wave: "np.ndarray") -> bytes:
    """Convert float waveform to 16-bit PCM bytes."""
    _require_numpy()
    wave = normalize(wave, 0.9)
    pcm = (wave * 32767).astype(np.int16)
    return pcm.tobytes()


def save_wav(filepath: str, wave: "np.ndarray") -> None:
    """Save waveform to WAV file."""
    _require_numpy()
    from scipy.io import wavfile
    wave = normalize(wave)
    wave_int = (wave * 32767).astype(np.int16)
    wavfile.write(filepath, SAMPLE_RATE, wave_int)


# ============================================================================
# Effects
# ============================================================================

def add_reverb(
    wave: "np.ndarray",
    decay: float = 0.3,
    delay_ms: float = 50
) -> "np.ndarray":
    """Add simple comb filter reverb."""
    _require_numpy()
    delay_samples = int(delay_ms * SAMPLE_RATE / 1000)
    output = wave.copy()
    for i in range(delay_samples, len(output)):
        output[i] += output[i - delay_samples] * decay
    return output


def add_distortion(wave: "np.ndarray", gain: float = 2.0, mix: float = 0.5) -> "np.ndarray":
    """Add soft clipping distortion."""
    _require_numpy()
    distorted = np.tanh(wave * gain)
    return wave * (1 - mix) + distorted * mix


def add_chorus(
    wave: "np.ndarray",
    depth_ms: float = 5,
    rate_hz: float = 1.5,
    mix: float = 0.5
) -> "np.ndarray":
    """Add chorus effect."""
    _require_numpy()
    t = np.arange(len(wave)) / SAMPLE_RATE
    lfo = np.sin(2 * np.pi * rate_hz * t)
    delay_samples = (depth_ms / 1000 * SAMPLE_RATE * (1 + lfo) / 2).astype(int)

    result = wave.copy()
    for i in range(len(wave)):
        delay = min(delay_samples[i], i)
        if delay > 0:
            result[i] = wave[i] * (1 - mix) + wave[i - delay] * mix

    return result


# ============================================================================
# Internal Helpers
# ============================================================================

def _require_numpy():
    """Raise ImportError if numpy is not available."""
    if not HAS_NUMPY:
        raise ImportError(
            "numpy and scipy are required for audio synthesis. "
            "Install with: pip install numpy scipy"
        )
