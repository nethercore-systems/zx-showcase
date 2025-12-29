#!/usr/bin/env python3
"""
Prism Survivors - Procedural SFX Generator

Generates all sound effects using numpy/scipy synthesis.
Does not require Blender.

Usage:
    python generate_sfx.py --game prism-survivors
    python generate_sfx.py --game prism-survivors --output path/to/audio
"""

import argparse
import sys
from pathlib import Path

try:
    import numpy as np
    from scipy.io import wavfile
except ImportError:
    print("Error: numpy and scipy are required.")
    print("Install with: pip install numpy scipy")
    sys.exit(1)


SAMPLE_RATE = 22050


def generate_sine_wave(freq: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
    """Generate a sine wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = amplitude * np.sin(2 * np.pi * freq * t)
    return wave


def generate_square_wave(freq: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
    """Generate a square wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = amplitude * np.sign(np.sin(2 * np.pi * freq * t))
    return wave


def generate_triangle_wave(freq: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
    """Generate a triangle wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = amplitude * (2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1)
    return wave


def generate_sawtooth_wave(freq: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
    """Generate a sawtooth wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = amplitude * (2 * (t * freq - np.floor(t * freq + 0.5)))
    return wave


def generate_noise(duration: float, amplitude: float = 0.3) -> np.ndarray:
    """Generate white noise."""
    samples = int(SAMPLE_RATE * duration)
    return amplitude * (np.random.random(samples) * 2 - 1)


def generate_pink_noise(duration: float, amplitude: float = 0.3) -> np.ndarray:
    """Generate pink noise (1/f noise)."""
    samples = int(SAMPLE_RATE * duration)
    white = np.random.random(samples) * 2 - 1

    # Simple pink noise approximation
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]

    from scipy.signal import lfilter
    pink = lfilter(b, a, white)
    return amplitude * pink / np.max(np.abs(pink))


def apply_envelope(
    wave: np.ndarray,
    attack: float,
    decay: float,
    sustain: float,
    release: float
) -> np.ndarray:
    """Apply ADSR envelope."""
    total_samples = len(wave)
    attack_samples = int(attack * SAMPLE_RATE)
    decay_samples = int(decay * SAMPLE_RATE)
    release_samples = int(release * SAMPLE_RATE)
    sustain_samples = max(0, total_samples - attack_samples - decay_samples - release_samples)

    envelope = np.zeros(total_samples)

    # Attack
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay
    decay_start = attack_samples
    decay_end = decay_start + decay_samples
    if decay_samples > 0 and decay_end <= total_samples:
        envelope[decay_start:decay_end] = np.linspace(1, sustain, decay_samples)

    # Sustain
    sustain_start = decay_end
    sustain_end = sustain_start + sustain_samples
    if sustain_end <= total_samples:
        envelope[sustain_start:sustain_end] = sustain

    # Release
    release_start = sustain_end
    if release_samples > 0 and release_start < total_samples:
        remaining = total_samples - release_start
        envelope[release_start:] = np.linspace(sustain, 0, remaining)

    return wave * envelope


def apply_lowpass(wave: np.ndarray, cutoff: float) -> np.ndarray:
    """Apply simple lowpass filter."""
    from scipy.signal import butter, filtfilt
    nyquist = SAMPLE_RATE / 2
    normalized_cutoff = min(cutoff / nyquist, 0.99)
    b, a = butter(2, normalized_cutoff, btype='low')
    return filtfilt(b, a, wave)


def apply_highpass(wave: np.ndarray, cutoff: float) -> np.ndarray:
    """Apply simple highpass filter."""
    from scipy.signal import butter, filtfilt
    nyquist = SAMPLE_RATE / 2
    normalized_cutoff = min(cutoff / nyquist, 0.99)
    b, a = butter(2, normalized_cutoff, btype='high')
    return filtfilt(b, a, wave)


def normalize(wave: np.ndarray) -> np.ndarray:
    """Normalize wave to -1 to 1 range."""
    max_val = np.max(np.abs(wave))
    if max_val > 0:
        return wave / max_val
    return wave


def save_wav(filepath: Path, wave: np.ndarray):
    """Save wave to WAV file."""
    wave = normalize(wave)
    wave_int = (wave * 32767 * 0.9).astype(np.int16)
    wavfile.write(filepath, SAMPLE_RATE, wave_int)
    print(f"  {filepath.name}")


# =============================================================================
# Prism Survivors SFX Recipes
# =============================================================================

def sfx_shoot() -> np.ndarray:
    """Quick crystalline blip for weapon fire."""
    # High pitched tone with quick decay
    tone1 = generate_sine_wave(880, 0.1, 0.5)
    tone2 = generate_sine_wave(1320, 0.08, 0.3)
    tone3 = generate_triangle_wave(1760, 0.06, 0.2)

    # Combine and pad
    wave = tone1.copy()
    wave[:len(tone2)] += tone2
    wave[:len(tone3)] += tone3

    wave = apply_envelope(wave, 0.005, 0.02, 0.3, 0.05)
    wave = apply_highpass(wave, 400)
    return wave


def sfx_hit() -> np.ndarray:
    """Impact sound for hitting enemies."""
    # Noise burst with low tone
    noise = generate_noise(0.1, 0.4)
    tone = generate_sine_wave(200, 0.1, 0.5)

    wave = noise + tone
    wave = apply_envelope(wave, 0.002, 0.03, 0.2, 0.05)
    wave = apply_lowpass(wave, 2000)
    return wave


def sfx_death() -> np.ndarray:
    """Glass shatter sound for enemy death."""
    # Noise with crystalline tones
    noise = generate_noise(0.35, 0.4)
    tone1 = generate_sine_wave(440, 0.3, 0.3)
    tone2 = generate_sine_wave(660, 0.25, 0.2)
    tone3 = generate_sine_wave(880, 0.2, 0.15)

    wave = noise.copy()
    wave[:len(tone1)] += tone1
    wave[:len(tone2)] += tone2
    wave[:len(tone3)] += tone3

    wave = apply_envelope(wave, 0.005, 0.1, 0.3, 0.15)
    return wave


def sfx_xp() -> np.ndarray:
    """Bright chime for XP gem pickup."""
    tone1 = generate_sine_wave(1200, 0.15, 0.5)
    tone2 = generate_sine_wave(1800, 0.12, 0.4)
    tone3 = generate_triangle_wave(2400, 0.1, 0.2)

    wave = tone1.copy()
    wave[:len(tone2)] += tone2
    wave[:len(tone3)] += tone3

    wave = apply_envelope(wave, 0.005, 0.02, 0.5, 0.1)
    return wave


def sfx_level_up() -> np.ndarray:
    """Triumphant chord for level up."""
    duration = 1.0

    # Major chord with harmonics
    frequencies = [440, 554, 659, 880, 1108, 1318]
    amplitudes = [0.3, 0.25, 0.2, 0.15, 0.1, 0.08]

    wave = np.zeros(int(SAMPLE_RATE * duration))
    for freq, amp in zip(frequencies, amplitudes):
        dur = duration - (freq - 440) / 2000
        tone = generate_sine_wave(freq, dur, amp)
        wave[:len(tone)] += tone

    wave = apply_envelope(wave, 0.05, 0.15, 0.6, 0.3)
    return wave


def sfx_hurt() -> np.ndarray:
    """Pain grunt for player damage."""
    noise = generate_noise(0.15, 0.3)
    tone = generate_sine_wave(300, 0.15, 0.4)
    tone2 = generate_sine_wave(200, 0.12, 0.3)

    wave = noise + tone
    wave[:len(tone2)] += tone2

    wave = apply_envelope(wave, 0.005, 0.05, 0.3, 0.08)
    wave = apply_lowpass(wave, 1500)
    return wave


def sfx_select() -> np.ndarray:
    """UI selection click."""
    tone1 = generate_sine_wave(600, 0.08, 0.5)
    tone2 = generate_sine_wave(800, 0.06, 0.4)

    wave = tone1.copy()
    wave[:len(tone2)] += tone2

    wave = apply_envelope(wave, 0.002, 0.02, 0.4, 0.03)
    return wave


def sfx_menu() -> np.ndarray:
    """Soft menu navigation tone."""
    wave = generate_sine_wave(500, 0.12, 0.5)
    wave = apply_envelope(wave, 0.01, 0.03, 0.4, 0.06)
    return wave


def sfx_back() -> np.ndarray:
    """Descending tone for back/cancel."""
    tone1 = generate_sine_wave(600, 0.1, 0.5)
    tone2 = generate_sine_wave(400, 0.1, 0.5)

    # Crossfade
    wave = np.zeros(int(SAMPLE_RATE * 0.15))
    wave[:len(tone1)] = tone1
    blend_start = len(tone1) // 2
    blend_end = min(blend_start + len(tone2), len(wave))
    actual_blend_len = blend_end - blend_start
    if actual_blend_len > 0:
        wave[blend_start:blend_end] += tone2[:actual_blend_len] * 0.7

    wave = apply_envelope(wave, 0.01, 0.03, 0.3, 0.05)
    return wave


def sfx_dash() -> np.ndarray:
    """Whoosh for dash ability."""
    noise = generate_noise(0.25, 0.5)
    noise = apply_highpass(noise, 500)
    noise = apply_lowpass(noise, 4000)
    noise = apply_envelope(noise, 0.02, 0.05, 0.2, 0.15)
    return noise


def sfx_coin() -> np.ndarray:
    """Metallic clink for coin pickup."""
    tone1 = generate_triangle_wave(1500, 0.12, 0.5)
    tone2 = generate_sine_wave(2000, 0.08, 0.3)
    tone3 = generate_sine_wave(2500, 0.06, 0.2)

    wave = tone1.copy()
    wave[:len(tone2)] += tone2
    wave[:len(tone3)] += tone3

    wave = apply_envelope(wave, 0.002, 0.02, 0.4, 0.08)
    return wave


def sfx_powerup() -> np.ndarray:
    """Ascending arpeggio for powerup."""
    duration = 0.5
    frequencies = [400, 500, 600, 800, 1000]

    wave = np.zeros(int(SAMPLE_RATE * duration))

    for i, freq in enumerate(frequencies):
        start = int(i * SAMPLE_RATE * 0.1)
        tone = generate_sine_wave(freq, 0.15, 0.4)
        tone = apply_envelope(tone, 0.01, 0.02, 0.5, 0.1)
        end = min(start + len(tone), len(wave))
        wave[start:end] += tone[:end - start]

    return wave


def sfx_combo_5() -> np.ndarray:
    """Brief sparkle for 5-kill combo."""
    tone1 = generate_sine_wave(1000, 0.1, 0.4)
    tone2 = generate_sine_wave(1500, 0.1, 0.3)
    wave = tone1 + tone2
    wave = apply_envelope(wave, 0.005, 0.02, 0.3, 0.05)
    return wave


def sfx_combo_10() -> np.ndarray:
    """Rising arpeggio for 10-kill combo."""
    wave = np.zeros(int(SAMPLE_RATE * 0.25))
    for i, freq in enumerate([800, 1000, 1200]):
        start = int(i * SAMPLE_RATE * 0.07)
        tone = generate_sine_wave(freq, 0.1, 0.4)
        tone = apply_envelope(tone, 0.005, 0.02, 0.5, 0.05)
        end = min(start + len(tone), len(wave))
        wave[start:end] += tone[:end - start]
    return wave


def sfx_combo_25() -> np.ndarray:
    """Triumphant chord for 25-kill combo."""
    freqs = [600, 750, 900, 1200]
    amps = [0.4, 0.35, 0.3, 0.25]
    wave = np.zeros(int(SAMPLE_RATE * 0.3))
    for freq, amp in zip(freqs, amps):
        tone = generate_sine_wave(freq, 0.3, amp)
        wave[:len(tone)] += tone
    wave = apply_envelope(wave, 0.01, 0.05, 0.6, 0.15)
    return wave


def sfx_combo_50() -> np.ndarray:
    """Full fanfare for 50-kill combo."""
    duration = 0.5
    wave = np.zeros(int(SAMPLE_RATE * duration))

    # Big chord
    freqs = [440, 554, 659, 880, 1108, 1318, 1760]
    for i, freq in enumerate(freqs):
        amp = 0.3 - i * 0.03
        tone = generate_sine_wave(freq, duration * 0.9, amp)
        wave[:len(tone)] += tone

    wave = apply_envelope(wave, 0.02, 0.1, 0.7, 0.2)
    return wave


def sfx_boss_spawn() -> np.ndarray:
    """Ominous rumble for boss appearance."""
    duration = 1.5

    # Low drone
    drone = generate_sine_wave(80, duration, 0.5)
    drone += generate_sine_wave(120, duration, 0.3)

    # Noise rumble
    noise = generate_noise(duration, 0.3)
    noise = apply_lowpass(noise, 200)

    wave = drone + noise
    wave = apply_envelope(wave, 0.3, 0.3, 0.5, 0.5)
    return wave


def sfx_wave_complete() -> np.ndarray:
    """Victory fanfare for completing a wave."""
    duration = 0.8

    # Ascending scale
    freqs = [523, 659, 784, 1047]  # C, E, G, C
    wave = np.zeros(int(SAMPLE_RATE * duration))

    for i, freq in enumerate(freqs):
        start = int(i * SAMPLE_RATE * 0.15)
        tone = generate_sine_wave(freq, 0.25, 0.4)
        tone = apply_envelope(tone, 0.01, 0.03, 0.6, 0.15)
        end = min(start + len(tone), len(wave))
        wave[start:end] += tone[:end - start]

    return wave


def generate_prism_survivors_sfx(output_dir: Path):
    """Generate all Prism Survivors sound effects."""
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n=== Generating Prism Survivors SFX ===")
    print(f"Output: {output_dir}\n")

    sfx_map = {
        # Core gameplay
        "shoot.wav": sfx_shoot,
        "hit.wav": sfx_hit,
        "death.wav": sfx_death,
        "hurt.wav": sfx_hurt,
        "dash.wav": sfx_dash,

        # Pickups
        "xp.wav": sfx_xp,
        "coin.wav": sfx_coin,
        "powerup.wav": sfx_powerup,
        "level_up.wav": sfx_level_up,

        # UI
        "select.wav": sfx_select,
        "menu.wav": sfx_menu,
        "back.wav": sfx_back,

        # Combo milestones
        "combo_5.wav": sfx_combo_5,
        "combo_10.wav": sfx_combo_10,
        "combo_25.wav": sfx_combo_25,
        "combo_50.wav": sfx_combo_50,

        # Events
        "boss_spawn.wav": sfx_boss_spawn,
        "wave_complete.wav": sfx_wave_complete,
    }

    for filename, generator in sfx_map.items():
        wave = generator()
        save_wav(output_dir / filename, wave)

    print(f"\nGenerated {len(sfx_map)} sound effects.")


def main():
    parser = argparse.ArgumentParser(description="Prism Survivors SFX Generator")
    parser.add_argument("--game", default="prism-survivors",
                        help="Target game (default: prism-survivors)")
    parser.add_argument("--output", type=str, help="Custom output directory")

    args = parser.parse_args()

    if args.output:
        output_dir = Path(args.output)
    else:
        # Default to game's audio directory
        script_dir = Path(__file__).parent
        showcase_root = script_dir.parent.parent
        game_dir = args.game.replace("-", "-")
        output_dir = showcase_root / "games" / game_dir / "assets" / "audio"

    generate_prism_survivors_sfx(output_dir)


if __name__ == "__main__":
    main()
