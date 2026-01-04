#!/usr/bin/env python3
"""Generate Sperm Whale mesh.

Output: ../../generated/meshes/sperm_whale.glb

Blocky head sperm whale. Zone 3 @ 2500m depth.
Epic encounter - distinctive spermaceti organ head shape.
Run with: blender --background --python sperm_whale.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from mesh_utils import (
    generate_tapered_body, generate_ellipsoid, generate_flipper,
    generate_fluke, merge_meshes, generate_and_export
)

ASSET_NAME = "sperm_whale"


def generate():
    """Generate sperm whale mesh."""
    meshes = []

    # Main body (shorter, stockier)
    body_verts, body_faces = generate_tapered_body(
        length=8.0, max_radius=1.0,
        taper_start=0.25, taper_end=0.65,
        segments_len=20, segments_circ=18
    )
    meshes.append((body_verts, body_faces))

    # Massive blocky head (spermaceti organ)
    head_verts, head_faces = generate_ellipsoid(0, 0.3, 3.5, 1.0, 1.0, 1.8, lat_segments=12, lon_segments=16)
    meshes.append((head_verts, head_faces))

    # Lower jaw (smaller)
    jaw_verts, jaw_faces = generate_ellipsoid(0, -0.6, 3.0, 0.4, 0.3, 1.0, lat_segments=8, lon_segments=10)
    meshes.append((jaw_verts, jaw_faces))

    # Left flipper (smaller than blue whale)
    left_flip_v, left_flip_f = generate_flipper(-1.1, -0.4, 1.5, 0.8, 0.35, 0.1, rotation=math.pi/5)
    meshes.append((left_flip_v, left_flip_f))

    # Right flipper
    right_flip_v, right_flip_f = generate_flipper(1.1, -0.4, 1.5, 0.8, 0.35, 0.1, rotation=-math.pi/5)
    meshes.append((right_flip_v, right_flip_f))

    # Dorsal hump (not a true fin)
    hump_verts, hump_faces = generate_ellipsoid(0, 0.7, -1.0, 0.15, 0.25, 0.6, lat_segments=6, lon_segments=8)
    meshes.append((hump_verts, hump_faces))

    # Tail flukes (triangular)
    fluke_v, fluke_f = generate_fluke(0, 0, -4.3, 2.8, 0.7, 0.1)
    meshes.append((fluke_v, fluke_f))

    vertices, faces = merge_meshes(meshes)
    generate_and_export(ASSET_NAME, vertices, faces)


if __name__ == "__main__":
    generate()
