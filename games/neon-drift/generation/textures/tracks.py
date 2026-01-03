#!/usr/bin/env python3
"""
NEON DRIFT Track & Prop Texture Generator
Generates textures for track segments and props

Run with: python tracks.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from lib.track_textures import TrackTextures
except ImportError as e:
    print(f"Error: {e}")
    print("Required: pip install Pillow")
    sys.exit(1)

# Output paths
OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated"
TEXTURE_DIR = OUTPUT_DIR / "textures"
TEXTURE_DIR.mkdir(parents=True, exist_ok=True)


def generate_track_texture(segment_type):
    """Generate texture for a track segment"""
    print(f"Generating texture for: track_{segment_type}")

    if segment_type == 'tunnel':
        texture = TrackTextures.generate_tunnel_texture()
    else:
        texture = TrackTextures.generate_road_texture(segment_type)

    texture_path = TEXTURE_DIR / f"track_{segment_type}.png"
    texture.save(texture_path)
    print(f"  OK: {texture_path.name}")


def generate_prop_texture(prop_type):
    """Generate texture for a prop"""
    # crystal_formation doesn't use prop_ prefix
    prefix = "" if prop_type == 'crystal_formation' else "prop_"
    print(f"Generating texture for: {prefix}{prop_type}")

    texture = TrackTextures.generate_prop_texture(prop_type)
    texture_path = TEXTURE_DIR / f"{prefix}{prop_type}.png"
    texture.save(texture_path)
    print(f"  OK: {texture_path.name}")

    # Generate emissive maps for glowing props
    # Reuse base texture with higher brightness for emissive
    if prop_type in ['barrier', 'boost_pad', 'billboard', 'crystal_formation']:
        emissive = TrackTextures.generate_prop_texture(prop_type)  # Reuse for now
        emissive_path = TEXTURE_DIR / f"{prefix}{prop_type}_emissive.png"
        emissive.save(emissive_path)
        print(f"  OK: {emissive_path.name}")


def main():
    """Generate all track and prop textures"""
    print("\n" + "="*60)
    print("NEON DRIFT - Track & Prop Texture Generation")
    print("="*60)

    # Generate track segment textures
    print("\n[Track Segments]")
    segments = ['straight', 'curve_left', 'curve_right', 'tunnel', 'jump']
    for segment in segments:
        generate_track_texture(segment)

    # Generate prop textures
    print("\n[Props]")
    props = ['barrier', 'boost_pad', 'billboard', 'building', 'crystal_formation']
    for prop in props:
        generate_prop_texture(prop)

    # Generate UI textures
    print("\n[UI]")
    print("Generating texture for: neon_font")
    # Create simple placeholder font texture
    from PIL import Image
    font_texture = Image.new('RGB', (256, 256), color='#00FFFF')
    font_path = TEXTURE_DIR / "neon_font.png"
    font_texture.save(font_path)
    print(f"  OK: {font_path.name}")

    print("\n" + "="*60)
    print(f"Generated textures in: {TEXTURE_DIR}")
    print("="*60)


if __name__ == "__main__":
    main()
