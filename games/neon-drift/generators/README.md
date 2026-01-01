# NEON DRIFT Asset Generators

Modular procedural generation system for cars, tracks, and props.

## Structure

```
generators/
├── __init__.py              # Package init
├── car_geometry.py          # Car mesh generation
├── car_textures.py          # Car texture generation
├── track_geometry.py        # Track segment mesh generation
├── prop_geometry.py         # Prop mesh generation
└── track_textures.py        # Track/prop texture generation
```

## Usage

### Generate Cars

```bash
cd D:/Development/nethercore-project/zx-showcase/games/neon-drift
blender --background --python scripts/generate_cars.py
```

**Output:**
- Meshes: `assets/models/meshes/*.glb`
- Textures: `assets/models/textures/*{car}.png` and `*{car}_emissive.png`

### Generate Tracks

```bash
cd D:/Development/nethercore-project/zx-showcase/games/neon-drift
blender --background --python scripts/generate_tracks.py
```

**Output:**
- Meshes: `assets/models/meshes/track_*.obj` and `prop_*.obj`
- Textures: `assets/models/textures/track_*.png` and `prop_*.png`

## Modules

### car_geometry.py

**Class:** `CarGeometry`

**Methods:**
- `create_wheel_with_spokes(radius, width, spokes)` - Detailed wheel with hub + spokes
- `create_side_mirror(side)` - Mirror stub geometry
- `create_rear_diffuser(width)` - Diffuser plate with fins
- `create_body_base(length, width, height)` - Main body with aggressive taper
- `create_windshield(car_type)` - Angled windshield
- `create_neon_accent_strips(car_type)` - Consistent neon placement
- `assemble_car(car_type, dimensions)` - Complete car assembly

**Data:** `CAR_DIMENSIONS` - (length, width, height, wheel_radius, spoke_count) per car

### car_textures.py

**Class:** `CarTextures`

**Methods:**
- `generate_base_texture(body_color_hex, width, height)` - Albedo with panel lines + metallic flake
- `generate_emissive_map(car_name, emissive_color_hex, width, height)` - Patterned neon strips with glow

### track_geometry.py

**Class:** `TrackGeometry`

**Methods:**
- `create_road_plane(length, width, segments)` - Basic road surface
- `add_barriers(road_obj, width, length, height)` - Side barriers with neon strips
- `generate_straight(length, width)` - Straight segment
- `generate_curve(length, width, angle, direction)` - Curved segment (left/right)
- `generate_tunnel(length, radius)` - Tunnel segment
- `generate_jump(length, width, height)` - Jump ramp segment
- `generate_checkpoint(length, width)` - Checkpoint with timing gate

### prop_geometry.py

**Class:** `PropGeometry`

**Methods:**
- `generate_barrier(width, height, thickness)` - Barrier prop
- `generate_boost_pad(width, length, height)` - Boost pad prop
- `generate_billboard(width, height, thickness)` - Billboard with support pole
- `generate_building(width, depth, height)` - Building prop
- `generate_crystal(size, height)` - Crystal formation prop

### track_textures.py

**Class:** `TrackTextures`

**Methods:**
- `generate_road_texture(texture_type, width, height)` - Road surface with markings
- `generate_tunnel_texture(width, height)` - Metallic tunnel panels
- `generate_prop_texture(prop_type, width, height)` - Prop-specific textures

## Advantages of Modular Structure

1. **Better organization** - Related functionality grouped together
2. **Easier maintenance** - Smaller files are easier to understand and modify
3. **Reusability** - Modules can be imported and used independently
4. **Testability** - Individual modules can be tested in isolation
5. **Context savings** - Working on cars? Only load car modules
6. **Extensibility** - Easy to add new car types, track segments, or props

## Adding New Content

### New Car Type

1. Add dimensions to `car_geometry.py::CAR_DIMENSIONS`
2. Add preset to `procgen/configs/neon_drift.py::CAR_PRESETS`
3. Run `generate_cars.py`

### New Track Segment

1. Add method to `track_geometry.py::TrackGeometry`
2. Add to segments list in `generate_tracks.py::main()`
3. Run `generate_tracks.py`

### New Prop

1. Add method to `prop_geometry.py::PropGeometry`
2. Add to props list in `generate_tracks.py::main()`
3. Optionally add texture type to `track_textures.py::generate_prop_texture()`
4. Run `generate_tracks.py`

## Dependencies

- **Blender 3.0+** (with bpy module)
- **Pillow (PIL)** - Image generation
- **NumPy** - Array operations for textures

## Notes

- Original monolithic generators backed up as `*_old.py`
- All generators use ZX console budgets (cars: 1200 tris, tracks: 500 tris, props: 200 tris)
- Textures default to 256×256 PNG
- Meshes use smart UV unwrapping
- Normal calculation ensures consistent lighting
