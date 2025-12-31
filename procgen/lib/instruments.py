"""
Instrument sample synthesis for XM tracker modules.

Provides functions to generate instrument samples (drums, synths, etc.)
that can be embedded in XM files or saved as WAV.
"""

from typing import Dict, Optional
from .synthesis import (
    SAMPLE_RATE,
    sine_wave, square_wave, triangle_wave, sawtooth_wave,
    noise_white, noise_pink,
    apply_adsr, apply_exponential_decay,
    lowpass, highpass, bandpass,
    normalize, mix, fm_wave,
    ADSREnvelope,
)

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None


# ============================================================================
# Drum Instruments
# ============================================================================

def synth_kick(
    pitch_start: float = 150,
    pitch_end: float = 40,
    decay_rate: float = 8,
    click_freq: float = 1000,
    click_amount: float = 0.2,
    duration: float = 0.3
) -> "np.ndarray":
    """
    Synthesize punchy kick drum with pitch drop.

    Args:
        pitch_start: Initial pitch (Hz)
        pitch_end: Final pitch (Hz)
        decay_rate: Amplitude decay rate
        click_freq: Transient click frequency (Hz)
        click_amount: Click volume (0-1)
        duration: Total duration (seconds)
    """
    _require_numpy()
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples, False)

    # Pitch envelope: exponential drop
    freq = pitch_start * np.exp(-20 * t) + pitch_end
    wave = 0.8 * np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE)

    # Add click transient
    if click_amount > 0:
        click = sine_wave(click_freq, 0.01, click_amount)
        click = apply_exponential_decay(click, 50)
        wave[:len(click)] += click

    return wave * np.exp(-decay_rate * t)


def synth_snare(
    body_freq: float = 180,
    noise_amount: float = 0.5,
    body_decay: float = 15,
    noise_decay: float = 10,
    duration: float = 0.25
) -> "np.ndarray":
    """
    Synthesize snare drum with body and noise.

    Args:
        body_freq: Body tone frequency (Hz)
        noise_amount: Noise layer volume (0-1)
        body_decay: Body decay rate
        noise_decay: Noise decay rate
        duration: Total duration (seconds)
    """
    _require_numpy()
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    body = 0.4 * np.sin(2 * np.pi * body_freq * t) * np.exp(-body_decay * t)
    snare_noise = noise_white(duration, noise_amount) * np.exp(-noise_decay * t)

    return body + snare_noise


def synth_hihat(closed: bool = True, duration: float = None) -> "np.ndarray":
    """
    Synthesize hi-hat (closed or open).

    Args:
        closed: True for closed hi-hat, False for open
        duration: Override duration (seconds)
    """
    _require_numpy()
    dur = duration or (0.08 if closed else 0.4)
    env = ADSREnvelope(
        attack=0.001,
        decay=0.02,
        sustain=0.3 if closed else 0.5,
        release=0.05 if closed else 0.3
    )
    wave = noise_white(dur, 0.6)
    wave = highpass(wave, 5000)
    return apply_adsr(wave, env)


def synth_clap(duration: float = 0.2) -> "np.ndarray":
    """Synthesize clap sound with multiple bursts."""
    _require_numpy()
    waves = []
    for i in range(4):
        delay = i * 0.008
        burst = noise_white(0.02, 0.5)
        burst = bandpass(burst, 1000, 3500)
        burst = apply_exponential_decay(burst, 30)
        # Pad with delay
        padded = np.zeros(int(SAMPLE_RATE * duration))
        start = int(delay * SAMPLE_RATE)
        end = min(start + len(burst), len(padded))
        padded[start:end] = burst[:end - start] * (1 - i * 0.2)
        waves.append(padded)

    result = mix(*waves)
    return apply_adsr(result, ADSREnvelope(0.001, 0.05, 0.2, 0.1))


def synth_tom(
    pitch: float = 100,
    duration: float = 0.3
) -> "np.ndarray":
    """Synthesize tom drum."""
    _require_numpy()
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Pitch drop
    freq = pitch * np.exp(-5 * t) + pitch * 0.5
    wave = 0.7 * np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE)

    return wave * np.exp(-8 * t)


def synth_cymbal(duration: float = 1.5) -> "np.ndarray":
    """Synthesize crash cymbal."""
    _require_numpy()
    wave = noise_white(duration, 0.6)
    wave = highpass(wave, 3000)

    # Add metallic tone
    tone = mix(
        sine_wave(7000, duration, 0.1),
        sine_wave(9000, duration, 0.08),
        sine_wave(11000, duration, 0.05)
    )
    wave[:len(tone)] += tone

    return apply_adsr(wave, ADSREnvelope(0.005, 0.1, 0.4, 0.8))


# ============================================================================
# Synth Instruments
# ============================================================================

def synth_bass(
    base_freq: float = 55,
    detune_cents: float = 8,
    waveform: str = "sawtooth",
    filter_cutoff: float = 300,
    duration: float = 0.5
) -> "np.ndarray":
    """
    Synthesize detuned bass sound.

    Args:
        base_freq: Base frequency (Hz)
        detune_cents: Detune amount in cents
        waveform: "sawtooth" or "square"
        filter_cutoff: Lowpass filter cutoff (Hz)
        duration: Duration (seconds)
    """
    _require_numpy()
    detune_ratio = 2 ** (detune_cents / 1200)

    wave_func = sawtooth_wave if waveform == "sawtooth" else square_wave

    wave1 = wave_func(base_freq, duration, 0.4)
    wave2 = wave_func(base_freq * detune_ratio, duration, 0.3)

    wave = wave1 + wave2
    wave = lowpass(wave, filter_cutoff)
    return apply_adsr(wave, ADSREnvelope(0.01, 0.1, 0.7, 0.15))


def synth_lead(
    base_freq: float = 440,
    waveform: str = "square",
    filter_cutoff: float = 4000,
    duration: float = 0.5
) -> "np.ndarray":
    """
    Synthesize bright lead synth.

    Args:
        base_freq: Base frequency (Hz)
        waveform: "square" or "sawtooth"
        filter_cutoff: Lowpass filter cutoff (Hz)
        duration: Duration (seconds)
    """
    _require_numpy()
    wave_func = square_wave if waveform == "square" else sawtooth_wave

    wave = wave_func(base_freq, duration, 0.3)
    # Add octave harmonic
    wave += sine_wave(base_freq * 2, duration, 0.1)

    wave = lowpass(wave, filter_cutoff)
    return apply_adsr(wave, ADSREnvelope(0.01, 0.1, 0.6, 0.2))


def synth_pad(
    base_freq: float = 220,
    detune_cents: float = 5,
    voices: int = 4,
    duration: float = 1.0
) -> "np.ndarray":
    """
    Synthesize lush pad with multiple detuned voices.

    Args:
        base_freq: Base frequency (Hz)
        detune_cents: Detune spread in cents
        voices: Number of voices
        duration: Duration (seconds)
    """
    _require_numpy()
    waves = []
    for i in range(voices):
        detune = (i - voices / 2) * detune_cents
        ratio = 2 ** (detune / 1200)
        waves.append(sine_wave(base_freq * ratio, duration, 0.25))

    wave = mix(*waves)
    wave += sine_wave(base_freq * 2, duration, 0.1)  # Octave
    wave = lowpass(wave, 1000)
    return apply_adsr(wave, ADSREnvelope(0.15, 0.2, 0.7, 0.3))


def synth_arp(
    base_freq: float = 330,
    waveform: str = "sawtooth",
    duration: float = 0.15
) -> "np.ndarray":
    """
    Synthesize short pluck for arpeggios.

    Args:
        base_freq: Base frequency (Hz)
        waveform: "sawtooth" or "triangle"
        duration: Duration (seconds)
    """
    _require_numpy()
    wave_func = sawtooth_wave if waveform == "sawtooth" else triangle_wave

    wave = wave_func(base_freq, duration, 0.5)
    wave = lowpass(wave, 2000)
    return apply_adsr(wave, ADSREnvelope(0.002, 0.03, 0.3, 0.1))


def synth_pluck(
    base_freq: float = 440,
    decay: float = 0.3,
    brightness: float = 0.5,
    duration: float = 0.5
) -> "np.ndarray":
    """
    Karplus-Strong style plucked string.

    Args:
        base_freq: Pitch frequency (Hz)
        decay: Decay time (seconds)
        brightness: 0-1, higher = brighter
        duration: Total duration (seconds)
    """
    _require_numpy()
    samples = int(SAMPLE_RATE * duration)
    period = int(SAMPLE_RATE / base_freq)

    # Initialize with noise burst
    wave = np.zeros(samples)
    wave[:period] = np.random.random(period) * 2 - 1

    # Karplus-Strong averaging filter
    damping = 0.5 + brightness * 0.4
    for i in range(period, samples):
        wave[i] = damping * (wave[i - period] + wave[i - period + 1]) / 2

    return wave * np.exp(-np.arange(samples) / (decay * SAMPLE_RATE))


def synth_fm_bell(
    base_freq: float = 880,
    duration: float = 0.8
) -> "np.ndarray":
    """Synthesize FM bell sound."""
    _require_numpy()
    wave = fm_wave(
        carrier_freq=base_freq,
        mod_freq=base_freq * 1.4,
        mod_index=3.0,
        duration=duration,
        amplitude=0.4
    )
    return apply_adsr(wave, ADSREnvelope(0.001, 0.2, 0.3, 0.4))


# ============================================================================
# Instrument Kits
# ============================================================================

def neon_drift_kit() -> Dict[str, "np.ndarray"]:
    """Return Neon Drift synthwave instrument kit."""
    return {
        "kick": synth_kick(pitch_start=150, pitch_end=40),
        "snare": synth_snare(body_freq=180, noise_amount=0.5),
        "hihat": synth_hihat(closed=True),
        "openhat": synth_hihat(closed=False),
        "bass": synth_bass(base_freq=55, waveform="sawtooth"),
        "lead": synth_lead(base_freq=440, waveform="square"),
        "pad": synth_pad(base_freq=220),
        "arp": synth_arp(base_freq=330, waveform="sawtooth"),
    }


def prism_survivors_kit() -> Dict[str, "np.ndarray"]:
    """Return Prism Survivors crystalline instrument kit."""
    return {
        "kick": synth_kick(pitch_start=120, pitch_end=50, click_amount=0.3),
        "snare": synth_snare(body_freq=200, noise_amount=0.4),
        "hihat": synth_hihat(closed=True, duration=0.06),
        "openhat": synth_hihat(closed=False, duration=0.3),
        "bass": synth_bass(base_freq=55, waveform="square", filter_cutoff=400),
        "lead": synth_lead(base_freq=440, waveform="sawtooth"),
        "chime": synth_fm_bell(base_freq=1200, duration=0.5),
        "arp": synth_arp(base_freq=440, waveform="triangle"),
    }


def lumina_depths_kit() -> Dict[str, "np.ndarray"]:
    """Return Lumina Depths ambient underwater kit."""
    _require_numpy()
    return {
        "sub_bass": synth_bass(base_freq=40, filter_cutoff=200, duration=1.0),
        "pad": synth_pad(base_freq=110, detune_cents=10, duration=2.0),
        "bell": synth_fm_bell(base_freq=880, duration=0.8),
        "drone": apply_adsr(
            lowpass(noise_white(2.0, 0.3), 200),
            ADSREnvelope(0.5, 0.3, 0.5, 0.5)
        ),
        "pluck": synth_pluck(base_freq=330, decay=0.5, brightness=0.3),
    }


def override_kit() -> Dict[str, "np.ndarray"]:
    """Return Override industrial instrument kit."""
    _require_numpy()
    return {
        "kick": synth_kick(pitch_start=80, pitch_end=30, decay_rate=12),
        "snare": synth_snare(body_freq=150, noise_amount=0.6, noise_decay=15),
        "hihat": synth_hihat(closed=True, duration=0.04),
        "clap": synth_clap(),
        "bass": synth_bass(base_freq=40, waveform="square", filter_cutoff=250),
        "lead": synth_lead(base_freq=330, waveform="sawtooth", filter_cutoff=2000),
        "stab": apply_adsr(
            lowpass(sawtooth_wave(220, 0.2, 0.5), 1500),
            ADSREnvelope(0.001, 0.05, 0.4, 0.1)
        ),
    }


# ============================================================================
# Internal Helpers
# ============================================================================

def _require_numpy():
    """Raise ImportError if numpy is not available."""
    if not HAS_NUMPY:
        raise ImportError(
            "numpy and scipy are required for instrument synthesis. "
            "Install with: pip install numpy scipy"
        )
