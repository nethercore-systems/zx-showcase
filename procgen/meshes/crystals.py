"""
Crystal mesh generator for ZX console.

Generates faceted crystalline meshes for Prism Survivors.
"""

import math
from typing import Optional, List, Tuple
from .primitives import MeshData, create_prism, merge_meshes
from procgen.core import UniversalStyleParams, SymmetryMode


def generate_crystal(
    style: UniversalStyleParams,
    crystal_type: str = "shard",
    size: float = 1.0,
    seed: int = 42,
) -> MeshData:
    """
    Generate a crystal mesh.

    Args:
        style: Style tokens from game config
        crystal_type: "shard", "cluster", "pillar", "gem"
        size: Overall size multiplier
        seed: Random seed for procedural variation

    Returns:
        MeshData with crystal mesh
    """
    import random
    random.seed(seed)

    symmetry = style.geometry.symmetry_mode

    if crystal_type == "shard":
        return _generate_shard(size, symmetry)
    elif crystal_type == "cluster":
        return _generate_cluster(size, symmetry, seed)
    elif crystal_type == "pillar":
        return _generate_pillar(size, symmetry)
    elif crystal_type == "gem":
        return _generate_gem(size, symmetry)
    else:
        return _generate_shard(size, symmetry)


def _generate_shard(size: float, symmetry: SymmetryMode) -> MeshData:
    """Generate a single crystal shard."""
    # Get number of sides from symmetry
    if symmetry == SymmetryMode.RADIAL_6:
        sides = 6
    elif symmetry == SymmetryMode.RADIAL_4:
        sides = 4
    elif symmetry == SymmetryMode.RADIAL_8:
        sides = 8
    else:
        sides = 5  # Default pentagon

    return create_prism(
        sides=sides,
        radius=0.2 * size,
        height=0.8 * size,
        taper=0.05,  # Sharp point
        center=(0, 0, 0.4 * size),
    )


def _generate_cluster(size: float, symmetry: SymmetryMode, seed: int) -> MeshData:
    """Generate a cluster of crystals."""
    import random
    random.seed(seed)

    parts = []

    # Central crystal
    central = _generate_shard(size, symmetry)
    parts.append(central)

    # Surrounding crystals (3-6 based on symmetry)
    if symmetry == SymmetryMode.RADIAL_6:
        count = 6
    elif symmetry == SymmetryMode.RADIAL_4:
        count = 4
    else:
        count = random.randint(3, 5)

    for i in range(count):
        angle = 2 * math.pi * i / count + random.random() * 0.3
        distance = (0.15 + random.random() * 0.1) * size
        height_offset = random.random() * 0.2 * size - 0.1 * size
        sub_size = (0.4 + random.random() * 0.3) * size

        # Create offset crystal
        sub_crystal = create_prism(
            sides=random.choice([4, 5, 6]),
            radius=0.12 * sub_size,
            height=0.5 * sub_size,
            taper=0.1,
            center=(
                math.cos(angle) * distance,
                math.sin(angle) * distance,
                0.25 * sub_size + height_offset,
            ),
        )
        parts.append(sub_crystal)

    return merge_meshes(parts)


def _generate_pillar(size: float, symmetry: SymmetryMode) -> MeshData:
    """Generate a tall crystal pillar."""
    if symmetry == SymmetryMode.RADIAL_6:
        sides = 6
    elif symmetry == SymmetryMode.RADIAL_4:
        sides = 4
    else:
        sides = 6

    return create_prism(
        sides=sides,
        radius=0.3 * size,
        height=2.0 * size,
        taper=0.7,  # Slight taper
        center=(0, 0, 1.0 * size),
    )


def _generate_gem(size: float, symmetry: SymmetryMode) -> MeshData:
    """Generate a cut gemstone shape (double pyramid)."""
    parts = []

    if symmetry == SymmetryMode.RADIAL_6:
        sides = 6
    elif symmetry == SymmetryMode.RADIAL_8:
        sides = 8
    else:
        sides = 5

    # Top pyramid (crown)
    crown = create_prism(
        sides=sides,
        radius=0.3 * size,
        height=0.25 * size,
        taper=0.0,  # Point
        center=(0, 0, 0.125 * size),
    )
    parts.append(crown)

    # Bottom pyramid (pavilion)
    pavilion = create_prism(
        sides=sides,
        radius=0.3 * size,
        height=0.35 * size,
        taper=0.0,  # Point
        center=(0, 0, -0.175 * size),
    )
    # Flip pavilion (need to invert vertices z)
    flipped_verts = [(x, y, -z) for x, y, z in pavilion.vertices]
    pavilion = MeshData(vertices=flipped_verts, faces=pavilion.faces)
    parts.append(pavilion)

    return merge_meshes(parts)


def generate_xp_gem(size: float = 0.2) -> MeshData:
    """Generate an XP gem pickup for Prism Survivors."""
    parts = []

    # Simple diamond shape (octahedron approximation)
    # Top pyramid
    top = create_prism(
        sides=4,
        radius=size * 0.5,
        height=size * 0.4,
        taper=0.0,
        center=(0, 0, size * 0.2),
    )
    parts.append(top)

    # Bottom pyramid (inverted)
    bottom = create_prism(
        sides=4,
        radius=size * 0.5,
        height=size * 0.4,
        taper=0.0,
        center=(0, 0, -size * 0.2),
    )
    # Flip
    flipped_verts = [(x, y, -z) for x, y, z in bottom.vertices]
    bottom = MeshData(vertices=flipped_verts, faces=bottom.faces)
    parts.append(bottom)

    return merge_meshes(parts)


def generate_projectile(
    projectile_type: str = "shard",
    size: float = 0.15,
) -> MeshData:
    """Generate a projectile mesh for attacks."""
    if projectile_type == "shard":
        return create_prism(
            sides=3,
            radius=size * 0.3,
            height=size * 1.5,
            taper=0.05,
            center=(0, 0, 0),
        )
    elif projectile_type == "orb":
        from .primitives import create_sphere
        return create_sphere(
            radius=size * 0.4,
            segments=6,
            rings=4,
            center=(0, 0, 0),
        )
    elif projectile_type == "beam":
        from .primitives import create_cylinder
        return create_cylinder(
            radius=size * 0.1,
            height=size * 2.0,
            segments=4,
            center=(0, 0, 0),
        )
    else:
        return create_prism(
            sides=4,
            radius=size * 0.2,
            height=size,
            taper=0.1,
            center=(0, 0, 0),
        )
