"""
Blender Metaball-based Mesh Generation for Organic Creatures.

This module provides metaball primitives for creating smooth, organic shapes
like fish, jellyfish, and other sea creatures. Metaballs automatically blend
together creating natural organic forms.

Usage:
    from procgen.core.blender_metaball import MetaballCreature, export_metaball_creature

    creature = MetaballCreature("jellyfish")
    creature.add_ball(0, 0, 0, radius=0.3)  # Body
    creature.add_ball(0, 0, 0.2, radius=0.15)  # Top
    export_metaball_creature(creature, output_path, base_color=(0.2, 0.5, 0.8))
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import math

try:
    import bpy
    import bmesh
    from mathutils import Vector
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False
    bpy = None
    bmesh = None


@dataclass
class MetaElement:
    """A single metaball element."""
    x: float
    y: float
    z: float
    radius: float
    type: str = "BALL"  # BALL, CAPSULE, PLANE, ELLIPSOID, CUBE
    stiffness: float = 2.0  # How quickly it blends with neighbors (0.5-10)
    # For ellipsoid/capsule
    size_x: float = 1.0
    size_y: float = 1.0
    size_z: float = 1.0
    # For capsule direction
    rotation: Tuple[float, float, float] = (0, 0, 0)  # Euler angles in radians


@dataclass
class MetaballCreature:
    """Collection of metaball elements forming a creature."""
    name: str
    elements: List[MetaElement] = field(default_factory=list)
    resolution: float = 0.08  # Lower = smoother but more polys
    threshold: float = 0.0  # Surface threshold

    def add_ball(
        self,
        x: float, y: float, z: float,
        radius: float,
        stiffness: float = 2.0
    ) -> 'MetaballCreature':
        """Add a spherical metaball element."""
        self.elements.append(MetaElement(
            x=x, y=y, z=z, radius=radius,
            type="BALL", stiffness=stiffness
        ))
        return self

    def add_ellipsoid(
        self,
        x: float, y: float, z: float,
        radius: float,
        size_x: float = 1.0, size_y: float = 1.0, size_z: float = 1.0,
        stiffness: float = 2.0,
        rotation: Tuple[float, float, float] = (0, 0, 0)
    ) -> 'MetaballCreature':
        """Add an ellipsoid metaball element."""
        self.elements.append(MetaElement(
            x=x, y=y, z=z, radius=radius,
            type="ELLIPSOID", stiffness=stiffness,
            size_x=size_x, size_y=size_y, size_z=size_z,
            rotation=rotation
        ))
        return self

    def add_capsule(
        self,
        x: float, y: float, z: float,
        radius: float,
        length: float = 1.0,
        stiffness: float = 2.0,
        rotation: Tuple[float, float, float] = (0, 0, 0)
    ) -> 'MetaballCreature':
        """Add a capsule metaball element (cylinder with rounded ends)."""
        self.elements.append(MetaElement(
            x=x, y=y, z=z, radius=radius,
            type="CAPSULE", stiffness=stiffness,
            size_x=length, size_y=1.0, size_z=1.0,
            rotation=rotation
        ))
        return self

    def add_chain(
        self,
        start: Tuple[float, float, float],
        end: Tuple[float, float, float],
        count: int,
        radius_start: float,
        radius_end: float,
        stiffness: float = 2.0
    ) -> 'MetaballCreature':
        """Add a chain of metaballs from start to end (great for tentacles)."""
        for i in range(count):
            t = i / (count - 1) if count > 1 else 0
            x = start[0] + t * (end[0] - start[0])
            y = start[1] + t * (end[1] - start[1])
            z = start[2] + t * (end[2] - start[2])
            radius = radius_start + t * (radius_end - radius_start)
            self.add_ball(x, y, z, radius, stiffness)
        return self

    def add_radial(
        self,
        cx: float, cy: float, cz: float,
        count: int,
        orbit_radius: float,
        ball_radius: float,
        z_offset: float = 0,
        stiffness: float = 2.0
    ) -> 'MetaballCreature':
        """Add metaballs arranged radially around a center (great for spines)."""
        for i in range(count):
            angle = (2 * math.pi * i) / count
            x = cx + orbit_radius * math.cos(angle)
            y = cy + orbit_radius * math.sin(angle)
            z = cz + z_offset
            self.add_ball(x, y, z, ball_radius, stiffness)
        return self


def ensure_blender():
    """Raise error if not running in Blender."""
    if not BLENDER_AVAILABLE:
        raise RuntimeError(
            "Blender not available. Run this script with:\n"
            "  blender --background --python script.py"
        )


def clear_scene():
    """Clear all objects from the current Blender scene."""
    ensure_blender()
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Clear orphaned data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.metaballs:
        if block.users == 0:
            bpy.data.metaballs.remove(block)


def create_metaball_object(creature: MetaballCreature) -> 'bpy.types.Object':
    """
    Create a Blender metaball object from MetaballCreature definition.

    Args:
        creature: MetaballCreature with elements

    Returns:
        Blender metaball object
    """
    ensure_blender()

    # Create metaball data
    mball = bpy.data.metaballs.new(creature.name)
    mball.resolution = creature.resolution
    mball.threshold = creature.threshold

    # Add elements
    for elem in creature.elements:
        mb_elem = mball.elements.new()
        mb_elem.co = (elem.x, elem.y, elem.z)
        mb_elem.radius = elem.radius
        mb_elem.stiffness = elem.stiffness

        if elem.type == "BALL":
            mb_elem.type = 'BALL'
        elif elem.type == "CAPSULE":
            mb_elem.type = 'CAPSULE'
            mb_elem.size_x = elem.size_x
        elif elem.type == "ELLIPSOID":
            mb_elem.type = 'ELLIPSOID'
            mb_elem.size_x = elem.size_x
            mb_elem.size_y = elem.size_y
            mb_elem.size_z = elem.size_z
        elif elem.type == "CUBE":
            mb_elem.type = 'CUBE'
        elif elem.type == "PLANE":
            mb_elem.type = 'PLANE'

        # Apply rotation if needed
        if elem.rotation != (0, 0, 0):
            mb_elem.rotation = elem.rotation

    # Create object
    obj = bpy.data.objects.new(creature.name, mball)
    bpy.context.collection.objects.link(obj)

    return obj


def convert_metaball_to_mesh(mball_obj: 'bpy.types.Object', name: str) -> 'bpy.types.Object':
    """
    Convert metaball object to a mesh object (for export).

    Due to Blender background mode limitations with metaballs, this function
    uses a mesh-sphere fallback approach if metaball conversion fails.

    Args:
        mball_obj: Blender metaball object
        name: Name for the resulting mesh

    Returns:
        Blender mesh object
    """
    ensure_blender()

    # Count elements before conversion
    mball_data = mball_obj.data
    elem_count = len(mball_data.elements) if hasattr(mball_data, 'elements') else 0
    print(f"  Metaball {name}: {elem_count} elements, resolution={mball_data.resolution}")

    # Make sure we're in object mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Deselect all, then select and activate the metaball
    bpy.ops.object.select_all(action='DESELECT')
    mball_obj.select_set(True)
    bpy.context.view_layer.objects.active = mball_obj

    # Force scene update
    bpy.context.view_layer.update()

    # Get the evaluated depsgraph
    depsgraph = bpy.context.evaluated_depsgraph_get()
    depsgraph.update()

    # Get evaluated object
    eval_obj = mball_obj.evaluated_get(depsgraph)

    # Try to create mesh from evaluated geometry
    mesh = bpy.data.meshes.new_from_object(eval_obj)

    if len(mesh.polygons) > 0:
        mesh.name = name
        mesh_obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(mesh_obj)
        mesh_obj.location = mball_obj.location
        mesh_obj.rotation_euler = mball_obj.rotation_euler
        mesh_obj.scale = mball_obj.scale
        bpy.data.objects.remove(mball_obj, do_unlink=True)
        print(f"  Converted {name}: {len(mesh.polygons)} polygons")
        return mesh_obj

    # Metaball conversion failed - use mesh-sphere fallback
    print(f"  Metaball background mode issue - using mesh fallback...")
    bpy.data.meshes.remove(mesh)

    # Cache element data before removing metaball
    elements_data = [(e.co.copy(), e.radius) for e in mball_data.elements]

    # Create mesh by joining UV spheres at each element position
    bpy.data.objects.remove(mball_obj, do_unlink=True)

    # Create combined mesh
    bm = bmesh.new()

    for co, radius in elements_data:
        # Create a UV sphere for each element
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=12,
            ring_count=8,
            radius=radius,
            location=(co[0], co[1], co[2])
        )
        sphere = bpy.context.active_object

        # Join into bmesh
        bm.from_mesh(sphere.data)

        # Delete the temporary sphere
        bpy.data.objects.remove(sphere, do_unlink=True)

    # Create the final mesh
    final_mesh = bpy.data.meshes.new(name)
    bm.to_mesh(final_mesh)
    bm.free()

    # Remove doubles to merge overlapping vertices
    mesh_obj = bpy.data.objects.new(name, final_mesh)
    bpy.context.collection.objects.link(mesh_obj)
    bpy.context.view_layer.objects.active = mesh_obj
    mesh_obj.select_set(True)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.01)
    bpy.ops.mesh.faces_shade_smooth()
    bpy.ops.object.mode_set(mode='OBJECT')

    # Apply subdivision for smoother result
    mod = mesh_obj.modifiers.new(name="Subsurf", type='SUBSURF')
    mod.levels = 1
    mod.render_levels = 1
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    poly_count = len(mesh_obj.data.polygons)
    print(f"  Mesh fallback {name}: {poly_count} polygons (from {elem_count} spheres)")

    return mesh_obj


def create_underwater_material(
    name: str,
    base_color: Tuple[float, float, float] = (0.5, 0.6, 0.7),
    emission_color: Optional[Tuple[float, float, float]] = None,
    emission_strength: float = 0.5,
    roughness: float = 0.4,
    subsurface: float = 0.2,  # For fleshy/translucent look
    alpha: float = 1.0,
    specular: float = 0.5,
) -> 'bpy.types.Material':
    """
    Create a material suitable for underwater creatures.

    Args:
        name: Material name
        base_color: RGB tuple (0-1 range)
        emission_color: Optional bioluminescence color
        emission_strength: Emission intensity
        roughness: Surface roughness
        subsurface: Subsurface scattering amount (translucency)
        alpha: Transparency (1.0 = opaque)
        specular: Specular reflection amount

    Returns:
        Blender material
    """
    ensure_blender()

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Specular IOR Level'].default_value = specular
    bsdf.inputs['Subsurface Weight'].default_value = subsurface

    # Subsurface color slightly lighter than base
    ss_color = tuple(min(1.0, c * 1.3) for c in base_color)
    bsdf.inputs['Subsurface Radius'].default_value = (ss_color[0], ss_color[1], ss_color[2])

    # Emission (bioluminescence)
    if emission_color:
        bsdf.inputs['Emission Color'].default_value = (*emission_color, 1.0)
        bsdf.inputs['Emission Strength'].default_value = emission_strength

    # Alpha/transparency
    if alpha < 1.0:
        bsdf.inputs['Alpha'].default_value = alpha
        mat.blend_method = 'BLEND'
        # shadow_method was removed in Blender 4.0+, use shadow_mode instead if available
        if hasattr(mat, 'shadow_mode'):
            mat.shadow_mode = 'HASHED'

    # Create Material Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat


def generate_smart_uvs(obj: 'bpy.types.Object'):
    """Generate smart UVs for a mesh object."""
    ensure_blender()

    # Deselect all first
    bpy.ops.object.select_all(action='DESELECT')

    # Make sure we're in object mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Select and activate the object
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Check if mesh has faces
    if len(obj.data.polygons) == 0:
        print(f"Warning: {obj.name} has no polygons, skipping UV generation")
        return

    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Select all geometry
    bpy.ops.mesh.select_all(action='SELECT')

    # Create UV layer if needed
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name='UVMap')

    # Generate UVs
    try:
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    except RuntimeError as e:
        print(f"Warning: Smart UV projection failed for {obj.name}: {e}")
        # Fall back to simple unwrap
        try:
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.02)
        except RuntimeError:
            print(f"Warning: UV unwrap also failed for {obj.name}")

    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)


def export_metaball_creature(
    creature: MetaballCreature,
    output_path: Path,
    base_color: Tuple[float, float, float] = (0.5, 0.6, 0.7),
    emission_color: Optional[Tuple[float, float, float]] = None,
    emission_strength: float = 0.5,
    roughness: float = 0.4,
    subsurface: float = 0.2,
    alpha: float = 1.0,
    decimate_ratio: float = 1.0,  # 1.0 = no decimation, 0.5 = half polys
) -> Path:
    """
    Export a MetaballCreature to GLB format.

    Args:
        creature: MetaballCreature to export
        output_path: Path for GLB output
        base_color: RGB tuple (0-1 range)
        emission_color: Optional bioluminescence color
        emission_strength: Emission intensity
        roughness: Surface roughness
        subsurface: Subsurface scattering amount
        alpha: Transparency
        decimate_ratio: Polygon reduction ratio

    Returns:
        Path to exported file
    """
    ensure_blender()

    # Clear scene
    clear_scene()

    # Create metaball
    mball_obj = create_metaball_object(creature)

    # Convert to mesh
    mesh_obj = convert_metaball_to_mesh(mball_obj, creature.name)

    # Decimate if needed
    if decimate_ratio < 1.0:
        bpy.context.view_layer.objects.active = mesh_obj
        mod = mesh_obj.modifiers.new("Decimate", 'DECIMATE')
        mod.ratio = decimate_ratio
        bpy.ops.object.modifier_apply(modifier="Decimate")

    # Generate UVs
    generate_smart_uvs(mesh_obj)

    # Create and apply material
    material = create_underwater_material(
        name=f"{creature.name}_mat",
        base_color=base_color,
        emission_color=emission_color,
        emission_strength=emission_strength,
        roughness=roughness,
        subsurface=subsurface,
        alpha=alpha,
    )
    mesh_obj.data.materials.append(material)

    # Apply transforms
    bpy.context.view_layer.objects.active = mesh_obj
    mesh_obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Export to GLB
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
    )

    # Count triangles
    tri_count = sum(len(p.vertices) - 2 for p in mesh_obj.data.polygons)
    print(f"Exported: {output_path} ({tri_count} tris)")

    return output_path


# === CREATURE PRESETS ===
# These functions create common creature forms using metaballs

def create_jellyfish(name: str = "jellyfish", size: float = 1.0) -> MetaballCreature:
    """Create a jellyfish-like creature with dome and tentacles."""
    creature = MetaballCreature(name, resolution=0.06)

    # Bell dome - layered metaballs for shape
    creature.add_ball(0, 0, 0, 0.3 * size, stiffness=1.5)  # Main dome
    creature.add_ball(0, 0, 0.1 * size, 0.25 * size, stiffness=2.0)  # Top bulge
    creature.add_ball(0, 0, -0.15 * size, 0.2 * size, stiffness=2.5)  # Underside

    # Oral arms (4 main ones)
    for i in range(4):
        angle = (math.pi / 2) * i
        x = 0.08 * size * math.cos(angle)
        y = 0.08 * size * math.sin(angle)
        creature.add_chain(
            start=(x, y, -0.2 * size),
            end=(x * 2, y * 2, -0.6 * size),
            count=4,
            radius_start=0.05 * size,
            radius_end=0.02 * size,
            stiffness=3.0
        )

    # Trailing tentacles (8 of them)
    for i in range(8):
        angle = (math.pi / 4) * i
        x = 0.2 * size * math.cos(angle)
        y = 0.2 * size * math.sin(angle)
        creature.add_chain(
            start=(x, y, -0.15 * size),
            end=(x * 1.5, y * 1.5, -0.9 * size),
            count=6,
            radius_start=0.03 * size,
            radius_end=0.01 * size,
            stiffness=4.0
        )

    return creature


def create_fish(name: str = "fish", size: float = 1.0, elongation: float = 1.5) -> MetaballCreature:
    """Create a fish-like creature with body, fins, and tail."""
    creature = MetaballCreature(name, resolution=0.05)

    # Body - elongated ellipsoid shape using multiple balls
    body_length = 0.4 * size * elongation
    for i in range(5):
        t = i / 4
        z = -body_length/2 + t * body_length
        # Taper at head and tail
        radius = 0.15 * size * (1.0 - 0.7 * abs(t - 0.4))
        creature.add_ball(0, 0, z, radius, stiffness=1.5)

    # Head
    creature.add_ball(0, 0, body_length/2 + 0.05 * size, 0.1 * size, stiffness=2.0)

    # Dorsal fin
    creature.add_ellipsoid(
        0, 0.1 * size, 0,
        radius=0.08 * size,
        size_x=0.2, size_y=1.5, size_z=1.0,
        stiffness=3.5
    )

    # Tail fin
    creature.add_ellipsoid(
        0, 0, -body_length/2 - 0.1 * size,
        radius=0.12 * size,
        size_x=0.15, size_y=2.0, size_z=1.0,
        stiffness=3.0
    )

    # Pectoral fins (sides)
    for side in [-1, 1]:
        creature.add_ellipsoid(
            side * 0.12 * size, 0, 0.1 * size,
            radius=0.06 * size,
            size_x=0.3, size_y=1.5, size_z=0.5,
            stiffness=4.0
        )

    return creature


def create_octopus(name: str = "octopus", size: float = 1.0) -> MetaballCreature:
    """Create an octopus-like creature with mantle and tentacles."""
    creature = MetaballCreature(name, resolution=0.06)

    # Mantle (head/body)
    creature.add_ball(0, 0, 0.1 * size, 0.2 * size, stiffness=1.5)
    creature.add_ball(0, 0, 0.25 * size, 0.15 * size, stiffness=2.0)
    creature.add_ball(0, 0, 0, 0.18 * size, stiffness=1.8)

    # Eight tentacles
    for i in range(8):
        angle = (math.pi / 4) * i
        x = 0.12 * size * math.cos(angle)
        y = 0.12 * size * math.sin(angle)

        # Each tentacle curves outward and down
        end_x = x * 4
        end_y = y * 4
        end_z = -0.5 * size

        creature.add_chain(
            start=(x, y, -0.05 * size),
            end=(end_x, end_y, end_z),
            count=8,
            radius_start=0.05 * size,
            radius_end=0.015 * size,
            stiffness=2.5
        )

    return creature


def create_turtle(name: str = "turtle", size: float = 1.0) -> MetaballCreature:
    """Create a sea turtle with shell and flippers."""
    creature = MetaballCreature(name, resolution=0.06)

    # Shell (carapace) - dome
    creature.add_ellipsoid(
        0, 0, 0,
        radius=0.3 * size,
        size_x=1.0, size_y=0.6, size_z=1.3,
        stiffness=1.2
    )

    # Plastron (bottom) - flatter
    creature.add_ellipsoid(
        0, -0.08 * size, 0,
        radius=0.25 * size,
        size_x=1.0, size_y=0.3, size_z=1.2,
        stiffness=1.5
    )

    # Head
    creature.add_ball(0, 0, 0.35 * size, 0.1 * size, stiffness=2.0)
    creature.add_ball(0, 0.02 * size, 0.42 * size, 0.06 * size, stiffness=2.5)

    # Front flippers
    for side in [-1, 1]:
        creature.add_ellipsoid(
            side * 0.25 * size, -0.05 * size, 0.15 * size,
            radius=0.15 * size,
            size_x=2.0, size_y=0.3, size_z=0.8,
            stiffness=2.5
        )

    # Rear flippers (smaller)
    for side in [-1, 1]:
        creature.add_ellipsoid(
            side * 0.2 * size, -0.05 * size, -0.25 * size,
            radius=0.08 * size,
            size_x=1.5, size_y=0.25, size_z=0.6,
            stiffness=3.0
        )

    # Tail
    creature.add_chain(
        start=(0, -0.02 * size, -0.35 * size),
        end=(0, -0.02 * size, -0.5 * size),
        count=3,
        radius_start=0.04 * size,
        radius_end=0.015 * size,
        stiffness=3.0
    )

    return creature


def create_manta_ray(name: str = "manta_ray", size: float = 1.0) -> MetaballCreature:
    """Create a manta ray with wide wings and cephalic fins."""
    creature = MetaballCreature(name, resolution=0.06)

    # Body center
    creature.add_ellipsoid(
        0, 0, 0,
        radius=0.2 * size,
        size_x=0.8, size_y=0.3, size_z=1.0,
        stiffness=1.5
    )

    # Wings (pectoral fins) - wide and flat
    for side in [-1, 1]:
        # Wing base
        creature.add_ellipsoid(
            side * 0.3 * size, 0, 0,
            radius=0.15 * size,
            size_x=1.5, size_y=0.2, size_z=1.0,
            stiffness=1.8
        )
        # Wing tip
        creature.add_ellipsoid(
            side * 0.6 * size, 0, -0.1 * size,
            radius=0.1 * size,
            size_x=1.2, size_y=0.15, size_z=0.8,
            stiffness=2.5
        )

    # Head
    creature.add_ball(0, 0.02 * size, 0.25 * size, 0.12 * size, stiffness=2.0)

    # Cephalic fins (horn-like projections)
    for side in [-1, 1]:
        creature.add_chain(
            start=(side * 0.08 * size, 0.02 * size, 0.2 * size),
            end=(side * 0.15 * size, 0.08 * size, 0.35 * size),
            count=3,
            radius_start=0.04 * size,
            radius_end=0.02 * size,
            stiffness=3.0
        )

    # Tail
    creature.add_chain(
        start=(0, 0, -0.2 * size),
        end=(0, 0, -0.7 * size),
        count=5,
        radius_start=0.06 * size,
        radius_end=0.02 * size,
        stiffness=2.5
    )

    return creature


def create_anglerfish(name: str = "anglerfish", size: float = 1.0) -> MetaballCreature:
    """Create an anglerfish with large head, tiny body, and lure."""
    creature = MetaballCreature(name, resolution=0.06)

    # Large head
    creature.add_ball(0, 0, 0.1 * size, 0.25 * size, stiffness=1.5)
    creature.add_ball(0, 0.05 * size, 0.2 * size, 0.18 * size, stiffness=2.0)

    # Lower jaw
    creature.add_ellipsoid(
        0, -0.1 * size, 0.2 * size,
        radius=0.15 * size,
        size_x=1.0, size_y=0.4, size_z=0.6,
        stiffness=2.5
    )

    # Small body
    creature.add_ball(0, 0, -0.1 * size, 0.15 * size, stiffness=2.0)
    creature.add_ball(0, 0, -0.25 * size, 0.1 * size, stiffness=2.5)

    # Tail
    creature.add_ellipsoid(
        0, 0, -0.4 * size,
        radius=0.08 * size,
        size_x=0.3, size_y=1.5, size_z=0.8,
        stiffness=3.0
    )

    # Illicium (lure stalk)
    creature.add_chain(
        start=(0, 0.15 * size, 0.25 * size),
        end=(0, 0.35 * size, 0.35 * size),
        count=4,
        radius_start=0.02 * size,
        radius_end=0.015 * size,
        stiffness=4.0
    )

    # Esca (lure bulb at tip)
    creature.add_ball(0, 0.38 * size, 0.38 * size, 0.04 * size, stiffness=3.0)

    # Dorsal fin
    creature.add_ellipsoid(
        0, 0.08 * size, -0.15 * size,
        radius=0.06 * size,
        size_x=0.2, size_y=1.2, size_z=0.8,
        stiffness=3.5
    )

    # Pectoral fins
    for side in [-1, 1]:
        creature.add_ellipsoid(
            side * 0.15 * size, -0.05 * size, 0,
            radius=0.05 * size,
            size_x=0.3, size_y=1.0, size_z=0.5,
            stiffness=4.0
        )

    return creature


def create_squid(name: str = "squid", size: float = 1.0) -> MetaballCreature:
    """Create a squid with mantle, fins, and tentacles."""
    creature = MetaballCreature(name, resolution=0.06)

    # Mantle (torpedo-shaped body)
    for i in range(4):
        t = i / 3
        z = -0.1 * size + t * 0.5 * size
        # Taper at both ends
        radius = 0.12 * size * (1.0 - 0.5 * abs(t - 0.5))
        creature.add_ball(0, 0, z, radius, stiffness=1.8)

    # Mantle tip
    creature.add_ball(0, 0, 0.45 * size, 0.06 * size, stiffness=2.5)

    # Fins (at rear of mantle)
    for side in [-1, 1]:
        creature.add_ellipsoid(
            side * 0.1 * size, 0, 0.25 * size,
            radius=0.08 * size,
            size_x=0.3, size_y=1.5, size_z=1.0,
            stiffness=3.0
        )

    # Head (between mantle and arms)
    creature.add_ball(0, 0, -0.2 * size, 0.1 * size, stiffness=2.0)

    # Arms (8 shorter ones)
    for i in range(8):
        angle = (math.pi / 4) * i
        x = 0.06 * size * math.cos(angle)
        y = 0.06 * size * math.sin(angle)
        creature.add_chain(
            start=(x, y, -0.25 * size),
            end=(x * 3, y * 3, -0.5 * size),
            count=4,
            radius_start=0.03 * size,
            radius_end=0.012 * size,
            stiffness=3.0
        )

    # Tentacles (2 longer ones)
    for angle in [0, math.pi]:
        x = 0.05 * size * math.cos(angle)
        y = 0.05 * size * math.sin(angle)
        creature.add_chain(
            start=(x, y, -0.25 * size),
            end=(x * 5, y * 5, -0.7 * size),
            count=6,
            radius_start=0.025 * size,
            radius_end=0.02 * size,
            stiffness=3.5
        )

    return creature


def create_crab(name: str = "crab", size: float = 1.0) -> MetaballCreature:
    """Create a crab with body, claws, and legs."""
    creature = MetaballCreature(name, resolution=0.06)

    # Carapace (main body)
    creature.add_ellipsoid(
        0, 0, 0,
        radius=0.2 * size,
        size_x=1.3, size_y=0.5, size_z=1.0,
        stiffness=1.2
    )

    # Eyes on stalks
    for side in [-1, 1]:
        creature.add_chain(
            start=(side * 0.08 * size, 0.08 * size, 0.15 * size),
            end=(side * 0.1 * size, 0.15 * size, 0.2 * size),
            count=2,
            radius_start=0.02 * size,
            radius_end=0.025 * size,
            stiffness=4.0
        )

    # Claws
    for side in [-1, 1]:
        # Arm
        creature.add_chain(
            start=(side * 0.2 * size, 0, 0.1 * size),
            end=(side * 0.4 * size, 0, 0.2 * size),
            count=3,
            radius_start=0.04 * size,
            radius_end=0.05 * size,
            stiffness=2.5
        )
        # Claw pincer
        creature.add_ball(side * 0.45 * size, 0, 0.22 * size, 0.06 * size, stiffness=2.0)
        creature.add_ball(side * 0.48 * size, 0.03 * size, 0.25 * size, 0.03 * size, stiffness=3.0)
        creature.add_ball(side * 0.48 * size, -0.02 * size, 0.25 * size, 0.025 * size, stiffness=3.0)

    # Walking legs (4 pairs)
    leg_angles = [(0.7, 0.1), (0.9, -0.05), (1.1, -0.15), (1.3, -0.2)]
    for side in [-1, 1]:
        for angle_mult, z_offset in leg_angles:
            x = side * 0.18 * size * angle_mult
            creature.add_chain(
                start=(x * 0.6, -0.02 * size, z_offset * size),
                end=(x, -0.12 * size, z_offset * size * 1.2),
                count=3,
                radius_start=0.025 * size,
                radius_end=0.012 * size,
                stiffness=3.5
            )

    return creature


# Export presets for easy access
CREATURE_PRESETS = {
    "jellyfish": create_jellyfish,
    "fish": create_fish,
    "octopus": create_octopus,
    "turtle": create_turtle,
    "manta_ray": create_manta_ray,
    "anglerfish": create_anglerfish,
    "squid": create_squid,
    "crab": create_crab,
}
