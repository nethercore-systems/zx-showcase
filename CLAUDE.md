# ZX Showcase

Four showcase games for Nethercore ZX using the spec-driven asset pipeline.

## Games

| Game | Genre | Directory |
|------|-------|-----------|
| Override | Asymmetric 1v3 | `games/override/` |
| Neon Drift | Arcade Racing | `games/neon-drift/` |
| Lumina Depths | Underwater Exploration | `games/lumina-depths/` |
| Prism Survivors | Survivors-like | `games/prism-survivors/` |

## Structure

Each game follows the canonical spec-driven structure:

```
games/{game}/
├── .studio/
│   ├── generate.py           # Unified asset generator
│   ├── parsers/              # Parser modules
│   │   ├── texture.py
│   │   ├── sound.py
│   │   ├── character.py
│   │   ├── animation.py
│   │   ├── normal.py
│   │   ├── music.py
│   │   └── xm_*.py, it_*.py
│   └── specs/
│       ├── sounds/*.spec.py  # Sound effect specs
│       ├── textures/         # Texture specs
│       ├── meshes/           # Mesh specs
│       ├── characters/       # Character specs
│       ├── animations/       # Animation specs
│       └── music/            # Tracker music specs
├── generated/                # Output (gitignored)
├── src/                      # Rust game code
└── nether.toml               # Asset manifest
```

## Asset Generation

```bash
# Generate all assets from specs
python .studio/generate.py

# Generate specific category
python .studio/generate.py --only sounds

# List discovered specs
python .studio/generate.py --list

# Dry run (preview)
python .studio/generate.py --dry-run
```

## Build Commands

```bash
cargo xtask build-all           # All games
cargo xtask build <game>        # Single game
cargo xtask install             # Install to ~/.nethercore/games/
```

## Asset Budgets

| Category | Tris | Texture | Notes |
|----------|------|---------|-------|
| Player | 800-1500 | 256² | |
| Small Enemy | 200-600 | 128² | Swarm-friendly |
| Boss | 1000-2000 | 512² | Limited count |
| Vehicle | 800-1200 | 256² | |
| Prop | 50-200 | 64² | Instanced |

## SDK Usage

```rust
// In games/*/src/
let mesh = rom_mesh(b"runner");
let tex = rom_texture(b"runner_albedo");
```
