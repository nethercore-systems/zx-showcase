#!/usr/bin/env python3
"""
NEON DRIFT Car Generator
Generates car meshes only (textures are generated separately)

Run with: blender --background --python cars.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import bpy
    from lib.car_geometry import CarGeometry, CAR_DIMENSIONS
except ImportError as e:
    print(f"Error: {e}")
    print("Must run from Blender with generators module available")
    print("Usage: blender --background --python cars.py")
    sys.exit(1)

# Add procgen to path
# From: games/neon-drift/generation/meshes/cars.py
# Go up to: zx-showcase/
ZX_SHOWCASE = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(ZX_SHOWCASE))  # For procgen module
sys.path.insert(0, str(ZX_SHOWCASE / "procgen" / "configs"))  # For neon_drift config

from neon_drift import CAR_PRESETS

# Output paths
OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated"
MESH_DIR = OUTPUT_DIR / "meshes"
MESH_DIR.mkdir(parents=True, exist_ok=True)


def export_obj(car_obj, car_name):
    """Export car mesh to OBJ"""
    output_path = MESH_DIR / f"{car_name}.glb"

    # Select only the car
    bpy.ops.object.select_all(action='DESELECT')
    car_obj.select_set(True)
    bpy.context.view_layer.objects.active = car_obj

    # Export as GLB
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format='GLB',
        use_selection=True,
        export_apply=True
    )

    tri_count = len(car_obj.data.polygons)
    print(f"✓ Exported: {output_path} ({tri_count} tris)")

    return tri_count


def generate_car(car_name, preset):
    """Generate a single car mesh"""
    print(f"\n{'='*60}")
    print(f"Generating: {car_name}")
    print(f"{'='*60}")

    # Clear scene
    CarGeometry.clear_scene()

    # Get dimensions
    dimensions = CAR_DIMENSIONS[car_name]

    # Generate mesh
    car_obj = CarGeometry.assemble_car(car_name, dimensions)

    # Export mesh
    tri_count = export_obj(car_obj, car_name)

    print(f"✓ Complete! ({tri_count} / 1200 tris)")

    return tri_count


def main():
    """Generate all cars"""
    print("\n" + "="*60)
    print("NEON DRIFT - Car Generation")
    print("="*60)

    total_tris = 0
    results = []

    for car_name, preset in CAR_PRESETS.items():
        tri_count = generate_car(car_name, preset)
        total_tris += tri_count
        results.append((car_name, tri_count))

    # Final report
    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"{'Car':<15} {'Triangles':<12} {'Budget Status'}")
    print("-" * 60)

    for car_name, tri_count in results:
        budget = 1200
        status = "✓ OK" if tri_count <= budget else "✗ OVER"
        percentage = (tri_count / budget) * 100
        print(f"{car_name:<15} {tri_count:<12} {status} ({percentage:.1f}%)")

    print("-" * 60)
    print(f"{'TOTAL':<15} {total_tris:<12} Avg: {total_tris // len(results)}")
    print("="*60)


if __name__ == "__main__":
    main()
