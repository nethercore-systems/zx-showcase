#!/usr/bin/env python3
"""Animation utilities for procedural animation generation.

Aligned with zx-procgen generator-patterns skill.

Requires: Blender 3.0+ (run via `blender --background --python script.py`)
"""
import math
from typing import Tuple, List, Optional

try:
    import bpy
    HAS_BPY = True
except ImportError:
    HAS_BPY = False


Vector3 = Tuple[float, float, float]


# === Timeline Control ===

def set_frame_range(start: int, end: int):
    """Set the animation frame range."""
    if not HAS_BPY:
        return
    bpy.context.scene.frame_start = start
    bpy.context.scene.frame_end = end


def set_fps(fps: int):
    """Set frames per second."""
    if not HAS_BPY:
        return
    bpy.context.scene.render.fps = fps


def set_current_frame(frame: int):
    """Set the current frame."""
    if not HAS_BPY:
        return
    bpy.context.scene.frame_set(frame)


# === Keyframe Insertion ===

def keyframe_location(obj, frame: int, location: Vector3):
    """Insert a location keyframe."""
    obj.location = location
    obj.keyframe_insert(data_path="location", frame=frame)


def keyframe_rotation(obj, frame: int, rotation: Vector3):
    """Insert a rotation keyframe (Euler XYZ in radians)."""
    obj.rotation_euler = rotation
    obj.keyframe_insert(data_path="rotation_euler", frame=frame)


def keyframe_scale(obj, frame: int, scale: Vector3):
    """Insert a scale keyframe."""
    obj.scale = scale
    obj.keyframe_insert(data_path="scale", frame=frame)


def keyframe_transform(obj, frame: int, location: Optional[Vector3] = None,
                       rotation: Optional[Vector3] = None,
                       scale: Optional[Vector3] = None):
    """Insert location, rotation, and/or scale keyframes."""
    if location is not None:
        keyframe_location(obj, frame, location)
    if rotation is not None:
        keyframe_rotation(obj, frame, rotation)
    if scale is not None:
        keyframe_scale(obj, frame, scale)


# === Interpolation ===

def set_interpolation(obj, mode: str = 'BEZIER'):
    """Set interpolation mode for all keyframes.

    Modes: CONSTANT, LINEAR, BEZIER, SINE, QUAD, CUBIC, QUART, QUINT, EXPO, CIRC, BACK, BOUNCE, ELASTIC
    """
    if not obj.animation_data or not obj.animation_data.action:
        return

    for fcurve in obj.animation_data.action.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = mode


def set_extrapolation(obj, mode: str = 'CONSTANT'):
    """Set extrapolation mode for fcurves.

    Modes: CONSTANT, LINEAR, MAKE_CYCLIC, CLEAR_CYCLIC
    """
    if not obj.animation_data or not obj.animation_data.action:
        return

    for fcurve in obj.animation_data.action.fcurves:
        if mode == 'MAKE_CYCLIC':
            mod = fcurve.modifiers.new('CYCLES')
            mod.mode_before = 'REPEAT'
            mod.mode_after = 'REPEAT'
        elif mode == 'CLEAR_CYCLIC':
            for mod in fcurve.modifiers:
                if mod.type == 'CYCLES':
                    fcurve.modifiers.remove(mod)
        else:
            fcurve.extrapolation = mode


# === Bone Animation ===

def keyframe_bone_location(armature, bone_name: str, frame: int,
                           location: Vector3):
    """Insert a pose bone location keyframe."""
    bone = armature.pose.bones.get(bone_name)
    if bone:
        bone.location = location
        bone.keyframe_insert(data_path="location", frame=frame)


def keyframe_bone_rotation(armature, bone_name: str, frame: int,
                           rotation: Vector3, mode: str = 'XYZ'):
    """Insert a pose bone rotation keyframe.

    Args:
        armature: Armature object
        bone_name: Name of the bone
        frame: Frame number
        rotation: Euler rotation in radians
        mode: Rotation mode (XYZ, XZY, YXZ, YZX, ZXY, ZYX)
    """
    bone = armature.pose.bones.get(bone_name)
    if bone:
        bone.rotation_mode = mode
        bone.rotation_euler = rotation
        bone.keyframe_insert(data_path="rotation_euler", frame=frame)


def keyframe_bone_quaternion(armature, bone_name: str, frame: int,
                             quaternion: Tuple[float, float, float, float]):
    """Insert a pose bone quaternion rotation keyframe."""
    bone = armature.pose.bones.get(bone_name)
    if bone:
        bone.rotation_mode = 'QUATERNION'
        bone.rotation_quaternion = quaternion
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)


# === Animation Patterns ===

def create_loop_keyframes(obj, data_path: str, values: List,
                          frame_start: int, frame_duration: int):
    """Create looping keyframes from a list of values.

    Args:
        obj: Object to animate
        data_path: Property path (e.g., "location", "rotation_euler")
        values: List of values for each keyframe
        frame_start: Starting frame
        frame_duration: Total frames for the loop
    """
    frames_per_value = frame_duration // len(values)

    for i, value in enumerate(values):
        frame = frame_start + (i * frames_per_value)
        setattr(obj, data_path, value)
        obj.keyframe_insert(data_path=data_path, frame=frame)

    # Close the loop
    setattr(obj, data_path, values[0])
    obj.keyframe_insert(data_path=data_path, frame=frame_start + frame_duration)


def create_bounce(obj, height: float, duration: int, start_frame: int = 1):
    """Create a bouncing animation.

    Args:
        obj: Object to animate
        height: Maximum bounce height
        duration: Duration of one bounce cycle in frames
        start_frame: Starting frame
    """
    base_z = obj.location.z
    keyframe_location(obj, start_frame, tuple(obj.location))

    # Peak
    peak_frame = start_frame + duration // 2
    keyframe_location(obj, peak_frame, (obj.location.x, obj.location.y, base_z + height))

    # Land
    end_frame = start_frame + duration
    keyframe_location(obj, end_frame, (obj.location.x, obj.location.y, base_z))

    set_interpolation(obj, 'SINE')


def create_oscillate(obj, axis: str, amplitude: float, period: int,
                     start_frame: int = 1, cycles: int = 1):
    """Create oscillating motion (like pendulum).

    Args:
        obj: Object to animate
        axis: 'X', 'Y', or 'Z'
        amplitude: Maximum rotation in radians
        period: Frames per full oscillation
        start_frame: Starting frame
        cycles: Number of oscillation cycles
    """
    axis_idx = {'X': 0, 'Y': 1, 'Z': 2}[axis.upper()]

    for cycle in range(cycles):
        cycle_start = start_frame + (cycle * period)

        # Center
        rot = list(obj.rotation_euler)
        rot[axis_idx] = 0
        keyframe_rotation(obj, cycle_start, tuple(rot))

        # Max positive
        rot[axis_idx] = amplitude
        keyframe_rotation(obj, cycle_start + period // 4, tuple(rot))

        # Center
        rot[axis_idx] = 0
        keyframe_rotation(obj, cycle_start + period // 2, tuple(rot))

        # Max negative
        rot[axis_idx] = -amplitude
        keyframe_rotation(obj, cycle_start + 3 * period // 4, tuple(rot))

        # Center (close loop)
        rot[axis_idx] = 0
        keyframe_rotation(obj, cycle_start + period, tuple(rot))

    set_interpolation(obj, 'SINE')


def create_spin(obj, axis: str, revolutions: float, duration: int,
                start_frame: int = 1):
    """Create spinning animation.

    Args:
        obj: Object to animate
        axis: 'X', 'Y', or 'Z'
        revolutions: Number of full rotations
        duration: Animation duration in frames
        start_frame: Starting frame
    """
    axis_idx = {'X': 0, 'Y': 1, 'Z': 2}[axis.upper()]

    rot = list(obj.rotation_euler)
    rot[axis_idx] = 0
    keyframe_rotation(obj, start_frame, tuple(rot))

    rot[axis_idx] = revolutions * 2 * math.pi
    keyframe_rotation(obj, start_frame + duration, tuple(rot))

    set_interpolation(obj, 'LINEAR')


def create_bob(obj, amplitude: float, frequency: float, duration: int,
               start_frame: int = 1):
    """Create gentle bobbing animation (floating effect).

    Args:
        obj: Object to animate
        amplitude: Vertical movement range
        frequency: Bobs per duration
        duration: Animation duration in frames
        start_frame: Starting frame
    """
    base_z = obj.location.z
    frames_per_bob = int(duration / frequency)

    for i in range(int(frequency) + 1):
        frame = start_frame + (i * frames_per_bob)
        offset = amplitude if i % 2 == 0 else -amplitude
        keyframe_location(obj, frame, (obj.location.x, obj.location.y, base_z + offset))

    set_interpolation(obj, 'SINE')


# === Export ===

def export_animation_glb(filepath: str, armature=None):
    """Export animation to GLB format.

    Args:
        filepath: Output file path
        armature: Optional armature to select (exports selected only)
    """
    if not HAS_BPY:
        return

    if armature:
        bpy.ops.object.select_all(action='DESELECT')
        armature.select_set(True)
        if armature.children:
            for child in armature.children:
                child.select_set(True)

    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        use_selection=armature is not None,
        export_animations=True,
        export_frame_range=True,
        export_yup=True,
    )
    print(f"Exported animation: {filepath}")


def bake_animation(obj, frame_start: int, frame_end: int,
                   only_selected: bool = False):
    """Bake animation to keyframes.

    Useful for converting procedural animations to keyframe data.
    """
    if not HAS_BPY:
        return

    bpy.context.view_layer.objects.active = obj
    bpy.ops.nla.bake(
        frame_start=frame_start,
        frame_end=frame_end,
        only_selected=only_selected,
        visual_keying=True,
        clear_constraints=False,
        bake_types={'OBJECT'}
    )
