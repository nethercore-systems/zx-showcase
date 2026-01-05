"""
Character Parser - Interprets .spec.py files and generates character meshes.

Deterministic character generation from declarative specs. Follows the same pattern
as animation.py for animations and sound.py for audio.

Usage:
    blender --background --python character_parser.py -- \\
        character.spec.py \\
        output.glb

Arguments:
    character.spec.py - Path to character spec file (contains SPEC dict)
    output.glb        - Output path for character GLB

Example:
    blender --background --python character_parser.py -- \\
        .studio/characters/knight.spec.py \\
        assets/characters/knight.glb
"""

import bpy
import bmesh
import mathutils
from mathutils import Vector, Matrix
import math
import sys


# =============================================================================
# BLENDER VERSION COMPATIBILITY
# =============================================================================

BLENDER_VERSION = bpy.app.version
IS_BLENDER_4_PLUS = BLENDER_VERSION[0] >= 4


# =============================================================================
# SPEC LOADING
# =============================================================================

def load_spec(spec_path):
    """Load spec from .spec.py file via exec()."""
    with open(spec_path, 'r') as f:
        code = f.read()

    namespace = {}
    exec(code, namespace)

    if 'SPEC' not in namespace:
        raise ValueError(f"No SPEC dict found in {spec_path}")

    return namespace['SPEC']


# =============================================================================
# SCENE MANAGEMENT
# =============================================================================

def clear_scene():
    """Remove all objects from scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


# =============================================================================
# ARMATURE CREATION
# =============================================================================

def create_armature(skeleton_spec):
    """Create armature from skeleton definition."""
    bpy.ops.object.armature_add(enter_editmode=True)
    armature = bpy.context.active_object
    armature.name = "Armature"

    # Remove default bone
    bpy.ops.armature.select_all(action='SELECT')
    bpy.ops.armature.delete()

    arm_data = armature.data
    bones_created = {}

    for bone_def in skeleton_spec:
        if 'mirror' in bone_def:
            # Handle mirrored bones
            src = bones_created[bone_def['mirror']]
            bone = arm_data.edit_bones.new(bone_def['bone'])
            bone.head = mathutils.Vector(src.head)
            bone.head.x *= -1
            bone.tail = mathutils.Vector(src.tail)
            bone.tail.x *= -1
            if src.parent:
                parent_name = src.parent.name.replace('_L', '_R')
                bone.parent = arm_data.edit_bones.get(parent_name)
        else:
            bone = arm_data.edit_bones.new(bone_def['bone'])
            bone.head = mathutils.Vector(bone_def['head'])
            bone.tail = mathutils.Vector(bone_def['tail'])
            if bone_def.get('parent'):
                bone.parent = arm_data.edit_bones.get(bone_def['parent'])

        bones_created[bone_def['bone']] = bone

    bpy.ops.object.mode_set(mode='OBJECT')
    return armature


def get_bone_transform(armature, bone_name):
    """Get transformation matrix to align mesh along bone."""
    bone = armature.pose.bones[bone_name]

    # Bone direction
    head = armature.matrix_world @ bone.head
    tail = armature.matrix_world @ bone.tail
    direction = (tail - head).normalized()

    # Build rotation matrix (Z-up to bone direction)
    z_axis = mathutils.Vector((0, 0, 1))
    rotation = z_axis.rotation_difference(direction).to_matrix().to_4x4()

    # Translation to bone head
    translation = mathutils.Matrix.Translation(head)

    return translation @ rotation


# =============================================================================
# MESH MODIFIERS (BULGE/TILT)
# =============================================================================

def apply_bulge(vertices, center, bone_dir, bulge):
    """Asymmetric radial push. + = front bulges, - = back bulges."""
    if isinstance(bulge, (list, tuple)):
        bulge_side, bulge_fb = bulge[0], bulge[1] if len(bulge) > 1 else 0
    else:
        bulge_side, bulge_fb = 0, bulge

    up = Vector((0, 0, 1))
    if abs(bone_dir.z) > 0.9:
        forward, right = Vector((0, 1, 0)), Vector((1, 0, 0))
    else:
        right = bone_dir.cross(up).normalized()
        forward = right.cross(bone_dir).normalized()

    for v in vertices:
        radial = (v.co - center).normalized()
        if abs(bulge_fb) > 0.0001:
            facing = radial.dot(forward)
            alignment = max(0, facing * (1 if bulge_fb > 0 else -1))
            v.co += radial * alignment * abs(bulge_fb)
        if abs(bulge_side) > 0.0001:
            facing = abs(radial.dot(right))
            v.co += radial * facing * bulge_side


def apply_tilt(vertices, center, bone_dir, tilt):
    """Rotate face perpendicular to bone axis."""
    if isinstance(tilt, (list, tuple)):
        tilt_x, tilt_y = tilt[0], tilt[1] if len(tilt) > 1 else 0
    else:
        tilt_x, tilt_y = tilt, 0

    if abs(tilt_x) < 0.001 and abs(tilt_y) < 0.001:
        return

    up = Vector((0, 0, 1))
    if abs(bone_dir.z) > 0.9:
        right_axis, forward_axis = Vector((1, 0, 0)), Vector((0, 1, 0))
    else:
        right_axis = bone_dir.cross(up).normalized()
        forward_axis = right_axis.cross(bone_dir).normalized()

    rot = Matrix.Identity(4)
    if abs(tilt_x) > 0.001:
        rot = Matrix.Rotation(math.radians(tilt_x), 4, right_axis) @ rot
    if abs(tilt_y) > 0.001:
        rot = Matrix.Rotation(math.radians(tilt_y), 4, forward_axis) @ rot

    for v in vertices:
        v.co = center + rot @ (v.co - center)


# =============================================================================
# BODY PART CONSTRUCTION
# =============================================================================

def parse_step_string(step_str):
    """Parse step string like 'extrude: 0.05, scale: 1.15' to dict."""
    import ast
    result = {}
    parts = step_str.split(',')
    for part in parts:
        key, value = part.split(':')
        key = key.strip()
        value = value.strip()
        try:
            if value.startswith('['):
                result[key] = ast.literal_eval(value)
            else:
                result[key] = float(value)
        except:
            result[key] = value
    return result


def build_body_part(spec, armature):
    """Build mesh from extrude+scale sequence, oriented to bone."""

    # Parse base shape
    base_str = spec['base']
    if '(' in base_str:
        verts = int(base_str.split('(')[1].rstrip(')'))
    else:
        verts = 6  # default hexagon

    # Handle offset (for sub-parts like thumbs, hair)
    offset = spec.get('offset', [0, 0, 0])

    # Create cylinder (will be transformed to bone orientation)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=verts,
        radius=spec['base_radius'],
        depth=0.001,  # nearly flat disc
        end_fill_type='NGON',
        location=tuple(offset)
    )
    obj = bpy.context.active_object

    # Apply initial rotation if specified (for angled parts like thumbs)
    if 'rotation' in spec:
        rot = spec['rotation']  # [rx, ry, rz] in degrees
        obj.rotation_euler = (
            math.radians(rot[0]),
            math.radians(rot[1]),
            math.radians(rot[2])
        )
        bpy.ops.object.transform_apply(rotation=True)

    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)

    # Delete bottom face if cap_start is False
    if not spec.get('cap_start', True):
        bm.faces.ensure_lookup_table()
        for face in bm.faces:
            if face.calc_center_median().z < 0:
                bm.faces.remove(face)
                break

    bmesh.update_edit_mesh(obj.data)

    # Select top face for extrusion
    bpy.ops.mesh.select_all(action='DESELECT')
    bm = bmesh.from_edit_mesh(obj.data)
    bm.faces.ensure_lookup_table()

    for face in bm.faces:
        if face.calc_center_median().z > 0:
            face.select = True

    bmesh.update_edit_mesh(obj.data)

    # Get bone direction for bulge/tilt orientation
    bone = armature.pose.bones[spec['bone']]
    bone_head = armature.matrix_world @ bone.head
    bone_tail = armature.matrix_world @ bone.tail
    bone_dir = (bone_tail - bone_head).normalized()

    # Execute step sequence
    for step in spec['steps']:
        if isinstance(step, str):
            step = parse_step_string(step)

        # Extrude
        extrude_dist = step.get('extrude', 0.1)
        bpy.ops.mesh.extrude_region_move(
            TRANSFORM_OT_translate={"value": (0, 0, extrude_dist)}
        )

        # Scale
        scale = step.get('scale', 1.0)
        if isinstance(scale, (int, float)):
            scale_vec = (scale, scale, 1.0)
        elif len(scale) == 2:
            scale_vec = (scale[0], scale[1], 1.0)
        else:
            scale_vec = tuple(scale)
        bpy.ops.transform.resize(value=scale_vec)

        # Translate
        if 'translate' in step:
            bpy.ops.transform.translate(value=tuple(step['translate']))

        # Rotate
        if 'rotate' in step:
            bpy.ops.transform.rotate(
                value=math.radians(step['rotate']),
                orient_axis='Z'
            )

        # Bulge/Tilt - requires bmesh access
        if 'bulge' in step or 'tilt' in step:
            bm = bmesh.from_edit_mesh(obj.data)
            sel_verts = [v for v in bm.verts if v.select]
            if sel_verts:
                center = sum((v.co for v in sel_verts), Vector()) / len(sel_verts)
                if 'bulge' in step:
                    apply_bulge(sel_verts, center, bone_dir, step['bulge'])
                if 'tilt' in step:
                    apply_tilt(sel_verts, center, bone_dir, step['tilt'])
                bmesh.update_edit_mesh(obj.data)

    # Cap end if specified
    if spec.get('cap_end', True):
        bpy.ops.mesh.fill()

    bpy.ops.object.mode_set(mode='OBJECT')

    # Transform to bone orientation
    bone_name = spec['bone']
    transform = get_bone_transform(armature, bone_name)
    obj.matrix_world = transform

    # Apply transform
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Parent to bone
    obj.parent = armature
    obj.parent_type = 'BONE'
    obj.parent_bone = bone_name

    return obj


def build_instances(part_spec, armature, part_name):
    """Build multiple instances of a part at different positions/rotations.

    Used for hair spikes, decorative elements, etc.
    """
    instances = part_spec.get('instances', [])
    meshes = []

    for i, instance in enumerate(instances):
        # Clone spec with instance-specific transforms
        inst_spec = part_spec.copy()
        inst_spec['offset'] = instance.get('position', [0, 0, 0])
        inst_spec['rotation'] = instance.get('rotation', [0, 0, 0])

        # Remove instances to prevent recursion
        if 'instances' in inst_spec:
            del inst_spec['instances']

        mesh = build_body_part(inst_spec, armature)
        mesh.name = f"{part_name}_{i}"
        meshes.append(mesh)

    return meshes


# =============================================================================
# VALIDATION
# =============================================================================

def estimate_tris(spec):
    """Estimate triangle count from spec."""
    total = 0
    parts = spec.get('parts', {})

    for part_name, part_spec in parts.items():
        if 'mirror' in part_spec:
            src = part_spec['mirror']
            if src in parts:
                part_spec = parts[src]
            else:
                continue

        base_str = part_spec.get('base', 'hexagon(6)')
        if '(' in base_str:
            verts = int(base_str.split('(')[1].rstrip(')'))
        else:
            verts = 6

        steps = len(part_spec.get('steps', []))
        tris_per_step = verts * 2

        # Count caps
        caps = 0
        if part_spec.get('cap_start', True):
            caps += verts - 2
        if part_spec.get('cap_end', True):
            caps += verts - 2

        part_tris = (tris_per_step * steps) + caps
        total += part_tris

        # Instances multiply
        instances = part_spec.get('instances', [])
        if instances:
            total += part_tris * (len(instances) - 1)

    return total


def check_seam_compatibility(parts, warnings):
    """Check that connecting parts have compatible vertex counts."""
    connections = [
        ('torso', 'head'),
        ('arm_upper_L', 'arm_lower_L'),
        ('arm_upper_R', 'arm_lower_R'),
        ('leg_upper_L', 'leg_lower_L'),
        ('leg_upper_R', 'leg_lower_R'),
    ]

    for part_a, part_b in connections:
        if part_a not in parts or part_b not in parts:
            continue

        spec_a = parts[part_a]
        spec_b = parts[part_b]

        def get_verts(spec):
            if 'mirror' in spec:
                return None
            base = spec.get('base', 'hexagon(6)')
            if '(' in base:
                return int(base.split('(')[1].rstrip(')'))
            return 6

        verts_a = get_verts(spec_a)
        verts_b = get_verts(spec_b)

        if verts_a and verts_b and verts_a != verts_b:
            warnings.append(
                f"Seam mismatch: {part_a}({verts_a} verts) -> {part_b}({verts_b} verts)"
            )


def validate_spec(spec):
    """Validate character spec before generation.

    Raises ValueError if spec has issues.
    """
    errors = []
    warnings = []

    char = spec.get('character', spec)

    # Check triangle budget
    budget = char.get('tri_budget', 500)
    estimated = estimate_tris(char)
    if estimated > budget:
        errors.append(f"Triangle budget exceeded: ~{estimated} > {budget}")
    elif estimated > budget * 0.9:
        warnings.append(f"Near triangle budget: ~{estimated} / {budget}")

    # Check skeleton
    skeleton = char.get('skeleton', [])
    if not skeleton:
        errors.append("No skeleton defined")

    bone_names = set()
    for bone_def in skeleton:
        name = bone_def.get('bone')
        if name in bone_names:
            errors.append(f"Duplicate bone name: {name}")
        bone_names.add(name)

        # Check parent exists (except for root)
        parent = bone_def.get('parent')
        if parent and parent not in bone_names and 'mirror' not in bone_def:
            errors.append(f"Bone '{name}' references unknown parent '{parent}'")

    # Check parts reference valid bones
    parts = char.get('parts', {})
    for part_name, part_spec in parts.items():
        if 'mirror' in part_spec:
            continue
        bone = part_spec.get('bone')
        if bone and bone not in bone_names:
            errors.append(f"Part '{part_name}' references unknown bone '{bone}'")

    # Check seam compatibility
    check_seam_compatibility(parts, warnings)

    if errors:
        raise ValueError("Spec validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    if warnings:
        print("Spec warnings:\n" + "\n".join(f"  - {w}" for w in warnings))

    return True


# =============================================================================
# UV MAPPING
# =============================================================================

def apply_uvs(obj, spec):
    """Apply UV mapping to character mesh."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    uv_mode = spec.get('texturing', {}).get('uv_mode', 'smart_project')

    if uv_mode == 'smart_project':
        bpy.ops.uv.smart_project(
            angle_limit=66,
            island_margin=0.02,
            scale_to_bounds=True
        )
    elif uv_mode == 'region_based':
        regions = spec.get('texturing', {}).get('regions', {})
        apply_region_uvs(obj, regions)

    bpy.ops.object.mode_set(mode='OBJECT')


def apply_region_uvs(obj, regions):
    """Apply region-based UV mapping for texture atlas compatibility."""
    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()

    for region_name, region_spec in regions.items():
        uv_rect = region_spec.get('uv_rect', [0, 0, 1, 1])

        vg = obj.vertex_groups.get(region_name)
        if vg is None:
            continue

        vg_index = vg.index

        for face in bm.faces:
            in_region = False
            for vert in face.verts:
                for group in obj.data.vertices[vert.index].groups:
                    if group.group == vg_index and group.weight > 0.5:
                        in_region = True
                        break
                if in_region:
                    break

            if in_region:
                for loop in face.loops:
                    uv = loop[uv_layer].uv
                    uv.x = uv_rect[0] + uv.x * uv_rect[2]
                    uv.y = uv_rect[1] + uv.y * uv_rect[3]

    bmesh.update_edit_mesh(obj.data)


# =============================================================================
# MESH MERGING AND SKINNING
# =============================================================================

def merge_and_skin(parts, armature, spec=None):
    """Merge all parts into single mesh with automatic weights and UVs."""

    # Select all parts
    bpy.ops.object.select_all(action='DESELECT')
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]

    # Join into single mesh
    bpy.ops.object.join()
    merged = bpy.context.active_object
    merged.name = "Character"

    # Weld vertices at seams
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.002)  # 2mm tolerance
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Apply UV mapping
    if spec:
        apply_uvs(merged, spec)

    # Apply smooth skinning with automatic weights
    bpy.ops.object.select_all(action='DESELECT')
    merged.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature

    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    # Limit bone influences to 4 (ZX requirement)
    bpy.context.view_layer.objects.active = merged
    bpy.ops.object.vertex_group_limit_total(limit=4)

    return merged


# =============================================================================
# CHARACTER GENERATION
# =============================================================================

def generate_character(spec):
    """Generate complete character from spec."""

    validate_spec(spec)

    char = spec.get('character', spec)

    # Create armature first
    armature = create_armature(char['skeleton'])

    parts = []

    for part_name, part_spec in char['parts'].items():
        # Handle mirrored parts
        if 'mirror' in part_spec:
            src_spec = char['parts'][part_spec['mirror']].copy()
            src_spec['bone'] = part_name
            part_spec = src_spec

        # Handle instanced parts (hair spikes, etc.)
        if 'instances' in part_spec:
            instance_meshes = build_instances(part_spec, armature, part_name)
            parts.extend(instance_meshes)
        else:
            mesh = build_body_part(part_spec, armature)
            mesh.name = part_name
            parts.append(mesh)

        # Handle sub-parts (fingers, thumb)
        for sub_key in ['thumb', 'fingers']:
            if sub_key in part_spec:
                sub_parts = part_spec[sub_key]
                if not isinstance(sub_parts, list):
                    sub_parts = [sub_parts]
                for sub_spec in sub_parts:
                    if 'bone' not in sub_spec:
                        sub_spec['bone'] = part_spec.get('bone')
                    sub_mesh = build_body_part(sub_spec, armature)
                    sub_mesh.name = f"{part_name}_{sub_spec.get('name', sub_key)}"
                    parts.append(sub_mesh)

    # Merge into single mesh with smooth skinning and UVs
    merged = merge_and_skin(parts, armature, char)

    return armature, merged


# =============================================================================
# EXPORT
# =============================================================================

def export_character(armature, merged, filepath):
    """Export character as GLB."""
    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(True)
    merged.select_set(True)
    bpy.context.view_layer.objects.active = armature

    bpy.ops.export_scene.gltf(
        filepath=filepath,
        use_selection=True,
        export_format='GLB',
        export_animations=False,  # Animations handled separately
        export_skins=True,
        export_all_influences=False  # Limit to 4 bones/vertex
    )

    print(f"Exported to {filepath}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point for command-line usage."""
    # Parse arguments after '--'
    argv = sys.argv
    if '--' in argv:
        args = argv[argv.index('--') + 1:]
    else:
        print("Usage: blender --background --python character_parser.py -- "
              "spec.spec.py output.glb")
        sys.exit(1)

    if len(args) < 2:
        print("Error: Need spec_path and output_glb paths")
        sys.exit(1)

    spec_path = args[0]
    output_glb = args[1]

    print(f"Loading character spec: {spec_path}")
    print(f"Output: {output_glb}")

    # Clear default scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Load spec
    spec = load_spec(spec_path)

    # Generate character
    armature, merged = generate_character(spec)

    # Report stats
    char = spec.get('character', spec)
    tri_count = len(merged.data.polygons)
    budget = char.get('tri_budget', 500)
    print(f"Triangle count: {tri_count} / {budget}")

    # Export
    export_character(armature, merged, output_glb)

    print("Done!")


if __name__ == "__main__":
    main()
