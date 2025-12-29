# Neon Drift - Game Design Document

## Overview

**Title:** Neon Drift
**Genre:** Arcade Racing
**Platform:** Nethercore ZX
**Players:** 1-4 (local split-screen, online multiplayer)
**Render Mode:** 2 (Metallic-Roughness PBR)

### Concept

Race through an eternal synthwave sunset where neon lights streak past at impossible speeds. Neon Drift captures the feeling of 80s arcade racing reimagined - pick a car, hit the track, and experience pure speed as spectacle.

### Tagline

"Chase the horizon. Become the light."

---

## Game Pillars

### 1. Eternal Sunset
The game exists in a perpetual synthwave twilight. Every environment captures a moment of nostalgic beauty - the sun always setting, the neon always glowing, the night always electric.

### 2. Speed as Spectacle
Speed is not just functional but theatrical. Boost flames, drift smoke, speed lines, and camera effects transform velocity into visual drama.

### 3. Arcade Purity
Accessible controls, immediate feedback, no simulation complexity. Pick up and play within 10 seconds, master over weeks.

### 4. Neon Personality
Each car and track has distinct character through its neon signature. Colors tell stories - cyan is classic, magenta is aggressive, green is sinister.

---

## Core Mechanics

### Controls

| Input | Action |
|-------|--------|
| Left Stick | Steer |
| RT | Accelerate |
| LT | Brake/Reverse |
| A | Drift (hold while turning) |
| B | Boost (when meter full) |

### Drift System
- Hold drift button while turning to initiate drift
- Longer drifts build more boost meter
- Release to exit drift with speed boost
- Risk/reward: drift too long and lose control

### Boost System
- Meter fills from drifting and near-misses
- Full meter enables single boost activation
- Boost provides ~20% speed increase for 3 seconds
- Visual: flame trail, speed lines, camera zoom

---

## Car Roster (7)

| Car | Speed | Accel | Handling | Difficulty | Character |
|-----|-------|-------|----------|------------|-----------|
| **Speedster** | 100% | 100% | 100% | ★★☆ | Balanced classic |
| **Muscle** | 95% | 110% | 85% | ★★☆ | Power with oversteer |
| **Racer** | 115% | 90% | 110% | ★★★ | High skill ceiling |
| **Drift** | 90% | 95% | 120% | ★★☆ | Handling specialist |
| **Phantom** | 105% | 95% | 90% | ★★☆ | Stealth supercar |
| **Titan** | 85% | 85% | 75% | ★☆☆ | Beginner-friendly tank |
| **Viper** | 120% | 75% | 105% | ★★★ | Expert-only hypercar |

See `DESIGN_NOTES.md` for detailed car visual specifications.

---

## Track Roster (5)

| Track | Difficulty | Length | Signature Feature |
|-------|------------|--------|-------------------|
| **Sunset Strip** | ★☆☆ | Short | Wide roads, gentle curves |
| **Neon City** | ★★☆ | Medium | Urban with billboards |
| **Void Tunnel** | ★★★ | Medium | Disorienting tunnel rings |
| **Crystal Cavern** | ★★★ | Long | Underground crystals |
| **Solar Highway** | ★★★★ | Long | Space highway near star |

See `DESIGN_NOTES.md` for detailed track specifications and EPU environment configs.

---

## Game Modes

### Time Trial
- Race against the clock
- Ghost recording/playback
- Online leaderboards

### Grand Prix
- 3-5 race series
- Points-based placement
- Unlockable content rewards

### Multiplayer
- 2-4 player split-screen
- Online with rollback netcode
- All tracks and cars available

---

## Technical Specifications

### Asset Budget
- Cars: ~800 tris each × 7 = 5,600 tris
- Tracks: ~1,200 tris per segment
- Props: ~300 tris total
- Textures: ~140 KB total

### ROM Estimate
~350 KB (well within ZX limits)

### Rollback State
- Car positions/velocities: ~200 bytes × 4 = 800 bytes
- Track state: ~100 bytes
- **Total:** <1 KB per frame

---

## Development Status

**Phase: All Assets Complete - Ready for Build & Testing**

### Completed
- [x] All 7 cars implemented (Speedster, Muscle, Racer, Drift, Phantom, Titan, Viper)
- [x] All 5 tracks with EPU environments
- [x] All track segments (straight, curves, tunnel, jump)
- [x] All props (barrier, boost pad, building, billboard, crystal)
- [x] All sound effects (11 SFX)
- [x] All synth samples (8 samples)
- [x] All music tracks (5 XM files)
- [x] Car/track difficulty stars in UI

### Next Steps
- [ ] Build ROM package
- [ ] Test in Nethercore player
- [ ] Balance tuning
- [ ] Publish to nethercore.systems

See `.claude/project-status.md` for detailed asset inventory.

---

*Document Version: 1.1*
*Last Updated: 2025-12-29*
