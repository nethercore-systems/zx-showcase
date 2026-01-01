#!/usr/bin/env python3
"""
NEON DRIFT Track Generator
Main entry point for generating all track segments and props

Run with: blender --background --python generate_tracks.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import bpy
    from generators.track_geometry import TrackGeometry
    from generators.prop_geometry import PropGeometry
    from generators.track_textures import TrackTextures
except ImportError as e:
    print(f"Error: {e}")
    print("Must run from Blender with generators module available")
    print("Usage: blender --background --python generate_tracks.py")
    sys.exit(1)

# Output paths
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "models"
MESH_DIR = OUTPUT_DIR / "meshes"
TEXTURE_DIR = OUTPUT_DIR / "textures"
MESH_DIR.mkdir(parents=True, exist_ok=True)
TEXTURE_DIR.mkdir(parents=True, exist_ok=True)


def export_obj(obj, filename):
    """Export object to OBJ file"""
    filepath = MESH_DIR / filename

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Generate UVs
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Export
    bpy.ops.wm.obj_export(
        filepath=str(filepath),
        export_selected_objects=True,
        export_uv=True,
        export_normals=True,
        export_materials=False
    )

    tri_count = len(obj.data.polygons)
    print(f"✓ Exported: {filepath} ({tri_count} tris)")

    return tri_count


def generate_track_segment(segment_type):
    """Generate a track segment"""
    print(f"\nGenerating: track_{segment_type}")

    if segment_type == 'straight':
        obj = TrackGeometry.generate_straight()
        texture_type = 'straight'
    elif segment_type == 'curve_left':
        obj = TrackGeometry.generate_curve(direction='left')
        texture_type = 'curve'
    elif segment_type == 'curve_right':
        obj = TrackGeometry.generate_curve(direction='right')
        texture_type = 'curve'
    elif segment_type == 'tunnel':
        obj = TrackGeometry.generate_tunnel()
        texture_type = 'tunnel'
    elif segment_type == 'jump':
        obj = TrackGeometry.generate_jump()
        texture_type = 'jump'
    elif segment_type == 'checkpoint':
        obj = TrackGeometry.generate_checkpoint()
        texture_type = 'checkpoint'
    else:
        print(f"Unknown segment type: {segment_type}")
        return 0

    # Export mesh
    tri_count = export_obj(obj, f"track_{segment_type}.obj")

    # Generate texture
    if texture_type == 'tunnel':
        texture = TrackTextures.generate_tunnel_texture()
    else:
        texture = TrackTextures.generate_road_texture(texture_type)

    texture_path = TEXTURE_DIR / f"track_{segment_type}.png"
    texture.save(texture_path)
    print(f"✓ Generated: {texture_path}")

    return tri_count


def generate_prop(prop_type):
    """Generate a prop"""
    print(f"\nGenerating: prop_{prop_type}")

    if prop_type == 'barrier':
        obj = PropGeometry.generate_barrier()
    elif prop_type == 'boost_pad':
        obj = PropGeometry.generate_boost_pad()
    elif prop_type == 'billboard':
        obj = PropGeometry.generate_billboard()
    elif prop_type == 'building':
        obj = PropGeometry.generate_building()
    elif prop_type == 'crystal':
        obj = PropGeometry.generate_crystal()
    else:
        print(f"Unknown prop type: {prop_type}")
        return 0

    # Export mesh
    tri_count = export_obj(obj, f"prop_{prop_type}.obj")

    # Generate texture
    texture = TrackTextures.generate_prop_texture(prop_type)
    texture_path = TEXTURE_DIR / f"prop_{prop_type}.png"
    texture.save(texture_path)
    print(f"✓ Generated: {texture_path}")

    return tri_count


def main():
    """Generate all track segments and props"""
    print("\n" + "="*60)
    print("NEON DRIFT - Track & Prop Generation")
    print("="*60)

    total_tris = 0

    # Generate track segments
    print("\n[Track Segments]")
    segments = ['straight', 'curve_left', 'curve_right', 'tunnel', 'jump', 'checkpoint']
    for segment in segments:
        total_tris += generate_track_segment(segment)

    # Generate props
    print("\n[Props]")
    props = ['barrier', 'boost_pad', 'billboard', 'building', 'crystal']
    for prop in props:
        total_tris += generate_prop(prop)

    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"Total triangles: {total_tris}")
    print(f"Meshes: {MESH_DIR}")
    print(f"Textures: {TEXTURE_DIR}")
    print("="*60)


if __name__ == "__main__":
    main()
