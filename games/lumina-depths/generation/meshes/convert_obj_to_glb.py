#!/usr/bin/env python3
"""
Convert all .glb files that are actually OBJ format to proper GLB format.
Run with: blender --background --python convert_obj_to_glb.py
"""

import bpy
import os
from pathlib import Path

# Output directory
MESHES_DIR = Path(__file__).parent.parent.parent / "generated" / "meshes"

def convert_obj_to_glb(obj_path: Path):
    """Convert an OBJ file to GLB format."""
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Import OBJ
    bpy.ops.wm.obj_import(filepath=str(obj_path))

    # Select all imported objects
    bpy.ops.object.select_all(action='SELECT')

    # Join all into one mesh
    if len(bpy.context.selected_objects) > 1:
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
        bpy.ops.object.join()

    obj = bpy.context.active_object

    # Generate UVs if needed
    if obj and obj.type == 'MESH':
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.unwrap(method='ANGLE_BASED')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')

    # Export as GLB
    glb_path = obj_path
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format='GLB',
        use_selection=True,
        export_apply=True
    )

    print(f"Converted: {glb_path.name}")

def main():
    print("Converting OBJ files to GLB format...")

    # Find all .glb files (which are actually OBJ files)
    glb_files = sorted(MESHES_DIR.glob("*.glb"))

    for glb_file in glb_files:
        # Check if it's actually an OBJ file
        with open(glb_file, 'r') as f:
            first_line = f.readline().strip()
            if first_line.startswith('#') or first_line.startswith('v '):
                # It's an OBJ file, convert it
                convert_obj_to_glb(glb_file)

    print(f"\nConverted {len(glb_files)} files")

if __name__ == "__main__":
    main()
