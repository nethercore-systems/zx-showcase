#!/usr/bin/env python3
"""
Sound Parser - Interprets .spec.py files and generates audio.

Deterministic audio generation from declarative specs. Follows the same pattern
as animation.py for animations.

Usage:
    python sound_parser.py sfx laser.spec.py output.wav
    python sound_parser.py instrument bass.spec.py output.wav
    python sound_parser.py track boss_theme.spec.py output.xm

Arguments:
    mode          - One of: sfx, instrument, track
    spec_path     - Path to .spec.py file
    output_path   - Output file path (.wav for sfx/instrument, .xm/.it for track)

Example:
    python sound_parser.py sfx .studio/sounds/laser.spec.py generated/audio/laser.wav
"""

import sys
import os
import struct
import numpy as np
from scipy.signal import butter, lfilter
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

SAMPLE_RATE = 22050


# =============================================================================
# SPEC LOADING
# =============================================================================

def load_spec(spec_path: str) -> Dict[str, Any]:
    """Load spec from .spec.py file via exec()."""
    with open(spec_path, 'r') as f:
        code = f.read()

    namespace = {}
    exec(code, namespace)

    # Return whichever dict is present
    for key in ['SOUND', 'INSTRUMENT', 'TRACK']:
        if key in namespace:
            return namespace[key]

    raise ValueError(f"No SOUND/INSTRUMENT/TRACK dict found in {spec_path}")


# =============================================================================
# WAVEFORM GENERATORS
# =============================================================================

def sine_wave(freq: float, duration: float, t: np.ndarray = None) -> np.ndarray:
    """Generate pure sine wave."""
    if t is None:
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    return np.sin(2 * np.pi * freq * t)


def square_wave(freq: float, duration: float, duty: float = 0.5) -> np.ndarray:
    """Generate square/pulse wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    phase = (freq * t) % 1.0
    return np.where(phase < duty, 1.0, -1.0).astype(np.float32)


def saw_wave(freq: float, duration: float) -> np.ndarray:
    """Generate antialiased sawtooth wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    output = np.zeros_like(t)
    num_harmonics = min(20, int(SAMPLE_RATE / 2 / freq))
    for h in range(1, num_harmonics + 1):
        output += np.sin(2 * np.pi * freq * h * t) / h
    return (output * 2 / np.pi).astype(np.float32)


def triangle_wave(freq: float, duration: float) -> np.ndarray:
    """Generate triangle wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    phase = (freq * t) % 1.0
    return (4 * np.abs(phase - 0.5) - 1).astype(np.float32)


def white_noise(duration: float) -> np.ndarray:
    """Generate white noise."""
    num_samples = int(SAMPLE_RATE * duration)
    return np.random.randn(num_samples).astype(np.float32)


def pink_noise(duration: float) -> np.ndarray:
    """Generate pink noise (1/f spectrum)."""
    num_samples = int(SAMPLE_RATE * duration)
    white = np.random.randn(num_samples)
    fft = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(num_samples)
    freqs[0] = 1
    fft = fft / np.sqrt(freqs)
    pink = np.fft.irfft(fft, num_samples)
    return (pink / (np.max(np.abs(pink)) + 1e-10)).astype(np.float32)


def brown_noise(duration: float) -> np.ndarray:
    """Generate brown noise (random walk)."""
    num_samples = int(SAMPLE_RATE * duration)
    white = np.random.randn(num_samples)
    brown = np.cumsum(white)
    brown -= np.mean(brown)
    return (brown / (np.max(np.abs(brown)) + 1e-10)).astype(np.float32)


# =============================================================================
# SYNTHESIS MODULES
# =============================================================================

def fm_synth(
    carrier_freq: float,
    duration: float,
    mod_ratio: float = 1.0,
    mod_index: float = 2.0,
    index_decay: float = 5.0
) -> np.ndarray:
    """FM synthesis with decaying modulation index."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    mod_freq = carrier_freq * mod_ratio

    # Decaying modulation index for natural FM sound
    index = mod_index * np.exp(-t * index_decay)

    modulator = np.sin(2 * np.pi * mod_freq * t)
    carrier = np.sin(2 * np.pi * carrier_freq * t + index * modulator)

    return carrier.astype(np.float32)


def karplus_strong(
    freq: float,
    duration: float,
    damping: float = 0.996,
    brightness: float = 0.7
) -> np.ndarray:
    """Karplus-Strong plucked string synthesis."""
    num_samples = int(SAMPLE_RATE * duration)
    delay_length = max(2, int(SAMPLE_RATE / freq))

    # Initialize with filtered noise
    noise = np.random.randn(delay_length)
    if brightness < 1.0:
        cutoff = 0.1 + brightness * 0.8
        b, a = butter(2, cutoff, btype='low')
        noise = lfilter(b, a, noise)

    delay_line = noise.copy()
    output = np.zeros(num_samples)
    idx = 0

    for i in range(num_samples):
        output[i] = delay_line[idx]
        next_idx = (idx + 1) % delay_length
        averaged = 0.5 * (delay_line[idx] + delay_line[next_idx]) * damping
        delay_line[idx] = averaged
        idx = (idx + 1) % delay_length

    return output.astype(np.float32)


def noise_burst(duration: float, color: str = 'white') -> np.ndarray:
    """Generate noise burst."""
    if color == 'pink':
        return pink_noise(duration)
    elif color == 'brown':
        return brown_noise(duration)
    return white_noise(duration)


def pitched_body(
    duration: float,
    start_freq: float,
    end_freq: float
) -> np.ndarray:
    """Pitched sine with frequency sweep (for kicks/toms)."""
    num_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, num_samples)

    # Exponential frequency envelope
    freq = end_freq + (start_freq - end_freq) * np.exp(-t * 30)

    # Integrate frequency to get phase
    phase = np.cumsum(2 * np.pi * freq / SAMPLE_RATE)
    return np.sin(phase).astype(np.float32)


def metallic_partials(
    duration: float,
    base_freq: float,
    num_partials: int = 6,
    inharmonicity: float = 1.414
) -> np.ndarray:
    """Inharmonic partials for metallic sounds."""
    num_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, num_samples)
    output = np.zeros(num_samples)

    for i in range(num_partials):
        freq = base_freq * (inharmonicity ** i)
        if freq < SAMPLE_RATE / 2:
            amp = 1.0 / (i + 1)
            output += np.sin(2 * np.pi * freq * t) * amp

    return output.astype(np.float32)


def harmonics_synth(
    freqs: List[float],
    amplitudes: List[float],
    duration: float
) -> np.ndarray:
    """Additive synthesis from harmonics."""
    num_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, num_samples)
    output = np.zeros(num_samples)

    for freq, amp in zip(freqs, amplitudes):
        if freq < SAMPLE_RATE / 2:
            output += np.sin(2 * np.pi * freq * t) * amp

    return output.astype(np.float32)


# =============================================================================
# ENVELOPES
# =============================================================================

def adsr_envelope(
    t: np.ndarray,
    attack: float = 0.01,
    decay: float = 0.1,
    sustain: float = 0.7,
    release: float = 0.2
) -> np.ndarray:
    """Generate ADSR envelope."""
    env = np.zeros_like(t)
    duration = t[-1]

    attack_end = attack
    decay_end = attack_end + decay
    release_start = max(decay_end, duration - release)

    for i, time in enumerate(t):
        if time < attack_end:
            env[i] = time / attack if attack > 0 else 1.0
        elif time < decay_end:
            progress = (time - attack_end) / decay if decay > 0 else 1.0
            env[i] = 1.0 - (1.0 - sustain) * progress
        elif time < release_start:
            env[i] = sustain
        else:
            progress = (time - release_start) / release if release > 0 else 1.0
            env[i] = sustain * (1.0 - min(1.0, progress))

    return env


def percussive_envelope(t: np.ndarray, attack: float = 0.001, decay: float = 0.1) -> np.ndarray:
    """Fast attack, exponential decay envelope."""
    attack_env = 1 - np.exp(-t / attack)
    decay_env = np.exp(-t / decay)
    return attack_env * decay_env


# =============================================================================
# FILTERS
# =============================================================================

def apply_filter(
    signal: np.ndarray,
    filter_cfg: Dict[str, Any]
) -> np.ndarray:
    """Apply filter based on config dict."""
    filter_type = filter_cfg.get('type', 'lowpass')
    cutoff = filter_cfg.get('cutoff', 2000)
    cutoff_end = filter_cfg.get('cutoff_end')
    q = filter_cfg.get('q', 1.0)

    nyquist = SAMPLE_RATE / 2

    # Handle filter sweep
    if cutoff_end is not None and cutoff_end != cutoff:
        return filter_sweep(signal, cutoff, cutoff_end, filter_type)

    # Static filter
    norm_cutoff = max(0.01, min(cutoff / nyquist, 0.99))

    if filter_type == 'lowpass':
        b, a = butter(2, norm_cutoff, btype='low')
    elif filter_type == 'highpass':
        b, a = butter(2, norm_cutoff, btype='high')
    elif filter_type == 'bandpass':
        low = filter_cfg.get('cutoff_low', cutoff * 0.5)
        high = filter_cfg.get('cutoff_high', cutoff * 2.0)
        low_norm = max(0.01, min(low / nyquist, 0.99))
        high_norm = max(0.01, min(high / nyquist, 0.99))
        if low_norm >= high_norm:
            return signal
        b, a = butter(2, [low_norm, high_norm], btype='band')
    else:
        return signal

    return lfilter(b, a, signal)


def filter_sweep(
    signal: np.ndarray,
    start_cutoff: float,
    end_cutoff: float,
    filter_type: str = 'lowpass'
) -> np.ndarray:
    """Apply time-varying filter sweep."""
    num_samples = len(signal)
    output = np.zeros(num_samples, dtype=np.float32)
    chunk_size = 256

    btype = 'low' if filter_type == 'lowpass' else 'high'

    for i in range(0, num_samples, chunk_size):
        end = min(i + chunk_size, num_samples)
        progress = i / num_samples
        cutoff = start_cutoff * (1 - progress) + end_cutoff * progress

        nyquist = SAMPLE_RATE / 2
        norm_cutoff = max(0.01, min(cutoff / nyquist, 0.99))

        b, a = butter(2, norm_cutoff, btype=btype)
        output[i:end] = lfilter(b, a, signal[i:end])

    return output


# =============================================================================
# SFX GENERATION
# =============================================================================

def generate_layer(layer: Dict[str, Any], duration: float, t: np.ndarray) -> np.ndarray:
    """Generate a single layer from spec."""
    layer_type = layer.get('type', 'sine')
    layer_duration = layer.get('duration', duration)
    amplitude = layer.get('amplitude', 1.0)

    # Generate base waveform
    if layer_type == 'sine':
        freq = layer.get('freq', 440)
        freq_end = layer.get('freq_end')
        if freq_end is not None:
            # Frequency sweep
            num_samples = int(SAMPLE_RATE * layer_duration)
            lt = np.linspace(0, layer_duration, num_samples)
            freq_env = freq + (freq_end - freq) * (lt / layer_duration)
            phase = np.cumsum(2 * np.pi * freq_env / SAMPLE_RATE)
            signal = np.sin(phase)
        else:
            signal = sine_wave(freq, layer_duration)

    elif layer_type == 'square':
        freq = layer.get('freq', 440)
        duty = layer.get('duty', 0.5)
        signal = square_wave(freq, layer_duration, duty)

    elif layer_type == 'saw':
        freq = layer.get('freq', 440)
        signal = saw_wave(freq, layer_duration)

    elif layer_type == 'triangle':
        freq = layer.get('freq', 440)
        signal = triangle_wave(freq, layer_duration)

    elif layer_type == 'noise_burst':
        color = layer.get('color', 'white')
        signal = noise_burst(layer_duration, color)

    elif layer_type == 'fm_synth':
        signal = fm_synth(
            carrier_freq=layer.get('carrier_freq', 440),
            duration=layer_duration,
            mod_ratio=layer.get('mod_ratio', 1.0),
            mod_index=layer.get('mod_index', 2.0),
            index_decay=layer.get('index_decay', 5.0)
        )

    elif layer_type == 'karplus':
        signal = karplus_strong(
            freq=layer.get('freq', 440),
            duration=layer_duration,
            damping=layer.get('damping', 0.996),
            brightness=layer.get('brightness', 0.7)
        )

    elif layer_type == 'pitched_body':
        signal = pitched_body(
            duration=layer_duration,
            start_freq=layer.get('start_freq', 200),
            end_freq=layer.get('end_freq', 50)
        )

    elif layer_type == 'metallic':
        signal = metallic_partials(
            duration=layer_duration,
            base_freq=layer.get('base_freq', 800),
            num_partials=layer.get('num_partials', 6),
            inharmonicity=layer.get('inharmonicity', 1.414)
        )

    elif layer_type == 'harmonics':
        signal = harmonics_synth(
            freqs=layer.get('freqs', [440]),
            amplitudes=layer.get('amplitudes', [1.0]),
            duration=layer_duration
        )

    else:
        # Default to sine
        signal = sine_wave(440, layer_duration)

    # Apply per-layer envelope if specified
    if 'envelope' in layer:
        env_cfg = layer['envelope']
        lt = np.linspace(0, layer_duration, len(signal))
        env = adsr_envelope(
            lt,
            attack=env_cfg.get('attack', 0.01),
            decay=env_cfg.get('decay', 0.1),
            sustain=env_cfg.get('sustain', 0.7),
            release=env_cfg.get('release', 0.2)
        )
        signal = signal * env

    # Apply per-layer filter if specified
    if 'filter' in layer:
        signal = apply_filter(signal, layer['filter'])

    # Apply amplitude
    signal = signal * amplitude

    # Handle delay (offset in time)
    delay = layer.get('delay', 0.0)
    if delay > 0:
        delay_samples = int(SAMPLE_RATE * delay)
        signal = np.pad(signal, (delay_samples, 0))[:len(t)]

    # Pad or trim to match duration
    target_samples = len(t)
    if len(signal) < target_samples:
        signal = np.pad(signal, (0, target_samples - len(signal)))
    elif len(signal) > target_samples:
        signal = signal[:target_samples]

    return signal.astype(np.float32)


def generate_sfx(spec: Dict[str, Any]) -> np.ndarray:
    """Generate SFX from SOUND spec."""
    sound = spec.get('sound', spec)

    global SAMPLE_RATE
    duration = sound.get('duration', 1.0)
    sample_rate = sound.get('sample_rate', SAMPLE_RATE)
    SAMPLE_RATE = sample_rate

    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples)

    # Generate and mix layers
    layers = sound.get('layers', [])
    if not layers:
        # Default single sine layer
        layers = [{'type': 'sine', 'freq': 440}]

    mixed = np.zeros(num_samples, dtype=np.float32)
    for layer in layers:
        layer_signal = generate_layer(layer, duration, t)
        mixed += layer_signal

    # Apply master envelope
    if 'envelope' in sound:
        env_cfg = sound['envelope']
        env = adsr_envelope(
            t,
            attack=env_cfg.get('attack', 0.01),
            decay=env_cfg.get('decay', 0.1),
            sustain=env_cfg.get('sustain', 0.7),
            release=env_cfg.get('release', 0.2)
        )
        mixed = mixed * env

    # Apply master filter
    if 'master_filter' in sound:
        mixed = apply_filter(mixed, sound['master_filter'])

    # Normalize
    if sound.get('normalize', True):
        peak_db = sound.get('peak_db', -3.0)
        peak_linear = 10 ** (peak_db / 20.0)
        max_val = np.max(np.abs(mixed))
        if max_val > 0:
            mixed = mixed / max_val * peak_linear

    return mixed


# =============================================================================
# INSTRUMENT GENERATION
# =============================================================================

def note_to_freq(note: str) -> float:
    """Convert note name to frequency. E.g., 'C4' -> 261.63"""
    note_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

    if isinstance(note, (int, float)):
        # MIDI note number
        return 440.0 * (2 ** ((note - 69) / 12))

    note = note.upper()
    if '#' in note:
        base = note[0]
        octave = int(note[2:])
        semitone = note_map[base] + 1
    elif 'B' in note and len(note) > 2 and note[1] == 'B':
        # Flat
        base = note[0]
        octave = int(note[2:])
        semitone = note_map[base] - 1
    else:
        base = note[0]
        octave = int(note[1:])
        semitone = note_map[base]

    midi = 12 + octave * 12 + semitone
    return 440.0 * (2 ** ((midi - 69) / 12))


def generate_instrument(spec: Dict[str, Any]) -> np.ndarray:
    """Generate instrument sample from INSTRUMENT spec."""
    global SAMPLE_RATE
    inst = spec.get('instrument', spec)

    base_note = inst.get('base_note', 'C4')
    freq = note_to_freq(base_note)
    sample_rate = inst.get('sample_rate', SAMPLE_RATE)
    SAMPLE_RATE = sample_rate

    output_cfg = inst.get('output', {})
    duration = output_cfg.get('duration', 1.0)

    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples)

    # Get synthesis type
    synth = inst.get('synthesis', {'type': 'karplus_strong'})
    synth_type = synth.get('type', 'karplus_strong')

    # Generate based on synthesis type
    if synth_type == 'karplus_strong':
        signal = karplus_strong(
            freq=freq,
            duration=duration,
            damping=synth.get('damping', 0.996),
            brightness=synth.get('brightness', 0.7)
        )

    elif synth_type == 'fm':
        # Simple FM for now
        operators = synth.get('operators', [])
        if operators:
            signal = fm_synth(
                carrier_freq=freq,
                duration=duration,
                mod_ratio=operators[0].get('ratio', 1.0) if len(operators) > 1 else 1.0,
                mod_index=synth.get('index', 2.0),
                index_decay=synth.get('index_decay', 5.0)
            )
        else:
            signal = fm_synth(freq, duration)

    elif synth_type == 'subtractive':
        oscs = synth.get('oscillators', [{'waveform': 'saw'}])
        signal = np.zeros(num_samples, dtype=np.float32)

        for osc in oscs:
            waveform = osc.get('waveform', 'saw')
            detune = osc.get('detune', 0)  # cents
            osc_freq = freq * (2 ** (detune / 1200))

            if waveform == 'saw':
                signal += saw_wave(osc_freq, duration)
            elif waveform == 'square':
                signal += square_wave(osc_freq, duration, osc.get('duty', 0.5))
            elif waveform == 'sine':
                signal += sine_wave(osc_freq, duration)
            elif waveform == 'triangle':
                signal += triangle_wave(osc_freq, duration)

        signal /= len(oscs)

        # Apply filter
        if 'filter' in synth:
            signal = apply_filter(signal, synth['filter'])

    elif synth_type == 'additive':
        partials = synth.get('partials', [(1.0, 1.0)])  # (ratio, amplitude)
        signal = np.zeros(num_samples, dtype=np.float32)

        for ratio, amp in partials:
            partial_freq = freq * ratio
            if partial_freq < sample_rate / 2:
                signal += sine_wave(partial_freq, duration, t) * amp

    else:
        # Default to Karplus-Strong
        signal = karplus_strong(freq, duration)

    # Ensure signal is right length
    if len(signal) < num_samples:
        signal = np.pad(signal, (0, num_samples - len(signal)))
    elif len(signal) > num_samples:
        signal = signal[:num_samples]

    # Apply amplitude envelope
    if 'envelope' in inst:
        env_cfg = inst['envelope']
        env = adsr_envelope(
            t,
            attack=env_cfg.get('attack', 0.01),
            decay=env_cfg.get('decay', 0.3),
            sustain=env_cfg.get('sustain', 0.4),
            release=env_cfg.get('release', 0.2)
        )
        signal = signal * env

    # Apply pitch envelope if specified
    if 'pitch_envelope' in inst:
        # Note: This is a simplification - proper pitch envelope needs
        # to be applied during synthesis, not after
        pass

    # Normalize
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val * 0.9

    return signal.astype(np.float32)


# =============================================================================
# WAV OUTPUT
# =============================================================================

def write_wav(path: str, signal: np.ndarray, sample_rate: int = SAMPLE_RATE, bits: int = 16):
    """Write signal to WAV file."""
    # Ensure directory exists
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    # Convert to appropriate bit depth
    if bits == 8:
        samples = np.clip(signal * 127, -128, 127).astype(np.int8)
        bytes_per_sample = 1
    else:
        samples = np.clip(signal * 32767, -32768, 32767).astype(np.int16)
        bytes_per_sample = 2

    num_samples = len(samples)
    num_channels = 1

    with open(path, 'wb') as f:
        # RIFF header
        f.write(b'RIFF')
        data_size = num_samples * bytes_per_sample
        file_size = 36 + data_size
        f.write(struct.pack('<I', file_size))
        f.write(b'WAVE')

        # fmt chunk
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))  # Chunk size
        f.write(struct.pack('<H', 1))   # Audio format (PCM)
        f.write(struct.pack('<H', num_channels))
        f.write(struct.pack('<I', sample_rate))
        byte_rate = sample_rate * num_channels * bytes_per_sample
        f.write(struct.pack('<I', byte_rate))
        block_align = num_channels * bytes_per_sample
        f.write(struct.pack('<H', block_align))
        f.write(struct.pack('<H', bits))

        # data chunk
        f.write(b'data')
        f.write(struct.pack('<I', data_size))
        f.write(samples.tobytes())

    print(f"Wrote {path} ({num_samples} samples, {sample_rate}Hz, {bits}-bit)")


# =============================================================================
# TRACK GENERATION (XM/IT)
# =============================================================================

def generate_track(spec: Dict[str, Any], output_path: str, spec_dir: str):
    """
    Generate tracker module from TRACK spec.

    This is a simplified implementation. For full XM/IT support,
    see tracker-music/skills/xm-format/ and it-format/.
    """
    track = spec.get('track', spec)

    fmt = track.get('format', 'xm')
    name = track.get('name', 'Untitled')

    # Generate instrument samples first
    instrument_specs = track.get('instruments', [])
    samples = []

    for inst_path in instrument_specs:
        # Resolve path relative to spec directory
        if not os.path.isabs(inst_path):
            inst_path = os.path.join(spec_dir, inst_path)

        if os.path.exists(inst_path):
            inst_spec = load_spec(inst_path)
            sample = generate_instrument(inst_spec)
            samples.append(sample)
        else:
            print(f"Warning: Instrument spec not found: {inst_path}")
            # Generate a default sine wave
            samples.append(sine_wave(440, 0.5))

    # For now, output a placeholder message
    # Full XM/IT generation requires the tracker-music plugin's writers
    print(f"Track generation for {fmt.upper()} format")
    print(f"  Name: {name}")
    print(f"  BPM: {track.get('bpm', 120)}")
    print(f"  Channels: {track.get('channels', 8)}")
    print(f"  Instruments: {len(samples)}")
    print(f"  Patterns: {len(track.get('patterns', []))}")

    # Write instrument samples as individual WAVs
    sample_dir = Path(output_path).parent / 'samples'
    sample_dir.mkdir(parents=True, exist_ok=True)

    for i, sample in enumerate(samples):
        sample_path = sample_dir / f"inst_{i:02d}.wav"
        write_wav(str(sample_path), sample)

    print(f"\nNote: Full XM/IT generation requires tracker-music plugin.")
    print(f"Instrument samples written to: {sample_dir}")

    # TODO: Integrate with tracker-music/skills/xm-format/lib/xm_writer.py
    # for full module generation


# =============================================================================
# MAIN
# =============================================================================

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1]
    spec_path = sys.argv[2]
    output_path = sys.argv[3]

    print(f"Loading spec: {spec_path}")
    spec = load_spec(spec_path)
    spec_dir = os.path.dirname(os.path.abspath(spec_path))

    if mode == 'sfx':
        signal = generate_sfx(spec)
        sound = spec.get('sound', spec)
        sample_rate = sound.get('sample_rate', SAMPLE_RATE)
        write_wav(output_path, signal, sample_rate)

    elif mode == 'instrument':
        signal = generate_instrument(spec)
        inst = spec.get('instrument', spec)
        sample_rate = inst.get('sample_rate', SAMPLE_RATE)
        output_cfg = inst.get('output', {})
        bits = output_cfg.get('bit_depth', 16)
        write_wav(output_path, signal, sample_rate, bits)

    elif mode == 'track':
        generate_track(spec, output_path, spec_dir)

    else:
        print(f"Unknown mode: {mode}")
        print("Valid modes: sfx, instrument, track")
        sys.exit(1)

    print("Done!")


if __name__ == "__main__":
    main()
