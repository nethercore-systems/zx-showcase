#!/usr/bin/env python3
"""Mesh primitive generators for procedural mesh generation.

Shared primitives used by all mesh generators (Lumina Depths, etc.)
Aligned with zx-procgen generator-patterns skill.

These are pure Python primitives that output vertex/face lists.
For Blender-based generation, see bpy_utils.py instead.
"""
import math
from typing import List, Tuple


Vertex = Tuple[float, float, float]
Face = Tuple[int, int, int]
Mesh = Tuple[List[Vertex], List[Face]]


def generate_sphere(cx: float, cy: float, cz: float, radius: float,
                    lat_segments: int = 12, lon_segments: int = 16) -> Mesh:
    """Generate sphere vertices and faces."""
    vertices = []
    faces = []

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

    for lat in range(lat_segments):
        for lon in range(lon_segments):
            current = lat * lon_segments + lon
            next_lon = lat * lon_segments + (lon + 1) % lon_segments
            below = (lat + 1) * lon_segments + lon
            below_next = (lat + 1) * lon_segments + (lon + 1) % lon_segments

            faces.append((current, below, below_next))
            faces.append((current, below_next, next_lon))

    return vertices, faces


def generate_ellipsoid(cx: float, cy: float, cz: float,
                       rx: float, ry: float, rz: float,
                       lat_segments: int = 10, lon_segments: int = 14) -> Mesh:
    """Generate ellipsoid vertices and faces."""
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


def generate_hemisphere(cx: float, cy: float, cz: float,
                        rx: float, ry: float, rz: float,
                        lat_segments: int = 8, lon_segments: int = 12,
                        top: bool = True) -> Mesh:
    """Generate hemisphere (half ellipsoid)."""
    vertices = []
    faces = []

    start_lat = 0 if top else lat_segments // 2
    end_lat = lat_segments // 2 + 1 if top else lat_segments + 1

    for lat in range(start_lat, end_lat):
        theta = math.pi * lat / lat_segments
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        for lon in range(lon_segments):
            phi = 2 * math.pi * lon / lon_segments
            x = cx + rx * sin_theta * math.cos(phi)
            y = cy + ry * sin_theta * math.sin(phi)
            z = cz + rz * cos_theta
            vertices.append((x, y, z))

    rows = end_lat - start_lat - 1
    for lat in range(rows):
        for lon in range(lon_segments):
            current = lat * lon_segments + lon
            next_lon = lat * lon_segments + (lon + 1) % lon_segments
            below = (lat + 1) * lon_segments + lon
            below_next = (lat + 1) * lon_segments + (lon + 1) % lon_segments

            faces.append((current, below, below_next))
            faces.append((current, below_next, next_lon))

    return vertices, faces


def generate_cylinder(cx: float, cy: float, cz: float,
                      radius: float, height: float,
                      segments: int = 16, caps: bool = True,
                      axis: str = 'z') -> Mesh:
    """Generate cylinder vertices and faces along specified axis."""
    vertices = []
    faces = []

    for end in [0, 1]:
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            if axis == 'z':
                x = cx + radius * math.cos(angle)
                y = cy + radius * math.sin(angle)
                z = cz + (height/2 if end else -height/2)
            elif axis == 'x':
                y = cy + radius * math.cos(angle)
                z = cz + radius * math.sin(angle)
                x = cx + (height/2 if end else -height/2)
            else:  # y
                x = cx + radius * math.cos(angle)
                z = cz + radius * math.sin(angle)
                y = cy + (height/2 if end else -height/2)
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
        # Caps
        top_center = len(vertices)
        if axis == 'z':
            vertices.append((cx, cy, cz + height/2))
        elif axis == 'x':
            vertices.append((cx + height/2, cy, cz))
        else:
            vertices.append((cx, cy + height/2, cz))

        bot_center = len(vertices)
        if axis == 'z':
            vertices.append((cx, cy, cz - height/2))
        elif axis == 'x':
            vertices.append((cx - height/2, cy, cz))
        else:
            vertices.append((cx, cy - height/2, cz))

        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append((top_center, next_i, i))
            faces.append((bot_center, i + segments, next_i + segments))

    return vertices, faces


def generate_cone(cx: float, cy: float, cz: float,
                  radius: float, height: float,
                  segments: int = 16) -> Mesh:
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


def generate_fin(cx: float, cy: float, cz: float,
                 length: float, height: float, thickness: float,
                 rotation_y: float = 0, rotation_z: float = 0) -> Mesh:
    """Generate a triangular fin shape with rotation."""
    vertices = []
    faces = []

    # Triangle points (in local space)
    pts = [
        (0, 0, thickness/2),      # Base front
        (0, 0, -thickness/2),     # Base back
        (0, height, 0),           # Top
        (length, 0, 0),           # Tip
    ]

    # Apply rotations
    cos_y = math.cos(rotation_y)
    sin_y = math.sin(rotation_y)
    cos_z = math.cos(rotation_z)
    sin_z = math.sin(rotation_z)

    for px, py, pz in pts:
        # Rotate around Y
        x1 = px * cos_y + pz * sin_y
        z1 = -px * sin_y + pz * cos_y
        # Rotate around Z
        x2 = x1 * cos_z - py * sin_z
        y2 = x1 * sin_z + py * cos_z

        vertices.append((cx + x2, cy + y2, cz + z1))

    # Faces (triangles)
    faces.append((0, 2, 3))  # Front-top
    faces.append((1, 3, 2))  # Back-top
    faces.append((0, 3, 1))  # Bottom
    faces.append((0, 1, 2))  # Base

    return vertices, faces


def generate_tapered_body(length: float, max_radius: float,
                          taper_start: float, taper_end: float,
                          segments_len: int = 20, segments_circ: int = 16) -> Mesh:
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
            radius = max_radius * math.cos(local_t * math.pi / 2) * 0.3
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


def merge_meshes(mesh_list: List[Mesh], vertex_offset: int = 0) -> Mesh:
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


def write_obj(filepath: str, vertices: List[Vertex], faces: List[Face],
              name: str = "Mesh", comment: str = "") -> None:
    """Write mesh to OBJ file."""
    with open(filepath, 'w') as f:
        if comment:
            f.write(f"# {comment}\n")
        f.write(f"# {name}\n")
        f.write(f"# Vertices: {len(vertices)}\n")
        f.write(f"# Faces: {len(faces)}\n\n")

        for v in vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")

        f.write("\n")

        for face in faces:
            # OBJ uses 1-based indexing
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
