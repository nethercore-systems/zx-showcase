---
# Creative Direction Configuration
# Override - Asymmetric Multiplayer (3D Mode 0)

# Art Direction
art_style: industrial-surveillance-dystopia-3d
color_palette: cold-industrial-with-danger-accents
render_mode: 0  # Lambert - texture × vertex_color, no dynamic lighting
style_spectrums:
  fidelity: 4     # 1=stylized, 9=realistic (low-poly 3D with flat shading)
  detail: 5       # 1=simple, 9=complex (moderate for readability)
  saturation: 4   # 1=muted, 9=vibrant (muted base, saturated accents)
  contrast: 8     # 1=low-key, 9=high-key (very high for 3D silhouettes)
  form: 4         # 1=geometric, 9=organic (geometric industrial, some curves)
  line: 3         # 1=hard-edge, 9=soft (hard geometry edges via vertex colors)

# 3D Rendering Configuration
rendering:
  mode: 0  # Lambert
  resolution: "960x540"
  lighting: baked-vertex-colors  # No dynamic lights in Mode 0
  fog: true  # Distance fog for Runner view limiting
  camera_runner: low-angle-third-person
  camera_overseer: orthographic-godview

# Sound Direction
sonic_identity: industrial-tension
mix_priority: gameplay-first
audio_pillars:
  - "Mechanical Dread"
  - "Surveillance Presence"
  - "Escape Urgency"

# Tech Direction
architecture: rollback-deterministic
determinism: required
rom_size_estimate: 2.5  # MB
state_size_estimate: 50  # KB - small for fast rollback

# Creative Vision
creative_pillars:
  - Asymmetric Stress
  - Surveillance Paranoia
  - Narrow Escapes
target_audience: "Players who enjoy asymmetric multiplayer (Dead by Daylight, Among Us), hidden information games, and quick competitive sessions"
avoid_patterns:
  - Generic horror tropes
  - Gratuitous violence
  - Pay-to-win mechanics
  - RNG-heavy outcomes
  - Symmetrical gameplay
  - Complex PBR materials (Mode 0 is flat-shaded)
---

# Project Vision

Override delivers quick, tense asymmetric matches where one player's omniscient control battles three players' desperate stealth. Every round creates memorable "almost got you" moments as the Overseer manages limited energy to hunt while Runners exploit every opening to escape. Industrial thriller, not horror.

---

# Creative Pillars

## 1. Asymmetric Stress
The Overseer and Runners experience fundamentally different types of tension.

**Overseer Experience:**
- God-view omniscience but resource scarcity
- Satisfaction from sprung traps and caught runners
- Pressure of managing multiple threats

**Runner Experience:**
- Limited vision creates vulnerability
- Constant awareness of being watched
- Triumph from narrow escapes and teamwork

**Art:** Different UI layouts per role, Overseer sees all, Runners see limited
**Sound:** Overseer hears full facility, Runners hear proximity-based audio
**Code:** Separate input handling, role-dependent rendering

## 2. Surveillance Paranoia
The facility watches. Players should always feel observed.

**Art:** Camera indicators, screen walls with glow, drone red eyes
**Sound:** Ambient hum, camera ping sounds, drone hover loops
**Code:** Camera ping power, drone detection radius, visibility mechanics

## 3. Narrow Escapes
Victory comes through close calls, not domination.

**Art:** Extraction point glow, sprint dust effects, door animations
**Sound:** Heartbeat tension music, chase music triggers, extraction fanfare
**Code:** Energy management forcing strategic choices, timer pressure

---

# Art Direction Notes (3D Mode 0)

## Color Philosophy

| Element | Color (Hex) | Vertex Color Usage | Purpose |
|---------|-------------|-------------------|---------|
| **Base/Facility** | #1a1a2e to #5a5a6e | Floor/wall base tint | Industrial foundation |
| **Metallic** | #8888aa to #aaaacc | Edge highlights | Surface detail via vertex colors |
| **Cyan** | #00ffff, #45b991 | Emissive-like bright tint | Player-positive (cores, extraction, visor) |
| **Red** | #ff3333, #cc2222 | Danger indicator tint | Danger (traps, drones, locked doors) |
| **Yellow** | #ffcc00 | Interactive highlight | Interactive/Warning (doors, timer) |
| **Green** | #00ff88 | Runner suit base | Runner identity |
| **Shadow (baked)** | #0a0a15 | Corners, undersides | Fake ambient occlusion |
| **Highlight (baked)** | #ffffff tinted | Top faces, edges | Fake directional light |

## Mode 0 Visual Language

1. **Strong silhouettes** — Geometry readable at distance
2. **Baked lighting via vertex colors** — No dynamic lights, but pre-computed light/shadow
3. **Color coding for gameplay** — Red=danger, cyan=objective, yellow=interactive
4. **High contrast edges** — Vertex color gradients at mesh edges
5. **Fog for atmosphere** — Gray-blue fog for Runner view limiting

## 3D Asset Style

| Asset Type | Poly Budget | Texture | Vertex Colors | Notes |
|------------|-------------|---------|---------------|-------|
| Environment tiles | 4-30 tris | 128×128 | Baked AO + top light | Modular, snap together |
| Runners | 300-500 tris | 256×256 | Suit color per player | Skeletal animation |
| Drones | 100-200 tris | 128×128 | Red warning glow | Hover bob animation |
| Traps | 30-80 tris | 64×64 | Red when armed | State-based animation |
| Data Cores | 50-100 tris | 64×64 | Cyan pulse via color | Rotation animation |
| Doors | 20-50 tris | 128×128 | Yellow interactive | Open/close animation |

## Environment Mesh Design (3D)

| Mesh | Geometry | Vertex Colors | Texture |
|------|----------|---------------|---------|
| floor_metal | Flat plane, beveled edges | Top=light, edges=shadow | Metal grid pattern |
| floor_grate | Recessed plane with holes | Dark underneath, red optional | Grate texture |
| floor_panel | Raised panel with seams | Highlight on top, seam shadows | Tech panel texture |
| wall_solid | Box, inset panels | Shadow in panels, light on edges | Plain metal texture |
| wall_window | Wall with cutout + glass plane | Glass=cyan tint, frame=highlight | Window frame texture |
| wall_vent | Wall with dark recessed vent | Vent=dark interior | Vent grate texture |
| wall_pipe | Wall + pipe cylinder | Pipe=highlight on top | Pipe texture |
| wall_screen | Wall + emissive quad | Screen=cyan glow | Screen noise texture |
| wall_doorframe | Archway shape | Frame=yellow trim | Doorframe texture |

## Camera-Specific Considerations

**Runner View (third-person):**
- Fog limits view to 20-40 units
- Walls fully occlude (no see-through)
- Character silhouette must read against dark environment
- Cyan objectives must pop at distance

**Overseer View (orthographic god-view):**
- All entities must be distinguishable from above
- Runners as colored markers (green dots)
- Traps as red indicators
- Doors as yellow outlines
- Data cores as cyan diamonds

---

# Sound Direction Notes

## Role-Based Audio

### Overseer Hears:
- Full spatial audio of entire facility
- All Runner footsteps at appropriate volume
- All trap activations
- Energy regeneration sounds
- Music responds to Runner proximity to danger

### Runners Hear:
- Limited proximity radius (~48 pixels)
- Own footsteps loudest
- Distant sounds heavily filtered
- Chase music when drone nearby
- Heartbeat effect when trap armed nearby

## Music States

| State | Character | Trigger |
|-------|-----------|---------|
| Exploration | Low tension drone + subtle percussion | Default gameplay |
| Pursuit | Driving rhythm + faster tempo | Drone within 48px of Runner |
| Climax | Full instrumentation | Final 30 seconds OR 2+ Runners down |
| Victory | Triumphant fanfare | Extraction complete |
| Defeat | Ominous descent | All Runners eliminated |

---

# Current Focus

What's being worked on:
- Converting from 2D tile-based to 3D Mode 0 rendering
- Updating all assets for 3D (meshes instead of sprites)
- Implementing dual camera systems (third-person + god-view)

Next priorities:
1. Create 3D modular environment tile meshes
2. Create 3D character meshes with skeletal animation
3. Implement fog-based view limiting for Runners
4. Update procgen pipeline for 3D facility generation
5. Balance tuning (energy costs, trap cooldowns)
6. Audio implementation
