---
# Sonic Style Language Specification
# Prism Survivors - Roguelite Wave Survival

game: "Prism Survivors"
version: 1.0

identity:
  tagline: "Prismatic power through crystalline chaos"
  audio_pillars:
    - "Crystalline Resonance - Glass-like timbres, metallic harmonics"
    - "Responsive Power Fantasy - Combos audible, level-ups euphoric"
    - "Escalating Sonic Intensity - Audio mirrors gameplay intensity"
  signature_sounds:
    - crystal_shatter   # Enemy death - satisfying glass break
    - combo_milestone   # Combo 10/25/50 - escalating celebration
    - level_up          # Euphoric power surge

style:
  primary: Hybrid
  secondary: Synthwave
  intensity: High
  era: Modern

mood:
  title_screen: Mysterious + Epic
  class_selection: Heroic + Anticipation
  crystal_cavern: Mysterious + Tense
  enchanted_forest: Mystical + Aggressive
  volcanic_depths: Aggressive + Epic
  void_realm: Epic + Dread
  boss_encounter: Epic + Aggressive
  victory: Triumphant + Relief
  defeat: Melancholic + Acceptance
  level_up: Triumphant + Empowerment
  combo_milestone: Excitement + Power

instruments:
  primary:
    - synth.pad.crystalline    # Shimmering evolving pads
    - synth.lead.glass         # Clean high harmonics
    - synth.bass.sub           # Deep foundation
  accent:
    - percussion.electronic.metallic  # Crystalline hits
    - synth.arp.cascading      # Rapid arpeggios
    - orchestral.strings.staccato     # Dramatic punctuation
  texture:
    - synth.fx.shimmer         # Constant crystalline ambience
    - orchestral.choir.soft    # Ethereal backing
    - synth.pad.drone          # Low-frequency tension
---

# Music Direction

## Tempo Ranges

| Context | BPM Range | Character |
|---------|-----------|-----------|
| Title/Menu | 80-100 | Contemplative, building |
| Early Waves (1-5) | 110-120 | Energetic, approachable |
| Mid Waves (6-10) | 120-130 | Driving, intensifying |
| Late Waves (11-15) | 130-140 | Aggressive, urgent |
| Final Stage (16-20) | 140-150 | Climactic, relentless |
| Boss Encounter | 150-160 | Maximum intensity |

## Key Tendencies

| Context | Keys | Rationale |
|---------|------|-----------|
| Heroic/Positive | D Major, A Major, E Major | Bright, triumphant |
| Mysterious/Neutral | E minor, A minor (natural) | Crystalline, floating |
| Tense/Negative | D minor, F minor, diminished | Dark, threatening |
| Epic/Boss | E minor + raised 7th | Dramatic tension |

## Adaptive Music System

| Layer | Content | Trigger |
|-------|---------|---------|
| Layer 1 | Base ambient pad | Always playing |
| Layer 2 | Rhythmic percussion | Enemies spawn |
| Layer 3 | Melodic lead | Wave start |
| Layer 4 | Intensity layer | Combo > 10 |
| Layer 5 | Danger stinger | Low health |

---

# SFX Direction

## Impact Character

- **Style:** Crystalline, metallic, harmonically rich
- **Weight:** Medium-Heavy (satisfying but not sluggish)
- **Processing:** Short reverb tail, slight chorus

## Weapon SFX Families

| Weapon Type | Sound Character | Example |
|-------------|-----------------|---------|
| Melee (Cleave, Crush) | Heavy metallic impact + glass shatter | Low thunk + high sparkle |
| Ranged (Arrow, Missile) | Whoosh + crystalline ping on hit | Airy release + tonal impact |
| AoE (Nova, Fireball) | Swell + explosive release + sparkle decay | Build → burst → shimmer |
| Beam (Soul Drain) | Continuous harmonic drone | Oscillating resonance |
| Chain (Lightning) | Rapid crackling + pitched impacts | Crackle cascade |
| Orbit (Shadow Orb) | Humming oscillation + pulse | Rhythmic hum |

## Enemy SFX

| Enemy Tier | Sound Character | Volume |
|------------|-----------------|--------|
| Basic | Short, soft, non-intrusive | Low |
| Elite | Heavier, more menacing | Medium |
| Boss | Deep, resonant, imposing | High |

## UI SFX

- **Style:** Soft crystalline chimes
- **Family:** Glass bells, soft synthetic tones
- **Avoid:** Harsh clicks, industrial sounds

## Combo System Audio

| Combo Tier | Multiplier | Stinger Character |
|------------|------------|-------------------|
| 5+ | 1.2x | Brief sparkle |
| 10+ | 1.5x | Rising arpeggio |
| 25+ | 2.0x | Triumphant chord |
| 50+ | 2.5x | Full fanfare burst |

---

# Processing Signatures

| Element | Reverb | Decay | Character |
|---------|--------|-------|-----------|
| Music | Plate | 1.2s | Spacious, crystalline |
| Combat SFX | Room | 0.4s | Punchy, present |
| UI | Small Room | 0.2s | Clean, immediate |
| Ambient | Hall | 2.0s | Ethereal, distant |

## Mix Priorities (1 = highest)

1. Player Feedback (damage, level-up, death)
2. Combat/Action SFX (weapons, enemy deaths, combos)
3. Music (dynamic, never overpowers)
4. UI Sounds (navigation, selection)
5. Environmental Ambient (stage hazards)

---

# Reference Audio

Consider for inspiration (not direct copying):

- **Risk of Rain 2 (Chris Christodoulou):** Layered intensity, electronic/orchestral hybrid
- **Hades (Darren Korb):** Dynamic combat music, satisfying impacts
- **Vampire Survivors:** Retro-synth energy, escalating intensity
- **Celeste (Lena Raine):** Crystalline textures, emotional resonance

---

# Implementation Notes

## Audio Budget

| Category | Channels | Notes |
|----------|----------|-------|
| Music | 2 | Stereo adaptive layers |
| Player SFX | 2 | Weapons + movement |
| Enemy SFX | 3 | Death + attack + ambient |
| UI | 1 | Interruptible |
| Ambient | 1 | Stage background |
| **Total** | 9 | Well under 16 channel limit |

## File Formats

- **Music:** XM tracker format (5 tracks defined)
- **SFX:** WAV, mono, 22050 Hz
- **Max SFX Duration:** 2 seconds (except level-up: 3s)
