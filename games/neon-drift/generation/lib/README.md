# Neon Drift Generation Library

Shared utilities for procedural asset generation.

## Structure

```
lib/
├── car_geometry.py          # Car mesh generation helpers
├── car_textures.py          # Car texture generation (if needed)
└── README.md                # This file
```

## Usage

Individual asset generators import from this library:

```python
# In meshes/viper.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.car_geometry import CarGeometry, CAR_DIMENSIONS
```

## Running Generators

```bash
# Generate all assets
cd games/neon-drift/generation
python generate_all.py

# Generate single car mesh
blender --background --python meshes/viper.py
```

## Output

Assets are generated to `../../generated/`:
- Meshes: `generated/meshes/*.glb`
- Textures: `generated/textures/*.png`
- Sounds: `generated/sounds/*.wav`

## Dependencies

- **Blender 4.0+** (for mesh generation)
- **numpy/scipy** (for audio synthesis)
