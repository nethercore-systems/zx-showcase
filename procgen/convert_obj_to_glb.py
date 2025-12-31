#!/usr/bin/env python3
"""
Convert OBJ files to GLB format using Blender.

Usage:
    blender --background --python convert_obj_to_glb.py -- <input_dir> [--output_dir <dir>]

Example:
    blender --background --python convert_obj_to_glb.py -- games/lumina-depths/assets/models/meshes/

This is a TEMPORARY solution until proper Blender generators with metaballs are created.
"""

import argparse
import sys
from pathlib import Path

try:
    import bpy
except ImportError:
    print("Error: Must run from Blender. Use:")
    print(f"  blender --background --python {__file__} -- <input_dir>")
    sys.exit(1)


def convert_obj_to_glb(obj_path: Path, glb_path: Path) -> bool:
    """Convert a single OBJ file to GLB."""
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Import OBJ
    try:
        bpy.ops.wm.obj_import(filepath=str(obj_path))
    except Exception as e:
        print(f"  Error importing {obj_path.name}: {e}")
        return False

    # Select all imported objects
    bpy.ops.object.select_all(action='SELECT')

    # Create output directory if needed
    glb_path.parent.mkdir(parents=True, exist_ok=True)

    # Export to GLB
    try:
        bpy.ops.export_scene.gltf(
            filepath=str(glb_path),
            export_format='GLB',
            use_selection=True,
            export_apply=True,
            export_materials='EXPORT',
        )
        return True
    except Exception as e:
        print(f"  Error exporting {glb_path.name}: {e}")
        return False


def main():
    # Parse arguments after '--'
    argv = sys.argv
    if '--' in argv:
        argv = argv[argv.index('--') + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Convert OBJ files to GLB")
    parser.add_argument("input_dir", help="Directory containing OBJ files")
    parser.add_argument("--output_dir", help="Output directory (default: same as input)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be converted")

    args = parser.parse_args(argv)

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir) if args.output_dir else input_dir

    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)

    # Find all OBJ files
    obj_files = list(input_dir.glob("*.obj"))

    if not obj_files:
        print(f"No OBJ files found in {input_dir}")
        sys.exit(0)

    print(f"Found {len(obj_files)} OBJ files to convert")
    print(f"Output directory: {output_dir}")
    print()

    if args.dry_run:
        for obj_path in obj_files:
            glb_name = obj_path.stem + ".glb"
            print(f"  Would convert: {obj_path.name} -> {glb_name}")
        return

    success = 0
    failed = 0

    for obj_path in obj_files:
        glb_name = obj_path.stem + ".glb"
        glb_path = output_dir / glb_name

        print(f"Converting: {obj_path.name} -> {glb_name}")

        if convert_obj_to_glb(obj_path, glb_path):
            success += 1
            print(f"  -> OK")
        else:
            failed += 1
            print(f"  -> FAILED")

    print()
    print(f"Conversion complete: {success} succeeded, {failed} failed")


if __name__ == "__main__":
    main()
