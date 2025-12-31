"""Generate whale meshes for Lumina Depths epic encounters.

Blue Whale: Majestic, smooth curves (Zone 1 @ 180m)
Sperm Whale: Blocky head, wrinkled (Zone 3 @ 2500m)

Output: ~2000 triangles each
"""

from pathlib import Path
import math

from procgen.lib.mesh_primitives import (
    generate_ellipsoid, generate_tapered_body,
    merge_meshes, write_obj
)


def _generate_flipper(cx, cy, cz, length, width, thickness, rotation=0):
    """Generate a whale flipper (flattened ellipsoid)."""
    vertices = []
    faces = []

    lat_segs = 8
    lon_segs = 12

    for lat in range(lat_segs + 1):
        theta = math.pi * lat / lat_segs
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        for lon in range(lon_segs):
            phi = 2 * math.pi * lon / lon_segs
            x = length * sin_theta * math.cos(phi)
            y = thickness * sin_theta * math.sin(phi)
            z = width * cos_theta

            # Apply rotation around Z axis
            cos_r = math.cos(rotation)
            sin_r = math.sin(rotation)
            rx = x * cos_r - y * sin_r
            ry = x * sin_r + y * cos_r

            vertices.append((cx + rx, cy + ry, cz + z))

    for lat in range(lat_segs):
        for lon in range(lon_segs):
            current = lat * lon_segs + lon
            next_lon = lat * lon_segs + (lon + 1) % lon_segs
            below = (lat + 1) * lon_segs + lon
            below_next = (lat + 1) * lon_segs + (lon + 1) % lon_segs

            faces.append((current, below, below_next))
            faces.append((current, below_next, next_lon))

    return vertices, faces


def generate_blue_whale_mesh():
    """Generate blue whale - streamlined, majestic."""
    meshes = []

    # Main body
    body = generate_tapered_body(
        length=12.0, max_radius=1.2,
        taper_start=0.15, taper_end=0.85,
        segments_len=24, segments_circ=16
    )
    meshes.append(body)

    # Head bulge
    head = generate_ellipsoid(0, 0.2, 5.5, 0.9, 0.8, 1.0, lat_segments=10, lon_segments=14)
    meshes.append(head)

    # Jaw ridge
    jaw = generate_ellipsoid(0, -0.3, 5.0, 0.7, 0.4, 1.2, lat_segments=8, lon_segments=12)
    meshes.append(jaw)

    # Left flipper
    left_flip = _generate_flipper(-1.0, -0.3, 2.0, 2.0, 0.6, 0.15, rotation=-0.3)
    meshes.append(left_flip)

    # Right flipper
    right_flip = _generate_flipper(1.0, -0.3, 2.0, 2.0, 0.6, 0.15, rotation=0.3)
    meshes.append(right_flip)

    # Dorsal fin (small ridge)
    dorsal = generate_ellipsoid(0, 1.0, -3.0, 0.1, 0.4, 0.6, lat_segments=6, lon_segments=8)
    meshes.append(dorsal)

    # Tail flukes - left
    left_fluke = _generate_flipper(-1.5, 0, -5.8, 1.8, 0.8, 0.1, rotation=-0.5)
    meshes.append(left_fluke)

    # Tail flukes - right
    right_fluke = _generate_flipper(1.5, 0, -5.8, 1.8, 0.8, 0.1, rotation=0.5)
    meshes.append(right_fluke)

    return merge_meshes(meshes)


def generate_sperm_whale_mesh():
    """Generate sperm whale - blocky head, wrinkled texture."""
    meshes = []

    # Main body (shorter, stockier)
    body = generate_tapered_body(
        length=8.0, max_radius=1.0,
        taper_start=0.25, taper_end=0.8,
        segments_len=20, segments_circ=14
    )
    meshes.append(body)

    # Massive head (spermaceti organ) - blocky
    head = generate_ellipsoid(0, 0.3, 3.5, 1.3, 1.2, 2.5, lat_segments=12, lon_segments=16)
    meshes.append(head)

    # Lower jaw (narrow)
    jaw = generate_ellipsoid(0, -0.6, 2.8, 0.3, 0.25, 1.8, lat_segments=6, lon_segments=8)
    meshes.append(jaw)

    # Left flipper (smaller than blue whale)
    left_flip = _generate_flipper(-0.9, -0.4, 1.5, 1.2, 0.4, 0.12, rotation=-0.4)
    meshes.append(left_flip)

    # Right flipper
    right_flip = _generate_flipper(0.9, -0.4, 1.5, 1.2, 0.4, 0.12, rotation=0.4)
    meshes.append(right_flip)

    # Dorsal hump (not a true fin)
    for i in range(3):
        hump = generate_ellipsoid(0, 0.8 - i*0.15, -2.0 - i*0.5, 0.15, 0.3, 0.3,
                                   lat_segments=5, lon_segments=6)
        meshes.append(hump)

    # Tail flukes - left
    left_fluke = _generate_flipper(-1.2, 0, -3.8, 1.4, 0.6, 0.08, rotation=-0.6)
    meshes.append(left_fluke)

    # Tail flukes - right
    right_fluke = _generate_flipper(1.2, 0, -3.8, 1.4, 0.6, 0.08, rotation=0.6)
    meshes.append(right_fluke)

    return merge_meshes(meshes)


def generate_all_whales(output_dir: Path) -> int:
    """Generate and save all whale meshes."""
    whales = [
        ("blue_whale", generate_blue_whale_mesh, "Blue Whale (Zone 1)"),
        ("sperm_whale", generate_sperm_whale_mesh, "Sperm Whale (Zone 3)"),
    ]

    for filename, generator, display_name in whales:
        print(f"Generating {display_name}...")
        vertices, faces = generator()
        output_path = output_dir / f"{filename}.obj"

        write_obj(
            str(output_path),
            vertices, faces,
            name=display_name,
            comment="Lumina Depths - Epic Encounter"
        )

        print(f"  -> {output_path.name}")
        print(f"     Vertices: {len(vertices)}, Faces: {len(faces)}")

    return len(whales)
