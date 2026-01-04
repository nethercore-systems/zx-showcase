#!/usr/bin/env python3
"""Generate Speedster car mesh.

Output: ../../generated/meshes/speedster.glb

Classic sports car silhouette with cyan neon accents.
Run with: blender --background --python speedster.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import bpy
    from lib.car_geometry import CarGeometry, CAR_DIMENSIONS
except ImportError as e:
    print(f"Error: {e}")
    print("Must run from Blender")
    print("Usage: blender --background --python speedster.py")
    sys.exit(1)

CAR_NAME = "speedster"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated" / "meshes"


def generate():
    """Generate speedster car mesh."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Clear scene
    CarGeometry.clear_scene()

    # Get dimensions
    dimensions = CAR_DIMENSIONS[CAR_NAME]

    # Generate mesh
    car_obj = CarGeometry.assemble_car(CAR_NAME, dimensions)

    # Export
    output_path = OUTPUT_DIR / f"{CAR_NAME}.glb"
    bpy.ops.object.select_all(action='DESELECT')
    car_obj.select_set(True)
    bpy.context.view_layer.objects.active = car_obj

    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format='GLB',
        use_selection=True,
        export_apply=True
    )

    tri_count = len(car_obj.data.polygons)
    print(f"Generated: {output_path} ({tri_count} tris)")


if __name__ == "__main__":
    generate()
