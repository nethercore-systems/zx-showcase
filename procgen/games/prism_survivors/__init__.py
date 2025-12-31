"""Prism Survivors - Procedural Asset Generation Module.

Generates assets for the Prism Survivors game:
- 6 hero classes with distinct silhouettes
- 13 enemy types (7 basic, 4 elite, 2 bosses)
- Pickups (XP gems, coins, powerups)
- Projectiles (frost, void, lightning)
- Arena floor
- 18+ sound effects

All meshes are Blender-generated GLB files with matching textures.
Audio uses pure Python synthesis via shared audio_dsp library.
"""

from pathlib import Path
from typing import Dict

# Check for Blender availability
try:
    import bpy
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False


def generate_all(output_dir: Path, asset_type: str = "all") -> Dict[str, int]:
    """Generate all Prism Survivors assets.

    Args:
        output_dir: Base output directory for assets
        asset_type: Type of assets to generate:
            - "all": Generate everything
            - "heroes": Generate hero meshes only
            - "enemies": Generate enemy meshes only
            - "pickups": Generate pickup meshes only
            - "projectiles": Generate projectile meshes only
            - "arena": Generate arena mesh only
            - "audio": Generate sound effects only

    Returns:
        Dict mapping asset categories to counts generated
    """
    counts = {}

    meshes_dir = output_dir / "models" / "meshes"
    textures_dir = output_dir / "models" / "textures"
    audio_dir = output_dir / "audio"

    meshes_dir.mkdir(parents=True, exist_ok=True)
    textures_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    # Heroes (6)
    if asset_type in ("all", "heroes", "meshes"):
        if BLENDER_AVAILABLE:
            from .heroes import generate_all_heroes
            print("\n--- Heroes ---")
            counts["heroes"] = generate_all_heroes(meshes_dir, textures_dir)
        else:
            print("Skipping heroes (Blender not available)")
            counts["heroes"] = 0

    # Enemies (13)
    if asset_type in ("all", "enemies", "meshes"):
        if BLENDER_AVAILABLE:
            from .enemies import generate_all_enemies
            print("\n--- Enemies ---")
            counts["enemies"] = generate_all_enemies(meshes_dir, textures_dir)
        else:
            print("Skipping enemies (Blender not available)")
            counts["enemies"] = 0

    # Pickups (3)
    if asset_type in ("all", "pickups", "meshes"):
        if BLENDER_AVAILABLE:
            from .pickups import generate_all_pickups
            print("\n--- Pickups ---")
            counts["pickups"] = generate_all_pickups(meshes_dir, textures_dir)
        else:
            print("Skipping pickups (Blender not available)")
            counts["pickups"] = 0

    # Projectiles (3)
    if asset_type in ("all", "projectiles", "meshes"):
        if BLENDER_AVAILABLE:
            from .projectiles import generate_all_projectiles
            print("\n--- Projectiles ---")
            counts["projectiles"] = generate_all_projectiles(meshes_dir, textures_dir)
        else:
            print("Skipping projectiles (Blender not available)")
            counts["projectiles"] = 0

    # Arena (1)
    if asset_type in ("all", "arena", "meshes"):
        if BLENDER_AVAILABLE:
            from .arena import generate_arena
            print("\n--- Arena ---")
            counts["arena"] = generate_arena(meshes_dir, textures_dir)
        else:
            print("Skipping arena (Blender not available)")
            counts["arena"] = 0

    # Audio (18+)
    if asset_type in ("all", "audio"):
        from .audio import generate_all_audio
        print("\n--- Audio ---")
        counts["audio"] = generate_all_audio(audio_dir)

    return counts


# Validation
from .validate import validate_all

__all__ = [
    "generate_all",
    "validate_all",
    "BLENDER_AVAILABLE",
]
