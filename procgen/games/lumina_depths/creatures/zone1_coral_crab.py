"""Zone 1: Coral Crab - Rounded body, claws, walking legs."""
import math
from procgen.lib.mesh_primitives import generate_ellipsoid, generate_cylinder, merge_meshes


def generate_coral_crab():
    """Generate coral crab - rounded body, claws, legs."""
    meshes = []

    # Main body (carapace)
    body = generate_ellipsoid(0, 0, 0, 0.15, 0.08, 0.12, lat_segments=8, lon_segments=12)
    meshes.append(body)

    # Eye stalks
    left_eye_stalk = generate_cylinder(-0.06, 0.06, 0.1, 0.015, 0.06, segments=6, axis='y')
    meshes.append(left_eye_stalk)
    left_eyeball = generate_ellipsoid(-0.06, 0.1, 0.1, 0.02, 0.02, 0.02, lat_segments=5, lon_segments=6)
    meshes.append(left_eyeball)

    right_eye_stalk = generate_cylinder(0.06, 0.06, 0.1, 0.015, 0.06, segments=6, axis='y')
    meshes.append(right_eye_stalk)
    right_eyeball = generate_ellipsoid(0.06, 0.1, 0.1, 0.02, 0.02, 0.02, lat_segments=5, lon_segments=6)
    meshes.append(right_eyeball)

    # Claws (large)
    left_arm = generate_cylinder(-0.18, 0, 0.08, 0.025, 0.1, segments=6, axis='x')
    meshes.append(left_arm)
    left_claw = generate_ellipsoid(-0.28, 0, 0.08, 0.06, 0.04, 0.03, lat_segments=6, lon_segments=8)
    meshes.append(left_claw)

    # Right claw (slightly smaller - asymmetric like real crabs)
    right_arm = generate_cylinder(0.16, 0, 0.08, 0.02, 0.08, segments=6, axis='x')
    meshes.append(right_arm)
    right_claw = generate_ellipsoid(0.24, 0, 0.08, 0.045, 0.03, 0.025, lat_segments=6, lon_segments=8)
    meshes.append(right_claw)

    # Walking legs (4 pairs)
    leg_positions = [
        (-0.12, -0.02, 0.05, -0.4),
        (0.12, -0.02, 0.05, 0.4),
        (-0.13, -0.02, 0, -0.5),
        (0.13, -0.02, 0, 0.5),
        (-0.12, -0.02, -0.05, -0.6),
        (0.12, -0.02, -0.05, 0.6),
        (-0.1, -0.02, -0.08, -0.7),
        (0.1, -0.02, -0.08, 0.7),
    ]

    for lx, ly, lz, angle in leg_positions:
        leg_v, leg_f = generate_cylinder(lx, ly, lz, 0.012, 0.1, segments=5, axis='x')
        # Rotate vertices based on angle
        rotated = []
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        for vx, vy, vz in leg_v:
            dx, dz = vx - lx, vz - lz
            new_x = lx + dx * cos_a - dz * sin_a
            new_z = lz + dx * sin_a + dz * cos_a
            rotated.append((new_x, vy - 0.03, new_z))
        meshes.append((rotated, leg_f))

    return merge_meshes(meshes)
