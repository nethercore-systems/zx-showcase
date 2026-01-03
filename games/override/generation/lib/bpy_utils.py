"""Blender utilities for Override 3D asset generation."""

import bpy
import sys
from pathlib import Path

def setup_scene():
    """Clear default scene and set up for generation."""
    # Delete default objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Set render engine to EEVEE for real-time preview
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'

def export_glb(obj, output_path: Path):
    """Export object to GLB format."""
    # Select only this object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Apply transforms before export
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Export
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format='GLB',
        use_selection=True,
        export_apply=True,
    )

    print(f"Exported: {output_path}")

def get_output_dir() -> Path:
    """Get the generated/meshes/ output directory."""
    script_path = Path(bpy.data.filepath) if bpy.data.filepath else Path(sys.argv[-1])
    game_dir = script_path.parent.parent.parent
    return game_dir / "generated" / "meshes"

def create_dark_industrial_material(name: str):
    """Create Override's signature dark industrial sci-fi material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')

    # Dark metallic look
    bsdf.inputs['Base Color'].default_value = (0.2, 0.24, 0.3, 1.0)  # Dark metal
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Roughness'].default_value = 0.6

    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat

def create_glow_material(name: str, color: tuple, strength: float = 2.0):
    """Create emissive glow material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')

    emission.inputs['Color'].default_value = (*color, 1.0)
    emission.inputs['Strength'].default_value = strength

    links.new(emission.outputs['Emission'], output.inputs['Surface'])

    return mat
