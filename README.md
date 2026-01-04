# ZX Showcase

Official showcase games for Nethercore ZX, demonstrating what's possible on the platform.

## Games

| Game | Description | Players | Status |
|------|-------------|---------|--------|
| [Override](games/override/) | Asymmetric 1v3 multiplayer | 2-4 | Complete |
| [Prism Survivors](games/prism-survivors/) | Fantasy survival co-op | 1-4 | Active Development |
| [Lumina Depths](games/lumina-depths/) | Meditative underwater exploration | 1 | Active Development |
| [Neon Drift](games/neon-drift/) | Arcade racing | 1-4 | Active Development |

## Quick Start

### Prerequisites

1. **Rust toolchain** with `wasm32-unknown-unknown` target:
   ```bash
   rustup target add wasm32-unknown-unknown
   ```

2. **nether CLI** (build from nethercore repo or add to PATH):
   ```bash
   cd ../nethercore
   cargo build -p nether-cli --release
   ```

3. **Python 3.10+** and **Blender 4.0+** (for asset generation):
   ```bash
   pip install numpy scipy
   ```

### Build All Games

```bash
# Build and install all games (generates assets, compiles, packs, installs)
cargo xtask build-all

# Games are installed to ~/.nethercore/games/
```

### Run a Game

```bash
# Using the Nethercore player
nethercore ~/.nethercore/games/override/rom.nczx
```

## Build Commands

| Command | Description |
|---------|-------------|
| `cargo xtask build-all` | Generate assets, build, and install all games |
| `cargo xtask build <game>` | Build a specific game |
| `cargo xtask list` | Show games and their status |
| `cargo xtask gen-assets` | Generate assets only (no build) |
| `cargo xtask gen-assets <game>` | Generate assets for specific game |
| `cargo xtask install` | Install pre-built games |
| `cargo xtask clean` | Clean build artifacts |
| `cargo xtask clean --assets` | Clean including generated assets |

### Options

- `--skip-assets`: Skip asset generation phase
- `--sequential`: Build games one at a time (default is parallel)

## Asset Generation

All games use procedural asset generation with Python + Blender:

```
games/{game}/
├── generation/              # Source generators
│   ├── generate_all.py      # Batch runner (called by xtask)
│   ├── lib/                 # Game-specific utilities
│   ├── meshes/              # ONE .py per mesh asset
│   ├── textures/            # ONE .py per texture
│   └── sounds/              # ONE .py per sound
└── generated/               # OUTPUT (gitignored)
    ├── meshes/              # .glb files
    ├── textures/            # .png files
    └── sounds/              # .wav files
```

### Manual Asset Generation

```bash
# Generate all assets for a game
cd games/lumina-depths/generation && python generate_all.py

# Generate single mesh (requires Blender)
blender --background --python games/neon-drift/generation/meshes/viper.py

# Generate single sound (pure Python)
python games/override/generation/sounds/alarm.py
```

## Project Structure

```
zx-showcase/
├── Cargo.toml              # Workspace root (xtask only)
├── .cargo/config.toml      # cargo xtask alias
├── xtask/                   # Build orchestration
│   └── src/
│       ├── main.rs         # CLI entry point
│       ├── config.rs       # Game discovery
│       ├── asset_gen.rs    # Asset generation
│       ├── build.rs        # Build orchestration
│       └── install.rs      # Installation
└── games/
    ├── lumina-depths/
    ├── neon-drift/
    ├── prism-survivors/
    └── override/
```

## Development

### Building Individual Games

```bash
# Build and install a specific game
cargo xtask build override

# Or manually:
cd games/override
nether build
```

### Manual WASM Build

If you don't have the nether CLI:

```bash
cd games/<game-name>
cargo build --release --target wasm32-unknown-unknown
```

The WASM file will be at `target/wasm32-unknown-unknown/release/<game>.wasm`.

## License

MIT License - see [LICENSE](LICENSE)
