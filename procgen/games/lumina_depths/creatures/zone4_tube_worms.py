"""Zone 4: Tube Worms - Giant vent tube worms (Riftia pachyptila)."""
import math
import random
from procgen.lib.mesh_primitives import (
    generate_cylinder, generate_ellipsoid, generate_hemisphere, merge_meshes
)


def generate_tube_worms(num_worms: int = 8, seed: int = 42):
    """Generate cluster of giant tube worms - white tubes with red plumes.

    Args:
        num_worms: Number of worms in the cluster (default 8)
        seed: Random seed for consistent generation
    """
    meshes = []
    rng = random.Random(seed)

    # Generate cluster of tube worms
    for i in range(num_worms):
        # Random position within cluster
        angle = 2 * math.pi * i / num_worms + rng.uniform(-0.3, 0.3)
        radius = rng.uniform(0.05, 0.2)
        wx = radius * math.cos(angle)
        wz = radius * math.sin(angle)
        wy = 0  # Base at origin

        # Tube properties (vary height and width)
        tube_height = rng.uniform(0.4, 0.8)
        tube_radius = rng.uniform(0.025, 0.04)

        # White chitinous tube
        tube = generate_cylinder(wx, wy + tube_height/2, wz, tube_radius, tube_height,
                                 segments=8, axis='y')
        meshes.append(tube)

        # Tube opening (slightly wider rim)
        rim = generate_cylinder(wx, wy + tube_height, wz, tube_radius * 1.2, 0.02,
                               segments=8, axis='y')
        meshes.append(rim)

        # Red plume (feathery gill structure) - hemisphere of tentacles
        plume_center_y = wy + tube_height + 0.02

        # Central plume body
        plume_core = generate_hemisphere(wx, plume_center_y, wz,
                                         tube_radius * 1.5, tube_radius * 2, tube_radius * 1.5,
                                         lat_segments=6, lon_segments=8, top=True)
        meshes.append(plume_core)

        # Plume tentacles (radiating filaments)
        num_filaments = 12
        for j in range(num_filaments):
            f_angle = 2 * math.pi * j / num_filaments
            f_radius = tube_radius * 0.8
            fx = wx + f_radius * math.cos(f_angle)
            fz = wz + f_radius * math.sin(f_angle)

            # Each filament is a thin cylinder angled outward
            filament = generate_cylinder(fx, plume_center_y + 0.03, fz,
                                        0.005, 0.06, segments=4, axis='y')
            meshes.append(filament)

    # Base rock/substrate
    base = generate_ellipsoid(0, -0.05, 0, 0.35, 0.08, 0.35, lat_segments=6, lon_segments=10)
    meshes.append(base)

    return merge_meshes(meshes)
