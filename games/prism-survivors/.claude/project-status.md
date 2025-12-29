# Project Status: Prism Survivors

Last updated: 2025-12-29

## Setup Completed
- [x] Game Design Document (docs/GDD.md)
- [x] Creative Direction (.claude/creative-direction.local.md)
- [x] Sonic Identity (.claude/sonic-identity.local.md)
- [x] Asset Pipeline (Blender-based GLB/PNG generation)

## Phase
**Current:** Polish (Phase 3 per GDD)
- Phase 1 (Visual Overhaul): ✅ Complete
- Phase 2 (Character Selection): ✅ Complete

## Code Status
- Game logic: Complete
- Character selection: Implemented
- Co-op mechanics: Implemented
- Rollback netcode: Ready

## Asset Pipeline (NEW)
The project now uses a Blender-based procedural asset pipeline:

```bash
# Generate all assets (requires Blender)
blender --background --python procgen/run_blender.py -- --game prism-survivors --all

# Generate specific categories
blender --background --python procgen/run_blender.py -- --game prism-survivors --heroes
blender --background --python procgen/run_blender.py -- --game prism-survivors --enemies
blender --background --python procgen/run_blender.py -- --game prism-survivors --pickups
blender --background --python procgen/run_blender.py -- --game prism-survivors --arena
blender --background --python procgen/run_blender.py -- --game prism-survivors --font

# Generate audio (standalone, no Blender required)
python procgen/audio/generate_sfx.py --game prism-survivors
```

### Output Format
- Meshes: GLB (glTF Binary) with embedded materials
- Textures: PNG (256x256 for characters, 128x128 for basic enemies, 512x512 for bosses)
- Audio: WAV (22050 Hz, mono, 16-bit)

### Asset Locations
- Meshes: `assets/models/meshes/*.glb`
- Textures: `assets/models/textures/*.png`
- Audio: `assets/audio/*.wav`

## Asset Status
- Heroes (6): ✅ Generated (26 GLB meshes total)
- Enemies (13): ✅ Generated (all types)
- Pickups (3): ✅ Generated (xp_gem, coin, powerup_orb)
- Projectiles (3): ✅ Generated (frost_shard, void_orb, lightning_bolt)
- Arena floor: ✅ Generated
- Textures (59): ✅ Generated (albedo + emission for all entities)
- Font: ✅ Generated (placeholder)
- Audio SFX (18): ✅ Generated

## Next Steps

1. [ ] Build and test the game with new assets
2. [ ] Review generated assets for quality
3. [ ] Iterate on style tokens if needed
4. [ ] Add particle effects for abilities
5. [ ] Add damage numbers
6. [ ] Add combo celebration effects

## Quick Reference
- **Concept:** Fast-paced co-op survival roguelite with crystalline enemies
- **Art Style:** Prismatic, geometric, faceted crystals, full rainbow spectrum
- **Sonic Mood:** Crystalline resonance, escalating intensity, hybrid electronic
- **Players:** 1-4 (local/online co-op with rollback)
- **ROM Estimate:** ~6MB

## Pipeline Architecture

```
procgen/
├── core/
│   ├── base_params.py       # UniversalStyleParams dataclass
│   └── blender_export.py    # GLB/PNG export via Blender bpy
├── configs/
│   └── prism_survivors.py   # HERO_PRESETS, ENEMY_PRESETS, STAGE_PRESETS
├── meshes/
│   ├── primitives.py        # Box, sphere, cylinder, prism
│   ├── humanoid.py          # Hero/enemy mesh generation
│   └── crystals.py          # Crystal meshes, XP gems, projectiles
├── textures/
│   ├── pbr_textures.py      # Albedo, emission, roughness
│   ├── noise_patterns.py    # Perlin, voronoi, etc.
│   └── glow_effects.py      # Prismatic glow, bioluminescence
├── audio/
│   └── generate_sfx.py      # Standalone numpy/scipy SFX generator
└── run_blender.py           # Main Blender pipeline runner
```
