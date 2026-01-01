"""
Override - Procedural Asset Generation Module

Generates all assets for the Override game:
- Tilesets (floor and wall tiles) - one asset per file in floors/ and walls/
- Sprites (doors, traps, characters) - one asset per file in doors/, traps/, characters/
- VFX (gas clouds, laser beams, glows) - one asset per file in effects/
- UI elements (energy bars, timers, indicators) - one asset per file in ui_elements/
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

# Re-export individual generators for direct access
from .floors import (
    generate_floor_metal,
    generate_floor_grate,
    generate_floor_panel,
    generate_floor_damaged,
)
from .walls import (
    generate_wall_solid,
    generate_wall_window,
    generate_wall_vent,
    generate_wall_pipe,
    generate_wall_screen,
    generate_wall_doorframe,
)
from .doors import (
    generate_door_closed,
    generate_door_open,
    generate_door_locked,
)
from .traps import (
    generate_trap_spike,
    generate_trap_gas,
    generate_trap_laser,
)
from .characters import (
    generate_runner_idle,
    generate_drone_idle,
)
from .effects import (
    generate_gas_cloud,
    generate_laser_beam,
    generate_core_glow,
    generate_dust_particle,
    generate_flash,
    generate_spark,
)
from .ui_elements import (
    generate_energy_bar_bg,
    generate_energy_bar_fill,
    generate_timer_digit,
    generate_indicator,
    generate_power_button,
    generate_button,
)


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
    # Main generator
    "generate_all",
    # Config
    "STYLE_TOKENS",
    "PALETTE",
    # Batch generators
    "generate_all_tilesets",
    "generate_all_sprites",
    "generate_all_vfx",
    "generate_all_ui",
    "generate_all_sfx",
    # Floor tiles
    "generate_floor_metal",
    "generate_floor_grate",
    "generate_floor_panel",
    "generate_floor_damaged",
    # Wall tiles
    "generate_wall_solid",
    "generate_wall_window",
    "generate_wall_vent",
    "generate_wall_pipe",
    "generate_wall_screen",
    "generate_wall_doorframe",
    # Doors
    "generate_door_closed",
    "generate_door_open",
    "generate_door_locked",
    # Traps
    "generate_trap_spike",
    "generate_trap_gas",
    "generate_trap_laser",
    # Characters
    "generate_runner_idle",
    "generate_drone_idle",
    # Effects
    "generate_gas_cloud",
    "generate_laser_beam",
    "generate_core_glow",
    "generate_dust_particle",
    "generate_flash",
    "generate_spark",
    # UI Elements
    "generate_energy_bar_bg",
    "generate_energy_bar_fill",
    "generate_timer_digit",
    "generate_indicator",
    "generate_power_button",
    "generate_button",
]
