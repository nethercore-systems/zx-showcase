#!/usr/bin/env python3
"""Generate Zone 4 (Hydrothermal Vents) creature meshes for Lumina Depths.

Zone 4: 4000-5000m depth, volcanic warmth, primordial, edge of life
- tube_worms: Giant tubeworms with bright red plumes (chemosynthetic)
- vent_shrimp: Eyeless shrimp adapted to extreme heat
- ghost_fish: Pale, translucent fish adapted to vent ecosystems
- vent_octopus: Heat-tolerant octopus living near vents

Run with: blender --background --python zone4_creatures.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from mesh_utils import generate_and_export

OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated" / "meshes"


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


def generate_plume_filament(cx, cy, cz, length, thickness, curl_dir=1):
    """Generate a feathery plume filament for tubeworm."""
    vertices = []
    faces = []

    circ_segments = 5
    len_segments = 8

    for seg in range(len_segments + 1):
        t = seg / len_segments
        # Taper and curl outward
        radius = thickness * (1 - t * 0.5)
        curl = 0.03 * t * t * curl_dir

        z = cz + t * length
        x = cx + curl
        y = cy + curl * 0.5

        for c in range(circ_segments):
            angle = 2 * math.pi * c / circ_segments
            vx = x + radius * math.cos(angle)
            vy = y + radius * math.sin(angle)
            vertices.append((vx, vy, z))

    for seg in range(len_segments):
        for c in range(circ_segments):
            curr = seg * circ_segments + c
            next_c = seg * circ_segments + (c + 1) % circ_segments
            above = (seg + 1) * circ_segments + c
            above_next = (seg + 1) * circ_segments + (c + 1) % circ_segments

            faces.append((curr, next_c, above_next))
            faces.append((curr, above_next, above))

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


def generate_tube_worms():
    """Generate giant tubeworms - iconic hydrothermal vent life.

    Characteristics:
    - White/pale chitinous tube (up to 2m long in reality)
    - Bright red feathery plume (hemoglobin-rich, for gas exchange)
    - No mouth, gut, or eyes - rely on chemosynthetic bacteria
    - Cluster together in colonies
    - Generate a small cluster of 3 worms
    """
    meshes = []

    # Generate 3 tubeworms in a cluster
    worm_positions = [
        (0, 0, 0, 1.0),           # Center, full size
        (-0.12, 0.08, -0.1, 0.8), # Left, smaller
        (0.1, -0.06, -0.05, 0.7), # Right, smallest
    ]

    for wx, wy, wz_offset, scale in worm_positions:
        # Chitinous tube (white/pale)
        tube_height = 0.6 * scale
        tube_radius = 0.04 * scale
        tube_v, tube_f = generate_cylinder(wx, wy, wz_offset + tube_height/2, tube_radius, tube_height, segments=10, axis='z')
        meshes.append((tube_v, tube_f))

        # Tube rim (slightly flared at top)
        rim_v, rim_f = generate_tapered_tube(wx, wy, wz_offset + tube_height + 0.02*scale, tube_radius, tube_radius * 1.3, 0.04*scale, segments_len=3, segments_circ=10)
        meshes.append((rim_v, rim_f))

        # Red plume (feathery gill structure)
        plume_base_z = wz_offset + tube_height + 0.03*scale

        # Central plume filaments (arranged in a circular pattern)
        num_filaments = 12
        for i in range(num_filaments):
            angle = 2 * math.pi * i / num_filaments
            fx = wx + 0.02 * scale * math.cos(angle)
            fy = wy + 0.02 * scale * math.sin(angle)
            curl_dir = 1 if i % 2 == 0 else -1
            fil_v, fil_f = generate_plume_filament(fx, fy, plume_base_z, 0.12*scale, 0.008*scale, curl_dir * (1 + 0.5 * math.sin(angle)))
            meshes.append((fil_v, fil_f))

        # Inner shorter filaments
        for i in range(8):
            angle = 2 * math.pi * i / 8 + math.pi/8
            fx = wx + 0.01 * scale * math.cos(angle)
            fy = wy + 0.01 * scale * math.sin(angle)
            fil_v, fil_f = generate_plume_filament(fx, fy, plume_base_z, 0.08*scale, 0.006*scale, math.cos(angle))
            meshes.append((fil_v, fil_f))

    return merge_meshes(meshes)


def generate_vent_shrimp():
    """Generate vent shrimp - eyeless shrimp adapted to extreme heat.

    Characteristics:
    - No functional eyes (vestigial or absent)
    - Heat-sensing organ on back
    - Pale/white coloration
    - Cluster around vents eating bacteria
    - Long antennae for navigation
    """
    meshes = []

    # Carapace (main body shield)
    carapace_v, carapace_f = generate_ellipsoid(0, 0, 0, 0.06, 0.04, 0.12, lat_segments=8, lon_segments=10)
    meshes.append((carapace_v, carapace_f))

    # Abdomen (segmented tail, curves down)
    abdomen_segments = [
        (0, -0.01, -0.1, 0.04, 0.035, 0.04),
        (0, -0.025, -0.14, 0.035, 0.03, 0.03),
        (0, -0.04, -0.17, 0.03, 0.025, 0.025),
        (0, -0.055, -0.195, 0.025, 0.02, 0.02),
        (0, -0.07, -0.215, 0.02, 0.015, 0.018),
    ]
    for sx, sy, sz, rx, ry, rz in abdomen_segments:
        seg_v, seg_f = generate_ellipsoid(sx, sy, sz, rx, ry, rz, lat_segments=5, lon_segments=6)
        meshes.append((seg_v, seg_f))

    # Tail fan (telson and uropods)
    telson_v, telson_f = generate_ellipsoid(0, -0.08, -0.24, 0.025, 0.008, 0.03, lat_segments=4, lon_segments=6)
    meshes.append((telson_v, telson_f))
    # Uropods (tail fan sides)
    left_uro_v, left_uro_f = generate_ellipsoid(-0.025, -0.075, -0.235, 0.02, 0.006, 0.025, lat_segments=4, lon_segments=5)
    meshes.append((left_uro_v, left_uro_f))
    right_uro_v, right_uro_f = generate_ellipsoid(0.025, -0.075, -0.235, 0.02, 0.006, 0.025, lat_segments=4, lon_segments=5)
    meshes.append((right_uro_v, right_uro_f))

    # Head (fused with carapace front)
    head_v, head_f = generate_ellipsoid(0, 0.01, 0.1, 0.04, 0.035, 0.04, lat_segments=6, lon_segments=8)
    meshes.append((head_v, head_f))

    # Rostrum (pointed projection)
    rostrum_v, rostrum_f = generate_tapered_tube(0, 0.015, 0.16, 0.015, 0.005, 0.08, segments_len=5, segments_circ=6)
    meshes.append((rostrum_v, rostrum_f))

    # No eyes - but heat-sensing dorsal organ
    heat_organ_v, heat_organ_f = generate_ellipsoid(0, 0.045, 0.02, 0.025, 0.012, 0.04, lat_segments=5, lon_segments=6)
    meshes.append((heat_organ_v, heat_organ_f))

    # Long antennae (sensory, for navigation in darkness)
    left_ant_v, left_ant_f = generate_tentacle(-0.03, 0.02, 0.12, 0.25, 0.004, segments=10, wave_amp=0.02, wave_freq=1.5)
    meshes.append((left_ant_v, left_ant_f))
    right_ant_v, right_ant_f = generate_tentacle(0.03, 0.02, 0.12, 0.25, 0.004, segments=10, wave_amp=0.02, wave_freq=1.5)
    meshes.append((right_ant_v, right_ant_f))

    # Shorter antennules
    left_antl_v, left_antl_f = generate_tentacle(-0.02, 0.025, 0.13, 0.1, 0.003, segments=6, wave_amp=0.01, wave_freq=2)
    meshes.append((left_antl_v, left_antl_f))
    right_antl_v, right_antl_f = generate_tentacle(0.02, 0.025, 0.13, 0.1, 0.003, segments=6, wave_amp=0.01, wave_freq=2)
    meshes.append((right_antl_v, right_antl_f))

    # Walking legs (5 pairs, pereopods)
    for i in range(5):
        z_pos = 0.06 - i * 0.035
        for side in [-1, 1]:
            leg_v, leg_f = generate_tentacle(side * 0.05, -0.02, z_pos, 0.08, 0.006, segments=6, wave_amp=0.01, wave_freq=1)
            meshes.append((leg_v, leg_f))

    # Swimmerets (pleopods under abdomen)
    for i in range(4):
        z_pos = -0.11 - i * 0.025
        for side in [-1, 1]:
            swim_v, swim_f = generate_ellipsoid(side * 0.015, -0.04 - i*0.01, z_pos, 0.012, 0.004, 0.01, lat_segments=3, lon_segments=4)
            meshes.append((swim_v, swim_f))

    return merge_meshes(meshes)


def generate_ghost_fish():
    """Generate ghost fish - pale, translucent vent fish.

    Characteristics:
    - Pale/translucent body (no pigmentation needed in darkness)
    - Large head with sensory organs
    - Small eyes (some species) or none
    - Eel-like body for maneuvering in vent structures
    - Based on vent eelpout/snailfish morphology
    """
    meshes = []

    # Body (elongated, eel-like)
    body_v, body_f = generate_ellipsoid(0, 0, 0, 0.05, 0.045, 0.2, lat_segments=8, lon_segments=10)
    meshes.append((body_v, body_f))

    # Head (proportionally large, blunt)
    head_v, head_f = generate_ellipsoid(0, 0.01, 0.18, 0.055, 0.05, 0.08, lat_segments=7, lon_segments=10)
    meshes.append((head_v, head_f))

    # Snout (blunt, sensory)
    snout_v, snout_f = generate_ellipsoid(0, 0.015, 0.26, 0.035, 0.03, 0.04, lat_segments=5, lon_segments=6)
    meshes.append((snout_v, snout_f))

    # Small eyes (reduced but present)
    left_eye_v, left_eye_f = generate_ellipsoid(-0.04, 0.04, 0.22, 0.015, 0.015, 0.012, lat_segments=4, lon_segments=5)
    meshes.append((left_eye_v, left_eye_f))
    right_eye_v, right_eye_f = generate_ellipsoid(0.04, 0.04, 0.22, 0.015, 0.015, 0.012, lat_segments=4, lon_segments=5)
    meshes.append((right_eye_v, right_eye_f))

    # Tail section (tapers significantly)
    tail_sections = [
        (0, -0.005, -0.18, 0.04, 0.035),
        (0, -0.008, -0.28, 0.03, 0.025),
        (0, -0.01, -0.36, 0.02, 0.015),
        (0, -0.01, -0.42, 0.012, 0.01),
    ]
    for tx, ty, tz, rx, ry in tail_sections:
        tsec_v, tsec_f = generate_ellipsoid(tx, ty, tz, rx, ry, 0.06, lat_segments=5, lon_segments=6)
        meshes.append((tsec_v, tsec_f))

    # Continuous dorsal fin (runs along back)
    for i in range(8):
        dz = 0.1 - i * 0.07
        height = 0.025 - i * 0.002
        dy = 0.04 - i * 0.003
        dorsal_v, dorsal_f = generate_ellipsoid(0, dy, dz, 0.008, height, 0.04, lat_segments=4, lon_segments=5)
        meshes.append((dorsal_v, dorsal_f))

    # Continuous anal fin (runs along belly)
    for i in range(6):
        az = -0.05 - i * 0.06
        height = 0.02 - i * 0.002
        anal_v, anal_f = generate_ellipsoid(0, -0.035 + i*0.003, az, 0.006, height, 0.035, lat_segments=4, lon_segments=5)
        meshes.append((anal_v, anal_f))

    # Tail fin (rounded, continuous with dorsal/anal)
    tail_fin_v, tail_fin_f = generate_ellipsoid(0, -0.01, -0.48, 0.015, 0.03, 0.04, lat_segments=5, lon_segments=6)
    meshes.append((tail_fin_v, tail_fin_f))

    # Pectoral fins (rounded, paddle-like - for hovering near vents)
    left_pec_v, left_pec_f = generate_ellipsoid(-0.06, -0.01, 0.1, 0.04, 0.008, 0.025, lat_segments=4, lon_segments=5)
    meshes.append((left_pec_v, left_pec_f))
    right_pec_v, right_pec_f = generate_ellipsoid(0.06, -0.01, 0.1, 0.04, 0.008, 0.025, lat_segments=4, lon_segments=5)
    meshes.append((right_pec_v, right_pec_f))

    # Sensory pores (lateral line, visible on pale body)
    for i in range(6):
        pz = 0.15 - i * 0.08
        for side in [-1, 1]:
            pore_v, pore_f = generate_ellipsoid(side * 0.04, 0.01, pz, 0.006, 0.006, 0.006, lat_segments=3, lon_segments=4)
            meshes.append((pore_v, pore_f))

    return merge_meshes(meshes)


def generate_vent_octopus():
    """Generate vent octopus - heat-tolerant deep-sea octopus.

    Characteristics:
    - Pale/pinkish coloration (no need for camouflage)
    - Smaller than shallow-water octopi
    - 8 arms with reduced suckers
    - Large eyes (still functional at depth)
    - Webbing between arms
    - Lives on and around vent structures
    """
    meshes = []

    # Mantle (rounded, egg-shaped)
    mantle_v, mantle_f = generate_ellipsoid(0, 0, 0.1, 0.12, 0.1, 0.18, lat_segments=10, lon_segments=12)
    meshes.append((mantle_v, mantle_f))

    # Head (merged with mantle)
    head_v, head_f = generate_ellipsoid(0, 0, -0.06, 0.11, 0.1, 0.08, lat_segments=8, lon_segments=10)
    meshes.append((head_v, head_f))

    # Large eyes (functional in low light)
    left_eye_v, left_eye_f = generate_ellipsoid(-0.09, 0.04, -0.04, 0.04, 0.04, 0.035, lat_segments=6, lon_segments=8)
    meshes.append((left_eye_v, left_eye_f))
    right_eye_v, right_eye_f = generate_ellipsoid(0.09, 0.04, -0.04, 0.04, 0.04, 0.035, lat_segments=6, lon_segments=8)
    meshes.append((right_eye_v, right_eye_f))

    # Pupils
    left_pupil_v, left_pupil_f = generate_ellipsoid(-0.09, 0.07, -0.04, 0.02, 0.02, 0.015, lat_segments=4, lon_segments=5)
    meshes.append((left_pupil_v, left_pupil_f))
    right_pupil_v, right_pupil_f = generate_ellipsoid(0.09, 0.07, -0.04, 0.02, 0.02, 0.015, lat_segments=4, lon_segments=5)
    meshes.append((right_pupil_v, right_pupil_f))

    # 8 Arms (shorter and stubbier than shallow-water species)
    arm_angles = [i * math.pi / 4 for i in range(8)]
    for i, angle in enumerate(arm_angles):
        ax = 0.08 * math.cos(angle)
        ay = 0.08 * math.sin(angle)
        arm_length = 0.22 + 0.03 * math.sin(i * 1.5)  # Slight variation
        arm_v, arm_f = generate_arm(ax, ay, -0.12, arm_length, 0.025, segments=8, curl_amount=0.35)
        meshes.append((arm_v, arm_f))

        # Suckers along each arm (simplified as small bumps)
        for j in range(4):
            t = (j + 1) / 5
            sucker_x = ax * (1 + t * 0.3)
            sucker_y = ay * (1 + t * 0.3)
            sucker_z = -0.12 - t * arm_length * 0.6
            sucker_v, sucker_f = generate_ellipsoid(sucker_x, sucker_y, sucker_z, 0.008, 0.008, 0.006, lat_segments=3, lon_segments=4)
            meshes.append((sucker_v, sucker_f))

    # Webbing between arms (partial umbrella)
    web_v, web_f = generate_tapered_tube(0, 0, -0.18, 0.08, 0.15, 0.1, segments_len=4, segments_circ=16)
    meshes.append((web_v, web_f))

    # Siphon (jet propulsion tube)
    siphon_v, siphon_f = generate_cylinder(0, -0.08, -0.02, 0.02, 0.05, segments=6, axis='z')
    meshes.append((siphon_v, siphon_f))

    # Small fins (some deep-sea octopi have ear-like fins)
    left_fin_v, left_fin_f = generate_ellipsoid(-0.14, 0.02, 0.05, 0.04, 0.01, 0.06, lat_segments=4, lon_segments=5)
    meshes.append((left_fin_v, left_fin_f))
    right_fin_v, right_fin_f = generate_ellipsoid(0.14, 0.02, 0.05, 0.04, 0.01, 0.06, lat_segments=4, lon_segments=5)
    meshes.append((right_fin_v, right_fin_f))

    return merge_meshes(meshes)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    creatures = [
        ("tube_worms", generate_tube_worms, "Giant Tube Worms"),
        ("vent_shrimp", generate_vent_shrimp, "Vent Shrimp"),
        ("ghost_fish", generate_ghost_fish, "Ghost Fish"),
        ("vent_octopus", generate_vent_octopus, "Vent Octopus"),
    ]

    print("Generating Zone 4: Hydrothermal Vents creatures...")
    print("=" * 50)

    for asset_name, generator, display_name in creatures:
        print(f"\nGenerating {display_name}...")
        vertices, faces = generator()
        generate_and_export(asset_name, vertices, faces)

    print("\n" + "=" * 50)
    print("Zone 4 creatures complete!")


if __name__ == "__main__":
    main()
