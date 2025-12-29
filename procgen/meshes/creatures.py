"""
Creature mesh generator for ZX console.

Generates organic underwater creatures for Lumina Depths.
"""

import math
from typing import Optional, List
from .primitives import MeshData, create_sphere, create_cylinder, create_prism, merge_meshes, apply_noise
from procgen.core import UniversalStyleParams


def generate_creature(
    style: UniversalStyleParams,
    preset: Optional[dict] = None,
    creature_type: str = "jellyfish",
) -> MeshData:
    """
    Generate an organic creature mesh.

    Args:
        style: Style tokens from game config
        preset: Optional preset from CREATURE_PRESETS
        creature_type: "jellyfish", "fish", "eel", "predator"

    Returns:
        MeshData with creature mesh
    """
    curvature = style.geometry.curvature_bias

    if creature_type == "jellyfish":
        return _generate_jellyfish(style, preset)
    elif creature_type == "fish":
        return _generate_fish(style, preset)
    elif creature_type == "eel":
        return _generate_eel(style, preset)
    elif creature_type == "predator":
        return _generate_predator(style, preset)
    else:
        return _generate_jellyfish(style, preset)


def _generate_jellyfish(style: UniversalStyleParams, preset: Optional[dict]) -> MeshData:
    """Generate a jellyfish with bell and tentacles."""
    parts = []
    scale = preset.get("scale", 1.0) if preset else 1.0
    limb_count = preset.get("limb_count", 12) if preset else 12

    # Bell (dome)
    bell_radius = 0.3 * scale
    bell = create_sphere(
        radius=bell_radius,
        segments=max(8, 6 + int(style.geometry.curvature_bias * 4)),
        rings=4,
        center=(0, 0, 0.15 * scale),
    )
    # Flatten bottom half by scaling z
    flattened_verts = []
    for x, y, z in bell.vertices:
        if z < 0.15 * scale:
            z = 0.15 * scale + (z - 0.15 * scale) * 0.3
        flattened_verts.append((x, y, z))
    bell = MeshData(vertices=flattened_verts, faces=bell.faces)
    parts.append(bell)

    # Tentacles
    for i in range(limb_count):
        angle = 2 * math.pi * i / limb_count
        base_x = 0.25 * scale * math.cos(angle)
        base_y = 0.25 * scale * math.sin(angle)

        # Each tentacle is a thin tapered cylinder
        tentacle_length = (0.4 + (i % 3) * 0.15) * scale
        tentacle = create_cylinder(
            radius=0.02 * scale,
            height=tentacle_length,
            segments=4,
            caps=True,
            center=(base_x, base_y, -tentacle_length / 2),
        )
        parts.append(tentacle)

    return merge_meshes(parts)


def _generate_fish(style: UniversalStyleParams, preset: Optional[dict]) -> MeshData:
    """Generate a simple fish shape."""
    parts = []
    scale = preset.get("scale", 1.0) if preset else 1.0

    # Body (elongated sphere)
    body = create_sphere(
        radius=0.2 * scale,
        segments=6,
        rings=4,
        center=(0, 0, 0),
    )
    # Stretch along Y axis (length)
    stretched_verts = [(x, y * 2.5, z) for x, y, z in body.vertices]
    body = MeshData(vertices=stretched_verts, faces=body.faces)
    parts.append(body)

    # Tail fin
    tail = create_prism(
        sides=3,
        radius=0.15 * scale,
        height=0.05 * scale,
        taper=0.3,
        center=(0, -0.5 * scale, 0),
    )
    parts.append(tail)

    # Dorsal fin
    dorsal = create_prism(
        sides=3,
        radius=0.08 * scale,
        height=0.15 * scale,
        taper=0.2,
        center=(0, 0, 0.15 * scale),
    )
    parts.append(dorsal)

    # Side fins
    for side in [-1, 1]:
        side_fin = create_prism(
            sides=3,
            radius=0.08 * scale,
            height=0.02 * scale,
            taper=0.5,
            center=(side * 0.15 * scale, 0.1 * scale, 0),
        )
        parts.append(side_fin)

    return merge_meshes(parts)


def _generate_eel(style: UniversalStyleParams, preset: Optional[dict]) -> MeshData:
    """Generate an eel/serpent creature."""
    parts = []
    scale = preset.get("scale", 1.0) if preset else 1.0

    # Body segments along a curve
    num_segments = 8
    segment_length = 0.15 * scale
    segment_radius = 0.06 * scale

    for i in range(num_segments):
        t = i / (num_segments - 1)
        # S-curve along Y
        y = (t - 0.5) * 1.2 * scale
        x = math.sin(t * math.pi * 2) * 0.1 * scale
        z = 0

        # Taper radius toward tail
        radius = segment_radius * (1.0 - t * 0.5)

        segment = create_cylinder(
            radius=radius,
            height=segment_length,
            segments=6,
            caps=(i == 0 or i == num_segments - 1),
            center=(x, y, z),
        )
        parts.append(segment)

    # Head (larger segment at front)
    head = create_sphere(
        radius=0.08 * scale,
        segments=6,
        rings=4,
        center=(0, 0.6 * scale, 0),
    )
    parts.append(head)

    return merge_meshes(parts)


def _generate_predator(style: UniversalStyleParams, preset: Optional[dict]) -> MeshData:
    """Generate an angular predator creature."""
    parts = []
    scale = preset.get("scale", 1.0) if preset else 1.0
    limb_count = preset.get("limb_count", 6) if preset else 6

    # Angular body (using prism instead of sphere)
    body = create_prism(
        sides=6,
        radius=0.25 * scale,
        height=0.4 * scale,
        taper=0.6,
        center=(0, 0, 0.2 * scale),
    )
    parts.append(body)

    # Head (forward-pointing)
    head = create_prism(
        sides=4,
        radius=0.12 * scale,
        height=0.25 * scale,
        taper=0.2,
        center=(0, 0.3 * scale, 0.2 * scale),
    )
    parts.append(head)

    # Limbs/appendages
    for i in range(limb_count):
        angle = 2 * math.pi * i / limb_count
        offset_x = 0.2 * scale * math.cos(angle)
        offset_y = 0.2 * scale * math.sin(angle)

        limb = create_prism(
            sides=3,
            radius=0.04 * scale,
            height=0.2 * scale,
            taper=0.1,
            center=(offset_x, offset_y, 0.1 * scale),
        )
        parts.append(limb)

    return merge_meshes(parts)


def generate_coral(
    style: UniversalStyleParams,
    coral_type: str = "branching",
    scale: float = 1.0,
    seed: int = 42,
) -> MeshData:
    """Generate coral formations."""
    import random
    random.seed(seed)

    parts = []

    if coral_type == "branching":
        # Main stem
        stem = create_cylinder(
            radius=0.08 * scale,
            height=0.4 * scale,
            segments=6,
            center=(0, 0, 0.2 * scale),
        )
        parts.append(stem)

        # Branches
        for i in range(5):
            angle = 2 * math.pi * i / 5 + random.random() * 0.5
            height = 0.2 * scale + random.random() * 0.3 * scale
            branch_length = 0.15 * scale + random.random() * 0.1 * scale

            branch = create_cylinder(
                radius=0.03 * scale,
                height=branch_length,
                segments=4,
                center=(
                    0.1 * scale * math.cos(angle),
                    0.1 * scale * math.sin(angle),
                    height,
                ),
            )
            parts.append(branch)

    elif coral_type == "brain":
        # Bumpy sphere
        base = create_sphere(
            radius=0.3 * scale,
            segments=8,
            rings=6,
            center=(0, 0, 0.15 * scale),
        )
        # Apply noise for brain texture
        base = apply_noise(base, amplitude=0.05 * scale, seed=seed)
        parts.append(base)

    elif coral_type == "fan":
        # Flat fan shape
        fan = create_prism(
            sides=8,
            radius=0.4 * scale,
            height=0.02 * scale,
            taper=0.8,
            center=(0, 0, 0.3 * scale),
        )
        # Flatten
        flat_verts = [(x, y * 0.3, z) for x, y, z in fan.vertices]
        fan = MeshData(vertices=flat_verts, faces=fan.faces)
        parts.append(fan)

    return merge_meshes(parts)
