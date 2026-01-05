"""
Animation Parser - Interprets .spec.py animation specs in Blender.

Applies structured animation specifications to armatures, creating keyframed
animations. Skeleton-agnostic: works with any armature if bone names match.

Usage (standalone):
    blender --background --python animation.py -- \\
        animation_spec.spec.py \\
        armature.glb \\
        output.glb

Usage (via generate.py):
    Place .spec.py files in .studio/specs/animations/
    Run: python .studio/generate.py --only animations

Arguments:
    animation_spec.spec.py - Path to animation spec file (contains ANIMATION dict)
    armature.glb - Input armature/character GLB
    output.glb - Output path for animated GLB

Example:
    blender --background --python animation.py -- \\
        .studio/specs/animations/patch_idle.spec.py \\
        assets/characters/patch.glb \\
        assets/animations/patch_idle.glb
"""

import bpy
import math
import sys


# Blender version compatibility
BLENDER_VERSION = bpy.app.version
IS_BLENDER_5_PLUS = BLENDER_VERSION[0] >= 5


def get_action_fcurves(action):
    """
    Get FCurves from action, handling Blender 4.x vs 5.0+ API differences.

    Blender 5.0 changed from action.fcurves to action.layers[].strips[].channelbags[].fcurves
    """
    if IS_BLENDER_5_PLUS:
        # Blender 5.0+ layered animation system
        fcurves = []
        for layer in action.layers:
            for strip in layer.strips:
                for channelbag in strip.channelbags:
                    fcurves.extend(channelbag.fcurves)
        return fcurves
    else:
        # Blender 4.x and earlier
        return action.fcurves


def load_spec(spec_path):
    """Load animation spec from .spec.py file.

    Supports both ANIMATION and MOTION dict names for backwards compatibility.
    """
    with open(spec_path, 'r') as f:
        code = f.read()

    # Execute the spec file to get ANIMATION or MOTION dict
    namespace = {}
    exec(code, namespace)

    # Support both new ANIMATION and legacy MOTION names
    if 'ANIMATION' in namespace:
        return namespace['ANIMATION']
    elif 'MOTION' in namespace:
        return namespace['MOTION']
    else:
        raise ValueError(f"No ANIMATION or MOTION dict found in {spec_path}")


# Backwards compatibility alias
load_motion_spec = load_spec


def find_armature():
    """Find the armature object in the scene."""
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            return obj
    raise ValueError("No armature found in scene")


def apply_pose(armature, pose_data, frame):
    """
    Apply a pose to armature at specified frame.

    Args:
        armature: Blender armature object
        pose_data: Dict of {bone_name: {pitch, yaw, roll}}
        frame: Frame number for keyframe
    """
    bpy.context.scene.frame_set(frame)

    for bone_name, rotation in pose_data.items():
        if bone_name not in armature.pose.bones:
            print(f"Warning: Bone '{bone_name}' not found in armature, skipping")
            continue

        bone = armature.pose.bones[bone_name]
        bone.rotation_mode = 'XYZ'

        # Convert degrees to radians (pitch=X, yaw=Y, roll=Z)
        pitch = math.radians(rotation.get('pitch', 0))
        yaw = math.radians(rotation.get('yaw', 0))
        roll = math.radians(rotation.get('roll', 0))

        bone.rotation_euler = (pitch, yaw, roll)
        bone.keyframe_insert(data_path='rotation_euler', frame=frame)


def apply_timing_curve(action, timing_curve, start_frame, end_frame):
    """
    Apply interpolation mode to FCurves in frame range.

    Args:
        action: Blender action containing FCurves
        timing_curve: String like 'linear', 'ease_in', 'ease_out', etc.
        start_frame: Start of frame range
        end_frame: End of frame range
    """
    # Map timing_curve strings to Blender interpolation settings
    curve_settings = {
        'linear': ('LINEAR', None),
        'ease_in': ('SINE', 'EASE_IN'),
        'ease_out': ('SINE', 'EASE_OUT'),
        'ease_in_out': ('SINE', 'AUTO'),
        'exponential_in': ('EXPO', 'EASE_IN'),
        'exponential_out': ('EXPO', 'EASE_OUT'),
        'constant': ('CONSTANT', None),
    }

    interp, easing = curve_settings.get(timing_curve, ('LINEAR', None))

    for fcurve in get_action_fcurves(action):
        for keyframe in fcurve.keyframe_points:
            # Apply to keyframes in the phase's frame range
            if start_frame <= keyframe.co[0] <= end_frame:
                keyframe.interpolation = interp
                if easing and hasattr(keyframe, 'easing'):
                    keyframe.easing = easing


def apply_procedural_layer(action, layer, duration_frames, fps):
    """
    Add FCurve modifier for procedural motion (breathing, sway, noise).

    Args:
        action: Blender action to modify
        layer: Layer specification dict
        duration_frames: Total animation duration
        fps: Frames per second
    """
    layer_type = layer.get('type')
    target_bone = layer.get('target')
    axis = layer.get('axis', 'pitch')

    # Map axis to rotation_euler index
    axis_map = {'pitch': 0, 'yaw': 1, 'roll': 2}
    axis_index = axis_map.get(axis, 0)

    # Find the FCurve for this bone's rotation axis
    target_path = f'pose.bones["{target_bone}"].rotation_euler'
    fcurve = None

    for fc in get_action_fcurves(action):
        if fc.data_path == target_path and fc.array_index == axis_index:
            fcurve = fc
            break

    # If no existing FCurve, create keyframes first
    if fcurve is None:
        print(f"Warning: No FCurve for {target_bone}.{axis}, creating baseline")
        return

    if layer_type in ('breathing', 'sway', 'bob'):
        # Add CYCLES modifier for looping sine wave
        mod = fcurve.modifiers.new(type='CYCLES')
        mod.mode_before = 'REPEAT'
        mod.mode_after = 'REPEAT'

        # Add NOISE modifier for sine-like effect
        noise = fcurve.modifiers.new(type='NOISE')
        noise.scale = layer.get('period_frames', 60) / fps
        noise.strength = layer.get('amplitude', 0.01) * 100  # Scale for visibility
        noise.phase = 0

    elif layer_type == 'noise':
        # Add NOISE modifier for random micro-motion
        noise = fcurve.modifiers.new(type='NOISE')
        noise.scale = 1.0 / layer.get('frequency', 0.5)
        noise.strength = layer.get('amplitude', 0.005) * 100
        noise.phase = hash(target_bone) % 100  # Different phase per bone


def setup_ik_and_bake(armature, ik_hints, duration_frames):
    """
    Set up IK constraints and bake to FK for export.

    Note: This is a simplified implementation. Full IK setup should use
    the ik-utilities.md patterns for proper leg/arm IK chains.
    """
    if not ik_hints:
        return

    # For ground_contact, we'd set up leg IK targets
    # This requires more complex setup - see ik-utilities.md
    # For now, we just note that IK should be handled

    feet_mode = ik_hints.get('feet')
    hands_mode = ik_hints.get('hands')

    if feet_mode == 'ground_contact':
        print("Note: Foot IK requested. For production, use ik-utilities.md setup.")
        print("      This parser applies FK poses directly. Add IK post-process if needed.")

    if hands_mode == 'target_position':
        print("Note: Hand IK requested. For production, use ik-utilities.md setup.")


def apply_motion(spec, armature):
    """
    Apply full motion spec to armature, creating action with keyframes.

    Args:
        spec: MOTION dict from .motion.py file
        armature: Blender armature object

    Returns:
        Created action
    """
    anim = spec['animation']

    # Scene setup
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = anim['duration_frames']
    bpy.context.scene.render.fps = anim.get('fps', 30)

    # Create new action
    action_name = anim['name']
    action = bpy.data.actions.new(action_name)

    # Ensure armature has animation data
    if armature.animation_data is None:
        armature.animation_data_create()
    armature.animation_data.action = action

    # Make armature active
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)

    # Get poses and phases
    poses = anim.get('poses', {})
    phases = anim.get('phases', [])

    # Apply each phase
    for phase in phases:
        pose_name = phase['pose']
        if pose_name not in poses:
            print(f"Warning: Pose '{pose_name}' not found, skipping phase '{phase['name']}'")
            continue

        pose_data = poses[pose_name]
        start_frame = phase['frames'][0]

        # Apply pose at start of phase
        apply_pose(armature, pose_data, start_frame)

    # Apply timing curves after all keyframes are set
    for phase in phases:
        timing_curve = phase.get('timing_curve', 'linear')
        start_frame, end_frame = phase['frames']
        apply_timing_curve(action, timing_curve, start_frame, end_frame)

    # Apply procedural layers
    for layer in anim.get('procedural_layers', []):
        apply_procedural_layer(
            action,
            layer,
            anim['duration_frames'],
            anim.get('fps', 30)
        )

    # Handle IK hints
    setup_ik_and_bake(armature, anim.get('ik_hints'), anim['duration_frames'])

    print(f"Created action '{action_name}' with {len(phases)} phases")
    return action


def export_glb(output_path):
    """Export scene as GLB with animations."""
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_animations=True,
        export_animation_mode='ACTIONS',
        export_skins=True,
        export_all_influences=False,  # Max 4 bones per vertex for ZX
    )
    print(f"Exported to {output_path}")


def generate_animation(spec, output_path, input_glb=None):
    """
    Generate animation from spec dict.

    This is the main entry point when called from generate.py.
    For standalone usage, use main() via command line.

    Args:
        spec: ANIMATION dict from .spec.py file
        output_path: Path for output GLB
        input_glb: Optional input armature GLB. If None, uses spec['input_armature']
    """
    # Get input armature path
    if input_glb is None:
        input_glb = spec.get('animation', spec).get('input_armature')
        if not input_glb:
            raise ValueError("No input_armature specified in spec or arguments")

    # Clear default scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import the armature
    bpy.ops.import_scene.gltf(filepath=input_glb)

    # Find armature
    armature = find_armature()
    print(f"Found armature: {armature.name}")

    # Apply animation
    apply_motion(spec, armature)

    # Export
    export_glb(output_path)


def main():
    """Main entry point for command-line usage."""
    # Parse arguments after '--'
    argv = sys.argv
    if '--' in argv:
        args = argv[argv.index('--') + 1:]
    else:
        print("Usage: blender --background --python animation.py -- "
              "spec.spec.py input.glb output.glb")
        sys.exit(1)

    if len(args) < 3:
        print("Error: Need animation_spec, input_glb, and output_glb paths")
        sys.exit(1)

    spec_path = args[0]
    input_glb = args[1]
    output_glb = args[2]

    print(f"Loading animation spec: {spec_path}")
    print(f"Input armature: {input_glb}")
    print(f"Output: {output_glb}")

    # Load spec and generate
    spec = load_spec(spec_path)
    generate_animation(spec, output_glb, input_glb)

    print("Done!")


if __name__ == "__main__":
    main()
