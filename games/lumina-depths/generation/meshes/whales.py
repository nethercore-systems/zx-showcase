#!/usr/bin/env python3
"""Generate whale meshes for Lumina Depths epic encounters.

Blue Whale: Majestic, smooth curves (Zone 1 @ 180m)
Sperm Whale: Blocky head, wrinkled (Zone 3 @ 2500m)
"""

import math
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "generated", "meshes")

def generate_ellipsoid(cx, cy, cz, rx, ry, rz, lat_segments=16, lon_segments=24):
    """Generate ellipsoid (stretched sphere) vertices and faces."""
    vertices = []
    faces = []

    for lat in range(lat_segments + 1):
        theta = math.pi * lat / lat_segments
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        for lon in range(lon_segments):
            phi = 2 * math.pi * lon / lon_segments
            x = cx + rx * sin_theta * math.cos(phi)
            y = cy + ry * sin_theta * math.sin(phi)
            z = cz + rz * cos_theta
            vertices.append((x, y, z))

    for lat in range(lat_segments):
        for lon in range(lon_segments):
            current = lat * lon_segments + lon
            next_lon = lat * lon_segments + (lon + 1) % lon_segments
            below = (lat + 1) * lon_segments + lon
            below_next = (lat + 1) * lon_segments + (lon + 1) % lon_segments

            faces.append((current, below, below_next))
            faces.append((current, below_next, next_lon))

    return vertices, faces

def generate_tapered_body(length, max_radius, taper_start, taper_end, segments_len=20, segments_circ=16):
    """Generate a tapered body (like a whale body) along Z axis."""
    vertices = []
    faces = []

    for z_idx in range(segments_len + 1):
        t = z_idx / segments_len
        z = -length/2 + t * length

        # Calculate radius at this z position
        if t < taper_start:
            # Nose taper
            local_t = t / taper_start
            radius = max_radius * math.sin(local_t * math.pi / 2)
        elif t > taper_end:
            # Tail taper
            local_t = (t - taper_end) / (1 - taper_end)
            radius = max_radius * math.cos(local_t * math.pi / 2) * 0.3  # Thin tail
        else:
            radius = max_radius

        radius = max(radius, 0.05)  # Minimum radius

        for c_idx in range(segments_circ):
            angle = 2 * math.pi * c_idx / segments_circ
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertices.append((x, y, z))

    # Generate faces
    for z_idx in range(segments_len):
        for c_idx in range(segments_circ):
            curr = z_idx * segments_circ + c_idx
            next_c = z_idx * segments_circ + (c_idx + 1) % segments_circ
            below = (z_idx + 1) * segments_circ + c_idx
            below_next = (z_idx + 1) * segments_circ + (c_idx + 1) % segments_circ

            faces.append((curr, below, below_next))
            faces.append((curr, below_next, next_c))

    return vertices, faces

def generate_flipper(cx, cy, cz, length, width, thickness, rotation=0):
    """Generate a whale flipper (flattened ellipsoid)."""
    vertices = []
    faces = []

    lat_segs = 8
    lon_segs = 12

    for lat in range(lat_segs + 1):
        theta = math.pi * lat / lat_segs
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        for lon in range(lon_segs):
            phi = 2 * math.pi * lon / lon_segs
            x = length * sin_theta * math.cos(phi)
            y = thickness * sin_theta * math.sin(phi)
            z = width * cos_theta

            # Apply rotation around Z axis
            if rotation != 0:
                cos_r = math.cos(rotation)
                sin_r = math.sin(rotation)
                x, y = x * cos_r - y * sin_r, x * sin_r + y * cos_r

            vertices.append((cx + x, cy + y, cz + z))

    for lat in range(lat_segs):
        for lon in range(lon_segs):
            current = lat * lon_segs + lon
            next_lon = lat * lon_segs + (lon + 1) % lon_segs
            below = (lat + 1) * lon_segs + lon
            below_next = (lat + 1) * lon_segs + (lon + 1) % lon_segs

            faces.append((current, below, below_next))
            faces.append((current, below_next, next_lon))

    return vertices, faces

def generate_fluke(cx, cy, cz, span, chord, thickness):
    """Generate whale tail flukes."""
    vertices = []
    faces = []

    # Left fluke
    left_v, left_f = generate_flipper(cx - span/3, cy, cz, chord, span/2.5, thickness, rotation=math.pi/6)

    # Right fluke
    right_v, right_f = generate_flipper(cx + span/3, cy, cz, chord, span/2.5, thickness, rotation=-math.pi/6)

    # Merge
    vertices.extend(left_v)
    offset = len(left_v)
    vertices.extend(right_v)

    faces.extend(left_f)
    faces.extend([(f[0]+offset, f[1]+offset, f[2]+offset) for f in right_f])

    return vertices, faces

def merge_meshes(mesh_list):
    """Merge multiple meshes into one."""
    all_vertices = []
    all_faces = []
    offset = 0

    for vertices, faces in mesh_list:
        all_vertices.extend(vertices)
        adjusted_faces = [(f[0] + offset, f[1] + offset, f[2] + offset) for f in faces]
        all_faces.extend(adjusted_faces)
        offset += len(vertices)

    return all_vertices, all_faces

def generate_blue_whale():
    """Generate blue whale mesh - majestic, smooth curves."""
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

    return merge_meshes(meshes)

def generate_sperm_whale():
    """Generate sperm whale mesh - blocky head, distinctive shape."""
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

    return merge_meshes(meshes)

def write_obj(filename, vertices, faces, name):
    """Write mesh to OBJ file."""
    with open(filename, 'w') as f:
        f.write(f"# Lumina Depths - {name}\n")
        f.write(f"# Vertices: {len(vertices)}\n")
        f.write(f"# Faces: {len(faces)}\n\n")

        for v in vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")

        f.write("\n")

        for face in faces:
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Blue Whale
    print("Generating blue whale mesh...")
    blue_verts, blue_faces = generate_blue_whale()
    blue_path = os.path.join(OUTPUT_DIR, "blue_whale.glb")
    write_obj(blue_path, blue_verts, blue_faces, "Blue Whale")
    print(f"Generated: {blue_path}")
    print(f"  Vertices: {len(blue_verts)}, Faces: {len(blue_faces)}")

    # Sperm Whale
    print("\nGenerating sperm whale mesh...")
    sperm_verts, sperm_faces = generate_sperm_whale()
    sperm_path = os.path.join(OUTPUT_DIR, "sperm_whale.glb")
    write_obj(sperm_path, sperm_verts, sperm_faces, "Sperm Whale")
    print(f"Generated: {sperm_path}")
    print(f"  Vertices: {len(sperm_verts)}, Faces: {len(sperm_faces)}")

if __name__ == "__main__":
    main()
