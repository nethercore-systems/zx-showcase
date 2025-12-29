---
# Creative Direction Configuration
# Lumina Depths - Meditative Underwater Exploration

# Art Direction
art_style: organic-ethereal-underwater
color_palette: bioluminescent-gradient
style_spectrums:
  fidelity: 6     # 1=stylized, 9=realistic (leaning realistic for naturalism)
  detail: 7       # 1=simple, 9=complex (rich deep-sea detail)
  saturation: 5   # 1=muted, 9=vibrant (varies by zone)
  contrast: 6     # 1=low-key, 9=high-key (dramatic light/dark)
  form: 8         # 1=geometric, 9=organic (highly organic creatures)
  line: 7         # 1=hard-edge, 9=soft (soft underwater diffusion)

# Sound Direction
sonic_identity: subaquatic-ambient-ethereal
mix_priority: ambient-rich
audio_pillars:
  - "Immersive Subaquatic Acoustics"
  - "Creatures as Living Soundscape"
  - "Pressure as Audible Presence"

# Tech Direction
architecture: single-file-wasm
determinism: optional
file_size_limit: 2500  # KB - larger for showcase

# Creative Vision
creative_pillars:
  - Contemplative Wonder
  - Gradual Revelation
  - Living Ecosystem
target_audience: "Players seeking non-combat relaxation; nature documentary enthusiasts; exploration game fans"
avoid_patterns:
  - Jump scares
  - Time pressure
  - Combat or conflict
  - Score-chasing mechanics
  - Punitive failure states
---

# Project Vision

Lumina Depths delivers the experience of a one-way journey into the unknown. Players descend through the ocean's stratified light zones, from sun-drenched coral reefs to the crushing darkness of hydrothermal vents, finally emerging into the ethereal glow of creatures evolved to make their own light. The game evokes watching a nature documentary from inside it - awe without anxiety, discovery without danger.

---

# Creative Pillars

## 1. Contemplative Wonder
Every moment should evoke awe, not anxiety. The ocean's beauty exists at every depth.

**Art:** Soft gradients, gentle particle effects, bioluminescent glows
**Sound:** Ambient drones, distant whale calls, peaceful textures
**Code:** Slow camera movement, generous creature AI approach distances

## 2. Gradual Revelation
The deep ocean reveals itself slowly, rewarding patience.

**Art:** Each zone has distinct visual language that unfolds gradually
**Sound:** Zone ambients crossfade, new creature sounds emerge with depth
**Code:** Creature spawn rates increase with time in zone

## 3. Living Ecosystem
Creatures behave authentically, not as game objects.

**Art:** Natural animation cycles, organic movement patterns
**Sound:** Creature vocalizations feel real, not game-y
**Code:** Boids flocking, curiosity AI, individual behavior variation

---

# Art Direction Notes

## Zone Color Strategies

### Zone 1: Sunlit Waters (0-200m)
- **Zenith:** Sky blue (#87CEEB)
- **Horizon:** Ocean blue (#4A90D9)
- **God Rays:** Warm gold-white (#FFFAE8)
- **Coral:** Vibrant pinks, oranges, purples
- **Feel:** Warm, welcoming, familiar

### Zone 2: Twilight Realm (200-1000m)
- **Zenith:** Deep blue (#2E6B9E)
- **Horizon:** Navy (#1A3A5E)
- **Marine Snow:** White particles
- **Kelp:** Dark green-brown (#1A3A2A)
- **Feel:** Transitional, mysterious, hints of unknown

### Zone 3: Midnight Abyss (1000-4000m)
- **Background:** Near-black gradient (#050A15 to #000000)
- **Bioluminescence:** Cyan (#00FFFF), Magenta (#FF00FF)
- **Anglerfish Lure:** Sickly green (#44FF88)
- **Feel:** Isolated, wondrous, alien beauty

### Zone 4: Hydrothermal Vents (4000-5000m)
- **Background:** Black with volcanic warmth (#0A0505 to #150808)
- **Vent Smoke:** Brown-gray (#332211)
- **Thermal Shimmer:** Orange-red (#FF4422)
- **Tube Worms:** Bright red tips
- **Feel:** Otherworldly, primordial, edge of life

### Zone 5: Luminara Trench (5000m+)
- **Background:** Ethereal gradient (#0A0A1A to #1A1A3A)
- **Bioluminescence:** Full spectrum convergence
- **Feel:** Transcendent, culminating, reward

## Creature Material Guidelines

| Creature Type | Specular | Shininess | Emissive | Alpha |
|---------------|----------|-----------|----------|-------|
| Hard shell (crab, isopod) | High | 0.7-0.8 | None | Opaque |
| Soft body (jelly, squid) | Low | 0.2-0.4 | 0.2-0.5 | Translucent |
| Bony fish | Medium | 0.5-0.6 | None/Low | Opaque |
| Deep-sea (anglerfish) | Low | 0.6-0.7 | Lure only | Opaque |

## Submersible Design

- Industrial but not military
- Glass canopy for visibility
- Warm interior lighting (amber/yellow)
- Orange accent panels
- Visible propulsion system

---

# Sound Direction Notes

## Zone Ambient Character

| Zone | Dominant Frequency | Texture | Activity |
|------|-------------------|---------|----------|
| Sunlit | Higher, brighter | Bubbles, fish | Active |
| Twilight | Mid-range | Whale echoes | Occasional |
| Midnight | Sub-bass | Silence, sudden | Sparse |
| Vents | Low rumble | Hissing, bubbling | Constant |
| Luminara | Ethereal | Harmonic tones | Slow waves |

## Audio Processing by Depth

| Depth | Filtering | Reverb | Character |
|-------|-----------|--------|-----------|
| Surface | Clear | Minimal | Bright |
| Mid-depths | Lowpass 6kHz | Growing | Murky |
| Abyss | Lowpass 3kHz | Massive (8s) | Isolated |
| Vents | Bandpass | Metallic | Industrial |
| Trench | Light highpass | Ethereal | Transcendent |

---

# Current Focus

**Updated:** 2025-12-29

## Completed Assets
- **Meshes (18/26):** submersible, whales, Zone 1 creatures, Zone 2 creatures, corals, bioluminescent creatures
- **Audio (6/36):** 4 zone ambients, 2 whale calls

## In Progress
- Zone 3/4 creature meshes (anglerfish, gulper_eel, tube_worms, etc.)
- Flora meshes (kelp, anemone, sea_grass)

## Next Priorities
1. Zone 3 creatures (Midnight Abyss - bioluminescent deep-sea life)
2. Zone 4 creatures (Hydrothermal Vents - extremophile life)
3. Flora and terrain meshes
4. Creature proximity sounds
5. Submersible SFX (propeller, hull creaks)
6. Texture generation for all meshes
