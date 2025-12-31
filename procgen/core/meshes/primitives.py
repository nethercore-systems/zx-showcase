"""
Primitive mesh generators.

Provides basic geometric shapes for building more complex meshes.
"""

import math
from typing import Tuple, Optional
from ...lib.mesh_utils import MeshData


def create_box(
    width: float = 1.0,
    height: float = 1.0,
    depth: float = 1.0,
    segments: Tuple[int, int, int] = (1, 1, 1),
) -> MeshData:
    """
    Create a box/cube mesh.

    Args:
        width: Width (X dimension)
        height: Height (Y dimension)
        depth: Depth (Z dimension)
        segments: Subdivisions in each dimension
    """
    mesh = MeshData()
    hw, hh, hd = width / 2, height / 2, depth / 2
    sx, sy, sz = segments

    def add_face(normal, corners):
        """Add a subdivided face."""
        u_axis = corners[1] - corners[0]
        v_axis = corners[3] - corners[0]
        base = corners[0]

        u_segs = sx if abs(normal[0]) < 0.5 else sy if abs(normal[1]) < 0.5 else sz
        v_segs = sy if abs(normal[1]) < 0.5 else sz if abs(normal[2]) < 0.5 else sx

        for v in range(v_segs):
            for u in range(u_segs):
                # Create quad
                u0, u1 = u / u_segs, (u + 1) / u_segs
                v0, v1 = v / v_segs, (v + 1) / v_segs

                p0 = base + u_axis * u0 + v_axis * v0
                p1 = base + u_axis * u1 + v_axis * v0
                p2 = base + u_axis * u1 + v_axis * v1
                p3 = base + u_axis * u0 + v_axis * v1

                i0 = mesh.add_vertex(tuple(p0), normal, (u0, v0))
                i1 = mesh.add_vertex(tuple(p1), normal, (u1, v0))
                i2 = mesh.add_vertex(tuple(p2), normal, (u1, v1))
                i3 = mesh.add_vertex(tuple(p3), normal, (u0, v1))

                mesh.add_tri(i0, i1, i2)
                mesh.add_tri(i0, i2, i3)

    # Use numpy arrays for vector math
    import numpy as np

    # Define 6 faces
    faces = [
        ((0, 0, 1), np.array([
            np.array([-hw, -hh, hd]),
            np.array([hw, -hh, hd]),
            np.array([hw, hh, hd]),
            np.array([-hw, hh, hd]),
        ])),  # Front
        ((0, 0, -1), np.array([
            np.array([hw, -hh, -hd]),
            np.array([-hw, -hh, -hd]),
            np.array([-hw, hh, -hd]),
            np.array([hw, hh, -hd]),
        ])),  # Back
        ((1, 0, 0), np.array([
            np.array([hw, -hh, hd]),
            np.array([hw, -hh, -hd]),
            np.array([hw, hh, -hd]),
            np.array([hw, hh, hd]),
        ])),  # Right
        ((-1, 0, 0), np.array([
            np.array([-hw, -hh, -hd]),
            np.array([-hw, -hh, hd]),
            np.array([-hw, hh, hd]),
            np.array([-hw, hh, -hd]),
        ])),  # Left
        ((0, 1, 0), np.array([
            np.array([-hw, hh, hd]),
            np.array([hw, hh, hd]),
            np.array([hw, hh, -hd]),
            np.array([-hw, hh, -hd]),
        ])),  # Top
        ((0, -1, 0), np.array([
            np.array([-hw, -hh, -hd]),
            np.array([hw, -hh, -hd]),
            np.array([hw, -hh, hd]),
            np.array([-hw, -hh, hd]),
        ])),  # Bottom
    ]

    for normal, corners in faces:
        add_face(normal, corners)

    return mesh


def create_sphere(
    radius: float = 0.5,
    segments: int = 16,
    rings: int = 8,
) -> MeshData:
    """
    Create a UV sphere mesh.

    Args:
        radius: Sphere radius
        segments: Horizontal divisions
        rings: Vertical divisions
    """
    mesh = MeshData()

    for ring in range(rings + 1):
        phi = math.pi * ring / rings
        for seg in range(segments + 1):
            theta = 2 * math.pi * seg / segments

            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.cos(phi)
            z = radius * math.sin(phi) * math.sin(theta)

            nx = math.sin(phi) * math.cos(theta)
            ny = math.cos(phi)
            nz = math.sin(phi) * math.sin(theta)

            u = seg / segments
            v = ring / rings

            mesh.add_vertex((x, y, z), (nx, ny, nz), (u, v))

    # Create triangles
    for ring in range(rings):
        for seg in range(segments):
            i0 = ring * (segments + 1) + seg
            i1 = i0 + 1
            i2 = i0 + segments + 1
            i3 = i2 + 1

            if ring > 0:
                mesh.add_tri(i0, i2, i1)
            if ring < rings - 1:
                mesh.add_tri(i1, i2, i3)

    return mesh


def create_cylinder(
    radius: float = 0.5,
    height: float = 1.0,
    segments: int = 16,
    caps: bool = True,
) -> MeshData:
    """
    Create a cylinder mesh.

    Args:
        radius: Cylinder radius
        height: Cylinder height
        segments: Number of sides
        caps: Whether to include top and bottom caps
    """
    mesh = MeshData()
    hh = height / 2

    # Side vertices
    for i in range(segments + 1):
        theta = 2 * math.pi * i / segments
        x = radius * math.cos(theta)
        z = radius * math.sin(theta)
        nx = math.cos(theta)
        nz = math.sin(theta)
        u = i / segments

        mesh.add_vertex((x, -hh, z), (nx, 0, nz), (u, 0))
        mesh.add_vertex((x, hh, z), (nx, 0, nz), (u, 1))

    # Side faces
    for i in range(segments):
        i0 = i * 2
        i1 = i0 + 1
        i2 = i0 + 2
        i3 = i0 + 3

        mesh.add_tri(i0, i2, i1)
        mesh.add_tri(i1, i2, i3)

    if caps:
        # Top cap
        center_top = mesh.add_vertex((0, hh, 0), (0, 1, 0), (0.5, 0.5))
        for i in range(segments):
            theta1 = 2 * math.pi * i / segments
            theta2 = 2 * math.pi * (i + 1) / segments
            x1 = radius * math.cos(theta1)
            z1 = radius * math.sin(theta1)
            x2 = radius * math.cos(theta2)
            z2 = radius * math.sin(theta2)

            i1 = mesh.add_vertex((x1, hh, z1), (0, 1, 0), (0.5 + 0.5 * math.cos(theta1), 0.5 + 0.5 * math.sin(theta1)))
            i2 = mesh.add_vertex((x2, hh, z2), (0, 1, 0), (0.5 + 0.5 * math.cos(theta2), 0.5 + 0.5 * math.sin(theta2)))
            mesh.add_tri(center_top, i1, i2)

        # Bottom cap
        center_bottom = mesh.add_vertex((0, -hh, 0), (0, -1, 0), (0.5, 0.5))
        for i in range(segments):
            theta1 = 2 * math.pi * i / segments
            theta2 = 2 * math.pi * (i + 1) / segments
            x1 = radius * math.cos(theta1)
            z1 = radius * math.sin(theta1)
            x2 = radius * math.cos(theta2)
            z2 = radius * math.sin(theta2)

            i1 = mesh.add_vertex((x1, -hh, z1), (0, -1, 0), (0.5 + 0.5 * math.cos(theta1), 0.5 + 0.5 * math.sin(theta1)))
            i2 = mesh.add_vertex((x2, -hh, z2), (0, -1, 0), (0.5 + 0.5 * math.cos(theta2), 0.5 + 0.5 * math.sin(theta2)))
            mesh.add_tri(center_bottom, i2, i1)

    return mesh


def create_torus(
    major_radius: float = 0.5,
    minor_radius: float = 0.2,
    major_segments: int = 16,
    minor_segments: int = 8,
) -> MeshData:
    """
    Create a torus (donut) mesh.

    Args:
        major_radius: Distance from center to tube center
        minor_radius: Tube radius
        major_segments: Divisions around the ring
        minor_segments: Divisions around the tube
    """
    mesh = MeshData()

    for i in range(major_segments + 1):
        theta = 2 * math.pi * i / major_segments
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        for j in range(minor_segments + 1):
            phi = 2 * math.pi * j / minor_segments
            cos_phi = math.cos(phi)
            sin_phi = math.sin(phi)

            x = (major_radius + minor_radius * cos_phi) * cos_theta
            y = minor_radius * sin_phi
            z = (major_radius + minor_radius * cos_phi) * sin_theta

            nx = cos_phi * cos_theta
            ny = sin_phi
            nz = cos_phi * sin_theta

            u = i / major_segments
            v = j / minor_segments

            mesh.add_vertex((x, y, z), (nx, ny, nz), (u, v))

    # Create triangles
    for i in range(major_segments):
        for j in range(minor_segments):
            i0 = i * (minor_segments + 1) + j
            i1 = i0 + 1
            i2 = i0 + minor_segments + 1
            i3 = i2 + 1

            mesh.add_tri(i0, i2, i1)
            mesh.add_tri(i1, i2, i3)

    return mesh


def create_cone(
    radius: float = 0.5,
    height: float = 1.0,
    segments: int = 16,
    cap: bool = True,
) -> MeshData:
    """
    Create a cone mesh.

    Args:
        radius: Base radius
        height: Cone height
        segments: Number of sides
        cap: Whether to include bottom cap
    """
    mesh = MeshData()
    hh = height / 2

    # Apex
    apex = mesh.add_vertex((0, hh, 0), (0, 1, 0), (0.5, 0))

    # Base vertices and side faces
    for i in range(segments):
        theta1 = 2 * math.pi * i / segments
        theta2 = 2 * math.pi * (i + 1) / segments
        x1 = radius * math.cos(theta1)
        z1 = radius * math.sin(theta1)
        x2 = radius * math.cos(theta2)
        z2 = radius * math.sin(theta2)

        # Side normal (approximate)
        side_angle = math.atan2(radius, height)
        nx1 = math.cos(side_angle) * math.cos(theta1)
        ny = math.sin(side_angle)
        nz1 = math.cos(side_angle) * math.sin(theta1)
        nx2 = math.cos(side_angle) * math.cos(theta2)
        nz2 = math.cos(side_angle) * math.sin(theta2)

        i1 = mesh.add_vertex((x1, -hh, z1), (nx1, ny, nz1), (i / segments, 1))
        i2 = mesh.add_vertex((x2, -hh, z2), (nx2, ny, nz2), ((i + 1) / segments, 1))
        mesh.add_tri(apex, i1, i2)

    if cap:
        center = mesh.add_vertex((0, -hh, 0), (0, -1, 0), (0.5, 0.5))
        for i in range(segments):
            theta1 = 2 * math.pi * i / segments
            theta2 = 2 * math.pi * (i + 1) / segments
            x1 = radius * math.cos(theta1)
            z1 = radius * math.sin(theta1)
            x2 = radius * math.cos(theta2)
            z2 = radius * math.sin(theta2)

            i1 = mesh.add_vertex((x1, -hh, z1), (0, -1, 0), (0.5 + 0.5 * math.cos(theta1), 0.5 + 0.5 * math.sin(theta1)))
            i2 = mesh.add_vertex((x2, -hh, z2), (0, -1, 0), (0.5 + 0.5 * math.cos(theta2), 0.5 + 0.5 * math.sin(theta2)))
            mesh.add_tri(center, i2, i1)

    return mesh


def create_prism(
    radius: float = 0.5,
    height: float = 1.0,
    sides: int = 6,
    caps: bool = True,
) -> MeshData:
    """
    Create a prism with N sides.

    Args:
        radius: Distance from center to vertices
        height: Prism height
        sides: Number of sides (3=triangular, 6=hexagonal, etc.)
        caps: Whether to include top and bottom caps
    """
    mesh = MeshData()
    hh = height / 2

    # Create side faces
    for i in range(sides):
        theta1 = 2 * math.pi * i / sides
        theta2 = 2 * math.pi * (i + 1) / sides

        x1 = radius * math.cos(theta1)
        z1 = radius * math.sin(theta1)
        x2 = radius * math.cos(theta2)
        z2 = radius * math.sin(theta2)

        # Normal for this face
        mid_theta = (theta1 + theta2) / 2
        nx = math.cos(mid_theta)
        nz = math.sin(mid_theta)

        i0 = mesh.add_vertex((x1, -hh, z1), (nx, 0, nz), (i / sides, 0))
        i1 = mesh.add_vertex((x1, hh, z1), (nx, 0, nz), (i / sides, 1))
        i2 = mesh.add_vertex((x2, -hh, z2), (nx, 0, nz), ((i + 1) / sides, 0))
        i3 = mesh.add_vertex((x2, hh, z2), (nx, 0, nz), ((i + 1) / sides, 1))

        mesh.add_tri(i0, i2, i1)
        mesh.add_tri(i1, i2, i3)

    if caps:
        # Top cap (fan)
        center_top = mesh.add_vertex((0, hh, 0), (0, 1, 0), (0.5, 0.5))
        for i in range(sides):
            theta1 = 2 * math.pi * i / sides
            theta2 = 2 * math.pi * (i + 1) / sides
            x1 = radius * math.cos(theta1)
            z1 = radius * math.sin(theta1)
            x2 = radius * math.cos(theta2)
            z2 = radius * math.sin(theta2)

            i1 = mesh.add_vertex((x1, hh, z1), (0, 1, 0), (0.5 + 0.5 * math.cos(theta1), 0.5 + 0.5 * math.sin(theta1)))
            i2 = mesh.add_vertex((x2, hh, z2), (0, 1, 0), (0.5 + 0.5 * math.cos(theta2), 0.5 + 0.5 * math.sin(theta2)))
            mesh.add_tri(center_top, i1, i2)

        # Bottom cap (fan)
        center_bottom = mesh.add_vertex((0, -hh, 0), (0, -1, 0), (0.5, 0.5))
        for i in range(sides):
            theta1 = 2 * math.pi * i / sides
            theta2 = 2 * math.pi * (i + 1) / sides
            x1 = radius * math.cos(theta1)
            z1 = radius * math.sin(theta1)
            x2 = radius * math.cos(theta2)
            z2 = radius * math.sin(theta2)

            i1 = mesh.add_vertex((x1, -hh, z1), (0, -1, 0), (0.5 + 0.5 * math.cos(theta1), 0.5 + 0.5 * math.sin(theta1)))
            i2 = mesh.add_vertex((x2, -hh, z2), (0, -1, 0), (0.5 + 0.5 * math.cos(theta2), 0.5 + 0.5 * math.sin(theta2)))
            mesh.add_tri(center_bottom, i2, i1)

    return mesh


def create_pyramid(
    base_size: float = 1.0,
    height: float = 1.0,
    sides: int = 4,
    cap: bool = True,
) -> MeshData:
    """
    Create a pyramid with N-sided base.

    Args:
        base_size: Base width/depth
        height: Pyramid height
        sides: Number of base sides (4=square pyramid)
        cap: Whether to include base cap
    """
    mesh = MeshData()
    radius = base_size / 2
    hh = height / 2

    # Apex
    apex = mesh.add_vertex((0, hh, 0), (0, 1, 0), (0.5, 0))

    # Side faces
    for i in range(sides):
        theta1 = 2 * math.pi * i / sides + math.pi / sides
        theta2 = 2 * math.pi * (i + 1) / sides + math.pi / sides

        x1 = radius * math.cos(theta1)
        z1 = radius * math.sin(theta1)
        x2 = radius * math.cos(theta2)
        z2 = radius * math.sin(theta2)

        # Calculate face normal
        mid_theta = (theta1 + theta2) / 2
        side_angle = math.atan2(radius, height)
        nx = math.cos(side_angle) * math.cos(mid_theta)
        ny = math.sin(side_angle)
        nz = math.cos(side_angle) * math.sin(mid_theta)

        i1 = mesh.add_vertex((x1, -hh, z1), (nx, ny, nz), (i / sides, 1))
        i2 = mesh.add_vertex((x2, -hh, z2), (nx, ny, nz), ((i + 1) / sides, 1))
        mesh.add_tri(apex, i1, i2)

    if cap:
        center = mesh.add_vertex((0, -hh, 0), (0, -1, 0), (0.5, 0.5))
        for i in range(sides):
            theta1 = 2 * math.pi * i / sides + math.pi / sides
            theta2 = 2 * math.pi * (i + 1) / sides + math.pi / sides
            x1 = radius * math.cos(theta1)
            z1 = radius * math.sin(theta1)
            x2 = radius * math.cos(theta2)
            z2 = radius * math.sin(theta2)

            i1 = mesh.add_vertex((x1, -hh, z1), (0, -1, 0), (0.5 + 0.5 * math.cos(theta1), 0.5 + 0.5 * math.sin(theta1)))
            i2 = mesh.add_vertex((x2, -hh, z2), (0, -1, 0), (0.5 + 0.5 * math.cos(theta2), 0.5 + 0.5 * math.sin(theta2)))
            mesh.add_tri(center, i2, i1)

    return mesh


def create_capsule(
    radius: float = 0.25,
    height: float = 1.0,
    segments: int = 16,
    rings: int = 4,
) -> MeshData:
    """
    Create a capsule (cylinder with hemispherical caps).

    Args:
        radius: Capsule radius
        height: Total height including caps
        segments: Horizontal divisions
        rings: Vertical divisions for each cap
    """
    mesh = MeshData()
    cylinder_height = max(0, height - 2 * radius)
    half_cyl = cylinder_height / 2

    # Top hemisphere
    for ring in range(rings + 1):
        phi = math.pi / 2 * ring / rings
        y = half_cyl + radius * math.cos(phi)

        for seg in range(segments + 1):
            theta = 2 * math.pi * seg / segments
            x = radius * math.sin(phi) * math.cos(theta)
            z = radius * math.sin(phi) * math.sin(theta)

            nx = math.sin(phi) * math.cos(theta)
            ny = math.cos(phi)
            nz = math.sin(phi) * math.sin(theta)

            u = seg / segments
            v = ring / (2 * rings)

            mesh.add_vertex((x, y, z), (nx, ny, nz), (u, v))

    # Cylinder body
    for i in range(2):
        y = half_cyl if i == 0 else -half_cyl
        for seg in range(segments + 1):
            theta = 2 * math.pi * seg / segments
            x = radius * math.cos(theta)
            z = radius * math.sin(theta)

            u = seg / segments
            v = 0.5 if i == 0 else 0.5

            mesh.add_vertex((x, y, z), (math.cos(theta), 0, math.sin(theta)), (u, v))

    # Bottom hemisphere
    for ring in range(rings + 1):
        phi = math.pi / 2 + math.pi / 2 * ring / rings
        y = -half_cyl + radius * math.cos(phi)

        for seg in range(segments + 1):
            theta = 2 * math.pi * seg / segments
            x = radius * math.sin(phi) * math.cos(theta)
            z = radius * math.sin(phi) * math.sin(theta)

            nx = math.sin(phi) * math.cos(theta)
            ny = math.cos(phi)
            nz = math.sin(phi) * math.sin(theta)

            u = seg / segments
            v = 0.5 + (ring + rings) / (2 * rings)

            mesh.add_vertex((x, y, z), (nx, ny, nz), (u, v))

    # Generate triangles
    total_rows = 2 * rings + 2
    for row in range(total_rows):
        for seg in range(segments):
            i0 = row * (segments + 1) + seg
            i1 = i0 + 1
            i2 = i0 + segments + 1
            i3 = i2 + 1

            if row < total_rows - 1:
                mesh.add_tri(i0, i2, i1)
                mesh.add_tri(i1, i2, i3)

    return mesh
