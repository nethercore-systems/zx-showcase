---
# Sonic Style Language Specification
# Lumina Depths - Meditative Underwater Exploration

game: "Lumina Depths"
version: 1.0

identity:
  tagline: "Descend into the light beneath the dark"
  audio_pillars:
    - "Immersive Subaquatic Acoustics - everything sounds underwater"
    - "Creatures as Living Soundscape - ecosystem, not sound effects"
    - "Pressure as Audible Presence - the ocean weighs on you"
  signature_sounds:
    - whale_call         # Distant, reverberant, emotional
    - bubbles_rising     # Constant gentle reminder of depth
    - hull_creak         # Pressure awareness without anxiety

style:
  primary: Dark Ambient
  secondary: Ambient
  intensity: Minimal
  era: Modern

mood:
  sunlit_waters: Peaceful + Bright
  twilight_realm: Mysterious + Transitional
  midnight_abyss: Eerie + Wondrous
  hydrothermal_vents: Alien + Primordial
  luminara_trench: Ethereal + Transcendent
  whale_encounter: Awe + Emotional
  discovery: Satisfaction + Quiet

instruments:
  primary:
    - synth.pad.evolving       # Slow, harmonic drones
    - sfx.ambient.underwater   # Water movement, bubbles
    - synth.pad.cold           # Deep zone isolation
  accent:
    - orchestral.harp.glissando  # Discovery moments
    - orchestral.choir.ethereal  # Whale encounters
    - synth.fx.sweep             # Zone transitions
  texture:
    - sfx.ambient.loop           # Constant water presence
    - synth.pad.warm             # Submersible interior
    - percussion.metallic        # Hull interactions
---

# Zone Ambient Specifications

## ambient_sunlit.wav
- **Duration:** 60s loop
- **Layers:**
  1. Base: Bright filtered water movement (pink noise @ 2-6kHz)
  2. Mid: Occasional fish school swishes
  3. High: Bubble streams (randomized intervals)
  4. Low: Distant muffled surface waves
- **Processing:** Light reverb, high-pass at 80Hz
- **Character:** Active, bright, safe

## ambient_twilight.wav
- **Duration:** 90s loop
- **Layers:**
  1. Base: Darker water texture (filtered noise, lower bands)
  2. Mid: Whale song echoes (every 15-30s, pitch-shifted)
  3. High: Marine snow tinkle (subtle granular)
  4. Low: Pressure drone (40-60Hz sine)
- **Processing:** Heavy lowpass at 4kHz, large reverb (3s decay)
- **Character:** Transitional, mysterious, isolation hints

## ambient_midnight.wav
- **Duration:** 120s loop
- **Layers:**
  1. Base: Sub-bass pressure drone (30-50Hz)
  2. Mid: Near-silence with occasional distant sounds
  3. Accent: Sudden bioluminescent "pings" (rare, wondrous not scary)
  4. High: Minimal high-frequency content
- **Processing:** Massive reverb (8s decay), heavy lowpass at 2kHz
- **Character:** Isolated, vast, crushing weight

## ambient_vents.wav
- **Duration:** 90s loop
- **Layers:**
  1. Base: Rumbling volcanic drone (50-100Hz)
  2. Mid: Hissing vent releases (periodic, 5-15s intervals)
  3. Accent: Metallic thermal pings (mineral deposits)
  4. High: Bubble columns (low-volume, distant)
- **Processing:** Resonant filtering, metallic reverb, warm distortion
- **Character:** Alien, industrial, otherworldly

---

# Creature Sound Specifications

## Whale Sounds (whale.wav, whale_echo.wav)
- **Purpose:** Signature emotional moment
- **Pitch:** Low fundamental (80-150Hz) with harmonic overtones
- **Duration:** 4-8 seconds
- **Synthesis:** FM synthesis with slow modulation
- **Processing:** Cathedral reverb (10s decay), gradual highpass for distance
- **Emotional Goal:** Awe, connection to vastness, "you are small"

## Jellyfish (jellyfish.wav)
- **Purpose:** Ambient texture
- **Pitch:** High, glassy (800-2000Hz)
- **Duration:** 0.5-1.5s, proximity-triggered
- **Synthesis:** Glass FM synthesis, bell-like slow attack
- **Processing:** Shimmer reverb, chorus
- **Emotional Goal:** Ethereal, otherworldly, delicate

## Anglerfish Lure (anglerfish_lure.wav)
- **Purpose:** Tension texture (beautiful-but-dangerous)
- **Pitch:** Pulsing mid-frequency (300-600Hz)
- **Duration:** 0.8s, loopable with random intervals
- **Synthesis:** Amplitude-modulated sine with subtle FM
- **Processing:** Bandpass filter, eerie resonance
- **Emotional Goal:** Hypnotic, slightly unsettling

## Sonar (sonar.wav)
- **Purpose:** UI/Feedback
- **Pitch:** Clean, clear (1-2kHz)
- **Duration:** 0.3s ping with 2s reverb tail
- **Synthesis:** Pure sine with fast attack, exponential decay
- **Processing:** Ping-pong delay, submarine-style reverb
- **Emotional Goal:** Technological, reassuring

---

# Submersible Sound Specifications

## Propeller (propeller.wav)
- **Duration:** 10s seamless loop
- **Layers:**
  1. Motor hum (60-120Hz)
  2. Blade turbulence (filtered noise 200-800Hz)
  3. Cavitation bubbles (subtle, 1-3kHz)
- **Dynamic:** Pitch/intensity varies with thrust input
- **Processing:** Underwater filtering, room reverb for interior
- **Emotional Goal:** Mechanical companion, reliable presence

## Hull Creak (hull_creak.wav)
- **Duration:** 0.5-2s
- **Pitch:** Low metallic groan (100-300Hz)
- **Synthesis:** Granular metal or FM with resonance
- **Trigger:** Random, probability increases with depth
- **Processing:** Resonant bandpass, metallic plate reverb
- **Emotional Goal:** Pressure awareness, not fear

## Pressure Warning (pressure_warning.wav)
- **Duration:** 0.5s repeated tone
- **Pitch:** Mid-range alert (500-800Hz)
- **Synthesis:** Clipped triangle wave with vibrato
- **Processing:** Slight distortion, interior acoustics
- **Emotional Goal:** Information, not alarm

---

# Discovery Sound Specifications

## Discovery Fanfare (discovery.wav)
- **Duration:** 1.5-2s
- **Pitch:** Rising major arpeggio
- **Synthesis:** Harp glissando + pad swell + subtle choir
- **Processing:** Shimmer reverb, slight delay
- **Emotional Goal:** Satisfaction, quiet triumph (not celebration)

## Artifact (artifact.wav)
- **Duration:** 2-3s
- **Pitch:** Mysterious suspended chord resolving
- **Synthesis:** Pad with evolving timbre + crystalline FM accent
- **Processing:** Long reverb, stereo widening
- **Emotional Goal:** Ancient, significant, connected to depths

---

# Processing Signatures

| Context | Reverb Type | Decay | Character |
|---------|-------------|-------|-----------|
| Surface | Room | 0.5s | Clear |
| Mid-depth | Hall | 2s | Growing murk |
| Deep | Cathedral | 8s | Massive isolation |
| Vents | Plate (metallic) | 1.5s | Industrial |
| Interior | Small Room | 0.3s | Cockpit |

## Depth-Based Filtering

| Depth | Lowpass Frequency | Notes |
|-------|-------------------|-------|
| 0-200m | None | Full clarity |
| 200-1000m | 6kHz | Beginning murk |
| 1000-4000m | 3kHz | Heavy filtering |
| 4000-5000m | 2kHz | Extreme depth |
| 5000m+ | 4kHz (rising) | Ethereal opening |

---

# Mix Priorities (1 = highest)

1. Ambient Zone Soundscape (always present, establishes world)
2. Submersible Interior (propeller, creaks - player's anchor)
3. Creature Proximity (nearby life sounds)
4. Discovery/UI Feedback (clear but not intrusive)
5. Epic Encounter Music (swells during whale/isopod)

---

# Audio Budget

| Category | Channels | Notes |
|----------|----------|-------|
| Zone Ambient | 1 | Crossfade between zones |
| Propeller | 1 | Constant loop |
| Creature SFX | 2 | Dynamic allocation |
| UI/Discovery | 1 | Interruptible |
| Encounter Music | 2 | Layered whale/epic |
| **Total** | 7 | Well under 16 channel limit |

---

# Reference Audio

For inspiration (not direct copying):

- **Subnautica:** Underwater ambience, creature vocalizations
- **Abzu:** Meditative underwater music
- **BBC Blue Planet II:** Documentary authenticity
- **Brian Eno - Music for Airports:** Ambient texture approach
