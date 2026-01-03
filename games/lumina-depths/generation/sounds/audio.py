#!/usr/bin/env python3
"""Generate audio assets for Lumina Depths.

Zone Ambients:
- ambient_sunlit.wav (60s) - Bright, active, bubbles
- ambient_twilight.wav (90s) - Mysterious, whale echoes
- ambient_midnight.wav (120s) - Sub-bass pressure, isolation
- ambient_vents.wav (90s) - Volcanic rumble, alien

Whale Calls:
- whale.wav (5s) - Low fundamental with harmonics
- whale_echo.wav (8s) - Distant reverberant whale song
"""

import math
import os
import struct
import wave
import random

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "generated", "sounds")
SAMPLE_RATE = 44100

def write_wav(filename, samples, sample_rate=SAMPLE_RATE):
    """Write samples to WAV file."""
    # Normalize to 16-bit range
    max_val = max(abs(min(samples)), abs(max(samples))) if samples else 1
    if max_val > 0:
        samples = [int(s / max_val * 32767 * 0.9) for s in samples]

    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        wav.writeframes(struct.pack(f'{len(samples)}h', *samples))

def sine_wave(freq, duration, sample_rate=SAMPLE_RATE, amplitude=1.0):
    """Generate sine wave."""
    samples = []
    for i in range(int(duration * sample_rate)):
        t = i / sample_rate
        samples.append(amplitude * math.sin(2 * math.pi * freq * t))
    return samples

def noise(duration, sample_rate=SAMPLE_RATE, amplitude=1.0):
    """Generate white noise."""
    return [amplitude * (random.random() * 2 - 1) for _ in range(int(duration * sample_rate))]

def lowpass_filter(samples, cutoff, sample_rate=SAMPLE_RATE):
    """Simple one-pole lowpass filter."""
    rc = 1.0 / (2 * math.pi * cutoff)
    dt = 1.0 / sample_rate
    alpha = dt / (rc + dt)

    filtered = []
    prev = 0
    for s in samples:
        prev = prev + alpha * (s - prev)
        filtered.append(prev)
    return filtered

def highpass_filter(samples, cutoff, sample_rate=SAMPLE_RATE):
    """Simple one-pole highpass filter."""
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

def add_reverb(samples, decay=0.3, delay_ms=50, sample_rate=SAMPLE_RATE):
    """Simple comb filter reverb."""
    delay_samples = int(delay_ms * sample_rate / 1000)
    output = samples.copy()

    for i in range(delay_samples, len(output)):
        output[i] += output[i - delay_samples] * decay

    return output

def envelope(samples, attack, decay, sustain, release, sample_rate=SAMPLE_RATE):
    """Apply ADSR envelope."""
    total = len(samples)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = total - attack_samples - decay_samples - release_samples

    output = []
    for i, s in enumerate(samples):
        if i < attack_samples:
            env = i / attack_samples
        elif i < attack_samples + decay_samples:
            env = 1.0 - (1.0 - sustain) * (i - attack_samples) / decay_samples
        elif i < attack_samples + decay_samples + sustain_samples:
            env = sustain
        else:
            env = sustain * (1.0 - (i - attack_samples - decay_samples - sustain_samples) / release_samples)
        output.append(s * max(0, env))
    return output

def mix(samples_list, volumes=None):
    """Mix multiple sample arrays."""
    if volumes is None:
        volumes = [1.0] * len(samples_list)

    max_len = max(len(s) for s in samples_list)
    output = [0.0] * max_len

    for samples, vol in zip(samples_list, volumes):
        for i, s in enumerate(samples):
            output[i] += s * vol

    return output

def generate_bubbles(duration, density=5, sample_rate=SAMPLE_RATE):
    """Generate bubble sounds."""
    samples = [0.0] * int(duration * sample_rate)

    num_bubbles = int(duration * density)
    for _ in range(num_bubbles):
        # Random bubble parameters
        start = random.randint(0, len(samples) - int(0.2 * sample_rate))
        freq = random.uniform(800, 2500)
        bubble_dur = random.uniform(0.02, 0.1)
        amp = random.uniform(0.1, 0.4)

        bubble = sine_wave(freq, bubble_dur, amplitude=amp)
        bubble = envelope(bubble, 0.005, 0.01, 0.3, bubble_dur * 0.6)

        # Add frequency sweep (rising pitch)
        for i in range(len(bubble)):
            t = i / sample_rate
            sweep = 1 + t * 2  # Pitch rises as bubble rises
            bubble[i] *= math.sin(2 * math.pi * freq * sweep * t) / (amp + 0.1)

        for i, b in enumerate(bubble):
            if start + i < len(samples):
                samples[start + i] += b

    return samples

def generate_ambient_sunlit(duration=60):
    """Zone 1: Bright, active, bubbles, fish activity."""
    print("Generating ambient_sunlit.wav...")

    # Base water movement (bright filtered noise)
    base = noise(duration, amplitude=0.3)
    base = highpass_filter(base, 200)
    base = lowpass_filter(base, 6000)

    # Bubbles
    bubbles = generate_bubbles(duration, density=8)
    bubbles = lowpass_filter(bubbles, 4000)

    # Occasional fish swishes (short noise bursts)
    fish = [0.0] * int(duration * SAMPLE_RATE)
    for _ in range(int(duration / 3)):
        start = random.randint(0, len(fish) - int(0.3 * SAMPLE_RATE))
        swish = noise(0.15, amplitude=0.2)
        swish = highpass_filter(swish, 1000)
        swish = lowpass_filter(swish, 5000)
        swish = envelope(swish, 0.01, 0.02, 0.3, 0.1)
        for i, s in enumerate(swish):
            if start + i < len(fish):
                fish[start + i] += s

    # Mix
    output = mix([base, bubbles, fish], [0.4, 0.5, 0.3])
    output = add_reverb(output, decay=0.2, delay_ms=30)

    return output

def generate_ambient_twilight(duration=90):
    """Zone 2: Mysterious, whale echoes, darker."""
    print("Generating ambient_twilight.wav...")

    # Darker base (more lowpass)
    base = noise(duration, amplitude=0.25)
    base = lowpass_filter(base, 2000)
    base = highpass_filter(base, 50)

    # Pressure drone (low sine)
    drone = sine_wave(55, duration, amplitude=0.3)
    # Add slow modulation
    for i in range(len(drone)):
        t = i / SAMPLE_RATE
        drone[i] *= 0.7 + 0.3 * math.sin(2 * math.pi * 0.05 * t)

    # Distant whale echoes (every 20-30s)
    whales = [0.0] * int(duration * SAMPLE_RATE)
    t = 15
    while t < duration - 5:
        # Short whale fragment
        whale_dur = random.uniform(1.5, 3.0)
        whale_freq = random.uniform(80, 150)
        whale = sine_wave(whale_freq, whale_dur, amplitude=0.15)

        # Add harmonics
        for harm in [2, 3, 5]:
            harm_wave = sine_wave(whale_freq * harm, whale_dur, amplitude=0.05 / harm)
            whale = mix([whale, harm_wave])

        whale = envelope(whale, 0.3, 0.2, 0.4, whale_dur * 0.4)
        whale = lowpass_filter(whale, 800)
        whale = add_reverb(whale, decay=0.5, delay_ms=100)

        start = int(t * SAMPLE_RATE)
        for i, w in enumerate(whale):
            if start + i < len(whales):
                whales[start + i] += w

        t += random.uniform(18, 28)

    # Marine snow tinkle (subtle high frequencies)
    snow = noise(duration, amplitude=0.05)
    snow = highpass_filter(snow, 3000)
    snow = lowpass_filter(snow, 8000)

    # Mix with heavy reverb
    output = mix([base, drone, whales, snow], [0.35, 0.4, 0.5, 0.15])
    output = add_reverb(output, decay=0.4, delay_ms=80)

    return output

def generate_ambient_midnight(duration=120):
    """Zone 3: Sub-bass pressure, isolation, bioluminescent pings."""
    print("Generating ambient_midnight.wav...")

    # Sub-bass pressure drone
    drone = sine_wave(35, duration, amplitude=0.4)
    # Very slow modulation
    for i in range(len(drone)):
        t = i / SAMPLE_RATE
        drone[i] *= 0.6 + 0.4 * math.sin(2 * math.pi * 0.02 * t)

    # Near-silence base (very quiet)
    base = noise(duration, amplitude=0.05)
    base = lowpass_filter(base, 500)

    # Rare bioluminescent pings
    pings = [0.0] * int(duration * SAMPLE_RATE)
    t = 10
    while t < duration - 3:
        # High, glassy ping
        ping_freq = random.uniform(1500, 3000)
        ping_dur = random.uniform(0.5, 1.5)
        ping = sine_wave(ping_freq, ping_dur, amplitude=0.15)
        ping = envelope(ping, 0.01, 0.05, 0.2, ping_dur * 0.7)
        ping = add_reverb(ping, decay=0.6, delay_ms=150)

        start = int(t * SAMPLE_RATE)
        for i, p in enumerate(ping):
            if start + i < len(pings):
                pings[start + i] += p

        t += random.uniform(15, 35)  # Rare

    # Mix
    output = mix([drone, base, pings], [0.6, 0.2, 0.25])
    output = lowpass_filter(output, 2000)  # Heavy filtering
    output = add_reverb(output, decay=0.6, delay_ms=200)  # Massive reverb

    return output

def generate_ambient_vents(duration=90):
    """Zone 4: Volcanic rumble, hissing, metallic."""
    print("Generating ambient_vents.wav...")

    # Volcanic rumble (low noise)
    rumble = noise(duration, amplitude=0.4)
    rumble = lowpass_filter(rumble, 150)
    # Modulate intensity
    for i in range(len(rumble)):
        t = i / SAMPLE_RATE
        rumble[i] *= 0.5 + 0.5 * abs(math.sin(2 * math.pi * 0.1 * t))

    # Hissing vents (periodic)
    hiss = [0.0] * int(duration * SAMPLE_RATE)
    t = 3
    while t < duration - 2:
        hiss_dur = random.uniform(0.5, 2.0)
        h = noise(hiss_dur, amplitude=0.3)
        h = highpass_filter(h, 800)
        h = lowpass_filter(h, 4000)
        h = envelope(h, 0.1, 0.1, 0.6, 0.2)

        start = int(t * SAMPLE_RATE)
        for i, s in enumerate(h):
            if start + i < len(hiss):
                hiss[start + i] += s

        t += random.uniform(5, 12)

    # Metallic pings
    pings = [0.0] * int(duration * SAMPLE_RATE)
    t = 5
    while t < duration - 1:
        freq = random.uniform(400, 1200)
        p = sine_wave(freq, 0.2, amplitude=0.2)
        # Make it metallic with harmonics
        for harm in [1.5, 2.5, 3.7]:  # Inharmonic = metallic
            p = mix([p, sine_wave(freq * harm, 0.2, amplitude=0.08)])
        p = envelope(p, 0.005, 0.02, 0.1, 0.15)

        start = int(t * SAMPLE_RATE)
        for i, s in enumerate(p):
            if start + i < len(pings):
                pings[start + i] += s

        t += random.uniform(4, 10)

    # Bubble columns (distant)
    bubbles = generate_bubbles(duration, density=2)
    bubbles = lowpass_filter(bubbles, 1500)

    # Mix
    output = mix([rumble, hiss, pings, bubbles], [0.5, 0.35, 0.2, 0.15])
    output = add_reverb(output, decay=0.3, delay_ms=40)

    return output

def generate_whale_call(duration=5):
    """Generate main whale call - low with harmonics."""
    print("Generating whale.wav...")

    fundamental = 60  # Hz

    # Fundamental
    main = sine_wave(fundamental, duration, amplitude=0.5)

    # Harmonics
    h2 = sine_wave(fundamental * 2, duration, amplitude=0.25)
    h3 = sine_wave(fundamental * 3, duration, amplitude=0.12)
    h5 = sine_wave(fundamental * 5, duration, amplitude=0.06)

    output = mix([main, h2, h3, h5])

    # Slow pitch modulation (characteristic whale "warble")
    for i in range(len(output)):
        t = i / SAMPLE_RATE
        mod = 1.0 + 0.02 * math.sin(2 * math.pi * 0.5 * t)  # Slow wobble
        output[i] *= mod

    # ADSR envelope
    output = envelope(output, 0.5, 0.3, 0.6, 1.5)

    # Reverb
    output = add_reverb(output, decay=0.5, delay_ms=100)

    return output

def generate_whale_echo(duration=8):
    """Generate distant whale echo - more reverb, filtered."""
    print("Generating whale_echo.wav...")

    fundamental = 80  # Slightly higher (different whale)

    # Base call
    main = sine_wave(fundamental, duration * 0.6, amplitude=0.3)

    # Harmonics (fewer, more filtered)
    h2 = sine_wave(fundamental * 2, duration * 0.6, amplitude=0.15)
    h3 = sine_wave(fundamental * 3, duration * 0.6, amplitude=0.05)

    call = mix([main, h2, h3])
    call = envelope(call, 0.8, 0.5, 0.4, 1.0)

    # Heavy lowpass (distant)
    call = lowpass_filter(call, 600)

    # Pad to full duration
    call = call + [0.0] * (int(duration * SAMPLE_RATE) - len(call))

    # Multiple reverb passes for cathedral effect
    call = add_reverb(call, decay=0.6, delay_ms=150)
    call = add_reverb(call, decay=0.4, delay_ms=300)
    call = add_reverb(call, decay=0.3, delay_ms=500)

    return call

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Zone ambients
    sunlit = generate_ambient_sunlit(60)
    write_wav(os.path.join(OUTPUT_DIR, "ambient_sunlit.wav"), sunlit)
    print(f"  -> {len(sunlit) / SAMPLE_RATE:.1f}s")

    twilight = generate_ambient_twilight(90)
    write_wav(os.path.join(OUTPUT_DIR, "ambient_twilight.wav"), twilight)
    print(f"  -> {len(twilight) / SAMPLE_RATE:.1f}s")

    midnight = generate_ambient_midnight(120)
    write_wav(os.path.join(OUTPUT_DIR, "ambient_midnight.wav"), midnight)
    print(f"  -> {len(midnight) / SAMPLE_RATE:.1f}s")

    vents = generate_ambient_vents(90)
    write_wav(os.path.join(OUTPUT_DIR, "ambient_vents.wav"), vents)
    print(f"  -> {len(vents) / SAMPLE_RATE:.1f}s")

    # Whale calls
    whale = generate_whale_call(5)
    write_wav(os.path.join(OUTPUT_DIR, "whale.wav"), whale)
    print(f"  -> {len(whale) / SAMPLE_RATE:.1f}s")

    whale_echo = generate_whale_echo(8)
    write_wav(os.path.join(OUTPUT_DIR, "whale_echo.wav"), whale_echo)
    print(f"  -> {len(whale_echo) / SAMPLE_RATE:.1f}s")

    print("\nAll audio generated!")

if __name__ == "__main__":
    main()
