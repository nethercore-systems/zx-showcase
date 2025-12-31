"""
File export utilities for procedural assets.

Provides functions to export meshes, textures, and audio.
"""

from pathlib import Path
from typing import Union
import struct

from .texture_buffer import TextureData
from .mesh_utils import MeshData


def export_obj(mesh: MeshData, filepath: Union[str, Path]) -> None:
    """
    Export mesh to Wavefront OBJ format.

    Args:
        mesh: Mesh data to export
        filepath: Output file path
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    lines = []

    # Header
    lines.append(f"# OBJ exported by ZX Showcase procgen")
    if mesh.name:
        lines.append(f"o {mesh.name}")

    # Vertices
    for v in mesh.vertices:
        lines.append(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}")

    # Normals
    if mesh.normals:
        for n in mesh.normals:
            lines.append(f"vn {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}")

    # UVs
    if mesh.uvs:
        for uv in mesh.uvs:
            lines.append(f"vt {uv[0]:.6f} {uv[1]:.6f}")

    # Faces
    for face in mesh.faces:
        if mesh.normals and mesh.uvs:
            # v/vt/vn format
            face_str = " ".join(f"{v + 1}/{v + 1}/{v + 1}" for v in face)
        elif mesh.normals:
            # v//vn format
            face_str = " ".join(f"{v + 1}//{v + 1}" for v in face)
        elif mesh.uvs:
            # v/vt format
            face_str = " ".join(f"{v + 1}/{v + 1}" for v in face)
        else:
            # v format only
            face_str = " ".join(str(v + 1) for v in face)
        lines.append(f"f {face_str}")

    filepath.write_text("\n".join(lines))


def export_ppm(texture: TextureData, filepath: Union[str, Path]) -> None:
    """
    Export texture to PPM format (portable pixmap).

    PPM is a simple uncompressed format readable by most image tools.

    Args:
        texture: Texture data to export
        filepath: Output file path
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'wb') as f:
        # PPM header (P6 for binary RGB)
        header = f"P6\n{texture.width} {texture.height}\n255\n"
        f.write(header.encode('ascii'))

        # Pixel data (RGB only, no alpha)
        for row in texture.pixels:
            for r, g, b, a in row:
                f.write(bytes([r, g, b]))


def export_png(texture: TextureData, filepath: Union[str, Path]) -> None:
    """
    Export texture to PNG format (requires PIL/Pillow).

    Args:
        texture: Texture data to export
        filepath: Output file path
    """
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("PIL/Pillow is required for PNG export. Install with: pip install pillow")

    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Create PIL image
    img = Image.new('RGBA', (texture.width, texture.height))

    # Set pixels
    for y, row in enumerate(texture.pixels):
        for x, pixel in enumerate(row):
            img.putpixel((x, y), pixel)

    img.save(filepath)


def export_wav(
    wave_data,  # np.ndarray
    filepath: Union[str, Path],
    sample_rate: int = 22050,
    normalize: bool = True,
) -> None:
    """
    Export audio data to WAV format.

    Args:
        wave_data: Audio samples as numpy array (float -1 to 1)
        filepath: Output file path
        sample_rate: Sample rate in Hz
        normalize: Whether to normalize to peak amplitude
    """
    try:
        import numpy as np
        from scipy.io import wavfile
    except ImportError:
        raise ImportError("numpy and scipy required for WAV export")

    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Ensure numpy array
    wave = np.array(wave_data)

    # Normalize if requested
    if normalize:
        max_val = np.max(np.abs(wave))
        if max_val > 0:
            wave = wave / max_val * 0.9

    # Convert to 16-bit PCM
    wave_int = (wave * 32767).astype(np.int16)

    wavfile.write(filepath, sample_rate, wave_int)


def export_raw_audio(
    wave_data,  # np.ndarray
    filepath: Union[str, Path],
    bits: int = 16,
) -> None:
    """
    Export raw PCM audio data (no header).

    Args:
        wave_data: Audio samples as numpy array
        filepath: Output file path
        bits: Bit depth (8 or 16)
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError("numpy required for raw audio export")

    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    wave = np.array(wave_data)

    # Normalize
    max_val = np.max(np.abs(wave))
    if max_val > 0:
        wave = wave / max_val * 0.9

    if bits == 8:
        # 8-bit unsigned
        data = ((wave + 1) * 127.5).astype(np.uint8)
    else:
        # 16-bit signed
        data = (wave * 32767).astype(np.int16)

    filepath.write_bytes(data.tobytes())


def export_glb(mesh: MeshData, filepath: Union[str, Path]) -> None:
    """
    Export mesh to GLB format (binary GLTF).

    GLB export is done via Blender for maximum compatibility and quality.
    Use procgen/run_blender.py for mesh generation workflows.

    This function is a stub - call run_blender.py with appropriate arguments
    to generate GLB files using Blender's native export.
    """
    raise NotImplementedError(
        "GLB export requires Blender. Use procgen/run_blender.py for GLB generation. "
        "Example: python run_blender.py --game neon-drift --asset cars"
    )


def get_export_func(filepath: Union[str, Path]):
    """
    Get the appropriate export function based on file extension.

    Returns:
        Export function for the given file type
    """
    suffix = Path(filepath).suffix.lower()

    exporters = {
        '.obj': export_obj,
        '.ppm': export_ppm,
        '.png': export_png,
        '.wav': export_wav,
        '.raw': export_raw_audio,
        '.glb': export_glb,
        '.gltf': export_glb,
    }

    if suffix in exporters:
        return exporters[suffix]
    else:
        raise ValueError(f"Unknown file format: {suffix}")
