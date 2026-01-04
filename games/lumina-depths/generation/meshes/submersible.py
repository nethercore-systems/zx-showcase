#!/usr/bin/env python3
"""Generate submersible mesh for Lumina Depths.

Output: ../../generated/meshes/submersible.glb

Design specs:
- Industrial but not military
- Glass canopy for visibility
- Warm interior lighting (amber/yellow)
- Orange accent panels
- Visible propulsion system

Run with: blender --background --python submersible.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from mesh_utils import (
    generate_ellipsoid, generate_cylinder, merge_meshes, generate_and_export
)

ASSET_NAME = "submersible"


def generate_sphere(cx, cy, cz, radius, lat_segments=12, lon_segments=16):
    """Generate sphere vertices and faces."""
    return generate_ellipsoid(cx, cy, cz, radius, radius, radius, lat_segments, lon_segments)


def generate_cone(cx, cy, cz, radius, height, segments=16):
    """Generate cone vertices and faces."""
    vertices = []
    faces = []

    # Apex
    apex_idx = 0
    vertices.append((cx, cy, cz + height))

    # Base ring
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        z = cz
        vertices.append((x, y, z))

    # Side faces
    for i in range(segments):
        curr = i + 1
        next_i = (i + 1) % segments + 1
        faces.append((apex_idx, next_i, curr))

    # Base center
    base_center = len(vertices)
    vertices.append((cx, cy, cz))

    # Base faces
    for i in range(segments):
        curr = i + 1
        next_i = (i + 1) % segments + 1
        faces.append((base_center, curr, next_i))

    return vertices, faces


def generate_submersible():
    """Generate complete submersible mesh."""
    meshes = []

    # Main hull (elongated cylinder)
    hull_verts, hull_faces = generate_cylinder(0, 0, 0, 0.4, 2.0, segments=20)
    meshes.append((hull_verts, hull_faces))

    # Glass canopy (sphere at front)
    canopy_verts, canopy_faces = generate_sphere(0, 0, 1.2, 0.5, lat_segments=10, lon_segments=16)
    meshes.append((canopy_verts, canopy_faces))

    # Rear thruster housing (cylinder)
    thruster_main_verts, thruster_main_faces = generate_cylinder(0, 0, -1.3, 0.3, 0.5, segments=12)
    meshes.append((thruster_main_verts, thruster_main_faces))

    # Thruster nozzle (cone)
    nozzle_verts, nozzle_faces = generate_cone(0, 0, -1.55, 0.25, -0.3, segments=12)
    meshes.append((nozzle_verts, nozzle_faces))

    # Left stabilizer fin
    left_fin_verts, left_fin_faces = generate_cylinder(-0.6, 0, -0.5, 0.08, 0.8, segments=8)
    meshes.append((left_fin_verts, left_fin_faces))

    # Right stabilizer fin
    right_fin_verts, right_fin_faces = generate_cylinder(0.6, 0, -0.5, 0.08, 0.8, segments=8)
    meshes.append((right_fin_verts, right_fin_faces))

    # Top dorsal fin
    dorsal_verts, dorsal_faces = generate_cylinder(0, 0.5, -0.3, 0.06, 0.6, segments=8)
    meshes.append((dorsal_verts, dorsal_faces))

    # Bottom skid
    skid_verts, skid_faces = generate_cylinder(0, -0.45, 0, 0.1, 1.5, segments=8)
    meshes.append((skid_verts, skid_faces))

    # Left thruster pod
    left_pod_verts, left_pod_faces = generate_sphere(-0.55, -0.2, -0.8, 0.15, lat_segments=8, lon_segments=10)
    meshes.append((left_pod_verts, left_pod_faces))

    # Right thruster pod
    right_pod_verts, right_pod_faces = generate_sphere(0.55, -0.2, -0.8, 0.15, lat_segments=8, lon_segments=10)
    meshes.append((right_pod_verts, right_pod_faces))

    # Headlight housing (front)
    headlight_verts, headlight_faces = generate_cylinder(0, -0.35, 0.9, 0.12, 0.15, segments=10)
    meshes.append((headlight_verts, headlight_faces))

    return merge_meshes(meshes)


def generate():
    """Generate and export submersible mesh."""
    print("Generating submersible mesh...")
    vertices, faces = generate_submersible()
    generate_and_export(ASSET_NAME, vertices, faces)


if __name__ == "__main__":
    generate()
