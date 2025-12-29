#!/usr/bin/env python3
"""Generate track segment and prop meshes for Neon Drift.

Creates low-poly OBJ files optimized for ZX console rendering.
All meshes are centered at origin with Y-up orientation.
"""

import math
from pathlib import Path


def write_obj(path: Path, vertices: list, faces: list, uvs: list = None):
    """Write an OBJ file with vertices, faces, and optional UVs."""
    with open(path, 'w') as f:
        f.write(f"# Generated track mesh for Neon Drift\n")
        f.write(f"# Vertices: {len(vertices)}, Faces: {len(faces)}\n\n")

        # Write vertices
        for v in vertices:
            f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")

        # Write UVs if provided
        if uvs:
            f.write("\n")
            for uv in uvs:
                f.write(f"vt {uv[0]:.4f} {uv[1]:.4f}\n")

        # Write faces
        f.write("\n")
        for face in faces:
            if uvs:
                f.write("f " + " ".join(f"{v}/{v}" for v in face) + "\n")
            else:
                f.write("f " + " ".join(str(v) for v in face) + "\n")

    print(f"  Generated: {path.name} ({len(vertices)} verts, {len(faces)} faces)")


def generate_track_straight(path: Path):
    """Generate a straight track segment (10x10 units, centered)."""
    # Simple flat quad with lane lines
    width = 10.0
    length = 10.0
    hw = width / 2
    hl = length / 2

    vertices = [
        (-hw, 0, -hl),  # 1: back-left
        (hw, 0, -hl),   # 2: back-right
        (hw, 0, hl),    # 3: front-right
        (-hw, 0, hl),   # 4: front-left
    ]

    faces = [
        (1, 2, 3, 4),  # road surface
    ]

    uvs = [
        (0, 0),
        (1, 0),
        (1, 1),
        (0, 1),
    ]

    write_obj(path, vertices, faces, uvs)


def generate_track_curve(path: Path, angle: float, direction: str):
    """Generate a curved track segment.

    Args:
        angle: Curve angle in degrees (45, 90, etc.)
        direction: 'left' or 'right'
    """
    segments = 8  # Number of arc segments
    width = 10.0
    inner_radius = 15.0  # Distance from center to inner edge
    outer_radius = inner_radius + width

    # Flip angle for left turns
    if direction == 'left':
        angle = -angle

    vertices = []
    uvs = []

    # Generate vertices along the curve
    for i in range(segments + 1):
        t = i / segments
        theta = math.radians(angle * t)

        # Inner edge
        ix = inner_radius * math.sin(theta)
        iz = inner_radius * (1 - math.cos(theta))
        vertices.append((ix, 0, iz))
        uvs.append((0, t))

        # Outer edge
        ox = outer_radius * math.sin(theta)
        oz = outer_radius * (1 - math.cos(theta))
        vertices.append((ox, 0, oz))
        uvs.append((1, t))

    # Generate quad faces
    faces = []
    for i in range(segments):
        base = i * 2 + 1  # OBJ indices are 1-based
        faces.append((base, base + 2, base + 3, base + 1))

    write_obj(path, vertices, faces, uvs)


def generate_track_tunnel(path: Path):
    """Generate a tunnel segment with walls and ceiling."""
    length = 10.0
    width = 10.0
    height = 6.0
    hw = width / 2
    hl = length / 2

    vertices = [
        # Floor
        (-hw, 0, -hl),     # 1
        (hw, 0, -hl),      # 2
        (hw, 0, hl),       # 3
        (-hw, 0, hl),      # 4
        # Left wall
        (-hw, 0, -hl),     # 5
        (-hw, height, -hl), # 6
        (-hw, height, hl),  # 7
        (-hw, 0, hl),      # 8
        # Right wall
        (hw, 0, -hl),      # 9
        (hw, height, -hl), # 10
        (hw, height, hl),  # 11
        (hw, 0, hl),       # 12
        # Ceiling
        (-hw, height, -hl), # 13
        (hw, height, -hl),  # 14
        (hw, height, hl),   # 15
        (-hw, height, hl),  # 16
    ]

    faces = [
        (1, 2, 3, 4),      # floor
        (5, 6, 7, 8),      # left wall
        (12, 11, 10, 9),   # right wall (reversed for correct facing)
        (13, 14, 15, 16),  # ceiling
    ]

    write_obj(path, vertices, faces)


def generate_track_jump(path: Path):
    """Generate a jump ramp segment."""
    length = 10.0
    width = 10.0
    ramp_height = 2.0
    hw = width / 2
    hl = length / 2

    vertices = [
        # Base (flat approach)
        (-hw, 0, -hl),         # 1
        (hw, 0, -hl),          # 2
        (hw, 0, 0),            # 3
        (-hw, 0, 0),           # 4
        # Ramp surface
        (-hw, 0, 0),           # 5
        (hw, 0, 0),            # 6
        (hw, ramp_height, hl), # 7
        (-hw, ramp_height, hl),# 8
        # Ramp front face
        (-hw, ramp_height, hl),# 9
        (hw, ramp_height, hl), # 10
        (hw, 0, hl),           # 11
        (-hw, 0, hl),          # 12
    ]

    faces = [
        (1, 2, 3, 4),      # approach
        (5, 6, 7, 8),      # ramp
        (9, 10, 11, 12),   # front face
    ]

    write_obj(path, vertices, faces)


def generate_prop_barrier(path: Path):
    """Generate a track barrier/wall segment."""
    length = 2.0
    height = 0.8
    depth = 0.3
    hd = depth / 2
    hl = length / 2

    vertices = [
        # Front face
        (-hl, 0, hd),       # 1
        (hl, 0, hd),        # 2
        (hl, height, hd),   # 3
        (-hl, height, hd),  # 4
        # Back face
        (-hl, 0, -hd),      # 5
        (hl, 0, -hd),       # 6
        (hl, height, -hd),  # 7
        (-hl, height, -hd), # 8
        # Top face
        (-hl, height, -hd), # 9
        (hl, height, -hd),  # 10
        (hl, height, hd),   # 11
        (-hl, height, hd),  # 12
    ]

    faces = [
        (1, 2, 3, 4),      # front
        (6, 5, 8, 7),      # back
        (9, 10, 11, 12),   # top
    ]

    write_obj(path, vertices, faces)


def generate_prop_boost_pad(path: Path):
    """Generate a boost pad with arrow shape."""
    width = 2.0
    length = 3.0
    height = 0.05
    hw = width / 2
    hl = length / 2

    # Arrow shape pointing forward (+Z)
    vertices = [
        # Arrow body
        (-hw * 0.6, height, -hl),     # 1
        (hw * 0.6, height, -hl),      # 2
        (hw * 0.6, height, hl * 0.3), # 3
        (-hw * 0.6, height, hl * 0.3),# 4
        # Arrow head
        (-hw, height, hl * 0.3),      # 5
        (0, height, hl),              # 6 (tip)
        (hw, height, hl * 0.3),       # 7
    ]

    faces = [
        (1, 2, 3, 4),  # body
        (5, 6, 7),     # head (triangle)
    ]

    write_obj(path, vertices, faces)


def generate_prop_building(path: Path):
    """Generate a simple building/tower prop."""
    width = 4.0
    depth = 4.0
    height = 10.0
    hw = width / 2
    hd = depth / 2

    vertices = [
        # Bottom face
        (-hw, 0, -hd),     # 1
        (hw, 0, -hd),      # 2
        (hw, 0, hd),       # 3
        (-hw, 0, hd),      # 4
        # Top face
        (-hw, height, -hd),# 5
        (hw, height, -hd), # 6
        (hw, height, hd),  # 7
        (-hw, height, hd), # 8
    ]

    faces = [
        # Walls
        (1, 2, 6, 5),  # front
        (2, 3, 7, 6),  # right
        (3, 4, 8, 7),  # back
        (4, 1, 5, 8),  # left
        # Top
        (5, 6, 7, 8),
    ]

    write_obj(path, vertices, faces)


def generate_prop_billboard(path: Path):
    """Generate a billboard prop with post."""
    panel_width = 4.0
    panel_height = 2.0
    post_height = 6.0
    post_size = 0.2

    hw = panel_width / 2
    hh = panel_height / 2
    hp = post_size / 2
    panel_y = post_height

    vertices = [
        # Post
        (-hp, 0, -hp),          # 1
        (hp, 0, -hp),           # 2
        (hp, 0, hp),            # 3
        (-hp, 0, hp),           # 4
        (-hp, post_height, -hp),# 5
        (hp, post_height, -hp), # 6
        (hp, post_height, hp),  # 7
        (-hp, post_height, hp), # 8
        # Panel (facing -Z)
        (-hw, panel_y - hh, 0), # 9
        (hw, panel_y - hh, 0),  # 10
        (hw, panel_y + hh, 0),  # 11
        (-hw, panel_y + hh, 0), # 12
    ]

    faces = [
        # Post walls
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 4, 8, 7),
        (4, 1, 5, 8),
        # Panel
        (9, 10, 11, 12),
    ]

    write_obj(path, vertices, faces)


def generate_crystal_formation(path: Path):
    """Generate a crystal prop for Crystal Cavern."""
    # A cluster of 3 pointed crystals
    vertices = []
    faces = []

    def add_crystal(cx, cz, height, base_size, vertex_offset):
        """Add a single crystal at position."""
        hs = base_size / 2
        # Base quad
        vertices.extend([
            (cx - hs, 0, cz - hs),
            (cx + hs, 0, cz - hs),
            (cx + hs, 0, cz + hs),
            (cx - hs, 0, cz + hs),
            (cx, height, cz),  # tip
        ])

        b = vertex_offset + 1  # OBJ is 1-indexed
        faces.extend([
            (b, b+1, b+4),     # front
            (b+1, b+2, b+4),   # right
            (b+2, b+3, b+4),   # back
            (b+3, b, b+4),     # left
        ])

        return vertex_offset + 5

    offset = 0
    offset = add_crystal(0, 0, 3.0, 1.0, offset)
    offset = add_crystal(-1.5, 0.5, 2.0, 0.7, offset)
    offset = add_crystal(1.2, -0.3, 2.5, 0.8, offset)

    write_obj(path, vertices, faces)


def main():
    base_dir = Path(__file__).parent.parent
    meshes_dir = base_dir / "assets" / "models" / "meshes"
    meshes_dir.mkdir(parents=True, exist_ok=True)

    print("Generating track and prop meshes...")

    # Track segments
    generate_track_straight(meshes_dir / "track_straight.obj")
    generate_track_curve(meshes_dir / "track_curve_left.obj", 45, 'left')
    generate_track_curve(meshes_dir / "track_curve_right.obj", 45, 'right')
    generate_track_tunnel(meshes_dir / "track_tunnel.obj")
    generate_track_jump(meshes_dir / "track_jump.obj")

    # Props
    generate_prop_barrier(meshes_dir / "prop_barrier.obj")
    generate_prop_boost_pad(meshes_dir / "prop_boost_pad.obj")
    generate_prop_building(meshes_dir / "prop_building.obj")
    generate_prop_billboard(meshes_dir / "prop_billboard.obj")
    generate_crystal_formation(meshes_dir / "crystal_formation.obj")

    print("\nDone! Generated 10 mesh files.")


if __name__ == "__main__":
    main()
