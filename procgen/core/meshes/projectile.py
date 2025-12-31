"""
Projectile mesh generators.

Provides shards, orbs, beams, bullets, and missiles.
"""

import math
from dataclasses import dataclass
from typing import Optional, Tuple
from ...lib.mesh_utils import MeshData, merge_meshes


@dataclass
class ProjectileParams:
    """Parameters for projectile generation."""
    length: float = 0.3
    width: float = 0.1
    segments: int = 8
    trail_segments: int = 4
    has_trail: bool = False


def create_shard_projectile(
    params: ProjectileParams = None,
    shard_type: str = "crystal",
) -> MeshData:
    """
    Create a shard/crystal projectile.

    Args:
        params: Projectile parameters
        shard_type: "crystal", "glass", "ice"
    """
    p = params or ProjectileParams()
    mesh = MeshData()

    if shard_type == "crystal":
        mesh = _create_crystal_shard(p)
    elif shard_type == "glass":
        mesh = _create_glass_shard(p)
    else:  # ice
        mesh = _create_ice_shard(p)

    return mesh


def _create_crystal_shard(p: ProjectileParams) -> MeshData:
    """Create faceted crystal shard."""
    mesh = MeshData()
    length = p.length
    width = p.width

    # Sharp pointed crystal
    tip = (0, 0, length * 0.5)
    back = (0, 0, -length * 0.5)

    # Create 6-sided prism with pointed ends
    sides = 6
    ring = []
    for i in range(sides):
        theta = 2 * math.pi * i / sides
        x = width * 0.5 * math.cos(theta)
        y = width * 0.5 * math.sin(theta)
        ring.append((x, y, 0))

    # Front cone
    tip_idx = mesh.add_vertex(tip, (0, 0, 1), (0.5, 0))
    for i in range(sides):
        r1 = ring[i]
        r2 = ring[(i + 1) % sides]

        # Normal pointing outward and forward
        nx = (r1[0] + r2[0]) / 2
        ny = (r1[1] + r2[1]) / 2
        length_n = math.sqrt(nx * nx + ny * ny)
        if length_n > 0:
            nx, ny = nx / length_n, ny / length_n

        i1 = mesh.add_vertex(r1, (nx, ny, 0.5), (i / sides, 0.5))
        i2 = mesh.add_vertex(r2, (nx, ny, 0.5), ((i + 1) / sides, 0.5))
        mesh.add_tri(tip_idx, i1, i2)

    # Back cone
    back_idx = mesh.add_vertex(back, (0, 0, -1), (0.5, 1))
    for i in range(sides):
        r1 = ring[i]
        r2 = ring[(i + 1) % sides]

        nx = (r1[0] + r2[0]) / 2
        ny = (r1[1] + r2[1]) / 2
        length_n = math.sqrt(nx * nx + ny * ny)
        if length_n > 0:
            nx, ny = nx / length_n, ny / length_n

        i1 = mesh.add_vertex(r1, (nx, ny, -0.5), (i / sides, 0.5))
        i2 = mesh.add_vertex(r2, (nx, ny, -0.5), ((i + 1) / sides, 0.5))
        mesh.add_tri(back_idx, i2, i1)

    return mesh


def _create_glass_shard(p: ProjectileParams) -> MeshData:
    """Create irregular glass shard."""
    mesh = MeshData()
    length = p.length
    width = p.width

    # Asymmetric shard shape
    verts = [
        (0, 0, length * 0.5),           # Tip
        (-width * 0.3, width * 0.2, 0),  # Left
        (width * 0.4, width * 0.15, 0),  # Right
        (0, -width * 0.25, -length * 0.3),  # Bottom back
    ]

    # Create 4 triangular faces (tetrahedron-ish)
    faces = [
        (0, 1, 2),  # Front
        (0, 2, 3),  # Right
        (0, 3, 1),  # Left
        (1, 3, 2),  # Back
    ]

    for face in faces:
        v0, v1, v2 = verts[face[0]], verts[face[1]], verts[face[2]]

        # Calculate face normal
        ax, ay, az = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
        bx, by, bz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
        nx = ay * bz - az * by
        ny = az * bx - ax * bz
        nz = ax * by - ay * bx
        length_n = math.sqrt(nx * nx + ny * ny + nz * nz)
        if length_n > 0:
            nx, ny, nz = nx / length_n, ny / length_n, nz / length_n

        i0 = mesh.add_vertex(v0, (nx, ny, nz), (0.5, 0))
        i1 = mesh.add_vertex(v1, (nx, ny, nz), (0, 1))
        i2 = mesh.add_vertex(v2, (nx, ny, nz), (1, 1))
        mesh.add_tri(i0, i1, i2)

    return mesh


def _create_ice_shard(p: ProjectileParams) -> MeshData:
    """Create ice shard with sharp edges."""
    from .primitives import create_prism

    mesh = create_prism(p.width * 0.5, p.length, sides=3)
    mesh.rotate(math.pi / 2, 0, 0)  # Point forward
    return mesh


def create_orb_projectile(
    params: ProjectileParams = None,
    orb_type: str = "energy",
) -> MeshData:
    """
    Create an orb/sphere projectile.

    Args:
        params: Projectile parameters
        orb_type: "energy", "plasma", "magic"
    """
    p = params or ProjectileParams()
    from .primitives import create_sphere, create_torus

    if orb_type == "energy":
        return create_sphere(p.width * 0.5, segments=p.segments)
    elif orb_type == "plasma":
        # Sphere with ring
        meshes = []
        core = create_sphere(p.width * 0.4, segments=p.segments)
        meshes.append(core)

        ring = create_torus(p.width * 0.5, p.width * 0.08, p.segments, p.segments // 2)
        meshes.append(ring)

        return merge_meshes(meshes)
    else:  # magic
        # Multiple overlapping spheres
        meshes = []
        core = create_sphere(p.width * 0.35, segments=p.segments)
        meshes.append(core)

        for i in range(3):
            theta = 2 * math.pi * i / 3
            orbit = create_sphere(p.width * 0.15, segments=p.segments // 2)
            orbit.translate(
                p.width * 0.4 * math.cos(theta),
                p.width * 0.4 * math.sin(theta),
                0
            )
            meshes.append(orbit)

        return merge_meshes(meshes)


def create_beam_projectile(
    params: ProjectileParams = None,
    beam_type: str = "laser",
) -> MeshData:
    """
    Create a beam/ray projectile.

    Args:
        params: Projectile parameters
        beam_type: "laser", "lightning", "energy"
    """
    p = params or ProjectileParams()

    if beam_type == "laser":
        from .primitives import create_cylinder
        mesh = create_cylinder(p.width * 0.3, p.length, segments=p.segments, caps=True)
        mesh.rotate(math.pi / 2, 0, 0)
        return mesh
    elif beam_type == "lightning":
        return _create_lightning_beam(p)
    else:  # energy
        from .primitives import create_capsule
        mesh = create_capsule(p.width * 0.3, p.length, segments=p.segments)
        mesh.rotate(math.pi / 2, 0, 0)
        return mesh


def _create_lightning_beam(p: ProjectileParams) -> MeshData:
    """Create jagged lightning bolt."""
    mesh = MeshData()
    width = p.width * 0.15
    segments = p.trail_segments * 2

    # Create zigzag path
    points = []
    for i in range(segments + 1):
        z = -p.length * 0.5 + p.length * i / segments
        offset = 0 if i % 2 == 0 else (width * 2 if i % 4 == 1 else -width * 2)
        points.append((offset, 0, z))

    # Create rectangular cross-section along path
    for i in range(len(points) - 1):
        p1, p2 = points[i], points[i + 1]

        # Direction
        dx = p2[0] - p1[0]
        dz = p2[2] - p1[2]
        length_d = math.sqrt(dx * dx + dz * dz)
        if length_d > 0:
            dx, dz = dx / length_d, dz / length_d

        # Perpendicular
        px, pz = -dz * width, dx * width

        # Create quad
        v0 = (p1[0] + px, p1[1] + width, p1[2] + pz)
        v1 = (p1[0] - px, p1[1] + width, p1[2] - pz)
        v2 = (p2[0] + px, p2[1] + width, p2[2] + pz)
        v3 = (p2[0] - px, p2[1] + width, p2[2] - pz)

        i0 = mesh.add_vertex(v0, (0, 1, 0), (0, i / segments))
        i1 = mesh.add_vertex(v1, (0, 1, 0), (1, i / segments))
        i2 = mesh.add_vertex(v2, (0, 1, 0), (0, (i + 1) / segments))
        i3 = mesh.add_vertex(v3, (0, 1, 0), (1, (i + 1) / segments))

        mesh.add_tri(i0, i1, i2)
        mesh.add_tri(i2, i1, i3)

    return mesh


def create_bullet_projectile(
    params: ProjectileParams = None,
    bullet_type: str = "standard",
) -> MeshData:
    """
    Create a bullet projectile.

    Args:
        params: Projectile parameters
        bullet_type: "standard", "tracer", "heavy"
    """
    p = params or ProjectileParams()
    from .primitives import create_capsule, create_cylinder, create_sphere

    if bullet_type == "standard":
        mesh = create_capsule(p.width * 0.25, p.length * 0.7, segments=p.segments)
        mesh.rotate(math.pi / 2, 0, 0)
        return mesh
    elif bullet_type == "tracer":
        meshes = []

        # Bullet head
        head = create_sphere(p.width * 0.25, segments=p.segments)
        head.translate(0, 0, p.length * 0.3)
        meshes.append(head)

        # Trail
        trail = create_cylinder(p.width * 0.15, p.length * 0.5, segments=p.segments)
        trail.rotate(math.pi / 2, 0, 0)
        meshes.append(trail)

        return merge_meshes(meshes)
    else:  # heavy
        meshes = []

        # Large round head
        head = create_sphere(p.width * 0.4, segments=p.segments)
        head.translate(0, 0, p.length * 0.25)
        meshes.append(head)

        # Body
        body = create_cylinder(p.width * 0.35, p.length * 0.5, segments=p.segments)
        body.rotate(math.pi / 2, 0, 0)
        body.translate(0, 0, -p.length * 0.1)
        meshes.append(body)

        return merge_meshes(meshes)


def create_missile_projectile(
    params: ProjectileParams = None,
    missile_type: str = "standard",
) -> MeshData:
    """
    Create a missile projectile.

    Args:
        params: Projectile parameters
        missile_type: "standard", "homing", "cluster"
    """
    p = params or ProjectileParams()
    from .primitives import create_cylinder, create_cone, create_box

    meshes = []

    # Main body
    body = create_cylinder(p.width * 0.25, p.length * 0.6, segments=p.segments)
    body.rotate(math.pi / 2, 0, 0)
    meshes.append(body)

    # Nose cone
    nose = create_cone(p.width * 0.25, p.length * 0.25, segments=p.segments)
    nose.rotate(-math.pi / 2, 0, 0)
    nose.translate(0, 0, p.length * 0.4)
    meshes.append(nose)

    # Fins
    fin_count = 4 if missile_type != "cluster" else 6
    for i in range(fin_count):
        theta = 2 * math.pi * i / fin_count
        fin = create_box(p.width * 0.02, p.width * 0.3, p.length * 0.2)
        fin.translate(
            p.width * 0.35 * math.cos(theta),
            p.width * 0.35 * math.sin(theta),
            -p.length * 0.25
        )
        meshes.append(fin)

    if missile_type == "homing":
        # Add sensor dome
        from .primitives import create_sphere
        sensor = create_sphere(p.width * 0.15, segments=p.segments // 2)
        sensor.translate(0, 0, p.length * 0.5)
        meshes.append(sensor)

    return merge_meshes(meshes)
