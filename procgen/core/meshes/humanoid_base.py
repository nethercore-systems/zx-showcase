"""
Humanoid mesh and skeleton generators.

Provides base humanoid templates for characters and enemies.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from ...lib.mesh_utils import MeshData


@dataclass
class HumanoidParams:
    """Parameters for humanoid generation."""
    height: float = 1.8
    body_width: float = 0.4
    leg_length: float = 0.9
    arm_length: float = 0.7
    head_size: float = 0.25
    shoulder_width: float = 0.5
    hip_width: float = 0.35
    chest_depth: float = 0.25
    limb_segments: int = 8
    body_segments: int = 6


@dataclass
class Bone:
    """Represents a bone in the skeleton."""
    name: str
    head: Tuple[float, float, float]
    tail: Tuple[float, float, float]
    parent: Optional[str] = None


def create_humanoid_skeleton(params: HumanoidParams = None) -> List[Bone]:
    """
    Create a humanoid skeleton (bone hierarchy).

    Args:
        params: Humanoid parameters

    Returns:
        List of Bone objects defining the skeleton
    """
    p = params or HumanoidParams()

    hip_height = p.leg_length
    spine_height = hip_height + p.body_width * 0.5
    chest_height = spine_height + p.body_width * 0.4
    neck_height = chest_height + p.body_width * 0.3
    head_top = neck_height + p.head_size

    bones = [
        # Spine
        Bone("root", (0, hip_height, 0), (0, hip_height, 0), None),
        Bone("spine", (0, hip_height, 0), (0, spine_height, 0), "root"),
        Bone("chest", (0, spine_height, 0), (0, chest_height, 0), "spine"),
        Bone("neck", (0, chest_height, 0), (0, neck_height, 0), "chest"),
        Bone("head", (0, neck_height, 0), (0, head_top, 0), "neck"),

        # Left leg
        Bone("hip.L", (p.hip_width / 2, hip_height, 0),
             (p.hip_width / 2, hip_height * 0.5, 0), "root"),
        Bone("knee.L", (p.hip_width / 2, hip_height * 0.5, 0),
             (p.hip_width / 2, 0.1, 0), "hip.L"),
        Bone("foot.L", (p.hip_width / 2, 0.1, 0),
             (p.hip_width / 2, 0, 0.15), "knee.L"),

        # Right leg
        Bone("hip.R", (-p.hip_width / 2, hip_height, 0),
             (-p.hip_width / 2, hip_height * 0.5, 0), "root"),
        Bone("knee.R", (-p.hip_width / 2, hip_height * 0.5, 0),
             (-p.hip_width / 2, 0.1, 0), "hip.R"),
        Bone("foot.R", (-p.hip_width / 2, 0.1, 0),
             (-p.hip_width / 2, 0, 0.15), "knee.R"),

        # Left arm
        Bone("shoulder.L", (p.shoulder_width / 2, chest_height, 0),
             (p.shoulder_width / 2 + 0.1, chest_height - 0.05, 0), "chest"),
        Bone("upper_arm.L", (p.shoulder_width / 2 + 0.1, chest_height - 0.05, 0),
             (p.shoulder_width / 2 + p.arm_length * 0.5, chest_height - 0.3, 0), "shoulder.L"),
        Bone("forearm.L", (p.shoulder_width / 2 + p.arm_length * 0.5, chest_height - 0.3, 0),
             (p.shoulder_width / 2 + p.arm_length, chest_height - 0.6, 0), "upper_arm.L"),
        Bone("hand.L", (p.shoulder_width / 2 + p.arm_length, chest_height - 0.6, 0),
             (p.shoulder_width / 2 + p.arm_length + 0.1, chest_height - 0.7, 0), "forearm.L"),

        # Right arm
        Bone("shoulder.R", (-p.shoulder_width / 2, chest_height, 0),
             (-p.shoulder_width / 2 - 0.1, chest_height - 0.05, 0), "chest"),
        Bone("upper_arm.R", (-p.shoulder_width / 2 - 0.1, chest_height - 0.05, 0),
             (-p.shoulder_width / 2 - p.arm_length * 0.5, chest_height - 0.3, 0), "shoulder.R"),
        Bone("forearm.R", (-p.shoulder_width / 2 - p.arm_length * 0.5, chest_height - 0.3, 0),
             (-p.shoulder_width / 2 - p.arm_length, chest_height - 0.6, 0), "upper_arm.R"),
        Bone("hand.R", (-p.shoulder_width / 2 - p.arm_length, chest_height - 0.6, 0),
             (-p.shoulder_width / 2 - p.arm_length - 0.1, chest_height - 0.7, 0), "forearm.R"),
    ]

    return bones


def create_humanoid_mesh(
    params: HumanoidParams = None,
    style: str = "blocky",
) -> MeshData:
    """
    Create a humanoid mesh.

    Args:
        params: Humanoid parameters
        style: Mesh style - "blocky", "rounded", or "angular"

    Returns:
        MeshData for the humanoid
    """
    p = params or HumanoidParams()
    mesh = MeshData()

    hip_height = p.leg_length
    chest_height = hip_height + p.body_width

    if style == "blocky":
        # Blocky/voxel style humanoid
        mesh = _create_blocky_humanoid(p, hip_height, chest_height)
    elif style == "rounded":
        # Smooth rounded humanoid
        mesh = _create_rounded_humanoid(p, hip_height, chest_height)
    else:
        # Angular/faceted style
        mesh = _create_angular_humanoid(p, hip_height, chest_height)

    return mesh


def _create_blocky_humanoid(
    p: HumanoidParams,
    hip_height: float,
    chest_height: float,
) -> MeshData:
    """Create blocky/voxel style humanoid."""
    from .primitives import create_box

    meshes = []

    # Torso
    torso = create_box(p.body_width, p.body_width * 0.8, p.chest_depth)
    torso.translate(0, hip_height + p.body_width * 0.4, 0)
    meshes.append(torso)

    # Head
    head = create_box(p.head_size, p.head_size, p.head_size * 0.9)
    head.translate(0, chest_height + p.head_size * 0.6, 0)
    meshes.append(head)

    # Left leg upper
    leg_thickness = p.hip_width * 0.3
    upper_leg_height = p.leg_length * 0.5
    upper_leg_l = create_box(leg_thickness, upper_leg_height, leg_thickness)
    upper_leg_l.translate(p.hip_width * 0.25, hip_height * 0.5 + upper_leg_height * 0.25, 0)
    meshes.append(upper_leg_l)

    # Left leg lower
    lower_leg_l = create_box(leg_thickness * 0.9, upper_leg_height, leg_thickness * 0.9)
    lower_leg_l.translate(p.hip_width * 0.25, upper_leg_height * 0.5, 0)
    meshes.append(lower_leg_l)

    # Right leg upper
    upper_leg_r = create_box(leg_thickness, upper_leg_height, leg_thickness)
    upper_leg_r.translate(-p.hip_width * 0.25, hip_height * 0.5 + upper_leg_height * 0.25, 0)
    meshes.append(upper_leg_r)

    # Right leg lower
    lower_leg_r = create_box(leg_thickness * 0.9, upper_leg_height, leg_thickness * 0.9)
    lower_leg_r.translate(-p.hip_width * 0.25, upper_leg_height * 0.5, 0)
    meshes.append(lower_leg_r)

    # Arms
    arm_thickness = p.body_width * 0.15
    arm_length = p.arm_length * 0.5

    # Left arm upper
    arm_l = create_box(arm_thickness, arm_length, arm_thickness)
    arm_l.translate(p.shoulder_width * 0.5 + arm_thickness * 0.5, chest_height - arm_length * 0.5, 0)
    meshes.append(arm_l)

    # Left forearm
    forearm_l = create_box(arm_thickness * 0.9, arm_length, arm_thickness * 0.9)
    forearm_l.translate(p.shoulder_width * 0.5 + arm_thickness * 0.5, chest_height - arm_length * 1.5, 0)
    meshes.append(forearm_l)

    # Right arm upper
    arm_r = create_box(arm_thickness, arm_length, arm_thickness)
    arm_r.translate(-p.shoulder_width * 0.5 - arm_thickness * 0.5, chest_height - arm_length * 0.5, 0)
    meshes.append(arm_r)

    # Right forearm
    forearm_r = create_box(arm_thickness * 0.9, arm_length, arm_thickness * 0.9)
    forearm_r.translate(-p.shoulder_width * 0.5 - arm_thickness * 0.5, chest_height - arm_length * 1.5, 0)
    meshes.append(forearm_r)

    # Merge all meshes
    from ...lib.mesh_utils import merge_meshes
    return merge_meshes(meshes)


def _create_rounded_humanoid(
    p: HumanoidParams,
    hip_height: float,
    chest_height: float,
) -> MeshData:
    """Create smooth rounded humanoid."""
    from .primitives import create_sphere, create_capsule, create_cylinder

    meshes = []

    # Torso (capsule)
    torso = create_capsule(p.body_width * 0.4, p.body_width * 0.9, segments=p.body_segments)
    torso.translate(0, hip_height + p.body_width * 0.45, 0)
    meshes.append(torso)

    # Head (sphere)
    head = create_sphere(p.head_size * 0.5, segments=p.limb_segments)
    head.translate(0, chest_height + p.head_size * 0.5, 0)
    meshes.append(head)

    # Legs (capsules)
    leg_radius = p.hip_width * 0.12
    leg_height = p.leg_length * 0.45

    for side in [-1, 1]:
        # Upper leg
        upper_leg = create_capsule(leg_radius, leg_height, segments=p.limb_segments)
        upper_leg.translate(side * p.hip_width * 0.2, hip_height * 0.55, 0)
        meshes.append(upper_leg)

        # Lower leg
        lower_leg = create_capsule(leg_radius * 0.9, leg_height, segments=p.limb_segments)
        lower_leg.translate(side * p.hip_width * 0.2, leg_height * 0.6, 0)
        meshes.append(lower_leg)

    # Arms (capsules)
    arm_radius = p.body_width * 0.08
    arm_height = p.arm_length * 0.45

    for side in [-1, 1]:
        # Upper arm
        upper_arm = create_capsule(arm_radius, arm_height, segments=p.limb_segments)
        upper_arm.translate(side * (p.shoulder_width * 0.5 + arm_radius), chest_height - arm_height * 0.5, 0)
        meshes.append(upper_arm)

        # Forearm
        forearm = create_capsule(arm_radius * 0.9, arm_height, segments=p.limb_segments)
        forearm.translate(side * (p.shoulder_width * 0.5 + arm_radius), chest_height - arm_height * 1.5, 0)
        meshes.append(forearm)

    from ...lib.mesh_utils import merge_meshes
    return merge_meshes(meshes)


def _create_angular_humanoid(
    p: HumanoidParams,
    hip_height: float,
    chest_height: float,
) -> MeshData:
    """Create angular/faceted style humanoid."""
    from .primitives import create_prism, create_pyramid

    meshes = []

    # Torso (hexagonal prism)
    torso = create_prism(p.body_width * 0.35, p.body_width * 0.8, sides=6)
    torso.translate(0, hip_height + p.body_width * 0.4, 0)
    meshes.append(torso)

    # Head (pyramid on prism)
    head_base = create_prism(p.head_size * 0.4, p.head_size * 0.6, sides=6)
    head_base.translate(0, chest_height + p.head_size * 0.3, 0)
    meshes.append(head_base)

    head_top = create_pyramid(p.head_size * 0.6, p.head_size * 0.4, sides=6)
    head_top.translate(0, chest_height + p.head_size * 0.7, 0)
    meshes.append(head_top)

    # Legs (triangular prisms)
    for side in [-1, 1]:
        leg = create_prism(p.hip_width * 0.12, p.leg_length * 0.9, sides=4)
        leg.translate(side * p.hip_width * 0.2, p.leg_length * 0.45, 0)
        meshes.append(leg)

    # Arms (triangular prisms)
    arm_height = p.arm_length * 0.8
    for side in [-1, 1]:
        arm = create_prism(p.body_width * 0.08, arm_height, sides=4)
        arm.translate(side * (p.shoulder_width * 0.5 + p.body_width * 0.08),
                      chest_height - arm_height * 0.5, 0)
        meshes.append(arm)

    from ...lib.mesh_utils import merge_meshes
    return merge_meshes(meshes)
