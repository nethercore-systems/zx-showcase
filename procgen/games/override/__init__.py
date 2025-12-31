"""
Override - Procedural Asset Generation Module

Generates all assets for the Override game:
- Tilesets (floor and wall tiles)
- Sprites (doors, traps, characters)
- VFX (gas clouds, laser beams, glows)
- UI elements (energy bars, timers, indicators)
- Audio (SFX and music)

Usage:
    python run.py --game override --all
"""

from pathlib import Path
from typing import Dict, Optional

from procgen.configs.override import (
    STYLE_TOKENS, PALETTE, TILESET_DEFS, SPRITE_DEFS,
    VFX_DEFS, UI_DEFS, SFX_DEFS, MUSIC_DEFS,
)

from .tilesets import generate_all_tilesets
from .sprites import generate_all_sprites
from .vfx import generate_all_vfx
from .ui import generate_all_ui
from .audio import generate_all_sfx


def generate_all(output_dir: Path, asset_type: str = "all") -> Dict[str, int]:
    """
    Generate all Override assets.

    Args:
        output_dir: Output directory for generated assets
        asset_type: Type of assets to generate (all, tilesets, sprites, vfx, ui, audio)

    Returns:
        Dict with counts of generated assets per type
    """
    counts = {}

    if asset_type in ("all", "tilesets"):
        print("\n--- Generating Tilesets ---")
        tiles_dir = output_dir / "tilesets"
        tiles_dir.mkdir(parents=True, exist_ok=True)
        counts["tilesets"] = generate_all_tilesets(tiles_dir, PALETTE)

    if asset_type in ("all", "sprites"):
        print("\n--- Generating Sprites ---")
        sprites_dir = output_dir / "sprites"
        sprites_dir.mkdir(parents=True, exist_ok=True)
        counts["sprites"] = generate_all_sprites(sprites_dir, PALETTE)

    if asset_type in ("all", "vfx"):
        print("\n--- Generating VFX ---")
        vfx_dir = output_dir / "vfx"
        vfx_dir.mkdir(parents=True, exist_ok=True)
        counts["vfx"] = generate_all_vfx(vfx_dir, PALETTE)

    if asset_type in ("all", "ui"):
        print("\n--- Generating UI ---")
        ui_dir = output_dir / "ui"
        ui_dir.mkdir(parents=True, exist_ok=True)
        counts["ui"] = generate_all_ui(ui_dir, PALETTE)

    if asset_type in ("all", "audio"):
        print("\n--- Generating Audio ---")
        audio_dir = output_dir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        counts["audio"] = generate_all_sfx(audio_dir)

    return counts


__all__ = [
    "generate_all",
    "STYLE_TOKENS",
    "PALETTE",
]
