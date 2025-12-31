"""Prism Survivors - Audio Generation.

Sound Effects:
- Combat: shoot, hit, death, dash
- Progression: level_up, hurt, xp, coin, powerup
- UI: menu, select, back
- Combos: combo_5, combo_10, combo_25, combo_50
- Events: boss_spawn, wave_complete

Aesthetic: Crystalline, harmonic, punchy arcade sounds.
Uses 22050 Hz sample rate for smaller file sizes.
"""

import math
from pathlib import Path
from typing import List, Tuple
import sys

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from procgen.lib.audio_dsp import (
    SAMPLE_RATE, write_wav,
    sine_wave, square_wave, sawtooth_wave, triangle_wave, noise,
    lowpass_filter, highpass_filter,
    envelope_adsr, envelope_linear,
    reverb_comb, mix, insert_at, pad_to_length
)


# Use 22050 Hz for game SFX
PRISM_SAMPLE_RATE = 22050


def _resample(samples: List[float]) -> List[float]:
    """Downsample from 44100 to 22050 Hz."""
    return samples[::2]


# =============================================================================
# Combat Sounds
# =============================================================================

def generate_shoot(duration: float = 0.15) -> List[float]:
    """Projectile fire - crystalline zap."""
    # High frequency burst with quick decay
    wave = square_wave(1200, duration, amplitude=0.4)
    wave2 = sine_wave(2400, duration, amplitude=0.2)
    wave = mix([wave, wave2])

    # Quick envelope
    wave = envelope_adsr(wave, 0.005, 0.03, 0.2, 0.1)

    # High pass for crispness
    wave = highpass_filter(wave, 800)

    return _resample(wave)


def generate_hit(duration: float = 0.1) -> List[float]:
    """Enemy hit - punchy impact."""
    # Low thud
    thud = sine_wave(150, duration, amplitude=0.5)
    thud = envelope_adsr(thud, 0.002, 0.02, 0.1, 0.05)

    # High crack
    crack = noise(0.03, amplitude=0.4)
    crack = envelope_adsr(crack, 0.001, 0.01, 0.1, 0.02)

    wave = pad_to_length(thud, int(duration * SAMPLE_RATE))
    wave = insert_at(wave, crack, 0)

    return _resample(wave)


def generate_death(duration: float = 0.35) -> List[float]:
    """Enemy death - shattering crystal."""
    # Noise burst (shatter)
    shatter = noise(duration, amplitude=0.5)
    shatter = envelope_adsr(shatter, 0.01, 0.1, 0.2, 0.15)

    # Descending tone
    samples = int(duration * SAMPLE_RATE)
    tone = [0.0] * samples
    for i in range(samples):
        t = i / SAMPLE_RATE
        freq = 800 - 400 * (t / duration)
        tone[i] = 0.3 * math.sin(2 * math.pi * freq * t)
    tone = envelope_adsr(tone, 0.01, 0.05, 0.3, 0.2)

    wave = mix([shatter, tone])
    wave = lowpass_filter(wave, 3000)

    return _resample(wave)


def generate_dash(duration: float = 0.25) -> List[float]:
    """Dash ability - whoosh."""
    # White noise with frequency sweep
    whoosh = noise(duration, amplitude=0.4)
    whoosh = envelope_adsr(whoosh, 0.02, 0.08, 0.3, 0.12)

    # Rising pitch accent
    samples = int(duration * SAMPLE_RATE)
    sweep = [0.0] * samples
    for i in range(samples):
        t = i / SAMPLE_RATE
        freq = 300 + 600 * (t / duration)
        sweep[i] = 0.2 * math.sin(2 * math.pi * freq * t)
    sweep = envelope_adsr(sweep, 0.01, 0.1, 0.3, 0.1)

    wave = mix([whoosh, sweep])

    return _resample(wave)


# =============================================================================
# Progression Sounds
# =============================================================================

def generate_level_up(duration: float = 0.6) -> List[float]:
    """Level up - triumphant ascending arpeggio."""
    notes = [523, 659, 784, 1047]  # C5, E5, G5, C6
    samples = int(duration * SAMPLE_RATE)
    wave = [0.0] * samples

    for i, freq in enumerate(notes):
        start = int(i * SAMPLE_RATE * 0.12)
        note_dur = 0.35
        note = sine_wave(freq, note_dur, amplitude=0.35)
        note2 = triangle_wave(freq * 2, note_dur, amplitude=0.1)
        note = mix([note, note2])
        note = envelope_adsr(note, 0.02, 0.05, 0.5, 0.15)
        wave = insert_at(wave, note, start)

    wave = reverb_comb(wave, decay=0.2, delay_ms=30)

    return _resample(wave)


def generate_hurt(duration: float = 0.15) -> List[float]:
    """Player hurt - low impact."""
    wave = sine_wave(100, duration, amplitude=0.5)
    wave2 = noise(0.05, amplitude=0.3)
    wave = envelope_adsr(wave, 0.005, 0.03, 0.2, 0.1)
    wave = insert_at(wave, wave2, 0)
    wave = lowpass_filter(wave, 400)

    return _resample(wave)


def generate_xp(duration: float = 0.12) -> List[float]:
    """XP pickup - sparkle."""
    wave = sine_wave(1500, duration, amplitude=0.4)
    wave2 = sine_wave(2250, duration, amplitude=0.2)
    wave = mix([wave, wave2])
    wave = envelope_adsr(wave, 0.005, 0.02, 0.3, 0.08)

    return _resample(wave)


def generate_coin(duration: float = 0.1) -> List[float]:
    """Coin pickup - metallic ting."""
    wave = sine_wave(2000, duration, amplitude=0.4)
    wave2 = sine_wave(3000, duration, amplitude=0.2)
    wave3 = sine_wave(4000, duration, amplitude=0.1)
    wave = mix([wave, wave2, wave3])
    wave = envelope_adsr(wave, 0.002, 0.02, 0.2, 0.06)

    return _resample(wave)


def generate_powerup(duration: float = 0.4) -> List[float]:
    """Powerup pickup - magical ascending."""
    samples = int(duration * SAMPLE_RATE)
    wave = [0.0] * samples

    for i in range(samples):
        t = i / SAMPLE_RATE
        freq = 400 + 800 * (t / duration)
        wave[i] = 0.4 * math.sin(2 * math.pi * freq * t)
        wave[i] += 0.15 * math.sin(2 * math.pi * freq * 1.5 * t)

    wave = envelope_adsr(wave, 0.02, 0.1, 0.5, 0.2)
    wave = reverb_comb(wave, decay=0.15, delay_ms=25)

    return _resample(wave)


# =============================================================================
# UI Sounds
# =============================================================================

def generate_menu(duration: float = 0.1) -> List[float]:
    """Menu navigate - soft tick."""
    wave = sine_wave(800, duration, amplitude=0.3)
    wave = envelope_adsr(wave, 0.005, 0.02, 0.2, 0.05)

    return _resample(wave)


def generate_select(duration: float = 0.08) -> List[float]:
    """Menu select - confirm click."""
    wave = sine_wave(1200, duration, amplitude=0.35)
    wave2 = sine_wave(1800, duration * 0.5, amplitude=0.15)
    wave = mix([wave, wave2])
    wave = envelope_adsr(wave, 0.002, 0.01, 0.2, 0.04)

    return _resample(wave)


def generate_back(duration: float = 0.12) -> List[float]:
    """Menu back - descending."""
    samples = int(duration * SAMPLE_RATE)
    wave = [0.0] * samples
    for i in range(samples):
        t = i / SAMPLE_RATE
        freq = 1000 - 400 * (t / duration)
        wave[i] = 0.3 * math.sin(2 * math.pi * freq * t)
    wave = envelope_adsr(wave, 0.005, 0.02, 0.2, 0.06)

    return _resample(wave)


# =============================================================================
# Combo Sounds
# =============================================================================

def generate_combo(level: int, duration: float = 0.2) -> List[float]:
    """Combo milestone - escalating chimes."""
    base_freq = 600 + level * 100
    notes = [base_freq, base_freq * 1.25, base_freq * 1.5]

    samples = int(duration * SAMPLE_RATE)
    wave = [0.0] * samples

    for i, freq in enumerate(notes[:min(level // 10 + 1, 3)]):
        start = int(i * SAMPLE_RATE * 0.05)
        note = sine_wave(freq, 0.12, amplitude=0.35)
        note = envelope_adsr(note, 0.005, 0.02, 0.4, 0.08)
        wave = insert_at(wave, note, start)

    return _resample(wave)


def generate_combo_5(duration: float = 0.1) -> List[float]:
    return generate_combo(5, duration)


def generate_combo_10(duration: float = 0.2) -> List[float]:
    return generate_combo(10, duration)


def generate_combo_25(duration: float = 0.25) -> List[float]:
    return generate_combo(25, duration)


def generate_combo_50(duration: float = 0.4) -> List[float]:
    return generate_combo(50, duration)


# =============================================================================
# Event Sounds
# =============================================================================

def generate_boss_spawn(duration: float = 1.0) -> List[float]:
    """Boss spawn - ominous rumble with impact."""
    samples = int(duration * SAMPLE_RATE)

    # Low rumble
    rumble = [0.0] * samples
    for i in range(samples):
        t = i / SAMPLE_RATE
        freq = 40 + 20 * math.sin(2 * math.pi * 2 * t)
        rumble[i] = 0.4 * math.sin(2 * math.pi * freq * t)
    rumble = envelope_adsr(rumble, 0.1, 0.3, 0.5, 0.4)

    # Impact at end
    impact = sine_wave(60, 0.3, amplitude=0.6)
    impact_noise = noise(0.1, amplitude=0.4)
    impact = mix([impact, impact_noise])
    impact = envelope_adsr(impact, 0.01, 0.1, 0.2, 0.15)

    wave = pad_to_length(rumble, samples)
    wave = insert_at(wave, impact, int(samples * 0.6))

    wave = lowpass_filter(wave, 500)

    return _resample(wave)


def generate_wave_complete(duration: float = 0.5) -> List[float]:
    """Wave complete - victory fanfare."""
    notes = [523, 659, 784, 880, 1047]  # C5-C6 arpeggio
    samples = int(duration * SAMPLE_RATE)
    wave = [0.0] * samples

    for i, freq in enumerate(notes):
        start = int(i * SAMPLE_RATE * 0.08)
        note = sine_wave(freq, 0.25, amplitude=0.3)
        note2 = sawtooth_wave(freq, 0.25, amplitude=0.1)
        note = mix([note, note2])
        note = envelope_adsr(note, 0.01, 0.05, 0.5, 0.15)
        wave = insert_at(wave, note, start)

    wave = reverb_comb(wave, decay=0.2, delay_ms=35)

    return _resample(wave)


# =============================================================================
# Generation Registry
# =============================================================================

AUDIO_ASSETS: List[Tuple[str, callable, str]] = [
    # Combat
    ("shoot", generate_shoot, "Projectile Fire"),
    ("hit", generate_hit, "Enemy Hit"),
    ("death", generate_death, "Enemy Death"),
    ("dash", generate_dash, "Dash Ability"),

    # Progression
    ("level_up", generate_level_up, "Level Up"),
    ("hurt", generate_hurt, "Player Hurt"),
    ("xp", generate_xp, "XP Pickup"),
    ("coin", generate_coin, "Coin Pickup"),
    ("powerup", generate_powerup, "Powerup Pickup"),

    # UI
    ("menu", generate_menu, "Menu Navigate"),
    ("select", generate_select, "Menu Select"),
    ("back", generate_back, "Menu Back"),

    # Combos
    ("combo_5", generate_combo_5, "Combo 5"),
    ("combo_10", generate_combo_10, "Combo 10"),
    ("combo_25", generate_combo_25, "Combo 25"),
    ("combo_50", generate_combo_50, "Combo 50"),

    # Events
    ("boss_spawn", generate_boss_spawn, "Boss Spawn"),
    ("wave_complete", generate_wave_complete, "Wave Complete"),
]


def generate_all_audio(output_dir: Path) -> int:
    """Generate all Prism Survivors audio assets."""
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    for filename, generator, description in AUDIO_ASSETS:
        print(f"  Generating {description}...")
        samples = generator()
        output_path = output_dir / f"{filename}.wav"
        write_wav(str(output_path), samples, sample_rate=PRISM_SAMPLE_RATE)
        count += 1

    return count


__all__ = [
    "generate_all_audio",
    "AUDIO_ASSETS",
]


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent.parent.parent / "games" / "prism-survivors" / "assets" / "audio"

    print("\n" + "=" * 60)
    print("  PRISM SURVIVORS - Audio Generator")
    print("=" * 60)

    count = generate_all_audio(output_dir)

    print(f"\nGenerated {count} audio files")
    print("=" * 60)
