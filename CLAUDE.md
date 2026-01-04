# ZX Showcase

Four showcase games for Nethercore ZX using procedural asset generation (Python + Blender).

## Games

| Game | Genre | Directory |
|------|-------|-----------|
| Neon Drift | Arcade Racing | `games/neon-drift/` |
| Lumina Depths | Underwater Exploration | `games/lumina-depths/` |
| Prism Survivors | Survivors-like | `games/prism-survivors/` |
| Override | Asymmetric 1v3 | `games/override/` |

## Structure

```
zx-showcase/
├── procgen/                    # SHARED generation utilities
│   ├── lib/                    # Core modules (see below)
│   ├── run.py                  # Unified asset runner
│   └── run_blender.py          # Blender batch runner
├── xtask/                      # Build orchestration
├── games/{game}/
│   ├── src/                    # Rust game code
│   ├── generated/              # OUTPUT: meshes/, textures/, sounds/
│   ├── generation/             # Per-game generators
│   │   ├── generate_all.py     # Batch runner
│   │   ├── lib/                # Game-specific utils (imports from ../../procgen/lib)
│   │   ├── meshes/*.py         # One file per mesh
│   │   └── sounds/*.py         # One file per sound
│   ├── assets/                 # Pre-existing/manual assets (some games)
│   ├── .studio/                # Plugin-managed files
│   │   ├── creative-direction.md
│   │   ├── sonic-identity.md
│   │   ├── project-status.md
│   │   └── characters/, music/, sfx/  # Spec directories (placeholder)
│   ├── docs/GDD.md
│   └── nether.toml             # Asset manifest
└── .github/workflows/build.yml
```

## Shared Procgen Library (`procgen/lib/`)

| Module | Purpose |
|--------|---------|
| `bpy_utils.py` | Blender scene setup, GLB export, materials |
| `mesh_primitives.py` | Procedural geometry (ellipsoid, cylinder, etc.) |
| `mesh_utils.py` | Mesh operations, merging, transforms |
| `synthesis.py` | Audio oscillators, envelopes, filters |
| `sfx.py` | Sound effect generation helpers |
| `audio_dsp.py` | DSP utilities (reverb, distortion, etc.) |
| `instruments.py` | Instrument synthesis |
| `music_theory.py` | Scales, chords, progressions |
| `texture_buffer.py` | Procedural texture generation |
| `pixel_art.py` | Pixel art utilities |
| `noise.py` | Noise functions (Perlin, etc.) |
| `color_utils.py` | Color manipulation |
| `xm_writer.py` | XM tracker format export |

## Build Commands

```bash
cargo xtask build-all           # Generate assets + compile + install all games
cargo xtask build <game>        # Single game
cargo xtask gen-assets [game]   # Generate assets only
cargo xtask list                # Show status
cargo xtask clean [--assets]    # Clean artifacts
```

## Generator Patterns

**Mesh (Blender):** `games/{game}/generation/meshes/{asset}.py`
```python
import bpy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from bpy_utils import setup_scene, export_glb, create_dark_industrial_material

def generate():
    setup_scene()
    # Create geometry with bpy.ops.mesh.primitive_*
    # Apply materials, join parts
    export_glb(obj, OUTPUT_DIR / f"{ASSET_NAME}.glb")
```

**Sound (Pure Python):** `games/{game}/generation/sounds/{asset}.py`
```python
from procgen.lib.sfx import generate_impact, write_wav
def generate():
    samples = generate_impact(freq=200, duration=0.3)
    write_wav(OUTPUT_DIR / f"{ASSET_NAME}.wav", samples)
```

Run: `blender --background --python meshes/runner.py` or `python sounds/explosion.py`

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

## Future: Spec-Driven Workflow

Planned but NOT YET IMPLEMENTED: `.studio/{type}/*.spec.py` files will define assets declaratively, with generators consuming specs to produce assets. Currently specs directories contain only `.gitkeep` placeholders.
