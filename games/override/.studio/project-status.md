# Project Status: Override

Last updated: 2025-12-29

## Setup Completed
- [x] Game Design Document v2.0 (docs/design/game-design.md) — Updated for 3D Mode 0
- [x] Asset Specifications (docs/design/asset-specs.md)
- [x] Constraint Validation (docs/design/constraint-validation.md)
- [x] Creative Direction v2.0 (.studio/creative-direction.local.md) — Updated for 3D
- [x] Sonic Identity v2.0 (.studio/sonic-identity.local.md) — Updated for 3D

## Phase
**Current:** 3D Conversion — Transitioning from 2D tile-based to 3D Mode 0

## Technical Approach
- **Render Mode:** 0 (Lambert) — `texture_sample × vertex_color`
- **Resolution:** 960×540 (ZX standard)
- **Lighting:** Baked into vertex colors (no dynamic lights)
- **Camera (Runner):** Low-angle third-person, FOV 70°, fog at 20-40 units
- **Camera (Overseer):** Orthographic god-view, 60 units wide

## Code Status
- [x] Game logic complete (lib.rs) — Needs 3D position updates
- [x] Overseer AI complete (ai.rs) — Works with any rendering
- [ ] 3D camera systems — Needs implementation
- [ ] Fog-based view limiting — Needs implementation
- [ ] 3D facility generation — Needs conversion from 2D tiles
- [x] Rollback netcode ready — State is position-based, works in 3D

## Asset Status (3D Conversion Needed)

### Environment Meshes
- [ ] Floor tiles (4 variants): metal, grate, panel, damaged
- [ ] Wall sections (6 variants): solid, window, vent, pipe, screen, doorframe
- [ ] Doors (3 states): open, closed, locked
- [ ] Corner/junction pieces
- [ ] Ceiling panels

### Character Meshes
- [ ] Runner (300-500 tris, skeletal animation)
- [ ] Drone (100-200 tris, hover animation)
- [ ] Data Core (50-100 tris, rotation animation)

### Trap Meshes
- [ ] Spike plate (30-60 tris)
- [ ] Gas vent (20-40 tris)
- [ ] Laser emitter (40-80 tris)

### Textures (RGBA8 for Mode 0)
- [ ] Environment textures (128×128)
- [ ] Character textures (256×256)
- [ ] Trap textures (64×64)
- [ ] Effect textures (various sizes)

### Audio
- [x] SFX specs defined (16 sounds)
- [x] Music specs defined (5 tracks)
- [ ] SFX implementation
- [ ] Music implementation

## Next Steps

### Immediate (3D Foundation)
1. [ ] Implement dual camera system (Runner + Overseer)
2. [ ] Create basic 3D floor/wall tile meshes
3. [ ] Update facility generator for 3D placement
4. [ ] Add fog for Runner view limiting
5. [ ] Test basic 3D movement and collision

### Short-term (Core Assets)
6. [ ] Create Runner character mesh with animations
7. [ ] Create Drone mesh with hover animation
8. [ ] Create Data Core mesh with rotation
9. [ ] Create door mesh with open/close animation

### Polish
10. [ ] Create trap meshes and animations
11. [ ] Implement particle effects (gas, sparks, dust)
12. [ ] Implement audio system
13. [ ] Balance tuning (energy costs, trap cooldowns)

## Quick Reference
- **Concept:** Asymmetric 1v3 multiplayer - Overseer vs Runners (now in 3D!)
- **Art Style:** Industrial flat-shaded 3D, vertex color lighting
- **Sonic Mood:** Industrial tension, mechanical dread
- **Render Mode:** 0 (Lambert)
- **Players:** 2-4 (1 Overseer + 1-3 Runners)
- **ROM Estimate:** ~2.5 MB
- **State Size:** ~50 KB (fast rollback)

## Files Updated in v2.0
- `docs/design/game-design.md` — Full 3D Mode 0 conversion
- `.studio/creative-direction.local.md` — 3D art direction, vertex colors, camera specs
- `.studio/sonic-identity.local.md` — 3D distance-based audio
- `.studio/project-status.md` — This file
