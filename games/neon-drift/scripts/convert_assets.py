#!/usr/bin/env python3
"""Convert PPM textures to PNG and rename assets for nether.toml compatibility."""

import os
import sys
from pathlib import Path

# Try to import PIL, otherwise use a simple PPM to PNG conversion
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("PIL not available, using manual PPM conversion")

def ppm_to_png_manual(ppm_path: Path, png_path: Path):
    """Manual PPM to PNG conversion without PIL (creates placeholder)."""
    # Read PPM file
    with open(ppm_path, 'rb') as f:
        # Read header
        magic = f.readline().decode().strip()
        if magic not in ('P3', 'P6'):
            print(f"  Unsupported PPM format: {magic}")
            return False

        # Skip comments
        line = f.readline().decode().strip()
        while line.startswith('#'):
            line = f.readline().decode().strip()

        # Get dimensions
        dims = line.split()
        if len(dims) == 2:
            width, height = int(dims[0]), int(dims[1])
        else:
            width = int(dims[0])
            height = int(f.readline().decode().strip())

        # Get max value
        max_val = int(f.readline().decode().strip())

        # Read pixel data
        if magic == 'P6':
            data = f.read()
        else:
            # P3 - ASCII format
            data = bytes([int(x) for x in f.read().split()])

    print(f"  {ppm_path.name}: {width}x{height}")

    # Since we can't create PNG without PIL, just copy the file
    # The actual conversion should use PIL
    return False

def convert_ppm_to_png(ppm_path: Path, png_path: Path):
    """Convert PPM to PNG using PIL."""
    if not HAS_PIL:
        return ppm_to_png_manual(ppm_path, png_path)

    try:
        img = Image.open(ppm_path)
        img.save(png_path, 'PNG')
        print(f"  {ppm_path.name} -> {png_path.name}")
        return True
    except Exception as e:
        print(f"  Error converting {ppm_path.name}: {e}")
        return False

def main():
    base_dir = Path(__file__).parent.parent
    generated_dir = base_dir / "assets" / "generated"
    meshes_dir = base_dir / "assets" / "models" / "meshes"
    textures_dir = base_dir / "assets" / "models" / "textures"

    # Create output directories
    meshes_dir.mkdir(parents=True, exist_ok=True)
    textures_dir.mkdir(parents=True, exist_ok=True)

    # Name mappings from generated format to nether.toml format
    car_mappings = {
        "car_speedster": "speedster",
        "car_muscle": "muscle",
        "car_racer": "racer",
        "car_drift": "drift",
        "car_phantom": "phantom",
        "car_titan": "titan",
        "car_viper": "viper",
    }

    track_mappings = {
        "track_straight": "track_straight",
        "track_checkpoint": "track_checkpoint",
    }

    print("Converting assets...")

    # Convert car assets
    for gen_name, toml_name in car_mappings.items():
        # Copy mesh
        obj_src = generated_dir / f"{gen_name}.obj"
        obj_dst = meshes_dir / f"{toml_name}.obj"
        if obj_src.exists():
            import shutil
            shutil.copy2(obj_src, obj_dst)
            print(f"  {gen_name}.obj -> {toml_name}.obj")

        # Convert albedo texture
        ppm_albedo = generated_dir / f"{gen_name}_albedo.ppm"
        png_albedo = textures_dir / f"{toml_name}.png"
        if ppm_albedo.exists():
            convert_ppm_to_png(ppm_albedo, png_albedo)

        # Convert emissive texture
        ppm_emissive = generated_dir / f"{gen_name}_emission.ppm"
        png_emissive = textures_dir / f"{toml_name}_emissive.png"
        if ppm_emissive.exists():
            convert_ppm_to_png(ppm_emissive, png_emissive)

    # Convert track assets
    for gen_name, toml_name in track_mappings.items():
        obj_src = generated_dir / f"{gen_name}.obj"
        obj_dst = meshes_dir / f"{toml_name}.obj"
        if obj_src.exists():
            import shutil
            shutil.copy2(obj_src, obj_dst)
            print(f"  {gen_name}.obj -> {toml_name}.obj")

    # Convert track grid texture
    grid_ppm = generated_dir / "track_grid.ppm"
    grid_png = textures_dir / "track_straight.png"
    if grid_ppm.exists():
        convert_ppm_to_png(grid_ppm, grid_png)

    print("\nDone!")
    if not HAS_PIL:
        print("\nNote: PIL not available. Install with: pip install Pillow")
        print("Then re-run this script to convert PPM to PNG.")

if __name__ == "__main__":
    main()
