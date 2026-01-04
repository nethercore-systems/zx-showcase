"""Shared mesh geometry utilities for Lumina Depths.

Uses Blender's bmesh for mesh generation and exports directly to GLB.
Run with: blender --background --python <script.py>
"""
import math
from pathlib import Path

try:
    import bpy
    import bmesh
    HAS_BLENDER = True
except ImportError:
    HAS_BLENDER = False

OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated" / "meshes"


def clear_scene():
    """Clear all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def create_mesh_from_data(name, vertices, faces):
    """Create a Blender mesh object from vertices and faces."""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def export_glb(obj, filepath):
    """Export object to GLB format."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Generate UVs
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.export_scene.gltf(
        filepath=str(filepath),
        export_format='GLB',
        use_selection=True,
        export_apply=True
    )

    print(f"Generated: {filepath}")
    vert_count = len(obj.data.vertices)
    face_count = len(obj.data.polygons)
    print(f"  Vertices: {vert_count}, Faces: {face_count}")


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


def generate_tapered_body(length, max_radius, taper_start, taper_end, segments_len=20, segments_circ=16):
    """Generate a tapered body (like a whale body) along Z axis."""
    vertices = []
    faces = []

    for z_idx in range(segments_len + 1):
        t = z_idx / segments_len
        z = -length/2 + t * length

        # Calculate radius at this z position
        if t < taper_start:
            local_t = t / taper_start
            radius = max_radius * math.sin(local_t * math.pi / 2)
        elif t > taper_end:
            local_t = (t - taper_end) / (1 - taper_end)
            radius = max_radius * math.cos(local_t * math.pi / 2) * 0.3
        else:
            radius = max_radius

        radius = max(radius, 0.05)

        for c_idx in range(segments_circ):
            angle = 2 * math.pi * c_idx / segments_circ
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertices.append((x, y, z))

    for z_idx in range(segments_len):
        for c_idx in range(segments_circ):
            curr = z_idx * segments_circ + c_idx
            next_c = z_idx * segments_circ + (c_idx + 1) % segments_circ
            below = (z_idx + 1) * segments_circ + c_idx
            below_next = (z_idx + 1) * segments_circ + (c_idx + 1) % segments_circ

            faces.append((curr, below, below_next))
            faces.append((curr, below_next, next_c))

    return vertices, faces


def generate_flipper(cx, cy, cz, length, width, thickness, rotation=0):
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

            if rotation != 0:
                cos_r = math.cos(rotation)
                sin_r = math.sin(rotation)
                x, y = x * cos_r - y * sin_r, x * sin_r + y * cos_r

            vertices.append((cx + x, cy + y, cz + z))

    for lat in range(lat_segs):
        for lon in range(lon_segs):
            current = lat * lon_segs + lon
            next_lon = lat * lon_segs + (lon + 1) % lon_segs
            below = (lat + 1) * lon_segs + lon
            below_next = (lat + 1) * lon_segs + (lon + 1) % lon_segs

            faces.append((current, below, below_next))
            faces.append((current, below_next, next_lon))

    return vertices, faces


def generate_fluke(cx, cy, cz, span, chord, thickness):
    """Generate whale tail flukes."""
    left_v, left_f = generate_flipper(cx - span/3, cy, cz, chord, span/2.5, thickness, rotation=math.pi/6)
    right_v, right_f = generate_flipper(cx + span/3, cy, cz, chord, span/2.5, thickness, rotation=-math.pi/6)

    vertices = list(left_v)
    offset = len(left_v)
    vertices.extend(right_v)

    faces = list(left_f)
    faces.extend([(f[0]+offset, f[1]+offset, f[2]+offset) for f in right_f])

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


def generate_and_export(name, vertices, faces):
    """Create mesh and export to GLB in one step."""
    clear_scene()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    obj = create_mesh_from_data(name, vertices, faces)
    filepath = OUTPUT_DIR / f"{name}.glb"
    export_glb(obj, filepath)
    return filepath
