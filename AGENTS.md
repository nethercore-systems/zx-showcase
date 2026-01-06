# zx-showcase

Showcase games for Nethercore ZX. Uses `cargo xtask` to orchestrate builds and a Python+Blender procgen pipeline for assets.

## Structure

- `xtask/` — Build orchestration (game discovery, asset gen, install)
- `games/<game>/` — Individual games (Rust + `nether.toml` + generators)
- `procgen/` — Shared Python procgen library used across games

Start here: `README.md`, `CLAUDE.md`.

## Prerequisites

- Rust + WASM target: `rustup target add wasm32-unknown-unknown`
- `nether` CLI available in PATH (build from `../nethercore` if needed)
- Python 3.10+ (plus deps as required by generators)
- Blender 4.x for mesh generation scripts that use `bpy`

## Common Commands

- Build everything: `cargo xtask build-all`
- Build one game: `cargo xtask build <game>`
- Generate assets only: `cargo xtask gen-assets` / `cargo xtask gen-assets <game>`
- List games: `cargo xtask list`
- Clean: `cargo xtask clean` (add `--assets` to also clean generated assets)

## Asset Generation Guardrails

- Treat `games/*/generated/` as build output (typically gitignored); don’t hand-edit outputs.
- Mesh generators are Blender scripts (`games/*/generation/meshes/*.py`); sound/texture generators are usually pure Python.
- Prefer shared helpers in `procgen/lib/` over per-game duplication.
