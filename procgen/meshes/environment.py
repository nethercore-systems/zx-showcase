"""
Environment mesh generator for ZX console.

Generates props, barriers, and environment pieces for all games.
"""

import math
from typing import Optional
from .primitives import MeshData, create_box, create_cylinder, create_prism, create_sphere, merge_meshes
from procgen.core import UniversalStyleParams


def generate_prop(
    style: UniversalStyleParams,
    prop_type: str = "barrier",
    size: float = 1.0,
) -> MeshData:
    """
    Generate an environment prop.

    Args:
        style: Style tokens from game config
        prop_type: "barrier", "building", "crate", "pillar", "sign"
        size: Overall size multiplier

    Returns:
        MeshData with prop mesh
    """
    curvature = style.geometry.curvature_bias

    if prop_type == "barrier":
        return _generate_barrier(size, curvature)
    elif prop_type == "building":
        return _generate_building(size, curvature)
    elif prop_type == "crate":
        return _generate_crate(size)
    elif prop_type == "pillar":
        return _generate_pillar(size, curvature)
    elif prop_type == "sign":
        return _generate_sign(size)
    else:
        return _generate_barrier(size, curvature)


def _generate_barrier(size: float, curvature: float) -> MeshData:
    """Generate a barrier/wall section."""
    if curvature < 0.3:
        # Angular barrier
        return create_box(
            width=0.2 * size,
            height=1.2 * size,
            depth=2.0 * size,
            center=(0, 0, 0.6 * size),
        )
    else:
        # Rounded barrier
        return create_cylinder(
            radius=0.15 * size,
            height=1.2 * size,
            segments=8,
            center=(0, 0, 0.6 * size),
        )


def _generate_building(size: float, curvature: float) -> MeshData:
    """Generate a simple building shape for backgrounds."""
    parts = []

    # Base building
    base = create_box(
        width=2.0 * size,
        height=4.0 * size,
        depth=1.5 * size,
        center=(0, 0, 2.0 * size),
    )
    parts.append(base)

    # Optional: Add levels/windows suggestion with smaller boxes
    for level in range(3):
        level_z = 0.8 * size + level * 1.2 * size
        # Window strip (indentation)
        window_strip = create_box(
            width=1.8 * size,
            height=0.1 * size,
            depth=1.6 * size,
            center=(0, 0, level_z),
        )
        parts.append(window_strip)

    return merge_meshes(parts)


def _generate_crate(size: float) -> MeshData:
    """Generate a simple crate prop."""
    return create_box(
        width=0.8 * size,
        height=0.8 * size,
        depth=0.8 * size,
        center=(0, 0, 0.4 * size),
    )


def _generate_pillar(size: float, curvature: float) -> MeshData:
    """Generate a pillar/column."""
    parts = []

    # Main shaft
    if curvature < 0.3:
        # Square pillar
        shaft = create_box(
            width=0.4 * size,
            height=3.0 * size,
            depth=0.4 * size,
            center=(0, 0, 1.5 * size),
        )
    else:
        # Round pillar
        shaft = create_cylinder(
            radius=0.2 * size,
            height=3.0 * size,
            segments=8,
            center=(0, 0, 1.5 * size),
        )
    parts.append(shaft)

    # Base
    base = create_box(
        width=0.6 * size,
        height=0.15 * size,
        depth=0.6 * size,
        center=(0, 0, 0.075 * size),
    )
    parts.append(base)

    # Capital
    capital = create_box(
        width=0.5 * size,
        height=0.1 * size,
        depth=0.5 * size,
        center=(0, 0, 3.05 * size),
    )
    parts.append(capital)

    return merge_meshes(parts)


def _generate_sign(size: float) -> MeshData:
    """Generate a sign/billboard prop."""
    parts = []

    # Post
    post = create_cylinder(
        radius=0.05 * size,
        height=2.0 * size,
        segments=6,
        center=(0, 0, 1.0 * size),
    )
    parts.append(post)

    # Sign board
    board = create_box(
        width=1.2 * size,
        height=0.1 * size,
        depth=0.6 * size,
        center=(0, 0, 1.8 * size),
    )
    parts.append(board)

    return merge_meshes(parts)


def generate_track_segment(
    style: UniversalStyleParams,
    segment_type: str = "straight",
    width: float = 12.0,
    length: float = 10.0,
) -> MeshData:
    """
    Generate a track segment for racing games.

    Args:
        style: Style tokens
        segment_type: "straight", "curve_left", "curve_right", "chicane"
        width: Track width
        length: Segment length
    """
    parts = []

    # Track surface (flat plane)
    track_surface = create_box(
        width=width,
        height=0.1,
        depth=length,
        center=(0, 0, -0.05),
    )
    parts.append(track_surface)

    # Side barriers
    barrier_height = 1.2
    barrier_width = 0.3

    left_barrier = create_box(
        width=barrier_width,
        height=barrier_height,
        depth=length,
        center=(-width / 2 - barrier_width / 2, 0, barrier_height / 2),
    )
    right_barrier = create_box(
        width=barrier_width,
        height=barrier_height,
        depth=length,
        center=(width / 2 + barrier_width / 2, 0, barrier_height / 2),
    )
    parts.extend([left_barrier, right_barrier])

    return merge_meshes(parts)


def generate_checkpoint_gate(
    style: UniversalStyleParams,
    width: float = 12.0,
    height: float = 4.0,
) -> MeshData:
    """Generate a checkpoint gate for racing."""
    parts = []

    # Left post
    left_post = create_cylinder(
        radius=0.3,
        height=height,
        segments=6,
        center=(-width / 2, 0, height / 2),
    )
    parts.append(left_post)

    # Right post
    right_post = create_cylinder(
        radius=0.3,
        height=height,
        segments=6,
        center=(width / 2, 0, height / 2),
    )
    parts.append(right_post)

    # Top bar
    top_bar = create_cylinder(
        radius=0.2,
        height=width,
        segments=6,
        center=(0, 0, height),
    )
    # Rotate 90 degrees (swap x and width direction)
    rotated_verts = [(z, y, x + height) for x, y, z in top_bar.vertices]
    top_bar = MeshData(vertices=rotated_verts, faces=top_bar.faces)
    parts.append(top_bar)

    return merge_meshes(parts)


def generate_health_pickup(size: float = 0.3) -> MeshData:
    """Generate a health pickup prop."""
    parts = []

    # Cross shape for health
    # Horizontal bar
    h_bar = create_box(0.25 * size, 0.08 * size, 0.08 * size, center=(0, 0, 0.15 * size))
    parts.append(h_bar)

    # Vertical bar
    v_bar = create_box(0.08 * size, 0.25 * size, 0.08 * size, center=(0, 0, 0.15 * size))
    parts.append(v_bar)

    return merge_meshes(parts)


def generate_powerup(powerup_type: str = "generic", size: float = 0.3) -> MeshData:
    """Generate a powerup mesh."""
    if powerup_type == "speed":
        # Arrow/lightning bolt shape
        return create_prism(
            sides=3,
            radius=size * 0.4,
            height=size * 0.8,
            taper=0.0,
            center=(0, 0, size * 0.4),
        )
    elif powerup_type == "shield":
        # Shield dome
        return create_sphere(
            radius=size * 0.4,
            segments=8,
            rings=4,
            center=(0, 0, size * 0.3),
        )
    elif powerup_type == "weapon":
        # Star shape approximation (octagon)
        return create_prism(
            sides=8,
            radius=size * 0.35,
            height=size * 0.15,
            taper=0.0,
            center=(0, 0, size * 0.3),
        )
    else:
        # Generic cube
        return create_box(
            size * 0.5, size * 0.5, size * 0.5,
            center=(0, 0, size * 0.25),
        )
