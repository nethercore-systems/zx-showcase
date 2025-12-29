"""
Humanoid mesh generator for ZX console.

Generates low-poly characters suitable for heroes, enemies, and NPCs.
Output respects style tokens for geometry preferences.
"""

from typing import Optional
from .primitives import MeshData, create_box, create_sphere, create_cylinder, create_prism, merge_meshes
from procgen.core import UniversalStyleParams, PolyBudget


def generate_humanoid(
    style: UniversalStyleParams,
    preset: Optional[dict] = None,
    size_class: str = "medium",
) -> MeshData:
    """
    Generate a humanoid character mesh.

    Args:
        style: Style tokens from game config
        preset: Optional preset overrides (from HERO_PRESETS, etc.)
        size_class: "small", "medium", or "large"

    Returns:
        MeshData with combined humanoid mesh
    """
    # Get polygon budget
    budget_key = f"character_{size_class}"
    max_tris = getattr(style.poly_budget, budget_key, 500)

    # Calculate detail level based on budget
    detail = _calculate_detail_level(max_tris)

    # Apply geometry style
    curvature = style.geometry.curvature_bias
    symmetry = style.geometry.symmetry_mode

    # Extract scale from preset if provided
    scale = preset.get("scale", 1.0) if preset else 1.0

    # Generate body parts
    parts = []

    # Torso
    torso = _generate_torso(detail, curvature, scale)
    parts.append(torso)

    # Head
    head = _generate_head(detail, curvature, scale)
    parts.append(head)

    # Arms (symmetric)
    left_arm = _generate_arm(detail, curvature, scale, side=-1)
    right_arm = _generate_arm(detail, curvature, scale, side=1)
    parts.append(left_arm)
    parts.append(right_arm)

    # Legs
    left_leg = _generate_leg(detail, curvature, scale, side=-1)
    right_leg = _generate_leg(detail, curvature, scale, side=1)
    parts.append(left_leg)
    parts.append(right_leg)

    # Armor/detail if budget allows
    if preset and preset.get("armored", False) and max_tris > 600:
        armor = _generate_armor(detail, scale)
        parts.append(armor)

    return merge_meshes(parts)


def _calculate_detail_level(max_tris: int) -> int:
    """Calculate detail level from triangle budget."""
    if max_tris < 300:
        return 1  # Very low poly
    elif max_tris < 600:
        return 2  # Low poly
    elif max_tris < 1000:
        return 3  # Medium
    else:
        return 4  # Higher detail


def _generate_torso(detail: int, curvature: float, scale: float) -> MeshData:
    """Generate torso mesh."""
    # Base dimensions
    width = 0.4 * scale
    height = 0.5 * scale
    depth = 0.25 * scale

    if curvature < 0.3:
        # Angular torso (box)
        return create_box(width, height, depth, center=(0, 0, height / 2))
    else:
        # More organic torso (tapered prism)
        segments = 4 + detail
        return create_prism(
            sides=segments,
            radius=width / 2,
            height=height,
            taper=0.8,
            center=(0, 0, height / 2),
        )


def _generate_head(detail: int, curvature: float, scale: float) -> MeshData:
    """Generate head mesh."""
    head_radius = 0.12 * scale
    head_z = 0.75 * scale

    if curvature < 0.3:
        # Angular head (box)
        return create_box(
            head_radius * 2, head_radius * 2.2, head_radius * 1.8,
            center=(0, 0, head_z)
        )
    else:
        # Rounded head (sphere)
        segments = max(4, 4 + detail)
        rings = max(3, 2 + detail)
        return create_sphere(
            radius=head_radius,
            segments=segments,
            rings=rings,
            center=(0, 0, head_z),
        )


def _generate_arm(detail: int, curvature: float, scale: float, side: int) -> MeshData:
    """Generate arm mesh."""
    arm_x = 0.3 * scale * side
    arm_z = 0.4 * scale
    arm_length = 0.35 * scale
    arm_radius = 0.06 * scale

    if curvature < 0.3:
        # Angular arm (box)
        return create_box(
            arm_radius * 2, arm_radius * 2, arm_length,
            center=(arm_x, 0, arm_z - arm_length / 2)
        )
    else:
        # Cylinder arm
        segments = max(4, 3 + detail)
        return create_cylinder(
            radius=arm_radius,
            height=arm_length,
            segments=segments,
            center=(arm_x, 0, arm_z - arm_length / 2),
        )


def _generate_leg(detail: int, curvature: float, scale: float, side: int) -> MeshData:
    """Generate leg mesh."""
    leg_x = 0.1 * scale * side
    leg_length = 0.4 * scale
    leg_radius = 0.08 * scale

    if curvature < 0.3:
        # Angular leg (box)
        return create_box(
            leg_radius * 2, leg_radius * 2, leg_length,
            center=(leg_x, 0, -leg_length / 2)
        )
    else:
        # Cylinder leg
        segments = max(4, 3 + detail)
        return create_cylinder(
            radius=leg_radius,
            height=leg_length,
            segments=segments,
            center=(leg_x, 0, -leg_length / 2),
        )


def _generate_armor(detail: int, scale: float) -> MeshData:
    """Generate armor plates for armored characters."""
    parts = []

    # Shoulder pauldrons
    pauldron_size = 0.1 * scale
    left_pauldron = create_sphere(
        radius=pauldron_size,
        segments=max(4, detail + 2),
        rings=max(3, detail),
        center=(-0.35 * scale, 0, 0.45 * scale),
    )
    right_pauldron = create_sphere(
        radius=pauldron_size,
        segments=max(4, detail + 2),
        rings=max(3, detail),
        center=(0.35 * scale, 0, 0.45 * scale),
    )
    parts.extend([left_pauldron, right_pauldron])

    # Chest plate
    chest = create_prism(
        sides=4,
        radius=0.22 * scale,
        height=0.25 * scale,
        taper=0.9,
        center=(0, 0.08 * scale, 0.35 * scale),
    )
    parts.append(chest)

    return merge_meshes(parts)


def generate_enemy(
    style: UniversalStyleParams,
    preset: Optional[dict] = None,
    tier: str = "basic",
) -> MeshData:
    """
    Generate an enemy mesh.

    Args:
        style: Style tokens from game config
        preset: Optional preset from ENEMY_PRESETS
        tier: "basic", "elite", or "boss"
    """
    # Get budget based on tier
    budget_key = f"enemy_{tier}" if tier != "basic" else "enemy_small"
    max_tris = getattr(style.poly_budget, budget_key, 200)

    detail = _calculate_detail_level(max_tris)
    curvature = style.geometry.curvature_bias
    scale = preset.get("scale", 1.0) if preset else 1.0

    parts = []

    # Enemy body (simpler than humanoid)
    if preset and preset.get("vertices"):
        # Use vertex count to determine shape complexity
        vertices = preset.get("vertices", 6)
        symmetry = preset.get("symmetry", 2)

        body = create_prism(
            sides=vertices,
            radius=0.2 * scale,
            height=0.3 * scale,
            taper=0.6,
            center=(0, 0, 0.15 * scale),
        )
        parts.append(body)
    else:
        # Default enemy body
        body = create_sphere(
            radius=0.2 * scale,
            segments=max(4, detail + 2),
            rings=max(3, detail),
            center=(0, 0, 0.15 * scale),
        )
        parts.append(body)

    # Add spikes or protrusions for elite/boss
    if tier == "elite" or tier == "boss":
        spike_count = 4 if tier == "elite" else 6
        for i in range(spike_count):
            import math
            angle = 2 * math.pi * i / spike_count
            spike_x = 0.15 * scale * math.cos(angle)
            spike_y = 0.15 * scale * math.sin(angle)
            spike = create_prism(
                sides=3,
                radius=0.05 * scale,
                height=0.15 * scale,
                taper=0.1,
                center=(spike_x, spike_y, 0.25 * scale),
            )
            parts.append(spike)

    return merge_meshes(parts)
