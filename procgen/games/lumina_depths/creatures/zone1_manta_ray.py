"""Zone 1: Manta Ray - Flat diamond body, wing-like fins."""
from procgen.lib.mesh_primitives import generate_ellipsoid, generate_cylinder, merge_meshes


def generate_manta_ray():
    """Generate manta ray - flat diamond body, wing-like pectoral fins, cephalic fins."""
    meshes = []

    # Main body disc (very flat ellipsoid)
    body = generate_ellipsoid(0, 0, 0, 1.2, 0.08, 0.6, lat_segments=8, lon_segments=20)
    meshes.append(body)

    # Wing tips (extend body) - left
    left_wing = generate_ellipsoid(-1.3, 0, 0.1, 0.4, 0.03, 0.25, lat_segments=6, lon_segments=10)
    meshes.append(left_wing)

    # Wing tip - right
    right_wing = generate_ellipsoid(1.3, 0, 0.1, 0.4, 0.03, 0.25, lat_segments=6, lon_segments=10)
    meshes.append(right_wing)

    # Head bulge
    head = generate_ellipsoid(0, 0.03, 0.55, 0.25, 0.1, 0.15, lat_segments=6, lon_segments=10)
    meshes.append(head)

    # Cephalic fins (horn-like feeding fins) - left
    left_ceph = generate_ellipsoid(-0.2, 0.02, 0.7, 0.06, 0.04, 0.15, lat_segments=5, lon_segments=6)
    meshes.append(left_ceph)

    # Cephalic fin - right
    right_ceph = generate_ellipsoid(0.2, 0.02, 0.7, 0.06, 0.04, 0.15, lat_segments=5, lon_segments=6)
    meshes.append(right_ceph)

    # Tail (long, thin)
    tail = generate_cylinder(0, 0, -0.9, 0.03, 0.8, segments=6, axis='z')
    meshes.append(tail)

    # Tail tip
    tail_tip = generate_ellipsoid(0, 0, -1.35, 0.02, 0.02, 0.08, lat_segments=4, lon_segments=6)
    meshes.append(tail_tip)

    # Gill slits (small bumps on underside)
    for i in range(5):
        offset = -0.15 + i * 0.08
        gill = generate_ellipsoid(offset, -0.06, 0.2, 0.02, 0.01, 0.08, lat_segments=4, lon_segments=6)
        meshes.append(gill)

    return merge_meshes(meshes)
