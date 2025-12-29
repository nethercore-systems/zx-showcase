# ZX Showcase - Claude Code Instructions

## Overview

This repository contains four showcase games for the Nethercore ZX console, all using a shared procedural asset generation pipeline.

| Game | Genre | Status | Directory |
|------|-------|--------|-----------|
| **Neon Drift** | Arcade Racing | Active Development | `games/neon-drift/` |
| **Lumina Depths** | Underwater Exploration | Early Development | `games/lumina-depths/` |
| **Prism Survivors** | Survivors-like | Active Development | `games/prism-survivors/` |
| **Override** | Asymmetric Multiplayer (1v3) | Design Complete | `games/override/` |

## Repository Structure

```
zx-showcase/
├── CLAUDE.md                    # This file
├── games/
│   ├── neon-drift/              # Neon racing game
│   │   ├── src/                 # Rust game code
│   │   ├── assets/              # Generated assets (GLB, PNG)
│   │   └── DESIGN_NOTES.md      # Game-specific design
│   ├── lumina-depths/           # Underwater exploration
│   │   ├── src/
│   │   └── assets/
│   ├── prism-survivors/         # Survivors-like
│   │   ├── src/
│   │   ├── assets/
│   │   └── docs/GDD.md          # Game Design Document
│   └── override/                # Asymmetric multiplayer (1v3)
│       ├── src/
│       ├── assets/
│       └── docs/design/         # GDD and design docs
├── procgen/                     # SHARED procedural asset pipeline
│   ├── core/                    # Universal generation systems
│   │   ├── base_params.py       # UniversalStyleParams dataclass
│   │   ├── geometry.py          # Mesh primitives (box, sphere, prism)
│   │   ├── materials.py         # Blender material node builders
│   │   └── export.py            # ZX-optimized GLB export
│   ├── textures/                # Procedural texture generators
│   │   ├── noise_patterns.py    # Voronoi, perlin, cellular
│   │   ├── glow_effects.py      # Bioluminescence, neon, prismatic
│   │   └── pbr_textures.py      # Albedo, roughness, emission maps
│   ├── meshes/                  # Procedural mesh generators
│   │   ├── humanoid.py          # Character/enemy base meshes
│   │   ├── vehicles.py          # Car mesh generation
│   │   ├── creatures.py         # Organic forms (jellyfish, fish)
│   │   ├── crystals.py          # Faceted geometric forms
│   │   └── environment.py       # Props, barriers, buildings
│   ├── audio/                   # Procedural audio (pyo synthesis)
│   │   ├── synth_engine.py      # Waveform generation
│   │   ├── sfx_recipes.py       # JSON-based SFX definitions
│   │   └── music_generator.py   # Adaptive music layers
│   └── configs/                 # Per-game style tokens
│       ├── neon_drift.py        # Neon synthwave aesthetic
│       ├── lumina_depths.py     # Underwater bioluminescence
│       ├── prism_survivors.py   # Prismatic crystal aesthetic
│       └── override.py          # Dark sci-fi industrial aesthetic
├── creative-direction/          # Art/Sound direction docs
│   ├── neon-drift.md
│   ├── lumina-depths.md
│   ├── prism-survivors.md
│   └── override.md
└── .github/workflows/
    └── build.yml                # CI/CD for all games
```

## Procedural Asset Pipeline

### Core Concept

All three games share the same Python/Blender procedural generation codebase, but each game provides its own **style tokens** that parameterize the output:

```python
# Example: Same generator, different output
from procgen.meshes.humanoid import generate_humanoid
from procgen.configs import neon_drift, lumina_depths, prism_survivors

# Generates a neon-glowing racer character
racer = generate_humanoid(neon_drift.STYLE_TOKENS)

# Generates a bioluminescent diver character
diver = generate_humanoid(lumina_depths.STYLE_TOKENS)

# Generates a crystalline hero character
hero = generate_humanoid(prism_survivors.STYLE_TOKENS)
```

### Style Token System

Each game defines a `STYLE_TOKENS` dict that configures:

```python
STYLE_TOKENS = {
    # Colors
    "palette": ["#FF00FF", "#00FFFF", ...],
    "saturation_range": (0.6, 1.0),
    "color_temperature": -0.4,  # -1 (cool) to 1 (warm)

    # Geometry
    "poly_budget": {"small": 200, "medium": 500, "large": 1000},
    "curvature_bias": 0.75,  # 0 (angular) to 1 (smooth)
    "symmetry_mode": "bilateral",  # none, bilateral, radial

    # Materials
    "emissive_enabled": True,
    "emissive_strength": (0.5, 2.0),
    "roughness_range": (0.3, 0.8),

    # Effects
    "bloom_intensity": 2.0,
    "trail_decay": 0.15,
}
```

### Running Generators

```bash
# Generate all Neon Drift assets
python procgen/run.py --game neon-drift --all

# Generate single asset
python procgen/run.py --game prism-survivors --asset hero_knight

# Preview in Blender (opens GUI)
python procgen/run.py --game lumina-depths --asset jellyfish --preview
```

## Game-Specific Notes

### Neon Drift
- **Aesthetic**: Synthwave, neon glows, speed lines
- **Key Assets**: Cars (7 types), tracks, barriers, buildings
- **Audio**: 128-140 BPM synthwave, engine sounds, drift SFX

### Lumina Depths
- **Aesthetic**: Underwater bioluminescence, alien beauty
- **Key Assets**: Creatures (jellyfish, fish), coral, ruins
- **Audio**: Ambient drones, subaquatic muffled sounds, ethereal melodies

### Prism Survivors
- **Aesthetic**: Prismatic violence, crystalline chaos
- **Key Assets**: Heroes (6 classes), enemies (13 types), projectiles
- **Audio**: Harmonic stacking, frequency-based threat level, generative music

### Override
- **Aesthetic**: Dark sci-fi industrial, high contrast, muted grays/blues
- **Key Assets**: Runners, drones, tilesets (floors, walls, doors), traps (spike, gas, laser)
- **Audio**: Industrial tension, ambient machinery, trap activations, adaptive chase music
- **Gameplay**: 1v3 asymmetric - Overseer controls facility (god-view) vs 3 Runners (chase-cam) collecting data cores

## Development Commands

### Build Games
```bash
# Build all games
cd games/neon-drift && cargo build --release
cd games/lumina-depths && cargo build --release
cd games/prism-survivors && cargo build --release
cd games/override && cargo build --release
```

### Generate Assets
```bash
# Requires Python 3.10+ and Blender 3.6+
pip install -r procgen/requirements.txt

# Generate for specific game
python procgen/run.py --game neon-drift
```

### Run Tests
```bash
# Game tests
cd games/prism-survivors && cargo test
cd games/override && cargo test

# Asset validation
python procgen/validate.py --game all
```

## Asset Budgets (ZX Console)

| Category | Poly Budget | Texture Size | Notes |
|----------|-------------|--------------|-------|
| Player Character | 800-1500 tris | 256x256 | Per-class variants |
| Small Enemy | 200-600 tris | 128x128 | Swarm-friendly |
| Large Enemy/Boss | 1000-2000 tris | 512x512 | Limited on-screen |
| Vehicle | 800-1200 tris | 256x256 | 4 wheels included |
| Prop (barrier, gem) | 50-200 tris | 64x64 | Instanced |
| Environment tile | 100-500 tris | 256x256 | Tiling textures |

## Integration with nethercore

Games are built using the Nethercore ZX SDK:

```toml
# games/*/Cargo.toml
[dependencies]
nethercore-zx = { path = "../../../nethercore/zx" }
```

Assets are referenced via ROM handles:
```rust
let mesh = rom_mesh(b"hero_knight");
let texture = rom_texture(b"hero_knight_albedo");
```

## Contributing

1. Run existing generators before modifying shared pipeline
2. Update game-specific style tokens if changing aesthetics
3. Validate poly/texture budgets with `procgen/validate.py`
4. Test assets in-game before committing

## Related Repositories

- [nethercore](../nethercore/) - Console runtime and SDK
- [nethercore-ai-plugins](../nethercore-ai-plugins/) - Claude Code plugins
