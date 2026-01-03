#!/usr/bin/env python3
"""Generate Zone 3 (Midnight Abyss) creature meshes for Lumina Depths.

Zone 3: 1000-4000m depth, near-black, bioluminescent, alien beauty
- anglerfish: Deep-sea predator with bioluminescent lure (esca)
- gulper_eel: Massive hinged jaw, long tapering body
- dumbo_octopus: Ear-like fins, soft rounded body, short arms
- vampire_squid: Web between arms, bioluminescent photophores, spines
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


def generate_arm(start_x, start_y, start_z, length, thickness, segments=10, curl_amount=0.3):
    """Generate a curling arm (like octopus arm)."""
    vertices = []
    faces = []

    circ_segments = 6

    for seg in range(segments + 1):
        t = seg / segments
        # Taper thickness
        radius = thickness * (1 - t * 0.6)

        # Curl downward and outward
        curl = curl_amount * t * t
        z = start_z - t * length * 0.8 - curl * length * 0.3
        x_offset = start_x * (1 + t * 0.3)  # Spread outward
        y_offset = start_y * (1 + t * 0.3)

        for c in range(circ_segments):
            angle = 2 * math.pi * c / circ_segments
            x = x_offset + radius * math.cos(angle)
            y = y_offset + radius * math.sin(angle)
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


def generate_fin(cx, cy, cz, width, height, thickness, angle_y=0):
    """Generate a flat fin shape."""
    vertices = []
    faces = []

    # Create diamond/oval fin shape
    segments = 8
    for t_idx in range(2):  # Top and bottom surface
        t_offset = thickness/2 if t_idx == 0 else -thickness/2
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            # Oval shape
            x = cx + width * math.cos(angle) * math.cos(angle_y)
            y = cy + t_offset
            z = cz + height * math.sin(angle)
            vertices.append((x, y, z))

    # Top and bottom faces (fan triangulation)
    top_center = len(vertices)
    bot_center = len(vertices) + 1
    vertices.append((cx, cy + thickness/2, cz))
    vertices.append((cx, cy - thickness/2, cz))

    for i in range(segments):
        next_i = (i + 1) % segments
        # Top surface
        faces.append((top_center, i, next_i))
        # Bottom surface
        faces.append((bot_center, next_i + segments, i + segments))

    # Side edges
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append((i, i + segments, next_i + segments))
        faces.append((i, next_i + segments, next_i))

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


def generate_anglerfish():
    """Generate anglerfish - grotesque predator with bioluminescent lure.

    Characteristics:
    - Large head with massive jaw and needle-like teeth
    - Bioluminescent esca (lure) on illicium (fishing rod)
    - Small eyes (rely on lure, not vision)
    - Rounded body tapering to small tail
    - Dark coloration (black/brown)
    """
    meshes = []

    # Main body (rounded, bulbous)
    body_v, body_f = generate_ellipsoid(0, 0, 0, 0.25, 0.2, 0.3, lat_segments=10, lon_segments=14)
    meshes.append((body_v, body_f))

    # Head (large, fused with body front)
    head_v, head_f = generate_ellipsoid(0, 0.02, 0.25, 0.22, 0.18, 0.18, lat_segments=8, lon_segments=12)
    meshes.append((head_v, head_f))

    # Upper jaw (massive, hinged)
    upper_jaw_v, upper_jaw_f = generate_ellipsoid(0, 0.08, 0.4, 0.18, 0.08, 0.12, lat_segments=6, lon_segments=10)
    meshes.append((upper_jaw_v, upper_jaw_f))

    # Lower jaw (even larger, prominent)
    lower_jaw_v, lower_jaw_f = generate_ellipsoid(0, -0.1, 0.38, 0.2, 0.12, 0.15, lat_segments=7, lon_segments=10)
    meshes.append((lower_jaw_v, lower_jaw_f))

    # Teeth (needle-like, on both jaws)
    # Upper teeth
    for i in range(8):
        angle = math.pi * 0.2 + i * math.pi * 0.6 / 7
        tx = 0.12 * math.cos(angle)
        ty = 0.02
        tz = 0.48 + 0.03 * math.sin(i * 0.7)
        tooth_v, tooth_f = generate_tapered_tube(tx, ty, tz, 0.012, 0.002, 0.08, segments_len=4, segments_circ=5)
        meshes.append((tooth_v, tooth_f))

    # Lower teeth (pointing up)
    for i in range(10):
        angle = math.pi * 0.15 + i * math.pi * 0.7 / 9
        tx = 0.14 * math.cos(angle)
        ty = -0.06
        tz = 0.5 + 0.02 * math.sin(i * 0.5)
        # Teeth pointing up
        tooth_v, tooth_f = generate_tapered_tube(tx, ty, tz, 0.01, 0.002, 0.07, segments_len=4, segments_circ=5)
        # Rotate vertices to point upward
        rotated_v = [(v[0], v[1] + 0.04, v[2] - 0.02) for v in tooth_v]
        meshes.append((rotated_v, tooth_f))

    # Small eyes (anglerfish have tiny eyes)
    left_eye_v, left_eye_f = generate_ellipsoid(-0.12, 0.12, 0.32, 0.025, 0.025, 0.02, lat_segments=5, lon_segments=6)
    meshes.append((left_eye_v, left_eye_f))
    right_eye_v, right_eye_f = generate_ellipsoid(0.12, 0.12, 0.32, 0.025, 0.025, 0.02, lat_segments=5, lon_segments=6)
    meshes.append((right_eye_v, right_eye_f))

    # Illicium (the "fishing rod" - modified dorsal spine)
    illicium_v, illicium_f = generate_tapered_tube(0, 0.2, 0.35, 0.015, 0.008, 0.35, segments_len=8, segments_circ=6, axis='y')
    meshes.append((illicium_v, illicium_f))

    # Esca (the bioluminescent lure at tip of illicium) - EMISSIVE
    esca_v, esca_f = generate_ellipsoid(0, 0.4, 0.35, 0.04, 0.04, 0.035, lat_segments=6, lon_segments=8)
    meshes.append((esca_v, esca_f))

    # Tail section (tapered)
    tail_v, tail_f = generate_tapered_tube(0, 0, -0.25, 0.15, 0.05, 0.3, segments_len=8, segments_circ=10)
    meshes.append((tail_v, tail_f))

    # Small tail fin
    tail_fin_v, tail_fin_f = generate_ellipsoid(0, 0, -0.45, 0.06, 0.08, 0.04, lat_segments=5, lon_segments=6)
    meshes.append((tail_fin_v, tail_fin_f))

    # Dorsal fin (small, jagged)
    for i in range(3):
        dx = 0
        dy = 0.2 + i * 0.02
        dz = -0.05 - i * 0.08
        spine_v, spine_f = generate_tapered_tube(dx, dy, dz, 0.02, 0.005, 0.06, segments_len=4, segments_circ=5, axis='y')
        meshes.append((spine_v, spine_f))

    # Pectoral fins (small, paddle-like)
    left_pec_v, left_pec_f = generate_ellipsoid(-0.22, -0.05, 0.1, 0.08, 0.02, 0.05, lat_segments=5, lon_segments=6)
    meshes.append((left_pec_v, left_pec_f))
    right_pec_v, right_pec_f = generate_ellipsoid(0.22, -0.05, 0.1, 0.08, 0.02, 0.05, lat_segments=5, lon_segments=6)
    meshes.append((right_pec_v, right_pec_f))

    return merge_meshes(meshes)


def generate_gulper_eel():
    """Generate gulper eel (pelican eel) - massive jaw, long whip-like body.

    Characteristics:
    - Enormous hinged mouth (can swallow prey larger than itself)
    - Long, slender, whip-like tail
    - Tiny eyes near mouth
    - Bioluminescent tail tip
    - No scales, loose skin
    """
    meshes = []

    # Enormous mouth/pouch (the defining feature)
    # Upper jaw pouch
    upper_pouch_v, upper_pouch_f = generate_ellipsoid(0, 0.1, 0.2, 0.25, 0.15, 0.25, lat_segments=10, lon_segments=14)
    meshes.append((upper_pouch_v, upper_pouch_f))

    # Lower jaw pouch (even larger, expandable)
    lower_pouch_v, lower_pouch_f = generate_ellipsoid(0, -0.15, 0.15, 0.3, 0.25, 0.3, lat_segments=10, lon_segments=14)
    meshes.append((lower_pouch_v, lower_pouch_f))

    # Head ridge (connecting to body)
    head_v, head_f = generate_ellipsoid(0, 0.05, -0.05, 0.12, 0.1, 0.15, lat_segments=8, lon_segments=10)
    meshes.append((head_v, head_f))

    # Tiny eyes (very small, near jaw hinge)
    left_eye_v, left_eye_f = generate_ellipsoid(-0.1, 0.15, 0.05, 0.015, 0.015, 0.012, lat_segments=4, lon_segments=5)
    meshes.append((left_eye_v, left_eye_f))
    right_eye_v, right_eye_f = generate_ellipsoid(0.1, 0.15, 0.05, 0.015, 0.015, 0.012, lat_segments=4, lon_segments=5)
    meshes.append((right_eye_v, right_eye_f))

    # Long whip-like body (extremely long and thin)
    # Body segments tapering dramatically
    body_segments = [
        (0, 0, -0.15, 0.1, 0.08),    # Near head
        (0, 0, -0.4, 0.07, 0.06),
        (0, 0, -0.7, 0.05, 0.04),
        (0, 0, -1.0, 0.035, 0.03),
        (0, 0, -1.3, 0.025, 0.02),
        (0, 0, -1.6, 0.015, 0.012),
    ]

    for cx, cy, cz, rx, ry in body_segments:
        seg_v, seg_f = generate_ellipsoid(cx, cy, cz, rx, ry, 0.15, lat_segments=6, lon_segments=8)
        meshes.append((seg_v, seg_f))

    # Whip tail (final ultra-thin section)
    tail_v, tail_f = generate_tapered_tube(0, 0, -1.85, 0.012, 0.003, 0.4, segments_len=10, segments_circ=6)
    meshes.append((tail_v, tail_f))

    # Bioluminescent tail tip organ
    tail_light_v, tail_light_f = generate_ellipsoid(0, 0, -2.1, 0.02, 0.02, 0.025, lat_segments=5, lon_segments=6)
    meshes.append((tail_light_v, tail_light_f))

    # Small dorsal fin (runs along body)
    for i in range(5):
        dz = -0.2 - i * 0.25
        height = 0.04 - i * 0.005
        dorsal_v, dorsal_f = generate_ellipsoid(0, 0.08 - i * 0.01, dz, 0.01, height, 0.06, lat_segments=4, lon_segments=5)
        meshes.append((dorsal_v, dorsal_f))

    # Pectoral fins (tiny)
    left_pec_v, left_pec_f = generate_ellipsoid(-0.12, 0, -0.1, 0.05, 0.015, 0.03, lat_segments=4, lon_segments=5)
    meshes.append((left_pec_v, left_pec_f))
    right_pec_v, right_pec_f = generate_ellipsoid(0.12, 0, -0.1, 0.05, 0.015, 0.03, lat_segments=4, lon_segments=5)
    meshes.append((right_pec_v, right_pec_f))

    return merge_meshes(meshes)


def generate_dumbo_octopus():
    """Generate dumbo octopus - cute deep-sea octopus with ear-like fins.

    Characteristics:
    - Rounded, bell-shaped mantle
    - Two large ear-like fins (namesake feature)
    - 8 short arms with webbing between them
    - Large eyes
    - Soft, gelatinous appearance
    - Often pinkish/orange (will be handled by texture)
    """
    meshes = []

    # Mantle (rounded bell shape)
    mantle_v, mantle_f = generate_ellipsoid(0, 0, 0.15, 0.2, 0.18, 0.25, lat_segments=10, lon_segments=14)
    meshes.append((mantle_v, mantle_f))

    # Head (merged with mantle bottom)
    head_v, head_f = generate_ellipsoid(0, 0, -0.08, 0.18, 0.16, 0.12, lat_segments=8, lon_segments=12)
    meshes.append((head_v, head_f))

    # "Ear" fins (the dumbo characteristic) - large, rounded, on sides of mantle
    # Left ear fin
    left_ear_v, left_ear_f = generate_ellipsoid(-0.28, 0.05, 0.1, 0.12, 0.03, 0.15, lat_segments=6, lon_segments=8)
    meshes.append((left_ear_v, left_ear_f))
    # Right ear fin
    right_ear_v, right_ear_f = generate_ellipsoid(0.28, 0.05, 0.1, 0.12, 0.03, 0.15, lat_segments=6, lon_segments=8)
    meshes.append((right_ear_v, right_ear_f))

    # Large eyes (characteristic cute look)
    left_eye_v, left_eye_f = generate_ellipsoid(-0.1, 0.08, -0.05, 0.05, 0.05, 0.04, lat_segments=6, lon_segments=8)
    meshes.append((left_eye_v, left_eye_f))
    right_eye_v, right_eye_f = generate_ellipsoid(0.1, 0.08, -0.05, 0.05, 0.05, 0.04, lat_segments=6, lon_segments=8)
    meshes.append((right_eye_v, right_eye_f))

    # Eye pupils (darker centers)
    left_pupil_v, left_pupil_f = generate_ellipsoid(-0.1, 0.12, -0.05, 0.025, 0.025, 0.02, lat_segments=4, lon_segments=5)
    meshes.append((left_pupil_v, left_pupil_f))
    right_pupil_v, right_pupil_f = generate_ellipsoid(0.1, 0.12, -0.05, 0.025, 0.025, 0.02, lat_segments=4, lon_segments=5)
    meshes.append((right_pupil_v, right_pupil_f))

    # 8 Arms with webbing (short, stubby compared to other octopi)
    arm_angles = [i * math.pi / 4 for i in range(8)]
    for i, angle in enumerate(arm_angles):
        ax = 0.12 * math.cos(angle)
        ay = 0.12 * math.sin(angle)
        arm_v, arm_f = generate_arm(ax, ay, -0.15, 0.25, 0.03, segments=8, curl_amount=0.4)
        meshes.append((arm_v, arm_f))

    # Webbing between arms (simplified as a skirt-like structure)
    web_v, web_f = generate_tapered_tube(0, 0, -0.22, 0.15, 0.22, 0.12, segments_len=4, segments_circ=16)
    meshes.append((web_v, web_f))

    # Siphon (small, underneath)
    siphon_v, siphon_f = generate_cylinder(0, -0.12, -0.05, 0.025, 0.06, segments=6, axis='z')
    meshes.append((siphon_v, siphon_f))

    return merge_meshes(meshes)


def generate_vampire_squid():
    """Generate vampire squid - not actually a squid or octopus, unique cephalopod.

    Characteristics:
    - Dark red/black coloration (like a vampire's cloak)
    - Web between arms that can be pulled over head (cloak defense)
    - Bioluminescent photophores along arms and body
    - Two retractable sensory filaments
    - Spines on arms (cirri)
    - Large blue eyes (largest eye-to-body ratio of any animal)
    """
    meshes = []

    # Mantle (bell-shaped)
    mantle_v, mantle_f = generate_ellipsoid(0, 0, 0.1, 0.18, 0.15, 0.22, lat_segments=10, lon_segments=14)
    meshes.append((mantle_v, mantle_f))

    # Head
    head_v, head_f = generate_ellipsoid(0, 0, -0.1, 0.16, 0.14, 0.1, lat_segments=8, lon_segments=12)
    meshes.append((head_v, head_f))

    # Large eyes (proportionally huge, blue)
    left_eye_v, left_eye_f = generate_ellipsoid(-0.12, 0.06, -0.08, 0.06, 0.06, 0.05, lat_segments=6, lon_segments=8)
    meshes.append((left_eye_v, left_eye_f))
    right_eye_v, right_eye_f = generate_ellipsoid(0.12, 0.06, -0.08, 0.06, 0.06, 0.05, lat_segments=6, lon_segments=8)
    meshes.append((right_eye_v, right_eye_f))

    # Two fins (small, on mantle)
    left_fin_v, left_fin_f = generate_ellipsoid(-0.22, 0.02, 0.05, 0.08, 0.02, 0.1, lat_segments=5, lon_segments=6)
    meshes.append((left_fin_v, left_fin_f))
    right_fin_v, right_fin_f = generate_ellipsoid(0.22, 0.02, 0.05, 0.08, 0.02, 0.1, lat_segments=5, lon_segments=6)
    meshes.append((right_fin_v, right_fin_f))

    # 8 Arms with webbing
    arm_angles = [i * math.pi / 4 for i in range(8)]
    for i, angle in enumerate(arm_angles):
        ax = 0.1 * math.cos(angle)
        ay = 0.1 * math.sin(angle)
        arm_v, arm_f = generate_arm(ax, ay, -0.18, 0.35, 0.025, segments=10, curl_amount=0.3)
        meshes.append((arm_v, arm_f))

        # Spines (cirri) along each arm
        for j in range(4):
            t = (j + 1) / 5
            spine_x = ax * (1 + t * 0.3)
            spine_y = ay * (1 + t * 0.3)
            spine_z = -0.18 - t * 0.28
            spine_v, spine_f = generate_tapered_tube(spine_x, spine_y, spine_z, 0.008, 0.002, 0.04, segments_len=3, segments_circ=4)
            meshes.append((spine_v, spine_f))

    # Webbing (the "cloak" - large membrane between arms)
    web_v, web_f = generate_tapered_tube(0, 0, -0.28, 0.12, 0.28, 0.2, segments_len=5, segments_circ=16)
    meshes.append((web_v, web_f))

    # Two sensory filaments (retractable, long and thin)
    left_fil_v, left_fil_f = generate_tentacle(-0.08, 0.08, -0.15, 0.5, 0.008, segments=12, wave_amp=0.03, wave_freq=1)
    meshes.append((left_fil_v, left_fil_f))
    right_fil_v, right_fil_f = generate_tentacle(0.08, 0.08, -0.15, 0.5, 0.008, segments=12, wave_amp=0.03, wave_freq=1)
    meshes.append((right_fil_v, right_fil_f))

    # Photophores (bioluminescent spots) - along body and arms
    photophore_positions = [
        # Body photophores
        (0, 0.15, 0.05),
        (-0.1, 0.12, 0),
        (0.1, 0.12, 0),
        (0, 0.14, -0.05),
        # Arm tip photophores
        (-0.15, -0.15, -0.45),
        (0.15, -0.15, -0.45),
        (0, -0.2, -0.45),
        (-0.18, 0, -0.4),
        (0.18, 0, -0.4),
    ]
    for px, py, pz in photophore_positions:
        photo_v, photo_f = generate_ellipsoid(px, py, pz, 0.012, 0.012, 0.01, lat_segments=4, lon_segments=5)
        meshes.append((photo_v, photo_f))

    return merge_meshes(meshes)


def write_obj(filename, vertices, faces, name):
    """Write mesh to OBJ file."""
    with open(filename, 'w') as f:
        f.write(f"# Lumina Depths - {name}\n")
        f.write(f"# Zone 3: Midnight Abyss (1000-4000m)\n")
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
        ("anglerfish", generate_anglerfish, "Anglerfish"),
        ("gulper_eel", generate_gulper_eel, "Gulper Eel"),
        ("dumbo_octopus", generate_dumbo_octopus, "Dumbo Octopus"),
        ("vampire_squid", generate_vampire_squid, "Vampire Squid"),
    ]

    print("Generating Zone 3: Midnight Abyss creatures...")
    print("=" * 50)

    for filename, generator, display_name in creatures:
        print(f"\nGenerating {display_name}...")
        vertices, faces = generator()
        output_path = os.path.join(OUTPUT_DIR, f"{filename}.glb")
        write_obj(output_path, vertices, faces, display_name)
        print(f"  -> {output_path}")
        print(f"     Vertices: {len(vertices)}, Faces: {len(faces)}")

    print("\n" + "=" * 50)
    print("Zone 3 creatures complete!")


if __name__ == "__main__":
    main()
