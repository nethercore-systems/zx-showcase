# Project Status: Neon Drift

Last updated: 2025-12-29

## Setup Completed
- [x] Game Design Document (docs/GDD.md)
- [x] Creative Direction (.studio/creative-direction.local.md)
- [x] Sonic Identity (.studio/sonic-identity.local.md)
- [x] Design Notes (DESIGN_NOTES.md - detailed asset specs)

## Phase
**Current:** All Assets Complete - Ready for Build & Testing

## Code Status
- [x] Racing mechanics: Complete
- [x] Drift/boost system: Complete
- [x] Split-screen multiplayer: Complete
- [x] Rollback netcode: Ready
- [x] All 7 cars implemented: Complete
- [x] All 5 tracks with EPU environments: Complete
- [x] Car selection with difficulty stars: Complete
- [x] Track selection with difficulty stars: Complete

## Asset Status

### Cars (7/7 Complete)
| Car | Mesh | Albedo | Emissive |
|-----|------|--------|----------|
| Speedster | speedster.obj | speedster.png | speedster_emissive.png |
| Muscle | muscle.obj | muscle.png | muscle_emissive.png |
| Racer | racer.obj | racer.png | racer_emissive.png |
| Drift | drift.obj | drift.png | drift_emissive.png |
| Phantom | phantom.obj | phantom.png | phantom_emissive.png |
| Titan | titan.obj | titan.png | titan_emissive.png |
| Viper | viper.obj | viper.png | viper_emissive.png |

### Track Segments (5/5 Complete)
| Segment | Mesh | Texture |
|---------|------|---------|
| Straight | track_straight.obj | track_straight.png |
| Curve Left | track_curve_left.obj | track_curve_left.png |
| Curve Right | track_curve_right.obj | track_curve_right.png |
| Tunnel | track_tunnel.obj | track_tunnel.png |
| Jump | track_jump.obj | track_jump.png |

### Props (5/5 Complete)
| Prop | Mesh | Albedo | Emissive |
|------|------|--------|----------|
| Barrier | prop_barrier.obj | prop_barrier.png | prop_barrier_emissive.png |
| Boost Pad | prop_boost_pad.obj | prop_boost_pad.png | prop_boost_pad_emissive.png |
| Building | prop_building.obj | prop_building.png | - |
| Billboard | prop_billboard.obj | prop_billboard.png | prop_billboard_emissive.png |
| Crystal | crystal_formation.obj | crystal_formation.png | crystal_formation_emissive.png |

### Sound Effects (11/11 Complete)
| SFX | File | Duration |
|-----|------|----------|
| Engine Idle | engine_idle.wav | 0.50s |
| Engine Rev | engine_rev.wav | 0.30s |
| Boost | boost.wav | 0.50s |
| Drift | drift.wav | 0.40s |
| Brake | brake.wav | 0.30s |
| Shift | shift.wav | 0.10s |
| Wall Collision | wall.wav | 0.40s |
| Barrier Collision | barrier.wav | 0.25s |
| Countdown | countdown.wav | 0.15s |
| Checkpoint | checkpoint.wav | 0.40s |
| Finish | finish.wav | 0.80s |

### Synth Samples (8/8 Complete)
| Sample | File | Duration |
|--------|------|----------|
| Kick | synth_kick.wav | 0.30s |
| Snare | synth_snare.wav | 0.25s |
| Hi-Hat | synth_hihat.wav | 0.05s |
| Open Hat | synth_openhat.wav | 0.30s |
| Bass | synth_bass.wav | 0.50s |
| Lead | synth_lead.wav | 0.50s |
| Pad | synth_pad.wav | 1.00s |
| Arp | synth_arp.wav | 0.15s |

### Music Tracks (5/5 Complete)
| Track | File | BPM | Key | Mood |
|-------|------|-----|-----|------|
| Sunset Strip | sunset_strip.xm | 128 | Am | Nostalgic, warm |
| Neon City | neon_city.xm | 132 | Em | Urban, energetic |
| Void Tunnel | void_tunnel.xm | 138 | Dm | Mysterious, intense |
| Crystal Cavern | crystal_cavern.xm | 130 | Bm | Ethereal, tense |
| Solar Highway | solar_highway.xm | 140 | Fm | Epic, triumphant |

## Recent Changes (2025-12-29)
1. Created proper asset directory structure (assets/models/)
2. Converted all 7 car meshes and 14 textures
3. Added difficulty star ratings to car selection UI
4. Generated 5 track segment meshes
5. Generated 5 prop meshes with textures
6. Generated 11 sound effects
7. Generated 8 synth instrument samples
8. Generated 5 XM tracker music files with spec documents

## Next Steps
1. [ ] Build ROM package with `nether build`
2. [ ] Test in Nethercore player
3. [ ] Balance tuning (car stats, track difficulty)
4. [ ] Polish visual effects (particles, camera)
5. [ ] Publish to nethercore.systems

## Quick Reference
- **Concept:** Synthwave arcade racing through eternal sunset
- **Art Style:** Synthwave, neon-on-dark, maximum vibrance
- **Sonic Mood:** 128-140 BPM synthwave, nostalgic futurism
- **Players:** 1-4 (local split-screen, online multiplayer)
- **ROM Estimate:** ~350KB

## Asset Summary
| Category | Meshes | Textures | Audio | Status |
|----------|--------|----------|-------|--------|
| Cars | 7 | 14 | - | Complete |
| Tracks | 6 | 5 | - | Complete |
| Props | 5 | 8 | - | Complete |
| SFX | - | - | 11 | Complete |
| Synth | - | - | 8 | Complete |
| Music | - | - | 5 | Complete |
| **Total** | 18 | 27 | 24 | **100%** |

## Scripts
- `scripts/convert_assets.py` - Convert PPM to PNG, organize assets
- `scripts/generate_track_meshes.py` - Generate track/prop OBJ meshes
- `scripts/generate_textures.py` - Generate track/prop PNG textures
- `scripts/generate_sfx.py` - Generate WAV sound effects and synth samples
- `scripts/generate_music.py` - Generate XM tracker music files
