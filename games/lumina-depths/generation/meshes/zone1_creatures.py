#!/usr/bin/env python3
"""Generate Zone 1 (Sunlit Waters) creature meshes for Lumina Depths.

Zone 1: 0-200m depth, bright, colorful reef life
- reef_fish: Small tropical schooling fish
- sea_turtle: Graceful swimmer with dome shell
- manta_ray: Majestic flat diamond shape
- coral_crab: Hard-shelled crustacean
"""

import math
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "generated", "meshes")


def generate_ellipsoid(cx, cy, cz, rx, ry, rz, lat_segments=10, lon_segments=14):
    """Generate ellipsoid vertices and faces."""
    vertices = []
    faces = []

    for lat in range(lat_segments + 1):
        theta = math.pi * lat / lat_segments
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        for lon in range(lon_segments):
            phi = 2 * math.pi * lon / lon_segments
            x = cx + rx * sin_theta * math.cos(phi)
            y = cy + ry * sin_theta * math.sin(phi)
            z = cz + rz * cos_theta
            vertices.append((x, y, z))

    for lat in range(lat_segments):
        for lon in range(lon_segments):
            current = lat * lon_segments + lon
            next_lon = lat * lon_segments + (lon + 1) % lon_segments
            below = (lat + 1) * lon_segments + lon
            below_next = (lat + 1) * lon_segments + (lon + 1) % lon_segments

            faces.append((current, below, below_next))
            faces.append((current, below_next, next_lon))

    return vertices, faces


def generate_hemisphere(cx, cy, cz, rx, ry, rz, lat_segments=8, lon_segments=12, top=True):
    """Generate hemisphere (half ellipsoid)."""
    vertices = []
    faces = []

    start_lat = 0 if top else lat_segments // 2
    end_lat = lat_segments // 2 + 1 if top else lat_segments + 1

    for lat in range(start_lat, end_lat):
        theta = math.pi * lat / lat_segments
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        for lon in range(lon_segments):
            phi = 2 * math.pi * lon / lon_segments
            x = cx + rx * sin_theta * math.cos(phi)
            y = cy + ry * sin_theta * math.sin(phi)
            z = cz + rz * cos_theta
            vertices.append((x, y, z))

    rows = end_lat - start_lat - 1
    for lat in range(rows):
        for lon in range(lon_segments):
            current = lat * lon_segments + lon
            next_lon = lat * lon_segments + (lon + 1) % lon_segments
            below = (lat + 1) * lon_segments + lon
            below_next = (lat + 1) * lon_segments + (lon + 1) % lon_segments

            faces.append((current, below, below_next))
            faces.append((current, below_next, next_lon))

    return vertices, faces


def generate_fin(cx, cy, cz, length, height, thickness, rotation_y=0, rotation_z=0):
    """Generate a triangular fin shape."""
    vertices = []
    faces = []

    # Triangle points (in local space)
    # Base at origin, tip extends in +X
    pts = [
        (0, 0, thickness/2),      # Base front
        (0, 0, -thickness/2),     # Base back
        (0, height, 0),           # Top
        (length, 0, 0),           # Tip
    ]

    # Apply rotations
    cos_y = math.cos(rotation_y)
    sin_y = math.sin(rotation_y)
    cos_z = math.cos(rotation_z)
    sin_z = math.sin(rotation_z)

    for px, py, pz in pts:
        # Rotate around Y
        x1 = px * cos_y + pz * sin_y
        z1 = -px * sin_y + pz * cos_y
        # Rotate around Z
        x2 = x1 * cos_z - py * sin_z
        y2 = x1 * sin_z + py * cos_z

        vertices.append((cx + x2, cy + y2, cz + z1))

    # Faces (triangles)
    faces.append((0, 2, 3))  # Front-top
    faces.append((1, 3, 2))  # Back-top
    faces.append((0, 3, 1))  # Bottom
    faces.append((0, 1, 2))  # Base

    return vertices, faces


def generate_cylinder(cx, cy, cz, radius, height, segments=10, axis='z'):
    """Generate cylinder along specified axis."""
    vertices = []
    faces = []

    for end in [0, 1]:
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            if axis == 'z':
                x = cx + radius * math.cos(angle)
                y = cy + radius * math.sin(angle)
                z = cz + (height/2 if end else -height/2)
            elif axis == 'x':
                y = cy + radius * math.cos(angle)
                z = cz + radius * math.sin(angle)
                x = cx + (height/2 if end else -height/2)
            else:  # y
                x = cx + radius * math.cos(angle)
                z = cz + radius * math.sin(angle)
                y = cy + (height/2 if end else -height/2)
            vertices.append((x, y, z))

    # Side faces
    for i in range(segments):
        top_curr = i
        top_next = (i + 1) % segments
        bot_curr = i + segments
        bot_next = (i + 1) % segments + segments

        faces.append((top_curr, bot_curr, bot_next))
        faces.append((top_curr, bot_next, top_next))

    # Caps
    top_center = len(vertices)
    if axis == 'z':
        vertices.append((cx, cy, cz + height/2))
    elif axis == 'x':
        vertices.append((cx + height/2, cy, cz))
    else:
        vertices.append((cx, cy + height/2, cz))

    bot_center = len(vertices)
    if axis == 'z':
        vertices.append((cx, cy, cz - height/2))
    elif axis == 'x':
        vertices.append((cx - height/2, cy, cz))
    else:
        vertices.append((cx, cy - height/2, cz))

    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append((top_center, next_i, i))
        faces.append((bot_center, i + segments, next_i + segments))

    return vertices, faces


def merge_meshes(mesh_list):
    """Merge multiple meshes into one."""
    all_vertices = []
    all_faces = []
    offset = 0

    for vertices, faces in mesh_list:
        all_vertices.extend(vertices)
        adjusted_faces = [(f[0] + offset, f[1] + offset, f[2] + offset) for f in faces]
        all_faces.extend(adjusted_faces)
        offset += len(vertices)

    return all_vertices, all_faces


def generate_reef_fish():
    """Generate small tropical reef fish - compact body, fins, forked tail."""
    meshes = []

    # Body (laterally compressed - wider than tall)
    body_v, body_f = generate_ellipsoid(0, 0, 0, 0.15, 0.08, 0.25, lat_segments=8, lon_segments=12)
    meshes.append((body_v, body_f))

    # Head bulge
    head_v, head_f = generate_ellipsoid(0, 0.01, 0.2, 0.08, 0.06, 0.1, lat_segments=6, lon_segments=8)
    meshes.append((head_v, head_f))

    # Dorsal fin (top)
    dorsal_v, dorsal_f = generate_fin(0, 0.08, 0, 0.12, 0.08, 0.01, rotation_y=0, rotation_z=0)
    meshes.append((dorsal_v, dorsal_f))

    # Anal fin (bottom)
    anal_v, anal_f = generate_fin(0, -0.08, -0.05, 0.08, -0.05, 0.01, rotation_y=0, rotation_z=math.pi)
    meshes.append((anal_v, anal_f))

    # Pectoral fins (sides)
    left_pec_v, left_pec_f = generate_fin(-0.1, 0, 0.05, 0.08, 0.04, 0.005, rotation_y=math.pi/3, rotation_z=math.pi/6)
    meshes.append((left_pec_v, left_pec_f))

    right_pec_v, right_pec_f = generate_fin(0.1, 0, 0.05, 0.08, 0.04, 0.005, rotation_y=-math.pi/3, rotation_z=-math.pi/6)
    meshes.append((right_pec_v, right_pec_f))

    # Tail fin (forked) - two lobes
    tail_top_v, tail_top_f = generate_fin(0, 0.02, -0.3, 0.1, 0.06, 0.005, rotation_y=math.pi, rotation_z=-math.pi/6)
    meshes.append((tail_top_v, tail_top_f))

    tail_bot_v, tail_bot_f = generate_fin(0, -0.02, -0.3, 0.1, -0.06, 0.005, rotation_y=math.pi, rotation_z=math.pi/6)
    meshes.append((tail_bot_v, tail_bot_f))

    return merge_meshes(meshes)


def generate_sea_turtle():
    """Generate sea turtle - dome shell, flippers, head."""
    meshes = []

    # Carapace (shell top) - dome hemisphere
    shell_v, shell_f = generate_hemisphere(0, 0.05, 0, 0.4, 0.25, 0.5, lat_segments=10, lon_segments=14, top=True)
    meshes.append((shell_v, shell_f))

    # Plastron (shell bottom) - flat ellipse
    plastron_v, plastron_f = generate_ellipsoid(0, -0.02, 0, 0.35, 0.08, 0.45, lat_segments=6, lon_segments=12)
    meshes.append((plastron_v, plastron_f))

    # Head
    head_v, head_f = generate_ellipsoid(0, 0.05, 0.5, 0.12, 0.1, 0.15, lat_segments=8, lon_segments=10)
    meshes.append((head_v, head_f))

    # Neck
    neck_v, neck_f = generate_cylinder(0, 0.02, 0.4, 0.08, 0.15, segments=8, axis='z')
    meshes.append((neck_v, neck_f))

    # Front left flipper
    fl_flip_v, fl_flip_f = generate_ellipsoid(-0.35, -0.02, 0.15, 0.3, 0.03, 0.12, lat_segments=6, lon_segments=10)
    meshes.append((fl_flip_v, fl_flip_f))

    # Front right flipper
    fr_flip_v, fr_flip_f = generate_ellipsoid(0.35, -0.02, 0.15, 0.3, 0.03, 0.12, lat_segments=6, lon_segments=10)
    meshes.append((fr_flip_v, fr_flip_f))

    # Rear left flipper (smaller)
    rl_flip_v, rl_flip_f = generate_ellipsoid(-0.25, -0.02, -0.35, 0.15, 0.02, 0.08, lat_segments=5, lon_segments=8)
    meshes.append((rl_flip_v, rl_flip_f))

    # Rear right flipper
    rr_flip_v, rr_flip_f = generate_ellipsoid(0.25, -0.02, -0.35, 0.15, 0.02, 0.08, lat_segments=5, lon_segments=8)
    meshes.append((rr_flip_v, rr_flip_f))

    # Tail (small)
    tail_v, tail_f = generate_ellipsoid(0, -0.02, -0.55, 0.04, 0.03, 0.1, lat_segments=5, lon_segments=6)
    meshes.append((tail_v, tail_f))

    return merge_meshes(meshes)


def generate_manta_ray():
    """Generate manta ray - flat diamond body, wing-like pectoral fins, cephalic fins."""
    meshes = []

    # Main body disc (very flat ellipsoid)
    body_v, body_f = generate_ellipsoid(0, 0, 0, 1.2, 0.08, 0.6, lat_segments=8, lon_segments=20)
    meshes.append((body_v, body_f))

    # Wing tips (extend body) - left
    left_wing_v, left_wing_f = generate_ellipsoid(-1.3, 0, 0.1, 0.4, 0.03, 0.25, lat_segments=6, lon_segments=10)
    meshes.append((left_wing_v, left_wing_f))

    # Wing tip - right
    right_wing_v, right_wing_f = generate_ellipsoid(1.3, 0, 0.1, 0.4, 0.03, 0.25, lat_segments=6, lon_segments=10)
    meshes.append((right_wing_v, right_wing_f))

    # Head bulge
    head_v, head_f = generate_ellipsoid(0, 0.03, 0.55, 0.25, 0.1, 0.15, lat_segments=6, lon_segments=10)
    meshes.append((head_v, head_f))

    # Cephalic fins (horn-like feeding fins) - left
    left_ceph_v, left_ceph_f = generate_ellipsoid(-0.2, 0.02, 0.7, 0.06, 0.04, 0.15, lat_segments=5, lon_segments=6)
    meshes.append((left_ceph_v, left_ceph_f))

    # Cephalic fin - right
    right_ceph_v, right_ceph_f = generate_ellipsoid(0.2, 0.02, 0.7, 0.06, 0.04, 0.15, lat_segments=5, lon_segments=6)
    meshes.append((right_ceph_v, right_ceph_f))

    # Tail (long, thin)
    tail_v, tail_f = generate_cylinder(0, 0, -0.9, 0.03, 0.8, segments=6, axis='z')
    meshes.append((tail_v, tail_f))

    # Tail tip
    tail_tip_v, tail_tip_f = generate_ellipsoid(0, 0, -1.35, 0.02, 0.02, 0.08, lat_segments=4, lon_segments=6)
    meshes.append((tail_tip_v, tail_tip_f))

    # Gill slits (small bumps on underside)
    for i in range(5):
        offset = -0.15 + i * 0.08
        gill_v, gill_f = generate_ellipsoid(offset, -0.06, 0.2, 0.02, 0.01, 0.08, lat_segments=4, lon_segments=6)
        meshes.append((gill_v, gill_f))

    return merge_meshes(meshes)


def generate_coral_crab():
    """Generate coral crab - rounded body, claws, legs."""
    meshes = []

    # Main body (carapace)
    body_v, body_f = generate_ellipsoid(0, 0, 0, 0.15, 0.08, 0.12, lat_segments=8, lon_segments=12)
    meshes.append((body_v, body_f))

    # Eye stalks
    left_eye_v, left_eye_f = generate_cylinder(-0.06, 0.06, 0.1, 0.015, 0.06, segments=6, axis='y')
    meshes.append((left_eye_v, left_eye_f))
    left_eyeball_v, left_eyeball_f = generate_ellipsoid(-0.06, 0.1, 0.1, 0.02, 0.02, 0.02, lat_segments=5, lon_segments=6)
    meshes.append((left_eyeball_v, left_eyeball_f))

    right_eye_v, right_eye_f = generate_cylinder(0.06, 0.06, 0.1, 0.015, 0.06, segments=6, axis='y')
    meshes.append((right_eye_v, right_eye_f))
    right_eyeball_v, right_eyeball_f = generate_ellipsoid(0.06, 0.1, 0.1, 0.02, 0.02, 0.02, lat_segments=5, lon_segments=6)
    meshes.append((right_eyeball_v, right_eyeball_f))

    # Claws (large)
    # Left claw arm
    left_arm_v, left_arm_f = generate_cylinder(-0.18, 0, 0.08, 0.025, 0.1, segments=6, axis='x')
    meshes.append((left_arm_v, left_arm_f))
    # Left claw pincer
    left_claw_v, left_claw_f = generate_ellipsoid(-0.28, 0, 0.08, 0.06, 0.04, 0.03, lat_segments=6, lon_segments=8)
    meshes.append((left_claw_v, left_claw_f))

    # Right claw (slightly smaller - asymmetric like real crabs)
    right_arm_v, right_arm_f = generate_cylinder(0.16, 0, 0.08, 0.02, 0.08, segments=6, axis='x')
    meshes.append((right_arm_v, right_arm_f))
    right_claw_v, right_claw_f = generate_ellipsoid(0.24, 0, 0.08, 0.045, 0.03, 0.025, lat_segments=6, lon_segments=8)
    meshes.append((right_claw_v, right_claw_f))

    # Walking legs (4 pairs)
    leg_positions = [
        (-0.12, -0.02, 0.05, -0.4),   # Left front
        (0.12, -0.02, 0.05, 0.4),     # Right front
        (-0.13, -0.02, 0, -0.5),      # Left mid-front
        (0.13, -0.02, 0, 0.5),        # Right mid-front
        (-0.12, -0.02, -0.05, -0.6),  # Left mid-back
        (0.12, -0.02, -0.05, 0.6),    # Right mid-back
        (-0.1, -0.02, -0.08, -0.7),   # Left back
        (0.1, -0.02, -0.08, 0.7),     # Right back
    ]

    for lx, ly, lz, angle in leg_positions:
        # Leg segment
        leg_v, leg_f = generate_cylinder(lx, ly, lz, 0.012, 0.1, segments=5, axis='x')
        # Rotate vertices based on angle
        rotated = []
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        for vx, vy, vz in leg_v:
            # Rotate around Y axis from leg base
            dx, dz = vx - lx, vz - lz
            new_x = lx + dx * cos_a - dz * sin_a
            new_z = lz + dx * sin_a + dz * cos_a
            rotated.append((new_x, vy - 0.03, new_z))  # Lower legs slightly
        meshes.append((rotated, leg_f))

    return merge_meshes(meshes)


def write_obj(filename, vertices, faces, name):
    """Write mesh to OBJ file."""
    with open(filename, 'w') as f:
        f.write(f"# Lumina Depths - {name}\n")
        f.write(f"# Zone 1: Sunlit Waters (0-200m)\n")
        f.write(f"# Vertices: {len(vertices)}\n")
        f.write(f"# Faces: {len(faces)}\n\n")

        for v in vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")

        f.write("\n")

        for face in faces:
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    creatures = [
        ("reef_fish", generate_reef_fish, "Reef Fish"),
        ("sea_turtle", generate_sea_turtle, "Sea Turtle"),
        ("manta_ray", generate_manta_ray, "Manta Ray"),
        ("coral_crab", generate_coral_crab, "Coral Crab"),
    ]

    for filename, generator, display_name in creatures:
        print(f"Generating {display_name}...")
        vertices, faces = generator()
        output_path = os.path.join(OUTPUT_DIR, f"{filename}.glb")
        write_obj(output_path, vertices, faces, display_name)
        print(f"  -> {output_path}")
        print(f"     Vertices: {len(vertices)}, Faces: {len(faces)}")

    print("\nZone 1 creatures complete!")


if __name__ == "__main__":
    main()
