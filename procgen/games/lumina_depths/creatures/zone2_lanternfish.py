"""Zone 2: Lanternfish - Small deep-sea fish with photophores."""
import math
from procgen.lib.mesh_primitives import (
    generate_ellipsoid, generate_fin, generate_cylinder, merge_meshes
)


def generate_lanternfish():
    """Generate lanternfish - elongated body with bioluminescent photophores."""
    meshes = []

    # Main body (elongated, laterally compressed)
    body = generate_ellipsoid(0, 0, 0, 0.08, 0.05, 0.2, lat_segments=8, lon_segments=12)
    meshes.append(body)

    # Head (slightly larger)
    head = generate_ellipsoid(0, 0.01, 0.18, 0.06, 0.05, 0.08, lat_segments=6, lon_segments=8)
    meshes.append(head)

    # Large eyes (characteristic of lanternfish)
    left_eye = generate_ellipsoid(-0.05, 0.02, 0.2, 0.025, 0.025, 0.02, lat_segments=5, lon_segments=6)
    meshes.append(left_eye)

    right_eye = generate_ellipsoid(0.05, 0.02, 0.2, 0.025, 0.025, 0.02, lat_segments=5, lon_segments=6)
    meshes.append(right_eye)

    # Dorsal fin
    dorsal = generate_fin(0, 0.05, 0, 0.08, 0.04, 0.008, rotation_y=0, rotation_z=0)
    meshes.append(dorsal)

    # Adipose fin (small, fleshy - characteristic of lanternfish)
    adipose = generate_ellipsoid(0, 0.04, -0.12, 0.015, 0.02, 0.025, lat_segments=4, lon_segments=6)
    meshes.append(adipose)

    # Anal fin
    anal = generate_fin(0, -0.05, -0.05, 0.06, -0.03, 0.006, rotation_y=0, rotation_z=math.pi)
    meshes.append(anal)

    # Pectoral fins
    left_pec = generate_fin(-0.06, 0, 0.1, 0.05, 0.025, 0.004, rotation_y=math.pi/3, rotation_z=math.pi/6)
    meshes.append(left_pec)

    right_pec = generate_fin(0.06, 0, 0.1, 0.05, 0.025, 0.004, rotation_y=-math.pi/3, rotation_z=-math.pi/6)
    meshes.append(right_pec)

    # Tail fin (forked)
    tail_top = generate_fin(0, 0.015, -0.22, 0.06, 0.04, 0.004, rotation_y=math.pi, rotation_z=-math.pi/6)
    meshes.append(tail_top)

    tail_bot = generate_fin(0, -0.015, -0.22, 0.06, -0.04, 0.004, rotation_y=math.pi, rotation_z=math.pi/6)
    meshes.append(tail_bot)

    # Photophores (bioluminescent spots along body)
    # Ventral photophore series
    photophore_positions = [
        (0, -0.04, 0.12),
        (0, -0.045, 0.06),
        (0, -0.045, 0),
        (0, -0.04, -0.06),
        (0, -0.035, -0.1),
    ]
    for px, py, pz in photophore_positions:
        photophore = generate_ellipsoid(px, py, pz, 0.012, 0.008, 0.012, lat_segments=4, lon_segments=6)
        meshes.append(photophore)

    # Lateral photophores
    for i in range(4):
        offset = 0.1 - i * 0.06
        left_photo = generate_ellipsoid(-0.055, 0, offset, 0.008, 0.006, 0.008, lat_segments=4, lon_segments=5)
        meshes.append(left_photo)
        right_photo = generate_ellipsoid(0.055, 0, offset, 0.008, 0.006, 0.008, lat_segments=4, lon_segments=5)
        meshes.append(right_photo)

    return merge_meshes(meshes)
