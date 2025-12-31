"""
Vehicle mesh generators.

Provides base vehicle chassis and wheel templates.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Optional
from ...lib.mesh_utils import MeshData, merge_meshes


@dataclass
class VehicleParams:
    """Parameters for vehicle generation."""
    length: float = 2.0
    width: float = 1.0
    height: float = 0.5
    wheel_radius: float = 0.25
    wheel_width: float = 0.15
    wheelbase: float = 1.4
    track_width: float = 0.8
    ground_clearance: float = 0.1
    body_style: str = "sport"  # sport, muscle, van, truck
    segments: int = 8


def create_wheel(
    radius: float = 0.25,
    width: float = 0.15,
    segments: int = 16,
    spoke_count: int = 5,
    has_spokes: bool = True,
) -> MeshData:
    """
    Create a vehicle wheel mesh.

    Args:
        radius: Wheel radius
        width: Wheel width (thickness)
        segments: Number of sides
        spoke_count: Number of spokes if has_spokes
        has_spokes: Whether to include spokes
    """
    mesh = MeshData()
    hw = width / 2
    hub_radius = radius * 0.3
    rim_depth = width * 0.6

    # Tire outer surface
    for i in range(segments):
        theta1 = 2 * math.pi * i / segments
        theta2 = 2 * math.pi * (i + 1) / segments

        x1 = radius * math.cos(theta1)
        y1 = radius * math.sin(theta1)
        x2 = radius * math.cos(theta2)
        y2 = radius * math.sin(theta2)

        # Outer surface normal (outward radial)
        mid_theta = (theta1 + theta2) / 2
        nx = math.cos(mid_theta)
        ny = math.sin(mid_theta)

        # Tire tread (outer surface)
        i0 = mesh.add_vertex((x1, y1, -hw), (nx, ny, 0), (i / segments, 0))
        i1 = mesh.add_vertex((x2, y2, -hw), (nx, ny, 0), ((i + 1) / segments, 0))
        i2 = mesh.add_vertex((x1, y1, hw), (nx, ny, 0), (i / segments, 1))
        i3 = mesh.add_vertex((x2, y2, hw), (nx, ny, 0), ((i + 1) / segments, 1))

        mesh.add_tri(i0, i1, i2)
        mesh.add_tri(i2, i1, i3)

    # Side walls
    for side in [-1, 1]:
        z = hw * side
        nz = side

        # Tire sidewall (outer ring to rim)
        for i in range(segments):
            theta1 = 2 * math.pi * i / segments
            theta2 = 2 * math.pi * (i + 1) / segments

            ox1 = radius * math.cos(theta1)
            oy1 = radius * math.sin(theta1)
            ox2 = radius * math.cos(theta2)
            oy2 = radius * math.sin(theta2)

            rim_radius = radius * 0.7
            ix1 = rim_radius * math.cos(theta1)
            iy1 = rim_radius * math.sin(theta1)
            ix2 = rim_radius * math.cos(theta2)
            iy2 = rim_radius * math.sin(theta2)

            rim_z = z * 0.8

            i0 = mesh.add_vertex((ox1, oy1, z), (0, 0, nz), (ox1 / radius * 0.5 + 0.5, oy1 / radius * 0.5 + 0.5))
            i1 = mesh.add_vertex((ox2, oy2, z), (0, 0, nz), (ox2 / radius * 0.5 + 0.5, oy2 / radius * 0.5 + 0.5))
            i2 = mesh.add_vertex((ix1, iy1, rim_z), (0, 0, nz), (ix1 / radius * 0.5 + 0.5, iy1 / radius * 0.5 + 0.5))
            i3 = mesh.add_vertex((ix2, iy2, rim_z), (0, 0, nz), (ix2 / radius * 0.5 + 0.5, iy2 / radius * 0.5 + 0.5))

            if side > 0:
                mesh.add_tri(i0, i1, i2)
                mesh.add_tri(i2, i1, i3)
            else:
                mesh.add_tri(i0, i2, i1)
                mesh.add_tri(i1, i2, i3)

        # Rim/hub area
        if has_spokes:
            # Create spoked wheel
            for spoke in range(spoke_count):
                spoke_angle = 2 * math.pi * spoke / spoke_count
                spoke_width = math.pi / spoke_count * 0.5

                for i in range(3):
                    theta = spoke_angle - spoke_width + spoke_width * i
                    next_theta = spoke_angle - spoke_width + spoke_width * (i + 1)

                    ix1 = rim_radius * 0.95 * math.cos(theta)
                    iy1 = rim_radius * 0.95 * math.sin(theta)
                    ix2 = rim_radius * 0.95 * math.cos(next_theta)
                    iy2 = rim_radius * 0.95 * math.sin(next_theta)

                    hx1 = hub_radius * math.cos(theta)
                    hy1 = hub_radius * math.sin(theta)
                    hx2 = hub_radius * math.cos(next_theta)
                    hy2 = hub_radius * math.sin(next_theta)

                    rim_z = z * 0.8

                    i0 = mesh.add_vertex((ix1, iy1, rim_z), (0, 0, nz), (0.5, 0.5))
                    i1 = mesh.add_vertex((ix2, iy2, rim_z), (0, 0, nz), (0.5, 0.5))
                    i2 = mesh.add_vertex((hx1, hy1, rim_z), (0, 0, nz), (0.5, 0.5))
                    i3 = mesh.add_vertex((hx2, hy2, rim_z), (0, 0, nz), (0.5, 0.5))

                    if side > 0:
                        mesh.add_tri(i0, i1, i2)
                        mesh.add_tri(i2, i1, i3)
                    else:
                        mesh.add_tri(i0, i2, i1)
                        mesh.add_tri(i1, i2, i3)
        else:
            # Solid disc wheel
            center = mesh.add_vertex((0, 0, z * 0.8), (0, 0, nz), (0.5, 0.5))
            for i in range(segments):
                theta1 = 2 * math.pi * i / segments
                theta2 = 2 * math.pi * (i + 1) / segments

                ix1 = rim_radius * math.cos(theta1)
                iy1 = rim_radius * math.sin(theta1)
                ix2 = rim_radius * math.cos(theta2)
                iy2 = rim_radius * math.sin(theta2)

                i1 = mesh.add_vertex((ix1, iy1, z * 0.8), (0, 0, nz), (ix1 / rim_radius * 0.5 + 0.5, iy1 / rim_radius * 0.5 + 0.5))
                i2 = mesh.add_vertex((ix2, iy2, z * 0.8), (0, 0, nz), (ix2 / rim_radius * 0.5 + 0.5, iy2 / rim_radius * 0.5 + 0.5))

                if side > 0:
                    mesh.add_tri(center, i1, i2)
                else:
                    mesh.add_tri(center, i2, i1)

    return mesh


def create_vehicle_chassis(
    params: VehicleParams = None,
    include_wheels: bool = True,
) -> MeshData:
    """
    Create a vehicle chassis mesh.

    Args:
        params: Vehicle parameters
        include_wheels: Whether to include wheels

    Returns:
        Complete vehicle mesh
    """
    p = params or VehicleParams()
    meshes = []

    if p.body_style == "sport":
        body = _create_sport_body(p)
    elif p.body_style == "muscle":
        body = _create_muscle_body(p)
    elif p.body_style == "van":
        body = _create_van_body(p)
    else:  # truck
        body = _create_truck_body(p)

    meshes.append(body)

    if include_wheels:
        wheel = create_wheel(p.wheel_radius, p.wheel_width, p.segments)

        # Front left
        wheel_fl = wheel.copy()
        wheel_fl.translate(-p.track_width / 2, p.wheel_radius + p.ground_clearance, p.wheelbase / 2)
        meshes.append(wheel_fl)

        # Front right
        wheel_fr = wheel.copy()
        wheel_fr.scale(-1, 1, 1)  # Mirror
        wheel_fr.translate(p.track_width / 2, p.wheel_radius + p.ground_clearance, p.wheelbase / 2)
        meshes.append(wheel_fr)

        # Rear left
        wheel_rl = wheel.copy()
        wheel_rl.translate(-p.track_width / 2, p.wheel_radius + p.ground_clearance, -p.wheelbase / 2)
        meshes.append(wheel_rl)

        # Rear right
        wheel_rr = wheel.copy()
        wheel_rr.scale(-1, 1, 1)  # Mirror
        wheel_rr.translate(p.track_width / 2, p.wheel_radius + p.ground_clearance, -p.wheelbase / 2)
        meshes.append(wheel_rr)

    return merge_meshes(meshes)


def _create_sport_body(p: VehicleParams) -> MeshData:
    """Create a sleek sport car body."""
    from .primitives import create_box

    meshes = []

    # Main body
    body_height = p.height * 0.4
    body = create_box(p.width, body_height, p.length)
    body.translate(0, p.ground_clearance + p.wheel_radius + body_height / 2, 0)
    meshes.append(body)

    # Cabin (tapered)
    cabin_height = p.height * 0.5
    cabin_length = p.length * 0.5
    cabin = create_box(p.width * 0.9, cabin_height, cabin_length)
    cabin.translate(0, p.ground_clearance + p.wheel_radius + body_height + cabin_height / 2, -p.length * 0.05)
    meshes.append(cabin)

    # Hood (angled down at front)
    hood = create_box(p.width * 0.85, p.height * 0.15, p.length * 0.35)
    hood.translate(0, p.ground_clearance + p.wheel_radius + body_height * 0.8, p.length * 0.3)
    meshes.append(hood)

    return merge_meshes(meshes)


def _create_muscle_body(p: VehicleParams) -> MeshData:
    """Create a muscle car body."""
    from .primitives import create_box

    meshes = []

    # Wide aggressive body
    body_height = p.height * 0.45
    body = create_box(p.width * 1.05, body_height, p.length)
    body.translate(0, p.ground_clearance + p.wheel_radius + body_height / 2, 0)
    meshes.append(body)

    # Cabin
    cabin_height = p.height * 0.45
    cabin = create_box(p.width * 0.85, cabin_height, p.length * 0.45)
    cabin.translate(0, p.ground_clearance + p.wheel_radius + body_height + cabin_height / 2, -p.length * 0.1)
    meshes.append(cabin)

    # Hood bulge
    bulge = create_box(p.width * 0.4, p.height * 0.12, p.length * 0.3)
    bulge.translate(0, p.ground_clearance + p.wheel_radius + body_height + p.height * 0.06, p.length * 0.25)
    meshes.append(bulge)

    return merge_meshes(meshes)


def _create_van_body(p: VehicleParams) -> MeshData:
    """Create a van/minivan body."""
    from .primitives import create_box

    meshes = []

    # Tall box body
    body_height = p.height * 1.2
    body = create_box(p.width, body_height, p.length * 0.9)
    body.translate(0, p.ground_clearance + p.wheel_radius + body_height / 2, -p.length * 0.05)
    meshes.append(body)

    # Front hood (short)
    hood = create_box(p.width * 0.9, p.height * 0.5, p.length * 0.2)
    hood.translate(0, p.ground_clearance + p.wheel_radius + p.height * 0.25, p.length * 0.4)
    meshes.append(hood)

    return merge_meshes(meshes)


def _create_truck_body(p: VehicleParams) -> MeshData:
    """Create a pickup truck body."""
    from .primitives import create_box

    meshes = []

    # Cab
    cab_height = p.height * 0.8
    cab = create_box(p.width, cab_height, p.length * 0.4)
    cab.translate(0, p.ground_clearance + p.wheel_radius + cab_height / 2, p.length * 0.25)
    meshes.append(cab)

    # Bed
    bed_height = p.height * 0.4
    bed_walls = p.height * 0.3
    bed = create_box(p.width, bed_height, p.length * 0.5)
    bed.translate(0, p.ground_clearance + p.wheel_radius + bed_height / 2, -p.length * 0.2)
    meshes.append(bed)

    # Bed walls
    for side in [-1, 1]:
        wall = create_box(p.width * 0.08, bed_walls, p.length * 0.5)
        wall.translate(side * p.width * 0.46, p.ground_clearance + p.wheel_radius + bed_height + bed_walls / 2, -p.length * 0.2)
        meshes.append(wall)

    # Tailgate
    tailgate = create_box(p.width, bed_walls, p.width * 0.08)
    tailgate.translate(0, p.ground_clearance + p.wheel_radius + bed_height + bed_walls / 2, -p.length * 0.45)
    meshes.append(tailgate)

    return merge_meshes(meshes)
