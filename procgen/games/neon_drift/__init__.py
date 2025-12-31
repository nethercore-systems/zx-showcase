"""
Neon Drift - Procedural Asset Generation Module

Generates all assets for the Neon Drift synthwave racing game:
- Vehicles (7 car types with distinct silhouettes)
- Track segments (straights, curves, tunnels, jumps, checkpoints)
- Props (barriers, boost pads, billboards, buildings, crystals)
- Audio (engine sounds, SFX, synth samples for XM music)

Usage:
    python run.py --game neon-drift --all

Aligned with zx-procgen generator-patterns skill.
"""

from pathlib import Path
from typing import Dict

# Audio uses pure Python, can always be imported
from .audio import generate_all_audio, generate_all_synth_samples, AUDIO_ASSETS

# Validation is pure Python
from .validate import validate_all

# Blender-dependent modules are imported conditionally
try:
    from .cars import generate_all_cars, CARS
    from .tracks import generate_all_tracks, generate_all_props
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False
    CARS = []

    def generate_all_cars(output_dir: Path) -> int:
        print("Warning: Blender not available, skipping car generation")
        return 0

    def generate_all_tracks(output_dir: Path) -> int:
        print("Warning: Blender not available, skipping track generation")
        return 0

    def generate_all_props(output_dir: Path) -> int:
        print("Warning: Blender not available, skipping prop generation")
        return 0


def generate_all(output_dir: Path, asset_type: str = "all") -> Dict[str, int]:
    """
    Generate all Neon Drift assets.

    Args:
        output_dir: Output directory for generated assets
        asset_type: Type of assets to generate (all, meshes, vehicles, tracks, props, audio)

    Returns:
        Dict with counts of generated assets per type
    """
    counts = {}

    if asset_type in ("all", "meshes", "vehicles"):
        print("\n--- Generating Vehicles ---")
        meshes_dir = output_dir / "models" / "meshes"
        textures_dir = output_dir / "models" / "textures"
        meshes_dir.mkdir(parents=True, exist_ok=True)
        textures_dir.mkdir(parents=True, exist_ok=True)
        counts["vehicles"] = generate_all_cars(meshes_dir, textures_dir)

    if asset_type in ("all", "meshes", "tracks"):
        print("\n--- Generating Tracks ---")
        meshes_dir = output_dir / "models" / "meshes"
        textures_dir = output_dir / "models" / "textures"
        meshes_dir.mkdir(parents=True, exist_ok=True)
        textures_dir.mkdir(parents=True, exist_ok=True)
        counts["tracks"] = generate_all_tracks(meshes_dir, textures_dir)

    if asset_type in ("all", "meshes", "props"):
        print("\n--- Generating Props ---")
        meshes_dir = output_dir / "models" / "meshes"
        textures_dir = output_dir / "models" / "textures"
        meshes_dir.mkdir(parents=True, exist_ok=True)
        textures_dir.mkdir(parents=True, exist_ok=True)
        counts["props"] = generate_all_props(meshes_dir, textures_dir)

    if asset_type in ("all", "audio"):
        print("\n--- Generating Audio ---")
        audio_dir = output_dir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        counts["audio"] = generate_all_audio(audio_dir)

    if asset_type in ("all", "audio", "synth"):
        print("\n--- Generating Synth Samples ---")
        audio_dir = output_dir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        counts["synth_samples"] = generate_all_synth_samples(audio_dir)

    return counts


__all__ = [
    "generate_all",
    "validate_all",
    "generate_all_cars",
    "generate_all_tracks",
    "generate_all_props",
    "generate_all_audio",
    "generate_all_synth_samples",
    "CARS",
    "AUDIO_ASSETS",
    "BLENDER_AVAILABLE",
]
