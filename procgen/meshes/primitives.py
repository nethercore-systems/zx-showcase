"""
Procedural mesh primitives for ZX console.

These functions generate mesh data that can be used with Blender's bmesh
or exported directly to GLB format.
"""

import math
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class MeshData:
    """Raw mesh data for export or Blender import."""
    vertices: List[Tuple[float, float, float]]
    faces: List[Tuple[int, ...]]
    normals: List[Tuple[float, float, float]] = None
    uvs: List[Tuple[float, float]] = None

    @property
    def triangle_count(self) -> int:
        """Count triangles (quads count as 2)."""
        return sum(len(f) - 2 for f in self.faces)


def create_box(
    width: float = 1.0,
    height: float = 1.0,
    depth: float = 1.0,
    center: Tuple[float, float, float] = (0, 0, 0),
    bevel: float = 0.0,
) -> MeshData:
    """
    Create a box mesh.

    Args:
        width: X dimension
        height: Z dimension
        depth: Y dimension
        center: Center position
        bevel: Bevel amount (0 = sharp corners)
    """
    hw, hh, hd = width / 2, height / 2, depth / 2
    cx, cy, cz = center

    # 8 corner vertices
    vertices = [
        (cx - hw, cy - hd, cz - hh),
        (cx + hw, cy - hd, cz - hh),
        (cx + hw, cy + hd, cz - hh),
        (cx - hw, cy + hd, cz - hh),
        (cx - hw, cy - hd, cz + hh),
        (cx + hw, cy - hd, cz + hh),
        (cx + hw, cy + hd, cz + hh),
        (cx - hw, cy + hd, cz + hh),
    ]

    # 6 quad faces
    faces = [
        (0, 1, 2, 3),  # bottom
        (4, 7, 6, 5),  # top
        (0, 4, 5, 1),  # front
        (2, 6, 7, 3),  # back
        (0, 3, 7, 4),  # left
        (1, 5, 6, 2),  # right
    ]

    return MeshData(vertices=vertices, faces=faces)


def create_sphere(
    radius: float = 1.0,
    segments: int = 8,
    rings: int = 6,
    center: Tuple[float, float, float] = (0, 0, 0),
) -> MeshData:
    """
    Create a UV sphere mesh.

    Args:
        radius: Sphere radius
        segments: Horizontal divisions (longitude)
        rings: Vertical divisions (latitude)
        center: Center position
    """
    cx, cy, cz = center
    vertices = []
    faces = []

    # Top pole
    vertices.append((cx, cy, cz + radius))

    # Rings between poles
    for ring in range(1, rings):
        phi = math.pi * ring / rings
        z = radius * math.cos(phi)
        ring_radius = radius * math.sin(phi)

        for seg in range(segments):
            theta = 2 * math.pi * seg / segments
            x = ring_radius * math.cos(theta)
            y = ring_radius * math.sin(theta)
            vertices.append((cx + x, cy + y, cz + z))

    # Bottom pole
    vertices.append((cx, cy, cz - radius))

    # Top cap triangles
    for seg in range(segments):
        next_seg = (seg + 1) % segments
        faces.append((0, 1 + seg, 1 + next_seg))

    # Ring quads
    for ring in range(rings - 2):
        ring_start = 1 + ring * segments
        next_ring_start = ring_start + segments

        for seg in range(segments):
            next_seg = (seg + 1) % segments
            v0 = ring_start + seg
            v1 = ring_start + next_seg
            v2 = next_ring_start + next_seg
            v3 = next_ring_start + seg
            faces.append((v0, v3, v2, v1))

    # Bottom cap triangles
    bottom_pole = len(vertices) - 1
    last_ring_start = 1 + (rings - 2) * segments
    for seg in range(segments):
        next_seg = (seg + 1) % segments
        faces.append((bottom_pole, last_ring_start + next_seg, last_ring_start + seg))

    return MeshData(vertices=vertices, faces=faces)


def create_cylinder(
    radius: float = 1.0,
    height: float = 2.0,
    segments: int = 8,
    caps: bool = True,
    center: Tuple[float, float, float] = (0, 0, 0),
) -> MeshData:
    """
    Create a cylinder mesh.

    Args:
        radius: Cylinder radius
        height: Total height
        segments: Number of sides
        caps: Include top and bottom caps
        center: Center position
    """
    cx, cy, cz = center
    half_h = height / 2
    vertices = []
    faces = []

    # Bottom ring
    for seg in range(segments):
        theta = 2 * math.pi * seg / segments
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        vertices.append((cx + x, cy + y, cz - half_h))

    # Top ring
    for seg in range(segments):
        theta = 2 * math.pi * seg / segments
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        vertices.append((cx + x, cy + y, cz + half_h))

    # Side faces (quads)
    for seg in range(segments):
        next_seg = (seg + 1) % segments
        v0 = seg
        v1 = next_seg
        v2 = segments + next_seg
        v3 = segments + seg
        faces.append((v0, v1, v2, v3))

    if caps:
        # Bottom cap (n-gon, will be triangulated)
        vertices.append((cx, cy, cz - half_h))
        bottom_center = len(vertices) - 1
        for seg in range(segments):
            next_seg = (seg + 1) % segments
            faces.append((bottom_center, next_seg, seg))

        # Top cap
        vertices.append((cx, cy, cz + half_h))
        top_center = len(vertices) - 1
        for seg in range(segments):
            next_seg = (seg + 1) % segments
            faces.append((top_center, segments + seg, segments + next_seg))

    return MeshData(vertices=vertices, faces=faces)


def create_prism(
    sides: int = 6,
    radius: float = 1.0,
    height: float = 2.0,
    taper: float = 1.0,
    center: Tuple[float, float, float] = (0, 0, 0),
) -> MeshData:
    """
    Create a prism/polygon extrusion mesh.

    Args:
        sides: Number of sides (3 = triangle, 6 = hexagon)
        radius: Base radius
        height: Total height
        taper: Top radius multiplier (0.5 = tapered, 1.0 = straight)
        center: Center position
    """
    cx, cy, cz = center
    half_h = height / 2
    top_radius = radius * taper
    vertices = []
    faces = []

    # Bottom ring
    for i in range(sides):
        theta = 2 * math.pi * i / sides
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        vertices.append((cx + x, cy + y, cz - half_h))

    # Top ring (possibly tapered)
    for i in range(sides):
        theta = 2 * math.pi * i / sides
        x = top_radius * math.cos(theta)
        y = top_radius * math.sin(theta)
        vertices.append((cx + x, cy + y, cz + half_h))

    # Side faces
    for i in range(sides):
        next_i = (i + 1) % sides
        v0 = i
        v1 = next_i
        v2 = sides + next_i
        v3 = sides + i
        faces.append((v0, v1, v2, v3))

    # Bottom cap
    vertices.append((cx, cy, cz - half_h))
    bottom_center = len(vertices) - 1
    for i in range(sides):
        next_i = (i + 1) % sides
        faces.append((bottom_center, next_i, i))

    # Top cap
    vertices.append((cx, cy, cz + half_h))
    top_center = len(vertices) - 1
    for i in range(sides):
        next_i = (i + 1) % sides
        faces.append((top_center, sides + i, sides + next_i))

    return MeshData(vertices=vertices, faces=faces)


def create_torus(
    major_radius: float = 1.0,
    minor_radius: float = 0.25,
    major_segments: int = 8,
    minor_segments: int = 6,
    center: Tuple[float, float, float] = (0, 0, 0),
) -> MeshData:
    """
    Create a torus mesh.

    Args:
        major_radius: Distance from center to tube center
        minor_radius: Tube radius
        major_segments: Segments around the ring
        minor_segments: Segments around the tube
        center: Center position
    """
    cx, cy, cz = center
    vertices = []
    faces = []

    for major in range(major_segments):
        major_angle = 2 * math.pi * major / major_segments

        # Center of tube at this major angle
        tube_center_x = major_radius * math.cos(major_angle)
        tube_center_y = major_radius * math.sin(major_angle)

        for minor in range(minor_segments):
            minor_angle = 2 * math.pi * minor / minor_segments

            # Point on tube surface
            x = tube_center_x + minor_radius * math.cos(minor_angle) * math.cos(major_angle)
            y = tube_center_y + minor_radius * math.cos(minor_angle) * math.sin(major_angle)
            z = minor_radius * math.sin(minor_angle)

            vertices.append((cx + x, cy + y, cz + z))

    # Connect faces
    for major in range(major_segments):
        next_major = (major + 1) % major_segments

        for minor in range(minor_segments):
            next_minor = (minor + 1) % minor_segments

            v0 = major * minor_segments + minor
            v1 = major * minor_segments + next_minor
            v2 = next_major * minor_segments + next_minor
            v3 = next_major * minor_segments + minor

            faces.append((v0, v1, v2, v3))

    return MeshData(vertices=vertices, faces=faces)


def apply_noise(mesh: MeshData, amplitude: float = 0.1, seed: int = 42) -> MeshData:
    """Apply noise displacement to vertices."""
    import random
    random.seed(seed)

    new_vertices = []
    for x, y, z in mesh.vertices:
        nx = x + (random.random() - 0.5) * amplitude
        ny = y + (random.random() - 0.5) * amplitude
        nz = z + (random.random() - 0.5) * amplitude
        new_vertices.append((nx, ny, nz))

    return MeshData(vertices=new_vertices, faces=mesh.faces)


def merge_meshes(meshes: List[MeshData]) -> MeshData:
    """Merge multiple meshes into one."""
    vertices = []
    faces = []
    offset = 0

    for mesh in meshes:
        vertices.extend(mesh.vertices)
        for face in mesh.faces:
            faces.append(tuple(v + offset for v in face))
        offset += len(mesh.vertices)

    return MeshData(vertices=vertices, faces=faces)
