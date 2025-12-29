---
# Sonic Style Language Specification
# Override - Asymmetric Multiplayer

game: "Override"
version: 1.0

identity:
  tagline: "Industrial surveillance thriller in 8 bits"
  audio_pillars:
    - "Mechanical Dread - Facility as living threat"
    - "Surveillance Presence - Always being watched"
    - "Escape Urgency - Time pressure and chase tension"
  signature_sounds:
    - drone_hover       # Oscillating electric hum (threat awareness)
    - trap_spike        # Metallic scrape + impact (danger)
    - core_pickup       # Rising arpeggio chime (positive feedback)

style:
  primary: Industrial
  secondary: Dark Ambient
  intensity: Moderate
  era: Modern Retro

mood:
  menu: Mysterious + Tense
  exploration: Tense + Mechanical
  pursuit: Aggressive + Frantic
  victory_runners: Triumphant + Relief
  victory_overseer: Satisfied + Dominant
  defeat: Ominous + Descending

instruments:
  primary:
    - synth.bass.sub               # Low-end menace
    - synth.pad.evolving           # Atmospheric tension
    - percussion.electronic.industrial  # Mechanical rhythm
  accent:
    - synth.lead.fm                # Alert stingers
    - sfx.noise.filtered           # Industrial texture
  texture:
    - sfx.ambient.machinery        # Background hum
    - sfx.ambient.electrical       # Surveillance presence
---

# Music Direction

## Tempo Ranges

| Context | BPM Range | Character |
|---------|-----------|-----------|
| Menu | 70-90 | Brooding, anticipation |
| Exploration | 80-100 | Creeping, methodical |
| Pursuit | 140-160 | Frantic, driving |
| Victory | 100-120 | Resolving |
| Defeat | 60-80 | Descending, ominous |

## Key Tendencies

| Context | Keys | Rationale |
|---------|------|-----------|
| Menu | Cm, Gm | Dark, mysterious |
| Exploration | Dm, Am | Tension, unease |
| Pursuit | Em, Bm | Aggressive, urgent |
| Victory | C, G | Resolution, triumph |
| Defeat | Dm, Am | Unresolved, ominous |

## Adaptive Music System

| Layer | Content | Trigger |
|-------|---------|---------|
| Base | Low drone + subtle percussion | Always playing |
| Exploration | Atmospheric pad | Default gameplay |
| Pursuit | Driving rhythm + faster tempo | Drone within 48px |
| Climax | Full instrumentation + chase theme | Final 30s OR 2+ down |

### Transitions
- Crossfade between layers (0.5s)
- Drum fill on state change
- Filter sweep on intensity increase

---

# SFX Direction

## Footsteps

| Surface | Character | Variation |
|---------|-----------|-----------|
| Metal | Sharp, resonant click | 3 variants |
| Grate | Hollow, multiple reflections | 3 variants |
| Sprint | Louder + faster cadence + noise | Built from base |
| Crouch | Quieter + slower + deliberate | Built from base |

## Doors

| Action | Sound Character | Duration |
|--------|-----------------|----------|
| Open | Hydraulic hiss rising in pitch | 0.4s |
| Close | Hydraulic hiss falling + metal clank | 0.5s |
| Locked | Lock engage + denial buzzer | 0.3s |

## Traps

| Trap | Sound Character | Processing |
|------|-----------------|------------|
| Spike | Brief warning flash sync + metallic scrape + impact | Short reverb |
| Gas | Extended hiss + bubbling + expanding texture | Filtered, wide |
| Laser | Continuous electric hum + harmonics | Oscillating |

## Drones

| Action | Sound Character | Notes |
|--------|-----------------|-------|
| Hover | Oscillating electric hum | Looping, proximity-based volume |
| Spawn | Mechanical deployment + power-up | One-shot, 0.8s |
| Detect | Alert ping + targeting sound | Triggers chase music |

## UI Feedback

| Event | Sound Character | Priority |
|-------|-----------------|----------|
| Core Pickup | Rising arpeggio chime | High |
| Timer Warning | Urgent beeps, increasing frequency | Critical |
| Extraction Open | Triumphant chord fanfare | High |
| Energy Depleted | Low warning tone | Medium |
| Trap Cooldown Ready | Subtle ready ping | Low |

---

# Role-Based Audio

## Overseer Audio Mix

| Category | Volume | Notes |
|----------|--------|-------|
| Full Facility Audio | 100% | Hears everything |
| Music | 80% | Slightly ducked |
| UI Feedback | 100% | Power activations satisfying |
| Trap Triggers | 100% | Rewarding feedback |

## Runner Audio Mix

| Category | Volume | Distance Rules |
|----------|--------|----------------|
| Own Footsteps | 100% | Always audible |
| Other Runners | 50-100% | Proximity-based |
| Drones | 30-100% | Proximity-based, filtered at distance |
| Traps | 50-100% | Proximity warning |
| Music | 100% | Responds to personal danger |

### Runner Proximity Audio

| Distance | Volume | Filtering |
|----------|--------|-----------|
| 0-24px | 100% | None |
| 24-48px | 70% | Light lowpass (4kHz) |
| 48-64px | 40% | Heavy lowpass (2kHz) |
| 64px+ | 0% | Inaudible |

---

# Processing Signatures

## Reverb Settings

| Context | Type | Decay | Character |
|---------|------|-------|-----------|
| Footsteps | Room | 0.3s | Tight, industrial |
| Doors | Room | 0.4s | Mechanical |
| Traps | Room | 0.5s | Impactful |
| Drones | Small Hall | 0.6s | Hovering presence |
| Music | Plate | 1.0s | Atmospheric |

## Master Processing

- **Compression:** Moderate, maintains dynamics
- **EQ:** Slight low-end boost, crisp highs
- **Ducking:** Music ducks under critical SFX
- **Limiting:** Soft limiting for consistency

---

# Mix Priorities (1 = highest)

1. Runner Death (critical feedback)
2. Trap Activation (high priority warning)
3. Core Pickup (positive feedback)
4. Drone Hover (threat awareness)
5. Footsteps (movement feedback)
6. Doors (environmental)
7. Music (background)
8. Ambient (texture)

---

# Audio Budget

| Category | Channels | Notes |
|----------|----------|-------|
| Music | 2 | Stereo adaptive layers |
| Footsteps | 1 | Player + proximity blend |
| SFX | 2 | Traps, doors, pickups |
| Drones | 1 | Proximity-based loop |
| Ambience | 1 | Facility hum |
| **Total** | 7 | Comfortable headroom |

---

# Reference Audio

For inspiration (not direct copying):

- **Dead by Daylight:** Chase music intensity system, terror radius
- **Alien: Isolation:** Environmental audio as threat indicator
- **Among Us:** Simple but effective alert sounds
- **FTL:** Retro-industrial ambient loops
- **Papers Please:** Industrial bureaucratic tension
