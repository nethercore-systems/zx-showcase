"""Neon Drift Track and Props Generators.

Track Segments:
- Straight, curves (left/right), tunnel, jump, checkpoint

Props:
- Barriers, boost pads, billboards, buildings, crystals

Requires Blender to run. Use: blender --background --python tracks.py
"""

import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

try:
    import bpy
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False
    bpy = None


@dataclass
class TrackSegmentSpec:
    """Track segment specification."""
    name: str
    segment_type: str
    texture_pattern: str
    description: str


@dataclass
class PropSpec:
    """Prop specification."""
    name: str
    prop_type: str
    texture_pattern: str
    has_emissive: bool
    description: str


# Track segment definitions
TRACK_SEGMENTS = [
    TrackSegmentSpec("track_straight", "straight", "road", "Straight track segment"),
    TrackSegmentSpec("track_curve_left", "curve_left", "road", "Left curve segment"),
    TrackSegmentSpec("track_curve_right", "curve_right", "road", "Right curve segment"),
    TrackSegmentSpec("track_tunnel", "tunnel", "road", "Tunnel track segment"),
    TrackSegmentSpec("track_jump", "jump", "road", "Jump ramp segment"),
    TrackSegmentSpec("track_checkpoint", "checkpoint", "checkpoint", "Checkpoint gate"),
]

# Prop definitions
PROPS = [
    PropSpec("prop_barrier", "barrier", "barrier", True, "Guardrail barrier"),
    PropSpec("prop_boost_pad", "boost_pad", "boost", True, "Boost pad"),
    PropSpec("prop_billboard", "billboard", "building", True, "Billboard sign"),
    PropSpec("prop_building", "building", "building", False, "Background building"),
    PropSpec("crystal_formation", "crystal", "crystal", True, "Crystal formation"),
]


# =============================================================================
# Blender Utilities
# =============================================================================

if BLENDER_AVAILABLE:

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

    def join_objects(objects: List) -> object:
        """Join multiple objects into one."""
        if not objects:
            return None
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        bpy.ops.object.join()
        return bpy.context.active_object

    def uv_unwrap(obj):
        """UV unwrap the object."""
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')

    def create_material(name: str, color: Tuple[float, float, float],
                        metallic: float = 0.0, roughness: float = 0.8):
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

    def export_glb(obj, filepath: Path):
        """Export to GLB format."""
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

    # Track segment builders
    def build_track_straight():
        """Build straight track segment."""
        clear_scene()
        parts = []

        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
        road = bpy.context.active_object
        road.scale = (6, 10, 1)
        bpy.ops.object.transform_apply(scale=True)
        parts.append(road)

        # Barriers
        for x in [-6.2, 6.2]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0.5))
            barrier = bpy.context.active_object
            barrier.scale = (0.2, 10, 0.5)
            bpy.ops.object.transform_apply(scale=True)
            parts.append(barrier)

        obj = join_objects(parts)
        obj.name = "track_straight"
        uv_unwrap(obj)

        mat = create_material("track_mat", (0.15, 0.15, 0.18), roughness=0.9)
        obj.data.materials.append(mat)

        return obj

    def build_track_curve(direction: str = "left"):
        """Build curved track segment."""
        clear_scene()
        parts = []

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

    def build_track_tunnel():
        """Build tunnel track segment."""
        clear_scene()
        parts = []

        length = 20
        width = 12

        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
        road = bpy.context.active_object
        road.scale = (width / 2, length / 2, 1)
        bpy.ops.object.transform_apply(scale=True)
        parts.append(road)

        for i in range(5):
            y = -length / 2 + 2 + i * (length - 4) / 4
            bpy.ops.mesh.primitive_torus_add(
                major_radius=7, minor_radius=0.4,
                major_segments=16, minor_segments=8,
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

    def build_track_jump():
        """Build jump ramp track segment."""
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

        # Ramps
        ramp_angle = math.atan2(peak_h, ramp_len)
        ramp_surface = math.sqrt(ramp_len**2 + peak_h**2)

        for y_mult, angle_mult in [(-0.5, 1), (0.5, -1)]:
            bpy.ops.mesh.primitive_plane_add(size=1,
                location=(0, ramp_len * y_mult, peak_h / 2))
            ramp = bpy.context.active_object
            ramp.scale = (width / 2, ramp_surface / 2, 1)
            ramp.rotation_euler = (ramp_angle * angle_mult, 0, 0)
            bpy.ops.object.transform_apply(rotation=True, scale=True)
            parts.append(ramp)

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

    def build_track_checkpoint():
        """Build checkpoint gate."""
        clear_scene()
        parts = []

        width = 14
        height = 6

        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
        road = bpy.context.active_object
        road.scale = (width / 2, 2, 1)
        bpy.ops.object.transform_apply(scale=True)
        parts.append(road)

        # Pillars
        for x in [-width / 2, width / 2]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, height / 2))
            pillar = bpy.context.active_object
            pillar.scale = (0.3, 0.3, height / 2)
            bpy.ops.object.transform_apply(scale=True)
            parts.append(pillar)

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

    # Prop builders
    def build_prop_barrier():
        """Build barrier/guardrail."""
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

    def build_prop_boost_pad():
        """Build boost pad."""
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

    def build_prop_billboard():
        """Build billboard sign."""
        clear_scene()
        parts = []

        for x in [-1.5, 1.5]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=4, location=(x, 0, 2))
            pole = bpy.context.active_object
            parts.append(pole)

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

    def build_prop_building():
        """Build background building."""
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

    def build_crystal_formation():
        """Build crystal formation prop."""
        clear_scene()
        parts = []

        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.6, depth=3, location=(0, 0, 1.5))
        main = bpy.context.active_object
        parts.append(main)

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

    TRACK_BUILDERS = {
        "straight": build_track_straight,
        "curve_left": lambda: build_track_curve("left"),
        "curve_right": lambda: build_track_curve("right"),
        "tunnel": build_track_tunnel,
        "jump": build_track_jump,
        "checkpoint": build_track_checkpoint,
    }

    PROP_BUILDERS = {
        "barrier": build_prop_barrier,
        "boost_pad": build_prop_boost_pad,
        "billboard": build_prop_billboard,
        "building": build_prop_building,
        "crystal": build_crystal_formation,
    }

    def generate_all_tracks(meshes_dir: Path, textures_dir: Path = None) -> int:
        """Generate all track segments."""
        if textures_dir is None:
            textures_dir = meshes_dir.parent / "textures"

        meshes_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for spec in TRACK_SEGMENTS:
            builder = TRACK_BUILDERS.get(spec.segment_type)
            if builder:
                obj = builder()
                export_glb(obj, meshes_dir / f"{spec.name}.glb")
                print(f"  {spec.name}")
                count += 1

        return count

    def generate_all_props(meshes_dir: Path, textures_dir: Path = None) -> int:
        """Generate all props."""
        if textures_dir is None:
            textures_dir = meshes_dir.parent / "textures"

        meshes_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for spec in PROPS:
            builder = PROP_BUILDERS.get(spec.prop_type)
            if builder:
                obj = builder()
                export_glb(obj, meshes_dir / f"{spec.name}.glb")
                print(f"  {spec.name}")
                count += 1

        return count


# Fallback when Blender is not available
if not BLENDER_AVAILABLE:
    def generate_all_tracks(meshes_dir: Path, textures_dir: Path = None) -> int:
        print("Warning: Blender not available, skipping track generation")
        return 0

    def generate_all_props(meshes_dir: Path, textures_dir: Path = None) -> int:
        print("Warning: Blender not available, skipping prop generation")
        return 0


__all__ = [
    "TRACK_SEGMENTS",
    "PROPS",
    "generate_all_tracks",
    "generate_all_props",
    "BLENDER_AVAILABLE",
]


# CLI entry point for Blender
if __name__ == "__main__" and BLENDER_AVAILABLE:
    script_dir = Path(__file__).parent
    output_base = script_dir.parent.parent.parent / "games" / "neon-drift" / "assets" / "models"
    meshes_dir = output_base / "meshes"
    textures_dir = output_base / "textures"

    print("\n" + "=" * 60)
    print("  NEON DRIFT - Track & Props Generator")
    print("=" * 60)
    print(f"\nOutput: {output_base}")

    print("\n--- TRACK SEGMENTS ---")
    track_count = generate_all_tracks(meshes_dir, textures_dir)

    print("\n--- PROPS ---")
    prop_count = generate_all_props(meshes_dir, textures_dir)

    print(f"\nGenerated {track_count} tracks and {prop_count} props")
    print("=" * 60)
