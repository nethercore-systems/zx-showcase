"""Zone 2: Moon Jelly - Translucent bell, trailing tentacles."""
import math
from procgen.lib.mesh_primitives import generate_hemisphere, generate_cylinder, merge_meshes


def generate_moon_jelly():
    """Generate moon jelly - dome bell, oral arms, trailing tentacles."""
    meshes = []

    # Bell (dome) - hemisphere facing down
    bell = generate_hemisphere(0, 0, 0, 0.4, 0.25, 0.4, lat_segments=12, lon_segments=16, top=True)
    meshes.append(bell)

    # Inner bell (slightly smaller, inverted for thickness)
    inner_bell = generate_hemisphere(0, -0.02, 0, 0.35, 0.2, 0.35, lat_segments=10, lon_segments=14, top=True)
    meshes.append(inner_bell)

    # Four-leaf clover gonads (characteristic moon jelly pattern)
    gonad_positions = [
        (0.12, -0.08, 0.12),
        (-0.12, -0.08, 0.12),
        (0.12, -0.08, -0.12),
        (-0.12, -0.08, -0.12),
    ]
    for gx, gy, gz in gonad_positions:
        from procgen.lib.mesh_primitives import generate_ellipsoid
        gonad = generate_ellipsoid(gx, gy, gz, 0.08, 0.03, 0.08, lat_segments=6, lon_segments=8)
        meshes.append(gonad)

    # Oral arms (4 frilly appendages hanging from center)
    for i in range(4):
        angle = i * math.pi / 2
        ox = 0.05 * math.cos(angle)
        oz = 0.05 * math.sin(angle)
        oral_arm = generate_cylinder(ox, -0.35, oz, 0.02, 0.25, segments=6, axis='y')
        meshes.append(oral_arm)

    # Marginal tentacles (many short ones around edge)
    num_tentacles = 24
    for i in range(num_tentacles):
        angle = 2 * math.pi * i / num_tentacles
        tx = 0.38 * math.cos(angle)
        tz = 0.38 * math.sin(angle)
        tentacle = generate_cylinder(tx, -0.2, tz, 0.008, 0.15, segments=4, axis='y')
        meshes.append(tentacle)

    return merge_meshes(meshes)
