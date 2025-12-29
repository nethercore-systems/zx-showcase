# ZX Showcase

Official showcase games for Nethercore ZX, demonstrating what's possible on the platform.

## Games

| Game | Description | Players | Asset Status |
|------|-------------|---------|--------------|
| [Override](games/override/) | Asymmetric 1v3 multiplayer | 2-4 | Auto-generated (build.rs) |
| [Prism Survivors](games/prism-survivors/) | Fantasy survival co-op | 1-4 | Tool-generated |
| [Lumina Depths](games/lumina-depths/) | Meditative underwater exploration | 1 | Needs AI procgen |
| [Neon Drift](games/neon-drift/) | Arcade racing | 1-4 | Needs AI procgen |

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

### Build All Games

```bash
# Clone the repository
git clone https://github.com/nethercore-systems/zx-showcase
cd zx-showcase

# Build and install all games
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
| `cargo xtask build-all` | Build and install all games |
| `cargo xtask build <game>` | Build a specific game |
| `cargo xtask list` | Show games and their status |
| `cargo xtask gen-assets` | Generate assets only |
| `cargo xtask install` | Install pre-built games |
| `cargo xtask clean` | Clean build artifacts |
| `cargo xtask clean --assets` | Clean including generated assets |

### Options

- `--skip-assets`: Skip asset generation phase
- `--sequential`: Build games one at a time (default is parallel)

## Asset Generation

Each game has a different asset generation strategy:

### Override (Automatic)
Assets are generated automatically during `cargo build` via `build.rs`. No manual steps needed.

### Prism Survivors (Tool)
Has a standalone asset generator:
```bash
cd games/prism-survivors/tools/asset-gen
cargo run --release
```
The xtask runs this automatically.

### Lumina Depths & Neon Drift (AI Procgen)
These games need assets generated using the nethercore-ai-plugins:

1. Install the plugins in Claude Code
2. Use `/generate-asset` for each asset defined in `nether.toml`
3. Assets will be created in the game's `assets/` directory

See the [nethercore-ai-plugins](https://github.com/nethercore-systems/nethercore-ai-plugins) for details.

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
