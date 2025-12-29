---
# Creative Direction Configuration
# Prism Survivors - Roguelite Wave Survival

# Art Direction
art_style: prismatic-crystalline-fantasy
color_palette: full-rainbow-spectrum
style_spectrums:
  fidelity: 4     # 1=stylized, 9=realistic (faceted low-poly aesthetic)
  detail: 5       # 1=simple, 9=complex (clean readable shapes)
  saturation: 8   # 1=muted, 9=vibrant (full prismatic spectrum)
  contrast: 7     # 1=low-key, 9=high-key (bright colors on dark void)
  form: 3         # 1=geometric, 9=organic (angular facets, crystalline)
  line: 3         # 1=hard-edge, 9=soft (sharp beveled edges)

# Sound Direction
sonic_identity: crystalline-hybrid-electronic
mix_priority: player-feedback-first
audio_pillars:
  - "Crystalline Resonance"
  - "Responsive Power Fantasy"
  - "Escalating Sonic Intensity"

# Tech Direction
architecture: rollback-deterministic
determinism: required
file_size_limit: 6000  # KB - larger for showcase

# Creative Vision
creative_pillars:
  - Prismatic Spectacle
  - Readable Chaos
  - Satisfying Violence
  - Class Fantasy
  - Escalating Intensity
target_audience: "Fans of Vampire Survivors, 20 Minutes Till Dawn, Brotato - players who enjoy auto-attack roguelites with build depth, satisfying power fantasy, and local co-op"
avoid_patterns:
  - Generic gray/brown palettes
  - Soft gradients or organic curves
  - Visual clutter that obscures gameplay
  - Identical enemy silhouettes
  - Muted hero colors
---

# Project Vision

Prism Survivors delivers the thrill of becoming an unstoppable crystal-powered hero. Start weak, choose synergizing upgrades, and end each run as a screen-clearing force of prismatic destruction. With friends in co-op, the chaos multiplies - revive downed allies, combo off each other's attacks, and survive the crystalline apocalypse together.

---

# Creative Pillars

## 1. Prismatic Spectacle
Light, color, and crystal are the visual language. Every effect should refract, shimmer, or glow. The screen should feel alive with chromatic energy.

**Art:** Rainbow color usage, crystalline particles, light refraction effects
**Sound:** Glass-like timbres, harmonic resonance, shimmering textures
**Code:** Color-coded damage types, prismatic particle systems

## 2. Readable Chaos
Even with 100 enemies and particle effects, players must instantly distinguish threats, pickups, and allies. Visual hierarchy is sacred.

**Art:** Clear silhouettes, size-based hierarchy, color-coded threat levels
**Sound:** Distinct audio cues per enemy tier, spatial audio for threats
**Code:** Z-ordering, enemy culling, particle limits

## 3. Satisfying Violence
Combat should feel punchy and rewarding. Enemies shatter like glass, combos trigger celebrations, and kills feel meaningful.

**Art:** Shatter effects, screen shake, hit flash, combo number popups
**Sound:** Impactful hits, glass breaking, combo stingers, level-up fanfares
**Code:** Hitstop frames, damage numbers, combo multiplier system

## 4. Class Fantasy
Each hero must feel distinct in silhouette, color, and playstyle. A player should know their role at a glance.

**Art:** Distinct silhouettes, class-specific colors, unique weapon visuals
**Sound:** Class-specific weapon sounds, movement audio
**Code:** Unique abilities, stat differentiation, starting weapon variety

## 5. Escalating Intensity
Visual and audio intensity scales with wave number, combo multiplier, and danger. Stage 1 is calm compared to Stage 4's cosmic chaos.

**Art:** Background intensity, particle density, color saturation increase
**Sound:** Music layers, tempo increase, filter sweeps
**Code:** Spawn rate scaling, difficulty multipliers, stage transitions

---

# Art Direction Notes

## Color Philosophy

| Context | Primary Colors | Accent | Notes |
|---------|---------------|--------|-------|
| Heroes | Class-specific | White glow | Brightest on screen |
| Basic Enemies | Muted rainbow | None | Should fade into background |
| Elite Enemies | Any | Purple glow | Stands out from basics |
| Bosses | Any | Red glow | Maximum visibility |
| Pickups | Green (XP), Gold (coins) | White sparkle | Must be visible in chaos |
| UI | White/Gold | Stage color | Clean, readable |

## Stage Color Palettes

| Stage | Primary | Secondary | Hazard |
|-------|---------|-----------|--------|
| Crystal Cavern | Blues, Purples | Cyan | Falling crystal shards |
| Enchanted Forest | Greens, Teals | Gold | Poison clouds |
| Volcanic Depths | Reds, Oranges | Yellow | Lava geysers |
| Void Realm | Deep Purple, Black | Cosmic Blue | Void rifts |

## Hero Class Colors

| Class | Primary | Secondary | Glow |
|-------|---------|-----------|------|
| Knight | Steel Blue | Silver | White |
| Mage | Purple | Dark Purple | Arcane Purple |
| Ranger | Forest Green | Brown | Leaf Green |
| Cleric | White | Gold | Holy Gold |
| Necromancer | Dark Purple | Sickly Green | Green |
| Paladin | Ornate Gold | White | Divine Gold |

## Visual Hierarchy (Enemy Tiers)

| Tier | Polygon Budget | Texture Size | Glow | Scale Range |
|------|---------------|--------------|------|-------------|
| Basic | 200-600 tris | 128x128 | None | 0.5-1.2 |
| Elite | 600-1000 tris | 256x256 | Purple | 1.1-1.6 |
| Boss | 1000-2000 tris | 512x512 | Red | 2.0-2.5 |

---

# Sound Direction Notes

## Audio Character

- **Primary Style:** Hybrid (Electronic + Orchestral)
- **Secondary Style:** Synthwave undertones
- **Intensity:** Medium-High (roguelites need energy)

## Tempo Progression

| Context | BPM Range |
|---------|-----------|
| Title/Menu | 80-100 |
| Early Waves (1-5) | 110-120 |
| Mid Waves (6-10) | 120-130 |
| Late Waves (11-15) | 130-140 |
| Final Stage (16-20) | 140-150 |
| Boss Encounter | 150-160 |

## Instrument Palette

- **Primary:** Crystalline pads, glass FM leads, sub bass
- **Accent:** Metallic percussion, cascading arpeggios, staccato strings
- **Texture:** Shimmer effects, soft choir, drone pads

---

# Current Focus

## Completed (2025-12-29)
- ✅ Visual asset pipeline overhauled (Blender Python workflow)
- ✅ All hero meshes generated (6 GLB files)
- ✅ All enemy meshes generated (13 GLB files)
- ✅ All pickup/projectile meshes generated
- ✅ All textures generated (59 PNG files with albedo + emission)
- ✅ All SFX generated (18 WAV files)
- ✅ Character selection screen implemented

## Next Priorities
1. Build and test with new assets
2. Add particle effects for abilities
3. Add damage numbers
4. Add combo celebration effects
5. Add boss intro animations
