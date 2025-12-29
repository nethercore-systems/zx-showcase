# Project Status: Neon Drift

Last updated: 2025-12-30

## Setup Completed
- [x] Game Design Document (docs/GDD.md)
- [x] Creative Direction (.studio/creative-direction.local.md)
- [x] Sonic Identity (.studio/sonic-identity.local.md)
- [x] Design Notes (DESIGN_NOTES.md - detailed asset specs)

## Phase
**Current:** Testing & Polish (ROM built, music composition pending)

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

### Cars (7/7 Complete - Enhanced Quality)
| Car | Mesh | Tris | Albedo | Emissive |
|-----|------|------|--------|----------|
| Speedster | speedster.glb | 742 | speedster.png | speedster_emissive.png |
| Muscle | muscle.glb | 690 | muscle.png | muscle_emissive.png |
| Racer | racer.glb | 810 | racer.png | racer_emissive.png |
| Drift | drift.glb | 734 | drift.png | drift_emissive.png |
| Phantom | phantom.glb | 742 | phantom.png | phantom_emissive.png |
| Titan | titan.glb | 762 | titan.png | titan_emissive.png |
| Viper | viper.glb | 670 | viper.png | viper_emissive.png |

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

### Music Tracks (0/5 - Specs Ready, XM Composition Pending)
| Track | Spec | BPM | Key | Mood | XM File |
|-------|------|-----|-----|------|---------|
| Sunset Strip | Ready | 128 | Am | Nostalgic, warm | NOT YET COMPOSED |
| Neon City | Ready | 132 | Em | Urban, energetic | NOT YET COMPOSED |
| Void Tunnel | Ready | 138 | Dm | Mysterious, intense | NOT YET COMPOSED |
| Crystal Cavern | Ready | 130 | Bm | Ethereal, tense | NOT YET COMPOSED |
| Solar Highway | Ready | 140 | Fm | Epic, triumphant | NOT YET COMPOSED |

**Note:** Synth samples (kick, snare, hihat, etc.) are ready for use as instruments.
Compose in MilkyTracker or OpenMPT, export as XM format.

## Recent Changes (2025-12-30)
1. **Enhanced car generator** - Complete rewrite with improved geometry
2. **Curved body panels** - Tapered boxes, beveled edges, aerodynamic shapes
3. **Distinct car silhouettes** - Each car type now has unique personality:
   - Speedster: Sleek low-slung magenta racer (742 tris)
   - Muscle: Boxy aggressive blue muscle car (690 tris)
   - Racer: F1-inspired green technical racer (810 tris)
   - Drift: Wide-body orange Japanese drift car (734 tris)
   - Phantom: Stealth wedge purple mystery car (742 tris)
   - Titan: Heavy cyan/silver truck (762 tris)
   - Viper: Compact yellow sports car (670 tris)
4. **Improved textures** - Metallic gradients, panel lines, window tint, neon placement
5. **All cars within ZX budget** - 670-810 triangles (target: 800-1200)
6. **Fixed car/track direction** - Cars now face +Z (same as track generation direction)
7. **Fixed AI navigation** - AI cars now steer correctly toward waypoints
8. **Fixed car selector textures** - Car preview now properly binds albedo/emissive textures

## Previous Changes (2025-12-29)
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
