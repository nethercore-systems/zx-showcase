---
# Creative Direction Configuration
# Override - Asymmetric Multiplayer

# Art Direction
art_style: industrial-surveillance-dystopia
color_palette: cold-industrial-with-danger-accents
style_spectrums:
  fidelity: 3     # 1=stylized, 9=realistic (stylized 8x8 pixel art)
  detail: 4       # 1=simple, 9=complex (moderate for readability)
  saturation: 4   # 1=muted, 9=vibrant (muted base, saturated accents)
  contrast: 7     # 1=low-key, 9=high-key (high for gameplay clarity)
  form: 3         # 1=geometric, 9=organic (geometric industrial)
  line: 2         # 1=hard-edge, 9=soft (hard pixel edges)

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
file_size_limit: 400  # KB - compact

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

# Art Direction Notes

## Color Philosophy

| Element | Color | Purpose |
|---------|-------|---------|
| **Base/Facility** | Cold grays (#1a1a2e to #5a5a6e) | Industrial foundation |
| **Metallic** | Silver highlights (#8888aa) | Surface detail |
| **Cyan** | #00ffff, #45b991 | Player-positive (cores, extraction, runner visor) |
| **Red** | #ff3333, #cc2222 | Danger (traps, drones, locked doors, Overseer cursor) |
| **Yellow** | #ffcc00 | Interactive/Warning (doors, timer) |
| **Green** | #00ff88 | Runner identity (suit glow) |

## Visual Language Rules

1. **Every gameplay element has distinct visual identity**
2. **Information through color coding, not labels**
3. **Readability over decoration**
4. **Clean pixel art with minimal noise**

## Asset Style

| Asset Type | Size | Animation | Notes |
|------------|------|-----------|-------|
| Tilesets | 8x8 | None | Floor/wall variants |
| Runners | 16x16 | 4 frames/state | Idle, walk, sprint, crouch, death |
| Drones | 12x12 | 4 frames | Hover animation |
| Traps | 8x8 | 2-4 frames | Inactive/active states |
| VFX | 8x8 to 16x16 | 4 frames | Core glow, gas, laser |
| UI | Variable | Varies | Energy bars, timer, indicators |

## Tileset Design

| Tileset | Character | Accent |
|---------|-----------|--------|
| floor_metal | Clean industrial | Grid lines |
| floor_grate | Open, dangerous feel | Red underglow possible |
| floor_panel | Tech facility | Blue light trim |
| floor_damaged | Hazard zones | Warning yellow |
| wall_solid | Impassable, solid | Minimal detail |
| wall_window | Visibility blocker with view | Cyan glass tint |
| wall_vent | Gameplay hint (Runner path?) | Dark interior |
| wall_pipe | Industrial detail | Steam possible |
| wall_screen | Overseer presence | Cyan glow |
| wall_doorframe | Interactive zone | Yellow trim |

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
- All assets auto-generated via build.rs
- Game logic complete in lib.rs
- AI system complete in ai.rs

Next priorities:
1. Balance tuning (energy costs, trap cooldowns)
2. Visual polish (particle effects)
3. Audio implementation
