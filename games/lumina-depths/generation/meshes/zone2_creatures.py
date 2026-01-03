#!/usr/bin/env python3
"""Generate Zone 2 (Twilight Realm) creature meshes for Lumina Depths.

Zone 2: 200-1000m depth, fading light, mysterious, bioluminescent
- moon_jelly: Classic bell jellyfish with trailing tentacles
- lanternfish: Small fish with bioluminescent photophores
- siphonophore: Colonial organism, long chain structure
- giant_squid: Large squid with mantle, fins, arms, tentacles
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


def generate_hemisphere(cx, cy, cz, rx, ry, rz, lat_segments=10, lon_segments=16, top=True):
    """Generate hemisphere (dome shape)."""
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

    for i in range(segments):
        top_curr = i
        top_next = (i + 1) % segments
        bot_curr = i + segments
        bot_next = (i + 1) % segments + segments

        faces.append((top_curr, bot_curr, bot_next))
        faces.append((top_curr, bot_next, top_next))

    # Caps
    top_center = len(vertices)
    bot_center = len(vertices) + 1

    if axis == 'z':
        vertices.append((cx, cy, cz + height/2))
        vertices.append((cx, cy, cz - height/2))
    elif axis == 'x':
        vertices.append((cx + height/2, cy, cz))
        vertices.append((cx - height/2, cy, cz))
    else:
        vertices.append((cx, cy + height/2, cz))
        vertices.append((cx, cy - height/2, cz))

    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append((top_center, next_i, i))
        faces.append((bot_center, i + segments, next_i + segments))

    return vertices, faces


def generate_tapered_tube(cx, cy, cz, radius_start, radius_end, length, segments_len=10, segments_circ=8, axis='z'):
    """Generate a tapered tube (cone-like cylinder)."""
    vertices = []
    faces = []

    for z_idx in range(segments_len + 1):
        t = z_idx / segments_len
        if axis == 'z':
            z = cz - length/2 + t * length
        elif axis == 'y':
            z = cy - length/2 + t * length
        else:
            z = cx - length/2 + t * length

        radius = radius_start + t * (radius_end - radius_start)

        for c_idx in range(segments_circ):
            angle = 2 * math.pi * c_idx / segments_circ
            if axis == 'z':
                x = cx + radius * math.cos(angle)
                y = cy + radius * math.sin(angle)
                vertices.append((x, y, z))
            elif axis == 'y':
                x = cx + radius * math.cos(angle)
                zz = cz + radius * math.sin(angle)
                vertices.append((x, z, zz))
            else:
                y = cy + radius * math.cos(angle)
                zz = cz + radius * math.sin(angle)
                vertices.append((z, y, zz))

    for z_idx in range(segments_len):
        for c_idx in range(segments_circ):
            curr = z_idx * segments_circ + c_idx
            next_c = z_idx * segments_circ + (c_idx + 1) % segments_circ
            below = (z_idx + 1) * segments_circ + c_idx
            below_next = (z_idx + 1) * segments_circ + (c_idx + 1) % segments_circ

            faces.append((curr, below, below_next))
            faces.append((curr, below_next, next_c))

    return vertices, faces


def generate_tentacle(start_x, start_y, start_z, length, thickness, segments=12, wave_amp=0.05, wave_freq=2):
    """Generate a wavy tentacle."""
    vertices = []
    faces = []

    circ_segments = 6

    for seg in range(segments + 1):
        t = seg / segments
        # Taper thickness
        radius = thickness * (1 - t * 0.7)

        # Position along tentacle with wave
        z = start_z - t * length
        wave = wave_amp * math.sin(t * wave_freq * math.pi * 2)
        x_offset = wave * math.cos(seg * 0.5)
        y_offset = wave * math.sin(seg * 0.5)

        for c in range(circ_segments):
            angle = 2 * math.pi * c / circ_segments
            x = start_x + x_offset + radius * math.cos(angle)
            y = start_y + y_offset + radius * math.sin(angle)
            vertices.append((x, y, z))

    # Generate faces
    for seg in range(segments):
        for c in range(circ_segments):
            curr = seg * circ_segments + c
            next_c = seg * circ_segments + (c + 1) % circ_segments
            below = (seg + 1) * circ_segments + c
            below_next = (seg + 1) * circ_segments + (c + 1) % circ_segments

            faces.append((curr, below, below_next))
            faces.append((curr, below_next, next_c))

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


def generate_moon_jelly():
    """Generate moon jellyfish - translucent bell with trailing tentacles."""
    meshes = []

    # Bell (dome) - top hemisphere
    bell_v, bell_f = generate_hemisphere(0, 0, 0, 0.4, 0.4, 0.25, lat_segments=10, lon_segments=16, top=True)
    meshes.append((bell_v, bell_f))

    # Bell underside (slightly concave)
    under_v, under_f = generate_hemisphere(0, 0, -0.02, 0.35, 0.35, 0.1, lat_segments=6, lon_segments=16, top=False)
    meshes.append((under_v, under_f))

    # Oral arms (4 frilly structures hanging from center)
    for i in range(4):
        angle = i * math.pi / 2
        ox = 0.08 * math.cos(angle)
        oy = 0.08 * math.sin(angle)
        arm_v, arm_f = generate_tapered_tube(ox, oy, -0.15, 0.04, 0.02, 0.25, segments_len=6, segments_circ=6)
        meshes.append((arm_v, arm_f))

    # Marginal tentacles (short, around the bell edge)
    num_tentacles = 24
    for i in range(num_tentacles):
        angle = 2 * math.pi * i / num_tentacles
        tx = 0.38 * math.cos(angle)
        ty = 0.38 * math.sin(angle)
        tent_v, tent_f = generate_tentacle(tx, ty, -0.05, 0.2, 0.01, segments=6, wave_amp=0.02, wave_freq=1.5)
        meshes.append((tent_v, tent_f))

    # Gonads (4 horseshoe shapes visible through bell - simplified as ellipsoids)
    for i in range(4):
        angle = i * math.pi / 2 + math.pi / 4
        gx = 0.18 * math.cos(angle)
        gy = 0.18 * math.sin(angle)
        gonad_v, gonad_f = generate_ellipsoid(gx, gy, 0.08, 0.08, 0.08, 0.03, lat_segments=6, lon_segments=8)
        meshes.append((gonad_v, gonad_f))

    return merge_meshes(meshes)


def generate_lanternfish():
    """Generate lanternfish - small deep-sea fish with photophores."""
    meshes = []

    # Body (torpedo shape)
    body_v, body_f = generate_ellipsoid(0, 0, 0, 0.06, 0.04, 0.18, lat_segments=8, lon_segments=10)
    meshes.append((body_v, body_f))

    # Head (slightly larger)
    head_v, head_f = generate_ellipsoid(0, 0.005, 0.15, 0.045, 0.035, 0.06, lat_segments=6, lon_segments=8)
    meshes.append((head_v, head_f))

    # Large eye (characteristic of lanternfish)
    left_eye_v, left_eye_f = generate_ellipsoid(-0.035, 0.015, 0.16, 0.02, 0.02, 0.015, lat_segments=5, lon_segments=6)
    meshes.append((left_eye_v, left_eye_f))
    right_eye_v, right_eye_f = generate_ellipsoid(0.035, 0.015, 0.16, 0.02, 0.02, 0.015, lat_segments=5, lon_segments=6)
    meshes.append((right_eye_v, right_eye_f))

    # Dorsal fin
    dorsal_v, dorsal_f = generate_ellipsoid(0, 0.055, 0, 0.01, 0.03, 0.05, lat_segments=5, lon_segments=6)
    meshes.append((dorsal_v, dorsal_f))

    # Adipose fin (small, near tail)
    adipose_v, adipose_f = generate_ellipsoid(0, 0.035, -0.12, 0.005, 0.015, 0.02, lat_segments=4, lon_segments=5)
    meshes.append((adipose_v, adipose_f))

    # Tail fin (forked)
    tail_top_v, tail_top_f = generate_ellipsoid(0, 0.02, -0.22, 0.005, 0.025, 0.04, lat_segments=4, lon_segments=6)
    meshes.append((tail_top_v, tail_top_f))
    tail_bot_v, tail_bot_f = generate_ellipsoid(0, -0.02, -0.22, 0.005, 0.025, 0.04, lat_segments=4, lon_segments=6)
    meshes.append((tail_bot_v, tail_bot_f))

    # Pectoral fins
    left_pec_v, left_pec_f = generate_ellipsoid(-0.055, -0.01, 0.08, 0.03, 0.005, 0.015, lat_segments=4, lon_segments=5)
    meshes.append((left_pec_v, left_pec_f))
    right_pec_v, right_pec_f = generate_ellipsoid(0.055, -0.01, 0.08, 0.03, 0.005, 0.015, lat_segments=4, lon_segments=5)
    meshes.append((right_pec_v, right_pec_f))

    # Photophores (bioluminescent spots along body)
    photophore_positions = [
        (0, -0.035, 0.1),
        (0, -0.038, 0.05),
        (0, -0.038, 0),
        (0, -0.035, -0.05),
        (0, -0.03, -0.1),
    ]
    for px, py, pz in photophore_positions:
        photo_v, photo_f = generate_ellipsoid(px, py, pz, 0.008, 0.006, 0.008, lat_segments=4, lon_segments=5)
        meshes.append((photo_v, photo_f))

    return merge_meshes(meshes)


def generate_siphonophore():
    """Generate siphonophore - colonial organism, long chain of connected units."""
    meshes = []

    # Pneumatophore (float at top)
    float_v, float_f = generate_ellipsoid(0, 0, 0.5, 0.08, 0.06, 0.12, lat_segments=8, lon_segments=10)
    meshes.append((float_v, float_f))

    # Nectosome (swimming bells below float)
    for i in range(4):
        z = 0.35 - i * 0.1
        bell_v, bell_f = generate_hemisphere(0, 0, z, 0.06, 0.06, 0.05, lat_segments=6, lon_segments=8, top=True)
        meshes.append((bell_v, bell_f))

    # Siphosome (long chain of specialized units)
    # Stem
    stem_v, stem_f = generate_cylinder(0, 0, -0.2, 0.015, 1.0, segments=6, axis='z')
    meshes.append((stem_v, stem_f))

    # Gastrozooids (feeding polyps) along the stem
    gastro_positions = [-0.1, -0.25, -0.4, -0.55, -0.7]
    for gz in gastro_positions:
        # Main polyp
        polyp_v, polyp_f = generate_ellipsoid(0.03, 0, gz, 0.025, 0.02, 0.04, lat_segments=5, lon_segments=6)
        meshes.append((polyp_v, polyp_f))
        # Tentacle from polyp
        tent_v, tent_f = generate_tentacle(0.05, 0, gz, 0.15, 0.008, segments=8, wave_amp=0.03, wave_freq=2)
        meshes.append((tent_v, tent_f))

    # Gonophores (reproductive units)
    gono_positions = [-0.17, -0.32, -0.47, -0.62]
    for gz in gono_positions:
        gono_v, gono_f = generate_ellipsoid(-0.025, 0, gz, 0.02, 0.015, 0.025, lat_segments=5, lon_segments=6)
        meshes.append((gono_v, gono_f))

    # Bracts (protective structures)
    bract_positions = [-0.05, -0.2, -0.35, -0.5, -0.65]
    for bz in bract_positions:
        bract_v, bract_f = generate_ellipsoid(0, 0.025, bz, 0.03, 0.02, 0.03, lat_segments=4, lon_segments=6)
        meshes.append((bract_v, bract_f))

    return merge_meshes(meshes)


def generate_giant_squid():
    """Generate giant squid - large mantle, fins, 8 arms, 2 long tentacles."""
    meshes = []

    # Mantle (main body)
    mantle_v, mantle_f = generate_ellipsoid(0, 0, 0, 0.25, 0.2, 0.7, lat_segments=12, lon_segments=16)
    meshes.append((mantle_v, mantle_f))

    # Fins (diamond-shaped, at rear of mantle)
    left_fin_v, left_fin_f = generate_ellipsoid(-0.35, 0, -0.4, 0.2, 0.02, 0.25, lat_segments=6, lon_segments=10)
    meshes.append((left_fin_v, left_fin_f))
    right_fin_v, right_fin_f = generate_ellipsoid(0.35, 0, -0.4, 0.2, 0.02, 0.25, lat_segments=6, lon_segments=10)
    meshes.append((right_fin_v, right_fin_f))

    # Head
    head_v, head_f = generate_ellipsoid(0, 0, 0.75, 0.18, 0.15, 0.15, lat_segments=8, lon_segments=12)
    meshes.append((head_v, head_f))

    # Eyes (very large - characteristic of giant squid)
    left_eye_v, left_eye_f = generate_ellipsoid(-0.15, 0.05, 0.75, 0.08, 0.08, 0.06, lat_segments=6, lon_segments=8)
    meshes.append((left_eye_v, left_eye_f))
    right_eye_v, right_eye_f = generate_ellipsoid(0.15, 0.05, 0.75, 0.08, 0.08, 0.06, lat_segments=6, lon_segments=8)
    meshes.append((right_eye_v, right_eye_f))

    # 8 Arms (shorter, around the mouth)
    arm_angles = [i * math.pi / 4 for i in range(8)]
    for i, angle in enumerate(arm_angles):
        ax = 0.1 * math.cos(angle)
        ay = 0.1 * math.sin(angle)
        arm_length = 0.5 + (i % 2) * 0.1  # Vary length slightly
        arm_v, arm_f = generate_tentacle(ax, ay, 0.85, arm_length, 0.03, segments=10, wave_amp=0.04, wave_freq=1.5)
        meshes.append((arm_v, arm_f))

    # 2 Long tentacles (feeding tentacles - much longer)
    for side in [-1, 1]:
        tx = side * 0.12
        tent_v, tent_f = generate_tentacle(tx, 0, 0.85, 1.2, 0.025, segments=16, wave_amp=0.08, wave_freq=2.5)
        meshes.append((tent_v, tent_f))
        # Club at end of tentacle
        club_v, club_f = generate_ellipsoid(tx + side * 0.1, 0, 0.85 - 1.2, 0.05, 0.03, 0.08, lat_segments=5, lon_segments=6)
        meshes.append((club_v, club_f))

    # Siphon (jet propulsion)
    siphon_v, siphon_f = generate_cylinder(0, -0.15, 0.6, 0.05, 0.15, segments=8, axis='z')
    meshes.append((siphon_v, siphon_f))

    return merge_meshes(meshes)


def write_obj(filename, vertices, faces, name):
    """Write mesh to OBJ file."""
    with open(filename, 'w') as f:
        f.write(f"# Lumina Depths - {name}\n")
        f.write(f"# Zone 2: Twilight Realm (200-1000m)\n")
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
        ("moon_jelly", generate_moon_jelly, "Moon Jellyfish"),
        ("lanternfish", generate_lanternfish, "Lanternfish"),
        ("siphonophore", generate_siphonophore, "Siphonophore"),
        ("giant_squid", generate_giant_squid, "Giant Squid"),
    ]

    for filename, generator, display_name in creatures:
        print(f"Generating {display_name}...")
        vertices, faces = generator()
        output_path = os.path.join(OUTPUT_DIR, f"{filename}.glb")
        write_obj(output_path, vertices, faces, display_name)
        print(f"  -> {output_path}")
        print(f"     Vertices: {len(vertices)}, Faces: {len(faces)}")

    print("\nZone 2 creatures complete!")


if __name__ == "__main__":
    main()
