"""
Pickup item mesh generators.

Provides gems, health pickups, XP orbs, powerups, and collectibles.
"""

import math
from dataclasses import dataclass
from typing import Optional, Tuple
from ...lib.mesh_utils import MeshData, merge_meshes


@dataclass
class PickupParams:
    """Parameters for pickup generation."""
    size: float = 0.3
    facets: int = 8
    segments: int = 12
    inner_glow: bool = True
    rotation_offset: float = 0.0


def create_gem_pickup(
    params: PickupParams = None,
    gem_type: str = "diamond",
) -> MeshData:
    """
    Create a gem/crystal pickup mesh.

    Args:
        params: Pickup parameters
        gem_type: "diamond", "emerald", "ruby", "prism"
    """
    p = params or PickupParams()
    mesh = MeshData()

    if gem_type == "diamond":
        mesh = _create_diamond_gem(p)
    elif gem_type == "emerald":
        mesh = _create_emerald_gem(p)
    elif gem_type == "ruby":
        mesh = _create_ruby_gem(p)
    else:  # prism
        mesh = _create_prism_gem(p)

    return mesh


def _create_diamond_gem(p: PickupParams) -> MeshData:
    """Create classic diamond shape (octahedron-based)."""
    mesh = MeshData()
    size = p.size

    # Top and bottom points
    top = (0, size, 0)
    bottom = (0, -size * 0.6, 0)

    # Middle ring (girdle)
    ring = []
    for i in range(p.facets):
        theta = 2 * math.pi * i / p.facets + p.rotation_offset
        x = size * 0.7 * math.cos(theta)
        z = size * 0.7 * math.sin(theta)
        ring.append((x, size * 0.2, z))

    # Create crown (top pyramid)
    top_idx = mesh.add_vertex(top, (0, 1, 0), (0.5, 0))
    for i in range(p.facets):
        r1 = ring[i]
        r2 = ring[(i + 1) % p.facets]

        # Calculate normal
        nx = (r1[0] + r2[0]) / 2
        nz = (r1[2] + r2[2]) / 2
        length = math.sqrt(nx * nx + nz * nz)
        if length > 0:
            nx, nz = nx / length, nz / length

        i1 = mesh.add_vertex(r1, (nx, 0.5, nz), (i / p.facets, 0.5))
        i2 = mesh.add_vertex(r2, (nx, 0.5, nz), ((i + 1) / p.facets, 0.5))
        mesh.add_tri(top_idx, i1, i2)

    # Create pavilion (bottom pyramid)
    bottom_idx = mesh.add_vertex(bottom, (0, -1, 0), (0.5, 1))
    for i in range(p.facets):
        r1 = ring[i]
        r2 = ring[(i + 1) % p.facets]

        nx = (r1[0] + r2[0]) / 2
        nz = (r1[2] + r2[2]) / 2
        length = math.sqrt(nx * nx + nz * nz)
        if length > 0:
            nx, nz = nx / length, nz / length

        i1 = mesh.add_vertex(r1, (nx, -0.5, nz), (i / p.facets, 0.5))
        i2 = mesh.add_vertex(r2, (nx, -0.5, nz), ((i + 1) / p.facets, 0.5))
        mesh.add_tri(bottom_idx, i2, i1)

    return mesh


def _create_emerald_gem(p: PickupParams) -> MeshData:
    """Create emerald cut (rectangular with beveled corners)."""
    mesh = MeshData()
    size = p.size

    # Emerald has 8 sides (rectangle with cut corners)
    # Top face
    w = size * 0.7
    d = size * 0.5
    bevel = size * 0.2

    top_verts = [
        (-w + bevel, size * 0.4, d),
        (w - bevel, size * 0.4, d),
        (w, size * 0.4, d - bevel),
        (w, size * 0.4, -d + bevel),
        (w - bevel, size * 0.4, -d),
        (-w + bevel, size * 0.4, -d),
        (-w, size * 0.4, -d + bevel),
        (-w, size * 0.4, d - bevel),
    ]

    bottom_verts = [
        (-w + bevel, -size * 0.4, d),
        (w - bevel, -size * 0.4, d),
        (w, -size * 0.4, d - bevel),
        (w, -size * 0.4, -d + bevel),
        (w - bevel, -size * 0.4, -d),
        (-w + bevel, -size * 0.4, -d),
        (-w, -size * 0.4, -d + bevel),
        (-w, -size * 0.4, d - bevel),
    ]

    # Top face (center)
    center_top = mesh.add_vertex((0, size * 0.4, 0), (0, 1, 0), (0.5, 0.5))
    for i in range(8):
        i1 = mesh.add_vertex(top_verts[i], (0, 1, 0), (0.5, 0.5))
        i2 = mesh.add_vertex(top_verts[(i + 1) % 8], (0, 1, 0), (0.5, 0.5))
        mesh.add_tri(center_top, i1, i2)

    # Bottom face
    center_bottom = mesh.add_vertex((0, -size * 0.4, 0), (0, -1, 0), (0.5, 0.5))
    for i in range(8):
        i1 = mesh.add_vertex(bottom_verts[i], (0, -1, 0), (0.5, 0.5))
        i2 = mesh.add_vertex(bottom_verts[(i + 1) % 8], (0, -1, 0), (0.5, 0.5))
        mesh.add_tri(center_bottom, i2, i1)

    # Side faces
    for i in range(8):
        t1, t2 = top_verts[i], top_verts[(i + 1) % 8]
        b1, b2 = bottom_verts[i], bottom_verts[(i + 1) % 8]

        # Calculate normal
        dx = (t2[0] - t1[0] + b2[0] - b1[0]) / 2
        dz = (t2[2] - t1[2] + b2[2] - b1[2]) / 2
        nx, nz = -dz, dx  # Perpendicular
        length = math.sqrt(nx * nx + nz * nz)
        if length > 0:
            nx, nz = nx / length, nz / length

        i0 = mesh.add_vertex(t1, (nx, 0, nz), (0, 0))
        i1 = mesh.add_vertex(t2, (nx, 0, nz), (1, 0))
        i2 = mesh.add_vertex(b1, (nx, 0, nz), (0, 1))
        i3 = mesh.add_vertex(b2, (nx, 0, nz), (1, 1))

        mesh.add_tri(i0, i1, i2)
        mesh.add_tri(i2, i1, i3)

    return mesh


def _create_ruby_gem(p: PickupParams) -> MeshData:
    """Create cabochon/oval ruby shape."""
    from .primitives import create_sphere

    mesh = create_sphere(p.size * 0.5, segments=p.segments, rings=p.segments // 2)
    mesh.scale(1.0, 0.6, 0.8)  # Flatten into oval

    return mesh


def _create_prism_gem(p: PickupParams) -> MeshData:
    """Create triangular prism gem."""
    from .primitives import create_prism

    mesh = create_prism(p.size * 0.6, p.size * 1.2, sides=3)
    return mesh


def create_health_pickup(
    params: PickupParams = None,
    style: str = "cross",
) -> MeshData:
    """
    Create a health pickup mesh.

    Args:
        params: Pickup parameters
        style: "cross", "heart", "orb"
    """
    p = params or PickupParams()

    if style == "cross":
        return _create_health_cross(p)
    elif style == "heart":
        return _create_health_heart(p)
    else:
        return _create_health_orb(p)


def _create_health_cross(p: PickupParams) -> MeshData:
    """Create 3D plus/cross shape."""
    from .primitives import create_box

    meshes = []
    arm_length = p.size
    arm_width = p.size * 0.35
    arm_depth = p.size * 0.25

    # Horizontal arm
    h_arm = create_box(arm_length, arm_width, arm_depth)
    meshes.append(h_arm)

    # Vertical arm
    v_arm = create_box(arm_width, arm_length, arm_depth)
    meshes.append(v_arm)

    return merge_meshes(meshes)


def _create_health_heart(p: PickupParams) -> MeshData:
    """Create stylized heart shape."""
    mesh = MeshData()
    size = p.size

    # Heart shape using spheres approximation
    from .primitives import create_sphere

    meshes = []

    # Two top lobes
    lobe1 = create_sphere(size * 0.35, segments=p.segments)
    lobe1.translate(-size * 0.2, size * 0.15, 0)
    meshes.append(lobe1)

    lobe2 = create_sphere(size * 0.35, segments=p.segments)
    lobe2.translate(size * 0.2, size * 0.15, 0)
    meshes.append(lobe2)

    # Bottom point (cone-ish)
    from .primitives import create_cone
    point = create_cone(size * 0.5, size * 0.6, segments=p.segments)
    point.rotate(math.pi, 0, 0)  # Flip upside down
    point.translate(0, -size * 0.1, 0)
    meshes.append(point)

    return merge_meshes(meshes)


def _create_health_orb(p: PickupParams) -> MeshData:
    """Create glowing orb health pickup."""
    from .primitives import create_sphere

    return create_sphere(p.size * 0.5, segments=p.segments)


def create_xp_orb(
    params: PickupParams = None,
    tier: int = 1,
) -> MeshData:
    """
    Create an XP/experience orb.

    Args:
        params: Pickup parameters
        tier: 1=small, 2=medium, 3=large
    """
    p = params or PickupParams()
    from .primitives import create_sphere

    size_mult = 0.7 + tier * 0.15
    mesh = create_sphere(p.size * size_mult * 0.4, segments=p.segments)

    return mesh


def create_powerup_cube(
    params: PickupParams = None,
    style: str = "solid",
) -> MeshData:
    """
    Create a powerup cube.

    Args:
        params: Pickup parameters
        style: "solid", "hollow", "floating"
    """
    p = params or PickupParams()
    from .primitives import create_box

    if style == "hollow":
        # Hollow frame cube
        meshes = []
        edge = p.size * 0.1
        half = p.size * 0.4

        # 12 edges
        for axis in range(3):
            for i in [-1, 1]:
                for j in [-1, 1]:
                    if axis == 0:  # X edges
                        edge_mesh = create_box(p.size * 0.8, edge, edge)
                        edge_mesh.translate(0, i * half, j * half)
                    elif axis == 1:  # Y edges
                        edge_mesh = create_box(edge, p.size * 0.8, edge)
                        edge_mesh.translate(i * half, 0, j * half)
                    else:  # Z edges
                        edge_mesh = create_box(edge, edge, p.size * 0.8)
                        edge_mesh.translate(i * half, j * half, 0)
                    meshes.append(edge_mesh)

        return merge_meshes(meshes)
    elif style == "floating":
        # Cube with smaller inner cube
        meshes = []
        outer = create_box(p.size * 0.6, p.size * 0.6, p.size * 0.6)
        meshes.append(outer)

        inner = create_box(p.size * 0.3, p.size * 0.3, p.size * 0.3)
        meshes.append(inner)

        return merge_meshes(meshes)
    else:
        # Solid cube
        return create_box(p.size * 0.6, p.size * 0.6, p.size * 0.6)


def create_ammo_pickup(
    params: PickupParams = None,
    ammo_type: str = "bullet",
) -> MeshData:
    """
    Create an ammo pickup mesh.

    Args:
        params: Pickup parameters
        ammo_type: "bullet", "shell", "energy"
    """
    p = params or PickupParams()

    if ammo_type == "bullet":
        from .primitives import create_capsule
        mesh = create_capsule(p.size * 0.15, p.size * 0.6, segments=p.segments)
        mesh.rotate(0, 0, math.pi / 6)  # Slight tilt
        return mesh
    elif ammo_type == "shell":
        from .primitives import create_cylinder
        mesh = create_cylinder(p.size * 0.2, p.size * 0.4, segments=p.segments)
        mesh.rotate(math.pi / 2, 0, 0)
        return mesh
    else:  # energy
        from .primitives import create_sphere, create_torus

        meshes = []
        core = create_sphere(p.size * 0.2, segments=p.segments)
        meshes.append(core)

        ring = create_torus(p.size * 0.35, p.size * 0.05, p.segments, p.segments // 2)
        meshes.append(ring)

        return merge_meshes(meshes)
