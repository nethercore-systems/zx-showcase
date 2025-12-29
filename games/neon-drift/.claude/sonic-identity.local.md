---
# Sonic Style Language Specification
# Neon Drift - Arcade Racing

game: "Neon Drift"
version: 1.0

identity:
  tagline: "Chase the horizon. Become the light."
  audio_pillars:
    - "Pumping Energy - 128-140 BPM synthwave drives forward"
    - "Nostalgic Futurism - 80s synths with modern clarity"
    - "Dynamic Feedback - Boost roars, drift squeals, collisions crunch"
  signature_sounds:
    - boost_activate    # Explosive whoosh + sub hit
    - drift_initiate    # Tire screech + rubber burn
    - checkpoint_pass   # Chime + woosh with delay

style:
  primary: Synthwave
  secondary: Outrun
  intensity: High
  era: 80s Retrofuture

mood:
  menu: Nostalgic + Anticipation
  sunset_strip: Warm + Cruising
  neon_city: Urban + Energetic
  void_tunnel: Mysterious + Intense
  crystal_cavern: Ethereal + Tense
  solar_highway: Epic + Triumphant
  victory: Euphoric + Celebratory
  defeat: Melancholic + Brief

instruments:
  primary:
    - synth.lead.sawtooth.detuned  # Fat, bright, singing leads
    - synth.bass.square_saw        # Punchy, sub-heavy bass
    - synth.pad.pwm                # Wide, warm atmospherics
  accent:
    - synth.arp.filtered           # Bubbly, rhythmic arpeggios
    - synth.brass.stab             # Punchy accent hits
  percussion:
    - drums.kick.808               # Deep, punchy kick
    - drums.snare.gated            # 80s gated reverb snare
    - drums.hihat.crispy           # Driving rhythm hats
---

# Music Direction

## Track-Specific Music

| Track | BPM | Key | Primary Mood | Signature Element |
|-------|-----|-----|--------------|-------------------|
| Sunset Strip | 128 | Am | Nostalgic, warm | Arpeggiated chords, mellow lead |
| Neon City | 132 | Em | Urban, energetic | Driving bass, punchy drums |
| Void Tunnel | 138 | Dm | Mysterious, intense | Dark pads, stuttered synths |
| Crystal Cavern | 130 | Bm | Ethereal, tense | Crystalline arps, deep sub bass |
| Solar Highway | 140 | Fm | Epic, triumphant | Soaring lead, layered chords |

## Composition Guidelines

### Verse/Build Sections
- Minimal drums, arpeggiated chords
- Bassline establishes groove
- Creates anticipation for chorus

### Chorus/Drop Sections
- Full drums with gated snare
- Soaring lead melody
- Layered synth chords
- Maximum energy

### Transitions
- Filter sweeps (low to high)
- Drum fills with toms
- Brief breakdown before drop

---

# SFX Direction

## Engine Sounds

| Car Class | Idle Character | Rev Character | Boost Modifier |
|-----------|---------------|---------------|----------------|
| Speedster | Mid rumble, clean | Linear rise | Turbo spool |
| Muscle | Deep rumble, burble | Aggressive roar | Supercharger whine |
| Racer | High whine | Screaming revs | Wastegate chirp |
| Drift | Turbo hiss | Sharp rise | Blow-off valve |
| Phantom | Electric hum | Whirring increase | Electric surge |
| Titan | Heavy diesel-like | Slow build | Deep whoosh |
| Viper | Exotic warble | Banshee scream | Multi-stage boost |

## Driving SFX

| Sound | Character | Trigger | Processing |
|-------|-----------|---------|------------|
| Engine Idle | Class-specific rumble | Always | Light chorus |
| Engine Rev | Pitch with speed | Throttle | Pitch envelope |
| Boost Activate | Explosive whoosh + sub | Boost button | Heavy compression |
| Boost Sustain | Rushing wind + flame | During boost | Stereo spread |
| Drift Initiate | Tire screech | Drift start | Pitch variation |
| Drift Sustain | Rubber burn loop | During drift | Modulated |
| Drift Exit | Tire chirp + speed burst | Drift end | Quick reverb |
| Wall Collision | Metal crunch + debris | Impact | Short reverb |
| Car-to-Car | Lighter metal clang | Contact | Minimal reverb |

## Race Events

| Sound | Character | Processing |
|-------|-----------|------------|
| Countdown 3-2-1 | Synth beeps, ascending | Clean, punchy |
| Race Start (GO!) | Synth brass fanfare | Wide stereo |
| Checkpoint | Chime + woosh | Delay tail |
| Lap Complete | Ascending arpeggio | Medium reverb |
| Finish (1st) | Full fanfare + synth brass | Celebratory |
| Finish (2nd-4th) | Shorter fanfare | Less dramatic |

---

# Processing Signatures

## Reverb Settings

| Context | Type | Decay | Character |
|---------|------|-------|-----------|
| Engine SFX | Room | 0.3s | Tight, present |
| Environment | Plate | 0.8s | Spacious |
| Music | Plate | 1.2s | Wide, warm |
| Victory Fanfare | Hall | 1.5s | Celebratory |

## Master Processing

- **Compression:** Side-chain pumping on music (keyed to kick)
- **EQ:** Warm low-mids, crisp highs
- **Stereo:** Wide music, centered SFX
- **Limiting:** Soft limiting for loudness

## Mix Priorities (1 = highest)

1. Player Feedback (boost, drift, collision)
2. Music (drives the experience)
3. Engine (class identity)
4. Environmental (checkpoints, ambience)
5. Other Players (in multiplayer)

---

# Adaptive Audio

## Speed-Based Modulation

| Speed Range | Music Volume | Engine Volume | Wind Volume |
|-------------|--------------|---------------|-------------|
| 0-30% | 100% | 80% | 0% |
| 30-70% | 95% | 90% | 30% |
| 70-100% | 90% | 100% | 60% |
| Boost | 85% | 110% | 100% |

## Position-Based Music

| Position | Music Intensity | Notes |
|----------|-----------------|-------|
| 1st Place | Full | All layers active |
| 2nd-3rd Place | Medium | Some layers reduced |
| 4th Place | Building | Tension layers added |
| Comeback | Rising | Filter sweep building |

---

# Implementation Notes

## Audio Budget

| Category | Channels | Notes |
|----------|----------|-------|
| Music | 2 | Stereo XM playback |
| Engine (Player) | 1 | Dynamic pitch |
| SFX | 2 | Boost/drift/collision |
| Ambience | 1 | Wind/environmental |
| Other Players | 2 | Engines in multiplayer |
| **Total** | 8 | Comfortable headroom |

## File Formats

- **Music:** XM tracker format (5 tracks)
- **SFX:** WAV, mono, 22050 Hz
- **Engine Loops:** Seamless 0.5-1s loops
- **Instrument Samples:** 8 synth samples for XM

## Reference Tracks

For inspiration (not direct copying):
- **Kavinsky - Nightcall:** Perfect synthwave driving feel
- **Lazerhawk - Redline:** High-energy racing synthwave
- **Miami Nights 1984:** Warm, nostalgic synthwave
- **Perturbator - Dangerous Days:** Darker, more intense
