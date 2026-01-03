#!/usr/bin/env python3
"""Generate submersible mesh for Lumina Depths.

Design specs:
- Industrial but not military
- Glass canopy for visibility
- Warm interior lighting (amber/yellow)
- Orange accent panels
- Visible propulsion system
"""

import math
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "generated", "meshes")

def generate_sphere(cx, cy, cz, radius, lat_segments=12, lon_segments=16):
    """Generate sphere vertices and faces."""
    vertices = []
    faces = []

    # Generate vertices
    for lat in range(lat_segments + 1):
        theta = math.pi * lat / lat_segments
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        for lon in range(lon_segments):
            phi = 2 * math.pi * lon / lon_segments
            x = cx + radius * sin_theta * math.cos(phi)
            y = cy + radius * sin_theta * math.sin(phi)
            z = cz + radius * cos_theta
            vertices.append((x, y, z))

    # Generate faces
    for lat in range(lat_segments):
        for lon in range(lon_segments):
            current = lat * lon_segments + lon
            next_lon = lat * lon_segments + (lon + 1) % lon_segments
            below = (lat + 1) * lon_segments + lon
            below_next = (lat + 1) * lon_segments + (lon + 1) % lon_segments

            faces.append((current, below, below_next))
            faces.append((current, below_next, next_lon))

    return vertices, faces

def generate_cylinder(cx, cy, cz, radius, height, segments=16, caps=True):
    """Generate cylinder vertices and faces."""
    vertices = []
    faces = []

    # Top ring
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        z = cz + height / 2
        vertices.append((x, y, z))

    # Bottom ring
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        z = cz - height / 2
        vertices.append((x, y, z))

    # Side faces
    for i in range(segments):
        top_curr = i
        top_next = (i + 1) % segments
        bot_curr = i + segments
        bot_next = (i + 1) % segments + segments

        faces.append((top_curr, bot_curr, bot_next))
        faces.append((top_curr, bot_next, top_next))

    if caps:
        # Top cap center
        top_center = len(vertices)
        vertices.append((cx, cy, cz + height / 2))

        # Bottom cap center
        bot_center = len(vertices)
        vertices.append((cx, cy, cz - height / 2))

        # Cap faces
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append((top_center, next_i, i))  # Top cap
            faces.append((bot_center, i + segments, next_i + segments))  # Bottom cap

    return vertices, faces

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

def merge_meshes(mesh_list, vertex_offset=0):
    """Merge multiple meshes into one."""
    all_vertices = []
    all_faces = []
    offset = vertex_offset

    for vertices, faces in mesh_list:
        all_vertices.extend(vertices)
        adjusted_faces = [(f[0] + offset, f[1] + offset, f[2] + offset) for f in faces]
        all_faces.extend(adjusted_faces)
        offset += len(vertices)

    return all_vertices, all_faces

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

def write_obj(filename, vertices, faces):
    """Write mesh to OBJ file."""
    with open(filename, 'w') as f:
        f.write("# Lumina Depths - Submersible\n")
        f.write(f"# Vertices: {len(vertices)}\n")
        f.write(f"# Faces: {len(faces)}\n\n")

        for v in vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")

        f.write("\n")

        for face in faces:
            # OBJ uses 1-based indexing
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating submersible mesh...")
    vertices, faces = generate_submersible()

    output_path = os.path.join(OUTPUT_DIR, "submersible.glb")
    write_obj(output_path, vertices, faces)

    print(f"Generated: {output_path}")
    print(f"  Vertices: {len(vertices)}")
    print(f"  Faces: {len(faces)}")

if __name__ == "__main__":
    main()
