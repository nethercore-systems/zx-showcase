#!/usr/bin/env python3
"""
Neon Drift - Track & Props Generator

Generates track segments and props using proper Blender primitives.
Run with: blender --background --python generate_tracks.py
"""

import sys
import math
from pathlib import Path
from typing import List, Tuple

try:
    import bpy
except ImportError:
    print("Error: Must run from Blender.")
    sys.exit(1)


def clear_scene():
    """Remove all objects from scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def join_objects(objects: List[bpy.types.Object]) -> bpy.types.Object:
    """Join multiple objects into one."""
    if not objects:
        return None
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    return bpy.context.active_object


def uv_unwrap(obj: bpy.types.Object):
    """UV unwrap the object and ensure proper normals."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')


def create_material(name: str, color: Tuple[float, float, float],
                   metallic: float = 0.0, roughness: float = 0.8) -> bpy.types.Material:
    """Create a PBR material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat


def generate_texture(size: int, base_color: Tuple[float, float, float],
                    pattern: str = "solid") -> bpy.types.Image:
    """Generate a texture with optional patterns."""
    img = bpy.data.images.new(name="temp", width=size, height=size, alpha=True)
    pixels = []

    for y in range(size):
        for x in range(size):
            r, g, b = base_color

            if pattern == "road":
                # Dark asphalt with lane markings
                r, g, b = 0.15, 0.15, 0.18
                # Edge lines (magenta neon)
                if x < 12 or x > size - 12:
                    r, g, b = 0.8, 0.0, 0.8
                # Center dashes
                elif abs(x - size // 2) < 4 and (y % 40) < 20:
                    r, g, b = 1.0, 1.0, 1.0

            elif pattern == "barrier":
                r, g, b = 0.12, 0.12, 0.15
                # Neon stripe at top
                if y > size - 20:
                    r, g, b = 0.0, 1.0, 1.0
                # Warning stripes
                elif (x + y) % 32 < 16:
                    r, g, b = 0.3, 0.25, 0.0

            elif pattern == "boost":
                # Orange glow with chevrons
                r, g, b = 1.0, 0.6, 0.0
                if (y % 24) < 4:
                    r, g, b = 1.0, 0.8, 0.3

            elif pattern == "building":
                r, g, b = 0.1, 0.1, 0.15
                # Window grid
                wx, wy = x % 32, y % 40
                if 4 < wx < 28 and 4 < wy < 36:
                    # Some windows lit
                    if ((x // 32 * 7 + y // 40 * 13) % 10) > 4:
                        intensity = 0.5 + ((x + y) % 100) / 200
                        r, g, b = intensity, intensity * 0.8, intensity * 0.4
                    else:
                        r, g, b = 0.05, 0.05, 0.08

            elif pattern == "crystal":
                # Purple/cyan prismatic
                base = 0.4 + 0.2 * math.sin(x * 0.1) * math.sin(y * 0.1)
                r, g, b = 0.4 * base, 0.2 * base, 0.8 * base
                if (x + y) % 24 < 4:
                    r, g, b = 0.0, 0.8, 0.8

            elif pattern == "checkpoint":
                r, g, b = 0.15, 0.15, 0.2
                # Vertical neon stripes
                if x % 48 < 8:
                    r, g, b = 1.0, 0.0, 1.0
                # Horizontal bands
                if y < 16 or y > size - 16:
                    r, g, b = 0.0, 1.0, 1.0

            pixels.extend([r, g, b, 1.0])

    img.pixels = pixels
    return img


def save_texture(img: bpy.types.Image, filepath: Path):
    """Save texture to PNG."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    img.filepath_raw = str(filepath)
    img.file_format = 'PNG'
    img.save()
    print(f"  Texture: {filepath.name}")
    bpy.data.images.remove(img)


def export_glb(obj: bpy.types.Object, filepath: Path):
    """Export to GLB with proper settings."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    filepath.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(filepath),
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
        export_normals=True,
        export_texcoords=True,
    )
    print(f"  Mesh: {filepath.name}")


# =============================================================================
# TRACK SEGMENTS
# =============================================================================

def create_track_straight():
    """Straight track segment."""
    clear_scene()
    parts = []

    # Road surface
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    road = bpy.context.active_object
    road.scale = (6, 10, 1)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(road)

    # Left barrier
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-6.2, 0, 0.5))
    bl = bpy.context.active_object
    bl.scale = (0.2, 10, 0.5)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(bl)

    # Right barrier
    bpy.ops.mesh.primitive_cube_add(size=1, location=(6.2, 0, 0.5))
    br = bpy.context.active_object
    br.scale = (0.2, 10, 0.5)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(br)

    obj = join_objects(parts)
    obj.name = "track_straight"
    uv_unwrap(obj)

    mat = create_material("track_mat", (0.15, 0.15, 0.18), roughness=0.9)
    obj.data.materials.append(mat)

    return obj


def create_track_curve(direction: str = "left"):
    """Curved track segment."""
    clear_scene()
    parts = []

    # Create curve with segments
    segments = 8
    inner_r = 15
    outer_r = 27
    mid_r = (inner_r + outer_r) / 2
    angle_span = math.pi / 2

    for i in range(segments):
        mid_a = (i + 0.5) * angle_span / segments
        seg_len = (mid_r * angle_span / segments)

        if direction == "left":
            x = math.sin(mid_a) * mid_r
            y = math.cos(mid_a) * mid_r
            rot_z = -mid_a
        else:
            x = -math.sin(mid_a) * mid_r
            y = math.cos(mid_a) * mid_r
            rot_z = mid_a

        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, 0))
        seg = bpy.context.active_object
        seg.scale = ((outer_r - inner_r) / 2, seg_len / 2, 1)
        seg.rotation_euler = (0, 0, rot_z)
        bpy.ops.object.transform_apply(rotation=True, scale=True)
        parts.append(seg)

    obj = join_objects(parts)
    obj.name = f"track_curve_{direction}"
    uv_unwrap(obj)

    mat = create_material("track_mat", (0.15, 0.15, 0.18), roughness=0.9)
    obj.data.materials.append(mat)

    return obj


def create_track_tunnel():
    """Tunnel track segment."""
    clear_scene()
    parts = []

    length = 20
    width = 12

    # Road
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    road = bpy.context.active_object
    road.scale = (width / 2, length / 2, 1)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(road)

    # Tunnel rings
    for i in range(5):
        y = -length / 2 + 2 + i * (length - 4) / 4
        bpy.ops.mesh.primitive_torus_add(
            major_radius=7,
            minor_radius=0.4,
            major_segments=16,
            minor_segments=8,
            location=(0, y, 0)
        )
        ring = bpy.context.active_object
        ring.rotation_euler = (math.pi / 2, 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        parts.append(ring)

    obj = join_objects(parts)
    obj.name = "track_tunnel"
    uv_unwrap(obj)

    mat = create_material("tunnel_mat", (0.1, 0.1, 0.15))
    obj.data.materials.append(mat)

    return obj


def create_track_jump():
    """Jump ramp track."""
    clear_scene()
    parts = []

    width = 12
    ramp_len = 6
    peak_h = 2

    # Approach
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -ramp_len - 2, 0))
    approach = bpy.context.active_object
    approach.scale = (width / 2, 2, 1)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(approach)

    # Ramp up
    ramp_angle = math.atan2(peak_h, ramp_len)
    ramp_surface = math.sqrt(ramp_len**2 + peak_h**2)

    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -ramp_len / 2, peak_h / 2))
    ramp_up = bpy.context.active_object
    ramp_up.scale = (width / 2, ramp_surface / 2, 1)
    ramp_up.rotation_euler = (ramp_angle, 0, 0)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    parts.append(ramp_up)

    # Ramp down
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, ramp_len / 2, peak_h / 2))
    ramp_down = bpy.context.active_object
    ramp_down.scale = (width / 2, ramp_surface / 2, 1)
    ramp_down.rotation_euler = (-ramp_angle, 0, 0)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    parts.append(ramp_down)

    # Landing
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, ramp_len + 2, 0))
    landing = bpy.context.active_object
    landing.scale = (width / 2, 2, 1)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(landing)

    obj = join_objects(parts)
    obj.name = "track_jump"
    uv_unwrap(obj)

    mat = create_material("jump_mat", (0.2, 0.15, 0.1))
    obj.data.materials.append(mat)

    return obj


def create_track_checkpoint():
    """Checkpoint gate."""
    clear_scene()
    parts = []

    width = 14
    height = 6

    # Road under gate
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    road = bpy.context.active_object
    road.scale = (width / 2, 2, 1)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(road)

    # Left pillar
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-width / 2, 0, height / 2))
    pl = bpy.context.active_object
    pl.scale = (0.3, 0.3, height / 2)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(pl)

    # Right pillar
    bpy.ops.mesh.primitive_cube_add(size=1, location=(width / 2, 0, height / 2))
    pr = bpy.context.active_object
    pr.scale = (0.3, 0.3, height / 2)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(pr)

    # Top beam
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height + 0.2))
    beam = bpy.context.active_object
    beam.scale = (width / 2 + 0.3, 0.3, 0.2)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(beam)

    obj = join_objects(parts)
    obj.name = "track_checkpoint"
    uv_unwrap(obj)

    mat = create_material("checkpoint_mat", (0.2, 0.2, 0.25))
    obj.data.materials.append(mat)

    return obj


# =============================================================================
# PROPS
# =============================================================================

def create_prop_barrier():
    """Barrier/guardrail."""
    clear_scene()

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
    barrier = bpy.context.active_object
    barrier.scale = (0.2, 2, 0.5)
    bpy.ops.object.transform_apply(scale=True)
    barrier.name = "prop_barrier"
    uv_unwrap(barrier)

    mat = create_material("barrier_mat", (0.1, 0.1, 0.12))
    barrier.data.materials.append(mat)

    return barrier


def create_prop_boost_pad():
    """Boost pad."""
    clear_scene()

    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.02))
    pad = bpy.context.active_object
    pad.scale = (1.5, 2.5, 1)
    bpy.ops.object.transform_apply(scale=True)
    pad.name = "prop_boost_pad"
    uv_unwrap(pad)

    mat = create_material("boost_mat", (1.0, 0.5, 0.0))
    pad.data.materials.append(mat)

    return pad


def create_prop_billboard():
    """Billboard sign."""
    clear_scene()
    parts = []

    # Poles
    for x in [-1.5, 1.5]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=4, location=(x, 0, 2))
        pole = bpy.context.active_object
        parts.append(pole)

    # Board
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 4.5))
    board = bpy.context.active_object
    board.scale = (3, 0.1, 1.5)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(board)

    obj = join_objects(parts)
    obj.name = "prop_billboard"
    uv_unwrap(obj)

    mat = create_material("billboard_mat", (0.1, 0.1, 0.15))
    obj.data.materials.append(mat)

    return obj


def create_prop_building():
    """Background building."""
    clear_scene()

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 10))
    building = bpy.context.active_object
    building.scale = (4, 3, 10)
    bpy.ops.object.transform_apply(scale=True)
    building.name = "prop_building"
    uv_unwrap(building)

    mat = create_material("building_mat", (0.1, 0.1, 0.15))
    building.data.materials.append(mat)

    return building


def create_crystal_formation():
    """Crystal formation prop."""
    clear_scene()
    parts = []

    # Main crystal
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.6, depth=3, location=(0, 0, 1.5))
    main = bpy.context.active_object
    parts.append(main)

    # Smaller crystals around
    for i in range(4):
        angle = i * math.pi / 2 + 0.3
        x = math.cos(angle) * 0.8
        y = math.sin(angle) * 0.8
        h = 1.2 + (i % 2) * 0.5

        bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=0.3, depth=h, location=(x, y, h / 2))
        crystal = bpy.context.active_object
        crystal.rotation_euler = (0.2 * math.cos(angle), 0.2 * math.sin(angle), 0)
        bpy.ops.object.transform_apply(rotation=True)
        parts.append(crystal)

    obj = join_objects(parts)
    obj.name = "crystal_formation"
    uv_unwrap(obj)

    mat = create_material("crystal_mat", (0.5, 0.2, 0.8), metallic=0.9, roughness=0.1)
    obj.data.materials.append(mat)

    return obj


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n" + "=" * 60)
    print("  NEON DRIFT - TRACKS & PROPS (Proper Primitives)")
    print("=" * 60)

    script_dir = Path(__file__).parent
    output_base = script_dir.parent / "assets" / "models"
    meshes_dir = output_base / "meshes"
    textures_dir = output_base / "textures"
    meshes_dir.mkdir(parents=True, exist_ok=True)
    textures_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nOutput: {output_base}")

    # === TRACKS ===
    print("\n--- TRACK SEGMENTS ---")

    tracks = [
        ("track_straight", create_track_straight, "road"),
        ("track_curve_left", lambda: create_track_curve("left"), "road"),
        ("track_curve_right", lambda: create_track_curve("right"), "road"),
        ("track_tunnel", create_track_tunnel, "road"),
        ("track_jump", create_track_jump, "road"),
        ("track_checkpoint", create_track_checkpoint, "checkpoint"),
    ]

    for name, create_fn, tex_pattern in tracks:
        print(f"\n{name}:")
        obj = create_fn()

        # Generate texture
        tex = generate_texture(256, (0.15, 0.15, 0.18), tex_pattern)
        save_texture(tex, textures_dir / f"{name}.png")

        export_glb(obj, meshes_dir / f"{name}.glb")

    # === PROPS ===
    print("\n--- PROPS ---")

    props = [
        ("prop_barrier", create_prop_barrier, "barrier"),
        ("prop_boost_pad", create_prop_boost_pad, "boost"),
        ("prop_billboard", create_prop_billboard, "building"),
        ("prop_building", create_prop_building, "building"),
        ("crystal_formation", create_crystal_formation, "crystal"),
    ]

    for name, create_fn, tex_pattern in props:
        print(f"\n{name}:")
        obj = create_fn()

        # Albedo texture
        tex = generate_texture(256, (0.2, 0.2, 0.25), tex_pattern)
        save_texture(tex, textures_dir / f"{name}.png")

        # Emissive texture (bright version)
        if name in ["prop_barrier", "prop_boost_pad", "prop_billboard", "crystal_formation"]:
            emit_colors = {
                "prop_barrier": (0.0, 1.0, 1.0),
                "prop_boost_pad": (1.0, 0.6, 0.0),
                "prop_billboard": (1.0, 0.0, 1.0),
                "crystal_formation": (0.5, 0.0, 1.0),
            }
            emit_tex = generate_texture(128, emit_colors[name], "solid")
            save_texture(emit_tex, textures_dir / f"{name}_emissive.png")

        export_glb(obj, meshes_dir / f"{name}.glb")

    # === FONT TEXTURE ===
    print("\n--- FONT ---")
    font_img = bpy.data.images.new(name="font", width=128, height=72, alpha=True)
    pixels = [0.0] * (128 * 72 * 4)
    # Simple placeholder - cyan on transparent
    for i in range(128 * 72):
        x, y = i % 128, i // 128
        if (x % 8 < 5) and (y % 12 < 8):
            pixels[i * 4 + 0] = 0.0
            pixels[i * 4 + 1] = 1.0
            pixels[i * 4 + 2] = 1.0
            pixels[i * 4 + 3] = 1.0
    font_img.pixels = pixels
    save_texture(font_img, textures_dir / "neon_font.png")

    print("\n" + "=" * 60)
    print("  COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
