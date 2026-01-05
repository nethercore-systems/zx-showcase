# .studio - AI Game Development Pipeline

This folder contains the spec-driven asset generation pipeline for Nethercore ZX games.

## Folder Structure

```
.studio/
├── generate.py           # Unified generator - run this to generate all assets
├── parsers/              # Parser modules (don't edit unless customizing)
│
├── direction/            # Creative direction (Markdown)
│   ├── creative.md       # Vision, pillars, audience
│   ├── visual.md         # Art style, palette, spectrums
│   ├── sonic.md          # Audio identity, music style
│   └── tech.md           # Architecture, constraints
│
├── specs/                # Parsable specifications (Python dicts)
│   ├── characters/       # *.spec.py → character meshes + rigs
│   ├── textures/         # *.spec.py → albedo, patterns
│   ├── meshes/           # *.spec.py → static meshes
│   ├── sounds/           # *.spec.py → SFX synthesis
│   ├── instruments/      # *.spec.py → instrument samples
│   ├── music/            # *.spec.py → tracker songs (XM/IT)
│   └── animations/       # *.spec.py → skeletal animations
│
├── designs/              # Human-readable design documents (NOT parsed)
│   ├── mechanics/        # Combat, movement, progression
│   ├── levels/           # Level layouts, flow
│   └── systems/          # Inventory, dialogue, etc.
│
├── analysis/             # Generated reports
│   ├── scope.md          # Scope assessment
│   ├── coverage.md       # GDD implementation coverage
│   └── quality.md        # Asset quality audit
│
└── status.md             # Project progress tracking
```

## Quick Start

```bash
# Generate all assets from specs
python .studio/generate.py

# Generate only textures
python .studio/generate.py --only textures

# Preview what would be generated
python .studio/generate.py --dry-run

# List all discovered specs
python .studio/generate.py --list
```

## Creating Specs

All specs use `.spec.py` extension and contain a Python dict:

### Texture Spec Example
```python
# .studio/specs/textures/stone.spec.py
TEXTURE = {
    'name': 'stone',
    'size': [256, 256],
    'layers': [
        {'type': 'noise', 'noise_type': 'perlin', 'scale': 0.05},
        {'type': 'noise', 'noise_type': 'voronoi', 'scale': 0.1, 'blend': 'overlay'},
    ],
    'color_ramp': ['#3A3A3A', '#5A5A5A', '#7A7A7A'],
}
```

### Sound Spec Example
```python
# .studio/specs/sounds/laser.spec.py
SOUND = {
    'name': 'laser',
    'duration': 0.3,
    'sample_rate': 22050,
    'layers': [
        {'type': 'sine', 'freq': 800, 'freq_end': 200, 'amplitude': 0.8},
    ],
    'envelope': {'attack': 0.01, 'decay': 0.1, 'sustain': 0.5, 'release': 0.2},
}
```

### Animation Spec Example
```python
# .studio/specs/animations/walk.spec.py
ANIMATION = {
    'animation': {
        'name': 'walk',
        'input_armature': 'assets/characters/player.glb',
        'fps': 30,
        'duration_frames': 30,
        'poses': {
            'contact_left': {'left_leg': {'pitch': -20}, 'right_leg': {'pitch': 20}},
            'passing': {'left_leg': {'pitch': 0}, 'right_leg': {'pitch': 0}},
        },
        'phases': [
            {'name': 'left_step', 'pose': 'contact_left', 'frames': [0, 15]},
            {'name': 'right_step', 'pose': 'passing', 'frames': [15, 30]},
        ],
    }
}
```

## Output

Generated assets go to `assets/` folder (parallel to `.studio/`):

```
project/
├── .studio/          # Specs and pipeline
├── assets/           # Generated output
│   ├── textures/
│   ├── meshes/
│   ├── sounds/
│   └── animations/
└── src/              # Game code
```

## Workflow

1. **Design** - Write creative direction in `direction/`
2. **Specify** - Create specs in `specs/<category>/`
3. **Generate** - Run `python .studio/generate.py`
4. **Integrate** - Reference generated assets in game code
5. **Iterate** - Edit specs and regenerate

## Parsers

The `parsers/` folder contains the generation code:

| Parser | Input | Output |
|--------|-------|--------|
| `texture.py` | TEXTURE dict | PNG |
| `sound.py` | SOUND dict | WAV |
| `character.py` | CHARACTER dict | GLB (mesh + rig) |
| `animation.py` | ANIMATION dict | GLB (animated) |
| `normal.py` | NORMAL dict | PNG (normal map) |
| `music.py` | SONG dict | XM/IT (tracker) |

Parsers are copied from the zx-procgen plugin. Don't edit unless you need custom behavior.
