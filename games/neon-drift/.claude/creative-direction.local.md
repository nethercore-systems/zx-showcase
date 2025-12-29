---
# Creative Direction Configuration
# Neon Drift - Arcade Racing

# Art Direction
art_style: synthwave-retrowave-neon
color_palette: neon-on-dark
style_spectrums:
  fidelity: 4     # 1=stylized, 9=realistic (stylized but recognizable cars)
  detail: 6       # 1=simple, 9=complex (moderate for vehicles)
  saturation: 9   # 1=muted, 9=vibrant (maximum vibrance)
  contrast: 7     # 1=low-key, 9=high-key (neon on dark)
  form: 4         # 1=geometric, 9=organic (angular cars, smooth tracks)
  line: 6         # 1=hard-edge, 9=soft (clean with glow softness)

# Sound Direction
sonic_identity: synthwave-outrun
mix_priority: feedback-and-music
audio_pillars:
  - "Pumping Energy"
  - "Nostalgic Futurism"
  - "Dynamic Feedback"

# Tech Direction
architecture: rollback-deterministic
determinism: required
file_size_limit: 400  # KB - compact racing game

# Creative Vision
creative_pillars:
  - Eternal Sunset
  - Speed as Spectacle
  - Arcade Purity
  - Neon Personality
target_audience: "Fans of OutRun, Ridge Racer, synthwave aesthetic - players who want immediate arcade racing fun with friends"
avoid_patterns:
  - Simulation complexity
  - Realistic damage/physics
  - Muted color palettes
  - Loading screens
  - Complex upgrade systems
---

# Project Vision

Neon Drift captures the feeling of 80s arcade racing reimagined for modern play. Every frame is a synthwave album cover come to life - neon-soaked highways stretching toward an eternal sunset, cars that glow with personality, and the pure joy of speed without complication. Pick a car, hit the track, become the light.

---

# Creative Pillars

## 1. Eternal Sunset
The game exists in a perpetual synthwave twilight. The sun never rises, never sets - it hangs at that perfect golden hour moment forever.

**Art:** Pink/orange/purple gradient skies, long shadows, warm light
**Sound:** Warm synth pads, nostalgic chord progressions
**Code:** EPU environments tuned for eternal dusk, no day/night cycle

## 2. Speed as Spectacle
Velocity should be felt, not just measured. Every aspect of the game should amplify the sensation of speed.

**Art:** Speed lines, motion blur, camera shake, boost flames, drift smoke
**Sound:** Doppler effects, wind rush, engine pitch scaling
**Code:** FOV zoom on boost, camera lead on turns, particle density scaling

## 3. Arcade Purity
Pick up and play. No tutorials needed, no complex systems. Anyone should be racing within 10 seconds of starting.

**Art:** Clear visual language (green = go, red = danger, blue = checkpoint)
**Sound:** Immediate audio feedback for all actions
**Code:** Simple input mapping, generous collision handling

## 4. Neon Personality
Each car and track has its own neon signature that tells its story at a glance.

**Art:** Distinct emissive colors per car, track-specific neon theming
**Sound:** Unique engine notes per car class
**Code:** Neon color as first-class design element

---

# Art Direction Notes

## Color Philosophy

### Player Colors (Split-Screen)
| Player | Base | Emissive | Character |
|--------|------|----------|-----------|
| P1 | Navy | Cyan | Classic, reliable |
| P2 | Purple | Magenta | Aggressive, flashy |
| P3 | Brown | Orange | Warm, powerful |
| P4 | Maroon | Pink | Stylish, different |

### Environment Colors
| Element | Color | Purpose |
|---------|-------|---------|
| Boost | Yellow | Power, speed |
| Danger | Red | Walls, hazards |
| Checkpoint | Blue | Progress |
| Background | Deep purple/black | Contrast base |

### Car Neon Signatures
| Car | Base Color | Emissive | Personality |
|-----|------------|----------|-------------|
| Speedster | Silver | Cyan | Classic cool |
| Muscle | Red | Orange | Raw power |
| Racer | White | Green | Technical precision |
| Drift | Blue | Pink | Flashy style |
| Phantom | Charcoal | Toxic Green | Stealth menace |
| Titan | Gunmetal | White | Imposing calm |
| Viper | Venom Red | Gold | Ultimate prestige |

## Style References

- **Primary:** Synthwave, Outrun, Retrowave
- **Secondary:** Vaporwave (soft), Cyberpunk (hard)
- **Visual Influences:** Miami Vice, Blade Runner, Kavinsky, Far Cry 3: Blood Dragon
- **Anti-influences:** Realistic racing sims, gritty aesthetics, desaturated palettes

## Track Visual Language

| Track | Sky | Ground | Signature Visual |
|-------|-----|--------|------------------|
| Sunset Strip | Orange-pink gradient | Warm asphalt | Palm silhouettes |
| Neon City | Purple-blue night | Wet reflections | Neon billboards |
| Void Tunnel | Black void | Tron-like grid | Spinning rings |
| Crystal Cavern | Deep purple | Crystalline floor | Luminescent formations |
| Solar Highway | White-to-orange | Metallic panels | Solar corona |

---

# Sound Direction Notes

## Audio Character

- **Primary Style:** Synthwave / Outrun
- **Secondary Style:** Italo Disco (lighter moments)
- **Character:** Warm, punchy, driving, euphoric

## Music by Track

| Track | BPM | Key | Mood |
|-------|-----|-----|------|
| Sunset Strip | 128 | Am | Nostalgic, warm |
| Neon City | 132 | Em | Urban, energetic |
| Void Tunnel | 138 | Dm | Mysterious, intense |
| Crystal Cavern | 130 | Bm | Ethereal, tense |
| Solar Highway | 140 | Fm | Epic, triumphant |

## Engine Audio Philosophy
Each car class should have distinct engine character:
- **Speedster/Racer:** High-pitched, whiny
- **Muscle/Titan:** Deep, rumbling
- **Drift:** Turbo whistle accent
- **Phantom:** Quiet, electric hum
- **Viper:** Exotic, screaming

---

# Current Focus

What's being worked on:
- 3 new car implementations (Phantom, Titan, Viper)
- 2 new track environments (Crystal Cavern, Solar Highway)
- Asset critique improvements from DESIGN_NOTES.md

Next priorities:
1. Add interior detail to cars
2. Improve wheel spoke patterns
3. Standardize neon accent placement
4. Add road markings to tracks
