# ZX Showcase - Claude Code Instructions

## Overview

This repository contains four showcase games for the Nethercore ZX console, all using procedural asset generation with Python + Blender.

| Game | Genre | Status | Directory |
|------|-------|--------|-----------|
| **Neon Drift** | Arcade Racing | Active Development | `games/neon-drift/` |
| **Lumina Depths** | Underwater Exploration | Active Development | `games/lumina-depths/` |
| **Prism Survivors** | Survivors-like | Active Development | `games/prism-survivors/` |
| **Override** | Asymmetric Multiplayer (1v3) | Complete | `games/override/` |

## Repository Structure

```
zx-showcase/
├── CLAUDE.md                    # This file
├── README.md                    # Public documentation
├── xtask/                       # Build orchestration (cargo xtask)
├── games/
│   └── {game}/                  # Each game follows this structure
│       ├── src/                 # Rust game code
│       ├── generated/           # OUTPUT: Generated assets (gitignored)
│       │   ├── meshes/          # .glb files
│       │   ├── textures/        # .png files
│       │   └── sounds/          # .wav files
│       ├── generation/          # Procedural generators
│       │   ├── generate_all.py  # Batch runner
│       │   ├── lib/             # Game-specific utilities
│       │   ├── meshes/          # ONE .py per mesh asset
│       │   ├── textures/        # ONE .py per texture
│       │   └── sounds/          # ONE .py per sound
│       ├── .studio/             # Plugin-managed project files
│       │   ├── project-status.md
│       │   ├── creative-direction.local.md
│       │   ├── characters/      # Asset specifications
│       │   ├── music/           # Music specifications
│       │   └── sfx/             # SFX specifications
│       ├── docs/                # Game documentation
│       │   └── GDD.md
│       └── nether.toml          # Asset manifest
└── .github/workflows/
    └── build.yml                # CI/CD for all games
```

## Build System

### Primary Command

```bash
# Build everything (generates assets, compiles, packs, installs all 4 games)
cargo xtask build-all
```

This single command:
1. **Phase 1**: Runs `python generate_all.py` for each game (Blender + Python)
2. **Phase 2**: Runs `nether build` for each game (Rust → WASM → ROM)
3. **Phase 3**: Installs ROMs to `~/.nethercore/games/`

### Other Commands

```bash
cargo xtask list              # Show games and asset status
cargo xtask build <game>      # Build single game
cargo xtask gen-assets        # Generate assets only (no build)
cargo xtask clean             # Clean build artifacts
cargo xtask clean --assets    # Also clean generated/ folders
```

## Asset Generation

### Per-Asset Generator Pattern

Each asset has its own dedicated generator file. Meshes use Blender, sounds use numpy/scipy:

**Mesh generator (requires Blender):**
```python
#!/usr/bin/env python3
"""Generate {asset_name} mesh.

Output: ../../generated/meshes/{asset_name}.glb
Run with: blender --background --python {asset_name}.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from mesh_utils import generate_and_export, merge_meshes, generate_ellipsoid

ASSET_NAME = "{asset_name}"

def generate():
    meshes = []
    # Build geometry using helper functions
    body_v, body_f = generate_ellipsoid(0, 0, 0, 1.0, 0.5, 0.5)
    meshes.append((body_v, body_f))

    vertices, faces = merge_meshes(meshes)
    generate_and_export(ASSET_NAME, vertices, faces)

if __name__ == "__main__":
    generate()
```

**Sound generator (pure Python):**
```python
#!/usr/bin/env python3
"""Generate {sound_name} sound.

Output: ../../generated/sounds/{sound_name}.wav
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from audio_utils import write_wav, sine_wave, apply_envelope

OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated" / "sounds"
ASSET_NAME = "{sound_name}"

def generate():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Generate audio samples
    samples = sine_wave(440, 1.0, 44100)
    samples = apply_envelope(samples, attack=0.1, release=0.3)
    write_wav(OUTPUT_DIR / f"{ASSET_NAME}.wav", samples, 44100)

if __name__ == "__main__":
    generate()
```

### Running Generators

```bash
# Generate all assets for a game (xtask does this automatically)
cd games/neon-drift/generation && python generate_all.py

# Generate single mesh (requires Blender in PATH)
blender --background --python games/override/generation/meshes/runner.py

# Generate single sound (pure Python)
python games/lumina-depths/generation/sounds/whale.py
```

## Game-Specific Notes

### Neon Drift
- **Aesthetic**: Synthwave, neon glows, speed lines
- **Key Assets**: Cars (7 types), tracks, barriers, buildings
- **Audio**: 128-140 BPM synthwave, engine sounds, drift SFX

### Lumina Depths
- **Aesthetic**: Underwater bioluminescence, alien beauty
- **Key Assets**: Creatures (16 species across 4 depth zones), whales, submersible
- **Audio**: Ambient drones, subaquatic muffled sounds, ethereal melodies

### Prism Survivors
- **Aesthetic**: Prismatic violence, crystalline chaos
- **Key Assets**: Heroes (6 classes), enemies (13 types), projectiles
- **Audio**: Harmonic stacking, frequency-based threat level, generative music

### Override
- **Aesthetic**: Dark sci-fi industrial, high contrast, muted grays/blues
- **Key Assets**: Runners, drones, tilesets (floors, walls, doors), traps
- **Audio**: Industrial tension, ambient machinery, trap activations
- **Gameplay**: 1v3 asymmetric - Overseer controls facility vs 3 Runners

## Development Commands

### Quick Reference
```bash
# Build everything
cargo xtask build-all

# Build single game
cargo xtask build override

# Generate assets only
cargo xtask gen-assets lumina-depths

# Check status
cargo xtask list

# Run game tests
cd games/prism-survivors && cargo test
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

## Related Repositories

- [nethercore](../nethercore/) - Console runtime and SDK
- [nethercore-ai-plugins](../nethercore-ai-plugins/) - Claude Code plugins
