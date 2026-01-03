#!/usr/bin/env python3
"""
NEON DRIFT Car Texture Generator
Generates car textures (albedo and emissive maps)

Run with: python cars.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from lib.car_textures import CarTextures
except ImportError as e:
    print(f"Error: {e}")
    print("Required: pip install Pillow")
    sys.exit(1)

# Add procgen to path
# From: games/neon-drift/generation/textures/cars.py
# Go up to: zx-showcase/
ZX_SHOWCASE = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(ZX_SHOWCASE))  # For procgen module
sys.path.insert(0, str(ZX_SHOWCASE / "procgen" / "configs"))  # For neon_drift config

from neon_drift import CAR_PRESETS

# Output paths
OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated"
TEXTURE_DIR = OUTPUT_DIR / "textures"
TEXTURE_DIR.mkdir(parents=True, exist_ok=True)


def generate_car_textures(car_name, preset):
    """Generate albedo and emissive textures for a car"""
    print(f"Generating textures for: {car_name}")

    # Generate base texture
    base_texture = CarTextures.generate_base_texture(preset['color_primary'])
    base_path = TEXTURE_DIR / f"{car_name}.png"
    base_texture.save(base_path)
    print(f"  OK: {base_path.name}")

    # Generate emissive texture
    emissive_texture = CarTextures.generate_emissive_map(car_name, preset['color_emissive'])
    emissive_path = TEXTURE_DIR / f"{car_name}_emissive.png"
    emissive_texture.save(emissive_path)
    print(f"  OK: {emissive_path.name}")


def main():
    """Generate all car textures"""
    print("\n" + "="*60)
    print("NEON DRIFT - Car Texture Generation")
    print("="*60)

    for car_name, preset in CAR_PRESETS.items():
        generate_car_textures(car_name, preset)

    print("\n" + "="*60)
    print(f"Generated textures in: {TEXTURE_DIR}")
    print("="*60)


if __name__ == "__main__":
    main()
