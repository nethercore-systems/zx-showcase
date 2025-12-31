"""Zone 1: Sea Turtle - Dome shell, flippers, graceful."""
from procgen.lib.mesh_primitives import (
    generate_ellipsoid, generate_hemisphere, generate_cylinder, merge_meshes
)


def generate_sea_turtle():
    """Generate sea turtle - dome shell, flippers, head."""
    meshes = []

    # Carapace (shell top) - dome hemisphere
    shell = generate_hemisphere(0, 0.05, 0, 0.4, 0.25, 0.5, lat_segments=10, lon_segments=14, top=True)
    meshes.append(shell)

    # Plastron (shell bottom) - flat ellipse
    plastron = generate_ellipsoid(0, -0.02, 0, 0.35, 0.08, 0.45, lat_segments=6, lon_segments=12)
    meshes.append(plastron)

    # Head
    head = generate_ellipsoid(0, 0.05, 0.5, 0.12, 0.1, 0.15, lat_segments=8, lon_segments=10)
    meshes.append(head)

    # Neck
    neck = generate_cylinder(0, 0.02, 0.4, 0.08, 0.15, segments=8, axis='z')
    meshes.append(neck)

    # Front left flipper
    fl_flip = generate_ellipsoid(-0.35, -0.02, 0.15, 0.3, 0.03, 0.12, lat_segments=6, lon_segments=10)
    meshes.append(fl_flip)

    # Front right flipper
    fr_flip = generate_ellipsoid(0.35, -0.02, 0.15, 0.3, 0.03, 0.12, lat_segments=6, lon_segments=10)
    meshes.append(fr_flip)

    # Rear left flipper (smaller)
    rl_flip = generate_ellipsoid(-0.25, -0.02, -0.35, 0.15, 0.02, 0.08, lat_segments=5, lon_segments=8)
    meshes.append(rl_flip)

    # Rear right flipper
    rr_flip = generate_ellipsoid(0.25, -0.02, -0.35, 0.15, 0.02, 0.08, lat_segments=5, lon_segments=8)
    meshes.append(rr_flip)

    # Tail (small)
    tail = generate_ellipsoid(0, -0.02, -0.55, 0.04, 0.03, 0.1, lat_segments=5, lon_segments=6)
    meshes.append(tail)

    return merge_meshes(meshes)
