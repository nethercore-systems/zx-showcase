# .studio Migration Status

## Installed Infrastructure
- Parsers: `.studio/parsers/` (11 modules)
- Unified generator: `.studio/generate.py`
- Documentation: `.studio/README.md`

## Current Workflow (Hybrid)
- Sound specs: `../specs/sounds/*.spec.py` (9 specs, working with new parsers)
- Mesh generators: `../generation/meshes/*.py` (traditional Blender)

## Usage

### Generate sounds (new way):
```bash
python .studio/generate.py --only sounds
```

### List discovered specs:
```bash
python .studio/generate.py --list
```

### Dry run (preview):
```bash
python .studio/generate.py --only sounds --dry-run
```

### Generate all assets (traditional way):
```bash
python generation/generate_all.py
```

## Benefits
- Token-efficient: Parsers are local (saves ~95% tokens in AI interactions)
- Unified interface: Single command for all asset types
- Future-ready: Easy to add new asset types via specs

## Next Steps
1. [FUTURE] Migrate mesh specs to .studio/specs/meshes/
2. [FUTURE] Update generate_all.py to call .studio/generate.py
3. [FUTURE] Consolidate creative docs into .studio/direction/
