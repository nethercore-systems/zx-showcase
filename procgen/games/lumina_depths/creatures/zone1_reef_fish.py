"""Zone 1: Reef Fish - Small tropical schooling fish."""
import math
from procgen.lib.mesh_primitives import generate_ellipsoid, generate_fin, merge_meshes


def generate_reef_fish():
    """Generate small tropical reef fish - compact body, fins, forked tail."""
    meshes = []

    # Body (laterally compressed - wider than tall)
    body = generate_ellipsoid(0, 0, 0, 0.15, 0.08, 0.25, lat_segments=8, lon_segments=12)
    meshes.append(body)

    # Head bulge
    head = generate_ellipsoid(0, 0.01, 0.2, 0.08, 0.06, 0.1, lat_segments=6, lon_segments=8)
    meshes.append(head)

    # Dorsal fin (top)
    dorsal = generate_fin(0, 0.08, 0, 0.12, 0.08, 0.01, rotation_y=0, rotation_z=0)
    meshes.append(dorsal)

    # Anal fin (bottom)
    anal = generate_fin(0, -0.08, -0.05, 0.08, -0.05, 0.01, rotation_y=0, rotation_z=math.pi)
    meshes.append(anal)

    # Pectoral fins (sides)
    left_pec = generate_fin(-0.1, 0, 0.05, 0.08, 0.04, 0.005, rotation_y=math.pi/3, rotation_z=math.pi/6)
    meshes.append(left_pec)

    right_pec = generate_fin(0.1, 0, 0.05, 0.08, 0.04, 0.005, rotation_y=-math.pi/3, rotation_z=-math.pi/6)
    meshes.append(right_pec)

    # Tail fin (forked) - two lobes
    tail_top = generate_fin(0, 0.02, -0.3, 0.1, 0.06, 0.005, rotation_y=math.pi, rotation_z=-math.pi/6)
    meshes.append(tail_top)

    tail_bot = generate_fin(0, -0.02, -0.3, 0.1, -0.06, 0.005, rotation_y=math.pi, rotation_z=math.pi/6)
    meshes.append(tail_bot)

    return merge_meshes(meshes)
