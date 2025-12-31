"""Zone 3: Anglerfish - Iconic deep-sea predator with bioluminescent lure."""
import math
from procgen.lib.mesh_primitives import (
    generate_ellipsoid, generate_cylinder, generate_fin, merge_meshes
)


def generate_anglerfish():
    """Generate anglerfish - bulbous body, huge mouth, glowing esca (lure)."""
    meshes = []

    # Main body (bulbous, somewhat flattened laterally)
    body = generate_ellipsoid(0, 0, 0, 0.2, 0.18, 0.25, lat_segments=10, lon_segments=14)
    meshes.append(body)

    # Head/mouth area (massive, extends forward)
    head = generate_ellipsoid(0, 0.02, 0.22, 0.18, 0.16, 0.15, lat_segments=8, lon_segments=12)
    meshes.append(head)

    # Lower jaw (hinged, slightly open)
    lower_jaw = generate_ellipsoid(0, -0.08, 0.25, 0.14, 0.08, 0.12, lat_segments=6, lon_segments=10)
    meshes.append(lower_jaw)

    # Teeth (jagged, curved) - upper row
    num_upper_teeth = 8
    for i in range(num_upper_teeth):
        angle = math.pi * 0.3 + (math.pi * 0.4) * i / (num_upper_teeth - 1)
        tx = 0.12 * math.cos(angle)
        ty = -0.02
        tz = 0.32 + 0.04 * math.sin(angle)
        tooth = generate_cylinder(tx, ty, tz, 0.01, 0.04, segments=4, axis='y')
        meshes.append(tooth)

    # Teeth - lower row
    for i in range(6):
        angle = math.pi * 0.35 + (math.pi * 0.3) * i / 5
        tx = 0.1 * math.cos(angle)
        ty = -0.12
        tz = 0.3 + 0.03 * math.sin(angle)
        tooth = generate_cylinder(tx, ty, tz, 0.008, 0.03, segments=4, axis='y')
        meshes.append(tooth)

    # Illicium (fishing rod) - dorsal spine modified into lure stalk
    illicium = generate_cylinder(0, 0.12, 0.2, 0.012, 0.2, segments=6, axis='y')
    meshes.append(illicium)

    # Esca (bioluminescent lure bulb at tip)
    esca = generate_ellipsoid(0, 0.35, 0.22, 0.035, 0.04, 0.035, lat_segments=6, lon_segments=8)
    meshes.append(esca)

    # Small eyes (proportionally tiny in deep-sea anglerfish)
    left_eye = generate_ellipsoid(-0.12, 0.08, 0.25, 0.025, 0.02, 0.02, lat_segments=4, lon_segments=6)
    meshes.append(left_eye)

    right_eye = generate_ellipsoid(0.12, 0.08, 0.25, 0.025, 0.02, 0.02, lat_segments=4, lon_segments=6)
    meshes.append(right_eye)

    # Pectoral fins (arm-like, used for "walking")
    left_pec = generate_fin(-0.18, -0.05, 0, 0.08, 0.04, 0.015, rotation_y=math.pi/2.5, rotation_z=math.pi/4)
    meshes.append(left_pec)

    right_pec = generate_fin(0.18, -0.05, 0, 0.08, 0.04, 0.015, rotation_y=-math.pi/2.5, rotation_z=-math.pi/4)
    meshes.append(right_pec)

    # Dorsal fin (small, set far back)
    dorsal = generate_fin(0, 0.15, -0.1, 0.06, 0.04, 0.01, rotation_y=0, rotation_z=0)
    meshes.append(dorsal)

    # Anal fin
    anal = generate_fin(0, -0.15, -0.1, 0.05, -0.03, 0.008, rotation_y=0, rotation_z=math.pi)
    meshes.append(anal)

    # Tail (small, rounded)
    tail = generate_ellipsoid(0, 0, -0.28, 0.06, 0.08, 0.06, lat_segments=6, lon_segments=8)
    meshes.append(tail)

    return merge_meshes(meshes)
