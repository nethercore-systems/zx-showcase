"""Lumina Depths Audio Generation.

Zone Ambients:
- ambient_sunlit.wav (60s) - Bright, active, bubbles
- ambient_twilight.wav (90s) - Mysterious, whale echoes
- ambient_midnight.wav (120s) - Sub-bass pressure, isolation
- ambient_vents.wav (90s) - Volcanic rumble, alien

Creature Sounds:
- whale.wav (5s) - Low fundamental with harmonics
- whale_echo.wav (8s) - Distant reverberant whale song
"""

import math
import random
from pathlib import Path
from typing import List, Tuple

from procgen.lib.audio_dsp import (
    SAMPLE_RATE, write_wav,
    sine_wave, noise,
    lowpass_filter, highpass_filter,
    envelope_adsr, reverb_comb, mix, insert_at, pad_to_length
)


# =============================================================================
# Utility Generators
# =============================================================================

def generate_bubbles(
    duration: float,
    density: float = 5,
    seed: int = 42
) -> List[float]:
    """Generate bubble sounds.

    Args:
        duration: Duration in seconds
        density: Bubbles per second
        seed: Random seed
    """
    rng = random.Random(seed)
    samples = [0.0] * int(duration * SAMPLE_RATE)

    num_bubbles = int(duration * density)
    for _ in range(num_bubbles):
        start = rng.randint(0, len(samples) - int(0.2 * SAMPLE_RATE))
        freq = rng.uniform(800, 2500)
        bubble_dur = rng.uniform(0.02, 0.1)
        amp = rng.uniform(0.1, 0.4)

        bubble = sine_wave(freq, bubble_dur, amplitude=amp)
        bubble = envelope_adsr(bubble, 0.005, 0.01, 0.3, bubble_dur * 0.6)

        # Add frequency sweep (rising pitch as bubble rises)
        for i in range(len(bubble)):
            t = i / SAMPLE_RATE
            sweep = 1 + t * 2
            bubble[i] *= math.sin(2 * math.pi * freq * sweep * t) / (amp + 0.1)

        samples = insert_at(samples, bubble, start)

    return samples


# =============================================================================
# Zone Ambient Generators
# =============================================================================

def generate_ambient_sunlit(duration: float = 60, seed: int = 1) -> List[float]:
    """Zone 1: Bright, active, bubbles, fish activity."""
    rng = random.Random(seed)

    # Base water movement (bright filtered noise)
    base = noise(duration, amplitude=0.3, seed=seed)
    base = highpass_filter(base, 200)
    base = lowpass_filter(base, 6000)

    # Bubbles
    bubbles = generate_bubbles(duration, density=8, seed=seed + 1)
    bubbles = lowpass_filter(bubbles, 4000)

    # Occasional fish swishes (short noise bursts)
    fish = [0.0] * int(duration * SAMPLE_RATE)
    for _ in range(int(duration / 3)):
        start = rng.randint(0, len(fish) - int(0.3 * SAMPLE_RATE))
        swish = noise(0.15, amplitude=0.2, seed=rng.randint(0, 10000))
        swish = highpass_filter(swish, 1000)
        swish = lowpass_filter(swish, 5000)
        swish = envelope_adsr(swish, 0.01, 0.02, 0.3, 0.1)
        fish = insert_at(fish, swish, start)

    # Mix
    output = mix([base, bubbles, fish], [0.4, 0.5, 0.3])
    output = reverb_comb(output, decay=0.2, delay_ms=30)

    return output


def generate_ambient_twilight(duration: float = 90, seed: int = 2) -> List[float]:
    """Zone 2: Mysterious, whale echoes, darker."""
    rng = random.Random(seed)

    # Darker base (more lowpass)
    base = noise(duration, amplitude=0.25, seed=seed)
    base = lowpass_filter(base, 2000)
    base = highpass_filter(base, 50)

    # Pressure drone (low sine with modulation)
    drone = sine_wave(55, duration, amplitude=0.3)
    for i in range(len(drone)):
        t = i / SAMPLE_RATE
        drone[i] *= 0.7 + 0.3 * math.sin(2 * math.pi * 0.05 * t)

    # Distant whale echoes (every 20-30s)
    whales = [0.0] * int(duration * SAMPLE_RATE)
    t = 15.0
    while t < duration - 5:
        whale_dur = rng.uniform(1.5, 3.0)
        whale_freq = rng.uniform(80, 150)
        whale = sine_wave(whale_freq, whale_dur, amplitude=0.15)

        # Add harmonics
        for harm in [2, 3, 5]:
            harm_wave = sine_wave(whale_freq * harm, whale_dur, amplitude=0.05 / harm)
            whale = mix([whale, harm_wave])

        whale = envelope_adsr(whale, 0.3, 0.2, 0.4, whale_dur * 0.4)
        whale = lowpass_filter(whale, 800)
        whale = reverb_comb(whale, decay=0.5, delay_ms=100)

        start = int(t * SAMPLE_RATE)
        whales = insert_at(whales, whale, start)
        t += rng.uniform(18, 28)

    # Marine snow tinkle
    snow = noise(duration, amplitude=0.05, seed=seed + 1)
    snow = highpass_filter(snow, 3000)
    snow = lowpass_filter(snow, 8000)

    # Mix with reverb
    output = mix([base, drone, whales, snow], [0.35, 0.4, 0.5, 0.15])
    output = reverb_comb(output, decay=0.4, delay_ms=80)

    return output


def generate_ambient_midnight(duration: float = 120, seed: int = 3) -> List[float]:
    """Zone 3: Sub-bass pressure, isolation, bioluminescent pings."""
    rng = random.Random(seed)

    # Sub-bass pressure drone
    drone = sine_wave(35, duration, amplitude=0.4)
    for i in range(len(drone)):
        t = i / SAMPLE_RATE
        drone[i] *= 0.6 + 0.4 * math.sin(2 * math.pi * 0.02 * t)

    # Near-silence base
    base = noise(duration, amplitude=0.05, seed=seed)
    base = lowpass_filter(base, 500)

    # Rare bioluminescent pings
    pings = [0.0] * int(duration * SAMPLE_RATE)
    t = 10.0
    while t < duration - 3:
        ping_freq = rng.uniform(1500, 3000)
        ping_dur = rng.uniform(0.5, 1.5)
        ping = sine_wave(ping_freq, ping_dur, amplitude=0.15)
        ping = envelope_adsr(ping, 0.01, 0.05, 0.2, ping_dur * 0.7)
        ping = reverb_comb(ping, decay=0.6, delay_ms=150)

        start = int(t * SAMPLE_RATE)
        pings = insert_at(pings, ping, start)
        t += rng.uniform(15, 35)

    # Mix with heavy filtering
    output = mix([drone, base, pings], [0.6, 0.2, 0.25])
    output = lowpass_filter(output, 2000)
    output = reverb_comb(output, decay=0.6, delay_ms=200)

    return output


def generate_ambient_vents(duration: float = 90, seed: int = 4) -> List[float]:
    """Zone 4: Volcanic rumble, hissing, metallic."""
    rng = random.Random(seed)

    # Volcanic rumble
    rumble = noise(duration, amplitude=0.4, seed=seed)
    rumble = lowpass_filter(rumble, 150)
    for i in range(len(rumble)):
        t = i / SAMPLE_RATE
        rumble[i] *= 0.5 + 0.5 * abs(math.sin(2 * math.pi * 0.1 * t))

    # Hissing vents
    hiss = [0.0] * int(duration * SAMPLE_RATE)
    t = 3.0
    while t < duration - 2:
        hiss_dur = rng.uniform(0.5, 2.0)
        h = noise(hiss_dur, amplitude=0.3, seed=rng.randint(0, 10000))
        h = highpass_filter(h, 800)
        h = lowpass_filter(h, 4000)
        h = envelope_adsr(h, 0.1, 0.1, 0.6, 0.2)

        start = int(t * SAMPLE_RATE)
        hiss = insert_at(hiss, h, start)
        t += rng.uniform(5, 12)

    # Metallic pings (inharmonic overtones)
    metal_pings = [0.0] * int(duration * SAMPLE_RATE)
    t = 5.0
    while t < duration - 1:
        freq = rng.uniform(400, 1200)
        p = sine_wave(freq, 0.2, amplitude=0.2)
        for harm in [1.5, 2.5, 3.7]:  # Inharmonic = metallic
            p = mix([p, sine_wave(freq * harm, 0.2, amplitude=0.08)])
        p = envelope_adsr(p, 0.005, 0.02, 0.1, 0.15)

        start = int(t * SAMPLE_RATE)
        metal_pings = insert_at(metal_pings, p, start)
        t += rng.uniform(4, 10)

    # Distant bubbles
    bubbles = generate_bubbles(duration, density=2, seed=seed + 1)
    bubbles = lowpass_filter(bubbles, 1500)

    # Mix
    output = mix([rumble, hiss, metal_pings, bubbles], [0.5, 0.35, 0.2, 0.15])
    output = reverb_comb(output, decay=0.3, delay_ms=40)

    return output


# =============================================================================
# Creature Sound Generators
# =============================================================================

def generate_whale_call(duration: float = 5) -> List[float]:
    """Main whale call - low fundamental with harmonics."""
    fundamental = 60

    # Fundamental and harmonics
    main = sine_wave(fundamental, duration, amplitude=0.5)
    h2 = sine_wave(fundamental * 2, duration, amplitude=0.25)
    h3 = sine_wave(fundamental * 3, duration, amplitude=0.12)
    h5 = sine_wave(fundamental * 5, duration, amplitude=0.06)

    output = mix([main, h2, h3, h5])

    # Slow pitch modulation (whale warble)
    for i in range(len(output)):
        t = i / SAMPLE_RATE
        mod = 1.0 + 0.02 * math.sin(2 * math.pi * 0.5 * t)
        output[i] *= mod

    output = envelope_adsr(output, 0.5, 0.3, 0.6, 1.5)
    output = reverb_comb(output, decay=0.5, delay_ms=100)

    return output


def generate_whale_echo(duration: float = 8) -> List[float]:
    """Distant whale echo - more reverb, filtered."""
    fundamental = 80

    # Base call (shorter than full duration)
    call_dur = duration * 0.6
    main = sine_wave(fundamental, call_dur, amplitude=0.3)
    h2 = sine_wave(fundamental * 2, call_dur, amplitude=0.15)
    h3 = sine_wave(fundamental * 3, call_dur, amplitude=0.05)

    call = mix([main, h2, h3])
    call = envelope_adsr(call, 0.8, 0.5, 0.4, 1.0)
    call = lowpass_filter(call, 600)

    # Pad to full duration
    call = pad_to_length(call, int(duration * SAMPLE_RATE))

    # Multiple reverb passes for cathedral effect
    call = reverb_comb(call, decay=0.6, delay_ms=150)
    call = reverb_comb(call, decay=0.4, delay_ms=300)
    call = reverb_comb(call, decay=0.3, delay_ms=500)

    return call


# =============================================================================
# Generation Registry
# =============================================================================

AUDIO_ASSETS: List[Tuple[str, callable, str]] = [
    # (filename, generator_func, description)
    # Zone Ambients
    ("ambient_sunlit", lambda: generate_ambient_sunlit(60), "Zone 1 Ambient (60s)"),
    ("ambient_twilight", lambda: generate_ambient_twilight(90), "Zone 2 Ambient (90s)"),
    ("ambient_midnight", lambda: generate_ambient_midnight(120), "Zone 3 Ambient (120s)"),
    ("ambient_vents", lambda: generate_ambient_vents(90), "Zone 4 Ambient (90s)"),
    # Creature Sounds
    ("whale", lambda: generate_whale_call(5), "Whale Call (5s)"),
    ("whale_echo", lambda: generate_whale_echo(8), "Whale Echo (8s)"),
]


def generate_all_audio(output_dir: Path) -> int:
    """Generate all audio assets.

    Args:
        output_dir: Directory to write WAV files

    Returns:
        Number of assets generated
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    for filename, generator, description in AUDIO_ASSETS:
        print(f"Generating {description}...")
        samples = generator()
        output_path = output_dir / f"{filename}.wav"
        write_wav(str(output_path), samples)
        duration = len(samples) / SAMPLE_RATE
        print(f"  -> {output_path.name} ({duration:.1f}s)")
        count += 1

    return count


__all__ = [
    "generate_all_audio",
    "generate_ambient_sunlit",
    "generate_ambient_twilight",
    "generate_ambient_midnight",
    "generate_ambient_vents",
    "generate_whale_call",
    "generate_whale_echo",
    "AUDIO_ASSETS",
]
