"""
Override - Audio Synthesis

Generates SFX and music using numpy/scipy synthesis.
"""

from pathlib import Path
from typing import List, Tuple
import math

# Try to import numpy/scipy, but make module loadable without them
try:
    import numpy as np
    from scipy.io import wavfile
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None


SAMPLE_RATE = 22050  # Lower for smaller files


def check_numpy():
    """Check if numpy is available, raise error if not."""
    if not HAS_NUMPY:
        raise ImportError(
            "numpy and scipy are required for audio synthesis. "
            "Install with: pip install numpy scipy"
        )


def save_wav(samples: List[float], filepath: Path) -> None:
    """Save audio samples to WAV file."""
    check_numpy()

    # Convert to numpy array
    wave = np.array(samples, dtype=np.float32)

    # Normalize
    max_val = np.max(np.abs(wave))
    if max_val > 0:
        wave = wave / max_val * 0.9

    # Convert to 16-bit PCM
    wave_int = (wave * 32767).astype(np.int16)

    wavfile.write(str(filepath), SAMPLE_RATE, wave_int)


# =============================================================================
# OSCILLATORS
# =============================================================================

def sine(phase: float) -> float:
    """Sine wave oscillator."""
    return math.sin(phase * 2.0 * math.pi)


def square(phase: float) -> float:
    """Square wave oscillator."""
    return 1.0 if (phase % 1.0) < 0.5 else -1.0


def saw(phase: float) -> float:
    """Sawtooth wave oscillator."""
    return 2.0 * (phase % 1.0) - 1.0


def noise(seed: int) -> float:
    """Deterministic noise generator."""
    x = ((seed * 0x5851f42d) + 0x14057b7e) & 0xFFFFFFFF
    return (x / 0xFFFFFFFF) * 2.0 - 1.0


# =============================================================================
# ENVELOPE
# =============================================================================

def adsr(t: float, attack: float, decay: float, sustain: float, release: float, duration: float) -> float:
    """ADSR envelope generator."""
    if t < attack:
        return t / attack  # Attack
    elif t < attack + decay:
        return 1.0 - (1.0 - sustain) * ((t - attack) / decay)  # Decay
    elif t < duration - release:
        return sustain  # Sustain
    elif t < duration:
        return sustain * (1.0 - (t - (duration - release)) / release)  # Release
    else:
        return 0.0


# =============================================================================
# FILTER
# =============================================================================

def lpf(samples: List[float], cutoff: float) -> List[float]:
    """Simple low-pass filter."""
    rc = 1.0 / (cutoff * 2.0 * math.pi)
    dt = 1.0 / SAMPLE_RATE
    alpha = dt / (rc + dt)

    result = samples.copy()
    prev = result[0]
    for i in range(len(result)):
        result[i] = prev + alpha * (result[i] - prev)
        prev = result[i]

    return result


# =============================================================================
# SOUND EFFECTS
# =============================================================================

def sfx_footstep() -> List[float]:
    """Generate footstep sound."""
    duration = 0.08
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.005, 0.03, 0.0, 0.04, duration)
        buf.append(noise(i) * env * 0.3)

    return lpf(buf, 2000.0)


def sfx_footstep_sprint() -> List[float]:
    """Generate sprint footstep sound."""
    duration = 0.06
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.003, 0.02, 0.0, 0.03, duration)
        buf.append(noise(i) * env * 0.4)

    return lpf(buf, 3000.0)


def sfx_door_open() -> List[float]:
    """Generate door opening sound."""
    duration = 0.25
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.01, 0.1, 0.3, 0.14, duration)
        freq = 150.0 + t * 200.0  # Rising pitch
        phase = t * freq / SAMPLE_RATE
        sample = (sine(phase) * 0.5 + noise(i) * 0.3) * env * 0.5
        buf.append(sample)

    return lpf(buf, 1500.0)


def sfx_door_close() -> List[float]:
    """Generate door closing sound."""
    duration = 0.2
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.01, 0.05, 0.2, 0.13, duration)
        freq = 200.0 - t * 100.0  # Falling pitch
        phase = t * freq / SAMPLE_RATE
        sample = (sine(phase) * 0.6 + noise(i) * 0.4) * env * 0.6
        buf.append(sample)

    return lpf(buf, 1200.0)


def sfx_door_locked() -> List[float]:
    """Generate locked door buzz sound."""
    duration = 0.15
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.005, 0.05, 0.0, 0.09, duration)
        phase = t * 400.0
        sample = (square(phase) * 0.3 + noise(i) * 0.2) * env * 0.5
        buf.append(sample)

    return buf


def sfx_trap_spike() -> List[float]:
    """Generate spike trap activation sound."""
    duration = 0.3
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.01, 0.1, 0.1, 0.18, duration)
        freq = 800.0 - t * 600.0  # Metallic scrape
        phase = t * freq
        sample = (saw(phase) * 0.4 + noise(i) * 0.3) * env * 0.6
        buf.append(sample)

    return lpf(buf, 2500.0)


def sfx_trap_gas() -> List[float]:
    """Generate gas trap hissing sound."""
    duration = 0.5
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.05, 0.1, 0.6, 0.25, duration)
        sample = noise(i) * env * 0.4
        buf.append(sample)

    return lpf(buf, 4000.0)


def sfx_trap_laser() -> List[float]:
    """Generate laser trap sound."""
    duration = 0.4
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.02, 0.1, 0.5, 0.18, duration)
        freq = 880.0 + sine(t * 10.0) * 100.0  # Wobble
        phase = t * freq
        sample = (sine(phase) * 0.5 + square(phase * 0.5) * 0.2) * env * 0.5
        buf.append(sample)

    return buf


def sfx_pickup() -> List[float]:
    """Generate pickup/collect sound."""
    duration = 0.15
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.01, 0.05, 0.0, 0.09, duration)
        freq = 400.0 + t * 800.0  # Rising pitch
        phase = t * freq / SAMPLE_RATE
        sample = sine(phase) * env * 0.5
        buf.append(sample)

    return buf


def sfx_alert() -> List[float]:
    """Generate alert/warning sound."""
    duration = 0.4
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.01, 0.05, 0.7, 0.24, duration)
        # Two-tone alternating
        freq = 880.0 if (int(t * 8) % 2 == 0) else 660.0
        phase = t * freq / SAMPLE_RATE
        sample = square(phase) * env * 0.3
        buf.append(sample)

    return buf


def sfx_damage() -> List[float]:
    """Generate damage/hit sound."""
    duration = 0.12
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.003, 0.04, 0.0, 0.07, duration)
        sample = noise(i) * env * 0.5
        buf.append(sample)

    return lpf(buf, 1500.0)


def sfx_death() -> List[float]:
    """Generate death/defeat sound."""
    duration = 0.6
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.01, 0.2, 0.3, 0.29, duration)
        freq = 400.0 - t * 350.0  # Falling pitch
        phase = t * freq / SAMPLE_RATE
        sample = (sine(phase) * 0.4 + noise(i) * 0.3) * env * 0.5
        buf.append(sample)

    return lpf(buf, 800.0)


def sfx_ui_click() -> List[float]:
    """Generate UI click sound."""
    duration = 0.03
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.001, 0.01, 0.0, 0.01, duration)
        phase = t * 1200.0 / SAMPLE_RATE
        sample = square(phase) * env * 0.2
        buf.append(sample)

    return buf


def sfx_ui_hover() -> List[float]:
    """Generate UI hover sound."""
    duration = 0.02
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.001, 0.008, 0.0, 0.008, duration)
        phase = t * 800.0 / SAMPLE_RATE
        sample = sine(phase) * env * 0.15
        buf.append(sample)

    return buf


def sfx_victory() -> List[float]:
    """Generate victory fanfare."""
    duration = 0.6
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    # Arpeggio notes
    notes = [523.25, 659.25, 783.99]  # C5, E5, G5

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.01, 0.15, 0.4, 0.34, duration)

        # Cycle through notes
        note_idx = int(t * 6) % 3
        freq = notes[note_idx]
        phase = t * freq / SAMPLE_RATE
        sample = sine(phase) * env * 0.4
        buf.append(sample)

    return buf


def sfx_defeat() -> List[float]:
    """Generate defeat sound."""
    duration = 0.8
    num_samples = int(duration * SAMPLE_RATE)
    buf = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = adsr(t, 0.02, 0.3, 0.2, 0.38, duration)
        freq = 300.0 - t * 200.0  # Falling
        phase = t * freq / SAMPLE_RATE
        sample = (sine(phase) * 0.3 + sine(phase * 0.5) * 0.2) * env * 0.5
        buf.append(sample)

    return lpf(buf, 600.0)


def generate_all_sfx(output_dir: Path) -> int:
    """
    Generate all SFX and save to output directory.

    Args:
        output_dir: Output directory

    Returns:
        Number of SFX files generated
    """
    check_numpy()

    sfx_dir = output_dir / "sfx"
    sfx_dir.mkdir(exist_ok=True)

    sfx_generators = {
        "footstep": sfx_footstep,
        "footstep_sprint": sfx_footstep_sprint,
        "door_open": sfx_door_open,
        "door_close": sfx_door_close,
        "door_locked": sfx_door_locked,
        "trap_spike": sfx_trap_spike,
        "trap_gas": sfx_trap_gas,
        "trap_laser": sfx_trap_laser,
        "pickup": sfx_pickup,
        "alert": sfx_alert,
        "damage": sfx_damage,
        "death": sfx_death,
        "ui_click": sfx_ui_click,
        "ui_hover": sfx_ui_hover,
        "victory": sfx_victory,
        "defeat": sfx_defeat,
    }

    count = 0
    for name, generator in sfx_generators.items():
        samples = generator()
        filepath = sfx_dir / f"{name}.wav"
        save_wav(samples, filepath)
        print(f"  Exported: sfx/{name}.wav")
        count += 1

    return count
