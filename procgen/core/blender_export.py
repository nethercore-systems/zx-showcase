"""
Blender-based asset export for ZX console.

This module provides GLB mesh export and PNG texture export using Blender's Python API.
Run this script from within Blender or via `blender --background --python`.

Usage:
    blender --background --python run_blender.py -- --game prism-survivors --all
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass

# Check if running inside Blender
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
class MeshData:
    """Raw mesh data for Blender import."""
    vertices: List[Tuple[float, float, float]]
    faces: List[Tuple[int, ...]]
    normals: Optional[List[Tuple[float, float, float]]] = None
    uvs: Optional[List[Tuple[float, float]]] = None
    name: str = "mesh"

    @property
    def triangle_count(self) -> int:
        """Count triangles (quads count as 2)."""
        return sum(len(f) - 2 for f in self.faces)


@dataclass
class TextureData:
    """Texture data for export."""
    pixels: List[List[Tuple[int, int, int, int]]]  # RGBA per pixel
    width: int
    height: int
    name: str = "texture"


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

    # Also clear orphaned data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)
    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)


def mesh_data_to_blender(mesh_data: MeshData) -> 'bpy.types.Object':
    """
    Convert MeshData to a Blender mesh object.

    Args:
        mesh_data: MeshData with vertices and faces

    Returns:
        Blender object containing the mesh
    """
    ensure_blender()

    # Create new mesh
    mesh = bpy.data.meshes.new(mesh_data.name)
    obj = bpy.data.objects.new(mesh_data.name, mesh)

    # Link to scene
    bpy.context.collection.objects.link(obj)

    # Create bmesh and add geometry
    bm = bmesh.new()

    # Add vertices
    for v in mesh_data.vertices:
        bm.verts.new(v)

    bm.verts.ensure_lookup_table()

    # Add faces
    for face in mesh_data.faces:
        try:
            face_verts = [bm.verts[i] for i in face]
            bm.faces.new(face_verts)
        except (ValueError, IndexError):
            # Skip invalid faces (duplicate verts, etc.)
            pass

    # Transfer to mesh
    bm.to_mesh(mesh)
    bm.free()

    # Update normals (Blender 4.0+ handles this automatically via mesh.update())
    mesh.update()

    # Generate UVs if not provided
    if mesh_data.uvs is None:
        # Simple box projection UVs
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.select_set(False)

    return obj


def create_material_with_texture(
    name: str,
    albedo_path: Optional[Path] = None,
    emission_path: Optional[Path] = None,
    base_color: Tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0),
    emission_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0),
    emission_strength: float = 1.0,
    roughness: float = 0.3,
    metallic: float = 0.0,
) -> 'bpy.types.Material':
    """
    Create a Blender material with optional textures.

    Args:
        name: Material name
        albedo_path: Path to albedo texture (PNG)
        emission_path: Path to emission texture (PNG)
        base_color: Fallback base color if no albedo texture
        emission_color: Fallback emission color if no emission texture
        emission_strength: Emission strength multiplier
        roughness: Material roughness (0-1)
        metallic: Material metallic value (0-1)

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
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic

    # Create Material Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # Add albedo texture or color
    if albedo_path and albedo_path.exists():
        tex_image = nodes.new('ShaderNodeTexImage')
        tex_image.location = (-400, 0)
        tex_image.image = bpy.data.images.load(str(albedo_path))
        links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = base_color

    # Add emission texture or color
    if emission_path and emission_path.exists():
        emit_image = nodes.new('ShaderNodeTexImage')
        emit_image.location = (-400, -300)
        emit_image.image = bpy.data.images.load(str(emission_path))

        # Multiply emission by strength
        emit_mult = nodes.new('ShaderNodeMath')
        emit_mult.operation = 'MULTIPLY'
        emit_mult.location = (-100, -300)
        emit_mult.inputs[1].default_value = emission_strength

        # For emission, we need to connect to emission socket
        links.new(emit_image.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = emission_strength
    elif emission_color[0] > 0 or emission_color[1] > 0 or emission_color[2] > 0:
        bsdf.inputs['Emission Color'].default_value = emission_color
        bsdf.inputs['Emission Strength'].default_value = emission_strength

    return mat


def export_mesh_glb(
    mesh_data: MeshData,
    output_path: Path,
    material: Optional['bpy.types.Material'] = None,
    albedo_path: Optional[Path] = None,
    emission_path: Optional[Path] = None,
    roughness: float = 0.3,
    emission_strength: float = 1.0,
    apply_transforms: bool = True,
) -> Path:
    """
    Export MeshData to GLB format.

    Args:
        mesh_data: MeshData to export
        output_path: Output file path (should end in .glb)
        material: Optional pre-created material to apply (deprecated, use paths instead)
        albedo_path: Path to albedo texture
        emission_path: Path to emission texture
        roughness: Material roughness
        emission_strength: Emission strength
        apply_transforms: Apply all transforms before export

    Returns:
        Path to exported file
    """
    ensure_blender()

    # Clear scene
    clear_scene()

    # Create mesh object
    obj = mesh_data_to_blender(mesh_data)

    # Create material AFTER clearing scene (to avoid it being deleted)
    if albedo_path or emission_path:
        material = create_material_with_texture(
            name=f"{mesh_data.name}_mat",
            albedo_path=albedo_path,
            emission_path=emission_path,
            roughness=roughness,
            emission_strength=emission_strength,
        )

    # Apply material if provided
    if material:
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)

    # Apply transforms
    if apply_transforms:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Export to GLB (Blender 4.0+/5.0 compatible)
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
    )

    print(f"Exported: {output_path} ({mesh_data.triangle_count} tris)")
    return output_path


def export_texture_png(
    texture_data: TextureData,
    output_path: Path,
) -> Path:
    """
    Export TextureData to PNG format.

    Args:
        texture_data: TextureData with RGBA pixels
        output_path: Output file path (should end in .png)

    Returns:
        Path to exported file
    """
    ensure_blender()

    # Create Blender image
    image = bpy.data.images.new(
        name=texture_data.name,
        width=texture_data.width,
        height=texture_data.height,
        alpha=True,
    )

    # Flatten pixels to 1D array (RGBA floats)
    flat_pixels = []
    # Blender expects bottom-to-top row order
    for row in reversed(texture_data.pixels):
        for r, g, b, a in row:
            flat_pixels.extend([r / 255.0, g / 255.0, b / 255.0, a / 255.0])

    # Set pixels
    image.pixels = flat_pixels

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to file
    image.filepath_raw = str(output_path)
    image.file_format = 'PNG'
    image.save()

    # Clean up
    bpy.data.images.remove(image)

    print(f"Exported: {output_path} ({texture_data.width}x{texture_data.height})")
    return output_path


def batch_export_assets(
    meshes: Dict[str, MeshData],
    textures: Dict[str, TextureData],
    output_dir: Path,
    mesh_texture_map: Optional[Dict[str, Tuple[str, str]]] = None,
) -> Dict[str, Path]:
    """
    Batch export multiple meshes and textures.

    Args:
        meshes: Dict of mesh_name -> MeshData
        textures: Dict of texture_name -> TextureData
        output_dir: Base output directory
        mesh_texture_map: Optional mapping of mesh_name -> (albedo_tex_name, emission_tex_name)

    Returns:
        Dict of asset_name -> exported_path
    """
    ensure_blender()

    exported = {}

    # Export textures first
    texture_paths = {}
    for tex_name, tex_data in textures.items():
        tex_path = output_dir / "textures" / f"{tex_name}.png"
        export_texture_png(tex_data, tex_path)
        texture_paths[tex_name] = tex_path
        exported[f"texture_{tex_name}"] = tex_path

    # Export meshes with materials
    for mesh_name, mesh_data in meshes.items():
        mesh_path = output_dir / "meshes" / f"{mesh_name}.glb"

        # Create material if texture mapping exists
        material = None
        if mesh_texture_map and mesh_name in mesh_texture_map:
            albedo_name, emission_name = mesh_texture_map[mesh_name]
            albedo_path = texture_paths.get(albedo_name)
            emission_path = texture_paths.get(emission_name)

            material = create_material_with_texture(
                name=f"{mesh_name}_mat",
                albedo_path=albedo_path,
                emission_path=emission_path,
            )

        export_mesh_glb(mesh_data, mesh_path, material=material)
        exported[f"mesh_{mesh_name}"] = mesh_path

    return exported


# Alias for compatibility with existing pipeline
def mesh_to_blender_and_export(mesh_data: MeshData, filepath: Path) -> Path:
    """Convenience function for simple mesh export."""
    return export_mesh_glb(mesh_data, filepath)


def texture_to_png(texture_data: TextureData, filepath: Path) -> Path:
    """Convenience function for simple texture export."""
    return export_texture_png(texture_data, filepath)
