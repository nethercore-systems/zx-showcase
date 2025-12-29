# Lumina Depths - Game Design Document

## Overview

**Title:** Lumina Depths
**Genre:** Meditative Underwater Exploration
**Platform:** Nethercore ZX
**Players:** 1 (Single-player contemplative experience)
**Render Mode:** 3 (Specular-Shininess Blinn-Phong)

### Concept

A meditative descent into the ocean's depths. Pilot a research submersible through five distinct biomes, discovering bioluminescent creatures and experiencing the transition from sunlit coral reefs to the alien world of hydrothermal vents. Wonder and discovery over conflict or challenge.

### Tagline

"Descend into the light beneath the dark."

---

## Game Pillars

### 1. Contemplative Wonder
Every moment should evoke awe, not anxiety. The ocean reveals beauty at every depth - from sun-dappled reefs to the ethereal glow of deep-sea creatures.

### 2. Gradual Revelation
The deep ocean reveals itself slowly, rewarding patience. Each zone introduces new visual languages and creature behaviors that feel earned through exploration.

### 3. Living Ecosystem
Creatures behave authentically, not as game objects. Fish school, whales pass majestically, jellies drift with currents. The player is a visitor in their world.

---

## Core Mechanics

### Submersible Controls

| Input | Action | Feel |
|-------|--------|------|
| Left Stick Y | Pitch (up/down) | Smooth, weighted |
| Left Stick X | Yaw (left/right) | Deliberate rotation |
| Right Stick | Camera orbit | Fluid observation |
| RT | Accelerate descent | Increased pressure |
| LT | Slow/Ascend | Decompression relief |
| A | Headlight pulse | Attracts curious creatures |
| B | Toggle headlight | Conserve/reveal |

### Depth Progression

No fail states. Descend at your own pace through 5 zones.

---

## Depth Zones (5)

| Zone | Depth | Light Character | Dominant Life |
|------|-------|-----------------|---------------|
| **Sunlit Waters** | 0-200m | God rays, blue gradient | Reef fish, turtles, mantas |
| **Twilight Realm** | 200-1000m | Fading blue, marine snow | Jellies, siphonophores, squid |
| **Midnight Abyss** | 1000-4000m | Near-black, bioluminescence | Anglerfish, gulper eel, octopus |
| **Hydrothermal Vents** | 4000-5000m | Volcanic glow, thermal shimmer | Tube worms, vent shrimp |
| **Luminara Trench** | 5000m+ | Ethereal finale glow | All bioluminescent species |

---

## Epic Encounters (3)

Scripted moments of profound awe:

| Encounter | Zone | Description |
|-----------|------|-------------|
| **Blue Whale** | Sunlit (180m) | Majestic pass from left to right, ~20 sec |
| **Sperm Whale** | Midnight (2500m) | Hunting dive, nose-down trajectory |
| **Giant Isopod** | Vents (4200m) | Curious approach to glass, retreats |

---

## Discovery System

- 16 discoverable creature types (4 per major zone)
- Visual popup: "NEW SPECIES" + name
- End screen: X/16 species discovered
- No collection pressure - purely observational

---

## Asset Summary

All assets defined in `nether.toml`:
- **Meshes:** 26 total (submersible, 16 creatures, 6 flora, 3 terrain)
- **Textures:** 31 total
- **Sounds:** 36 total (submersible, zone ambients, creatures, discovery)

---

## Technical Specifications

- **Frame Rate:** 60 FPS (tick_rate = 2)
- **Max Creatures On-Screen:** 40 small + 12 large
- **ROM Estimate:** ~2.5 MB (large for showcase quality)

---

*Document Version: 1.0*
*Last Updated: 2025-01-29*
