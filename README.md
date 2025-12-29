# ZX Showcase

Official showcase games for Nethercore ZX, demonstrating what's possible on the platform.

## Games

| Game | Description | Players |
|------|-------------|---------|
| [Lumina Depths](games/lumina-depths/) | Meditative underwater exploration | 1 |
| [Neon Drift](games/neon-drift/) | Arcade racing | 1-4 |
| [Prism Survivors](games/prism-survivors/) | Fantasy survival co-op | 1-4 |
| [Override](games/override/) | Asymmetric 1v3 multiplayer | 2-4 |

## Building

Each game is a standalone Rust project that compiles to WASM:

```bash
cd games/<game-name>
cargo build --release --target wasm32-unknown-unknown
```

## Running

Use the [Nethercore player](https://github.com/nethercore-systems/nethercore) to run the compiled `.wasm` files, or package as a ROM with `nether.toml`.

## License

MIT License - see [LICENSE](LICENSE)
