#!/usr/bin/env python3
"""Generate Racer car mesh.

Output: ../../generated/meshes/racer.glb

Formula-style racer with magenta neon accents.
Run with: blender --background --python racer.py
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
    sys.exit(1)

CAR_NAME = "racer"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated" / "meshes"


def generate():
    """Generate racer car mesh."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CarGeometry.clear_scene()
    dimensions = CAR_DIMENSIONS[CAR_NAME]
    car_obj = CarGeometry.assemble_car(CAR_NAME, dimensions)

    output_path = OUTPUT_DIR / f"{CAR_NAME}.glb"
    bpy.ops.object.select_all(action='DESELECT')
    car_obj.select_set(True)
    bpy.context.view_layer.objects.active = car_obj
    bpy.ops.export_scene.gltf(filepath=str(output_path), export_format='GLB', use_selection=True, export_apply=True)

    print(f"Generated: {output_path} ({len(car_obj.data.polygons)} tris)")


if __name__ == "__main__":
    generate()
