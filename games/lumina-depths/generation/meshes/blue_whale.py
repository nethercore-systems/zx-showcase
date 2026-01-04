#!/usr/bin/env python3
"""Generate Blue Whale mesh.

Output: ../../generated/meshes/blue_whale.glb

Majestic blue whale with smooth curves. Zone 1 @ 180m depth.
Epic encounter - 20m scale (10 units).
Run with: blender --background --python blue_whale.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from mesh_utils import (
    generate_tapered_body, generate_ellipsoid, generate_flipper,
    generate_fluke, merge_meshes, generate_and_export
)

ASSET_NAME = "blue_whale"


def generate():
    """Generate blue whale mesh."""
    meshes = []

    # Main body (20m scale, we'll use 10 units = 20m)
    body_verts, body_faces = generate_tapered_body(
        length=10.0, max_radius=1.2,
        taper_start=0.15, taper_end=0.7,
        segments_len=24, segments_circ=20
    )
    meshes.append((body_verts, body_faces))

    # Head bulge (slight)
    head_verts, head_faces = generate_ellipsoid(0, 0.2, 4.5, 0.8, 0.6, 1.0, lat_segments=10, lon_segments=14)
    meshes.append((head_verts, head_faces))

    # Left flipper
    left_flip_v, left_flip_f = generate_flipper(-1.3, -0.3, 2.0, 1.5, 0.5, 0.15, rotation=math.pi/4)
    meshes.append((left_flip_v, left_flip_f))

    # Right flipper
    right_flip_v, right_flip_f = generate_flipper(1.3, -0.3, 2.0, 1.5, 0.5, 0.15, rotation=-math.pi/4)
    meshes.append((right_flip_v, right_flip_f))

    # Dorsal fin (small ridge)
    dorsal_verts, dorsal_faces = generate_ellipsoid(0, 0.9, -2.0, 0.1, 0.3, 0.4, lat_segments=6, lon_segments=8)
    meshes.append((dorsal_verts, dorsal_faces))

    # Tail flukes
    fluke_v, fluke_f = generate_fluke(0, 0, -5.2, 3.5, 0.8, 0.12)
    meshes.append((fluke_v, fluke_f))

    vertices, faces = merge_meshes(meshes)
    generate_and_export(ASSET_NAME, vertices, faces)


if __name__ == "__main__":
    generate()
