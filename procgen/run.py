#!/usr/bin/env python3
"""
ZX Showcase - Procedural Asset Generation Runner

Usage:
    # Generate core assets (shared across games)
    python run.py --core --all
    python run.py --core --meshes
    python run.py --core --audio

    # Generate game-specific assets
    python run.py --game neon-drift --all
    python run.py --game prism-survivors --heroes
    python run.py --game override --all

    # Generate everything for a game (core + game-specific)
    python run.py --game neon-drift --full
"""

import argparse
import os
import sys
from pathlib import Path

# Add procgen to path
PROCGEN_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROCGEN_ROOT.parent))

from procgen.core.base_params import UniversalStyleParams


# ============================================================================
# Output Helpers
# ============================================================================

def get_output_dir(game_name: str) -> Path:
    """Get output directory for generated assets."""
    showcase_root = PROCGEN_ROOT.parent
    game_dir_name = game_name.replace("_", "-")
    output_dir = showcase_root / "games" / game_dir_name / "assets" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_core_output_dir() -> Path:
    """Get output directory for core/shared assets."""
    showcase_root = PROCGEN_ROOT.parent
    output_dir = showcase_root / "shared_assets"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


# ============================================================================
# Export Functions
# ============================================================================

def export_mesh_obj(mesh, filepath: Path):
    """Export mesh to OBJ format."""
    from procgen.lib.export import export_obj
    export_obj(mesh, str(filepath))
    print(f"  Exported: {filepath.name}")


def export_texture_ppm(texture, filepath: Path):
    """Export texture to PPM format."""
    from procgen.lib.export import export_ppm
    export_ppm(texture, str(filepath))
    print(f"  Exported: {filepath.name}")


def export_audio_wav(wave, filepath: Path):
    """Export audio to WAV format."""
    from procgen.lib.synthesis import save_wav
    save_wav(str(filepath), wave)
    print(f"  Exported: {filepath.name}")


# ============================================================================
# Core Asset Generation
# ============================================================================

def generate_core_meshes(output_dir: Path):
    """Generate core/shared mesh primitives."""
    print("\n=== Generating Core Meshes ===")

    from procgen.core.meshes import (
        create_box, create_sphere, create_cylinder, create_capsule,
        create_gem_pickup, create_health_pickup, create_xp_orb,
        create_shard_projectile, create_orb_projectile,
    )

    primitives_dir = output_dir / "primitives"
    primitives_dir.mkdir(exist_ok=True)

    # Basic primitives
    print("\n--- Primitives ---")
    export_mesh_obj(create_box(), primitives_dir / "box.obj")
    export_mesh_obj(create_sphere(), primitives_dir / "sphere.obj")
    export_mesh_obj(create_cylinder(), primitives_dir / "cylinder.obj")
    export_mesh_obj(create_capsule(), primitives_dir / "capsule.obj")

    # Pickups
    pickups_dir = output_dir / "pickups"
    pickups_dir.mkdir(exist_ok=True)

    print("\n--- Pickups ---")
    export_mesh_obj(create_gem_pickup(), pickups_dir / "gem.obj")
    export_mesh_obj(create_health_pickup(), pickups_dir / "health.obj")
    export_mesh_obj(create_xp_orb(), pickups_dir / "xp_orb.obj")

    # Projectiles
    projectiles_dir = output_dir / "projectiles"
    projectiles_dir.mkdir(exist_ok=True)

    print("\n--- Projectiles ---")
    export_mesh_obj(create_shard_projectile(), projectiles_dir / "shard.obj")
    export_mesh_obj(create_orb_projectile(), projectiles_dir / "orb.obj")

    print(f"\nCore meshes generated in: {output_dir}")


def generate_core_textures(output_dir: Path):
    """Generate core/shared texture patterns."""
    print("\n=== Generating Core Textures ===")

    from procgen.core.textures import (
        generate_grid_pattern, generate_checkerboard,
        generate_perlin_texture, generate_voronoi_texture,
    )

    patterns_dir = output_dir / "patterns"
    patterns_dir.mkdir(exist_ok=True)

    print("\n--- Patterns ---")
    export_texture_ppm(
        generate_grid_pattern(256, 256, cell_size=32),
        patterns_dir / "grid.ppm"
    )
    export_texture_ppm(
        generate_checkerboard(256, 256, cell_size=32),
        patterns_dir / "checkerboard.ppm"
    )

    noise_dir = output_dir / "noise"
    noise_dir.mkdir(exist_ok=True)

    print("\n--- Noise Textures ---")
    export_texture_ppm(
        generate_perlin_texture(256, 256, scale=0.05),
        noise_dir / "perlin.ppm"
    )
    export_texture_ppm(
        generate_voronoi_texture(256, 256, cell_count=20),
        noise_dir / "voronoi.ppm"
    )

    print(f"\nCore textures generated in: {output_dir}")


def generate_core_audio(output_dir: Path):
    """Generate core/shared audio samples."""
    print("\n=== Generating Core Audio ===")

    audio_dir = output_dir / "audio"
    audio_dir.mkdir(exist_ok=True)

    # UI SFX
    ui_dir = audio_dir / "ui"
    ui_dir.mkdir(exist_ok=True)

    print("\n--- UI SFX ---")
    from procgen.core.audio import (
        generate_menu_click, generate_menu_hover, generate_menu_confirm,
    )
    export_audio_wav(generate_menu_click(), ui_dir / "click.wav")
    export_audio_wav(generate_menu_hover(), ui_dir / "hover.wav")
    export_audio_wav(generate_menu_confirm(), ui_dir / "confirm.wav")

    # Impact SFX
    impact_dir = audio_dir / "impact"
    impact_dir.mkdir(exist_ok=True)

    print("\n--- Impact SFX ---")
    from procgen.core.audio import generate_hit, generate_explosion
    export_audio_wav(generate_hit(), impact_dir / "hit.wav")
    export_audio_wav(generate_explosion(), impact_dir / "explosion.wav")

    # Drum samples
    drums_dir = audio_dir / "drums"
    drums_dir.mkdir(exist_ok=True)

    print("\n--- Drum Samples ---")
    from procgen.lib.instruments import synth_kick, synth_snare, synth_hihat
    export_audio_wav(synth_kick(), drums_dir / "kick.wav")
    export_audio_wav(synth_snare(), drums_dir / "snare.wav")
    export_audio_wav(synth_hihat(), drums_dir / "hihat.wav")

    print(f"\nCore audio generated in: {output_dir}")


def generate_core_all(output_dir: Path):
    """Generate all core assets."""
    generate_core_meshes(output_dir)
    generate_core_textures(output_dir)
    generate_core_audio(output_dir)


# ============================================================================
# Game-Specific Asset Generation
# ============================================================================

def get_game_style(game_name: str):
    """Get style preset for a game."""
    from procgen.core.presets import (
        NeonSynthwavePreset, BioluminescentPreset,
        PrismaticPreset, IndustrialDarkPreset,
    )

    presets = {
        "neon-drift": NeonSynthwavePreset(),
        "lumina-depths": BioluminescentPreset(),
        "prism-survivors": PrismaticPreset(),
        "override": IndustrialDarkPreset(),
    }
    return presets.get(game_name.lower())


def generate_game_assets(game_name: str, output_dir: Path, asset_type: str = "all"):
    """Generate assets for a specific game."""
    print(f"\n=== Generating {game_name} Assets ===")

    style = get_game_style(game_name)
    if style is None:
        print(f"Error: No style preset found for '{game_name}'")
        return

    print(f"Using style: {style.name}")
    print(f"Output: {output_dir}")

    # Dispatch to game-specific generator
    if game_name == "neon-drift":
        _generate_neon_drift(style, output_dir, asset_type)
    elif game_name == "lumina-depths":
        _generate_lumina_depths(style, output_dir, asset_type)
    elif game_name == "prism-survivors":
        _generate_prism_survivors(style, output_dir, asset_type)
    elif game_name == "override":
        _generate_override(style, output_dir, asset_type)


def _generate_neon_drift(style, output_dir: Path, asset_type: str):
    """Generate Neon Drift specific assets."""
    from procgen.core.meshes import create_vehicle_chassis, VehicleParams
    from procgen.core.textures import generate_grid_pattern
    from procgen.lib.sfx import generate_game_sfx

    if asset_type in ("all", "meshes", "vehicles"):
        print("\n--- Vehicles ---")
        vehicles_dir = output_dir / "vehicles"
        vehicles_dir.mkdir(exist_ok=True)

        for body_style in ["sport", "muscle"]:
            params = VehicleParams(body_style=body_style)
            mesh = create_vehicle_chassis(params)
            export_mesh_obj(mesh, vehicles_dir / f"car_{body_style}.obj")

    if asset_type in ("all", "textures"):
        print("\n--- Textures ---")
        textures_dir = output_dir / "textures"
        textures_dir.mkdir(exist_ok=True)

        grid = generate_grid_pattern(
            256, 256, cell_size=32,
            line_color=(0, 255, 255), bg_color=(10, 10, 30)
        )
        export_texture_ppm(grid, textures_dir / "track_grid.ppm")

    if asset_type in ("all", "audio"):
        print("\n--- Audio ---")
        audio_dir = output_dir / "audio"
        audio_dir.mkdir(exist_ok=True)

        sfx = generate_game_sfx("neon-drift")
        for name, wave in sfx.items():
            export_audio_wav(wave, audio_dir / f"{name}.wav")


def _generate_lumina_depths(style, output_dir: Path, asset_type: str):
    """Generate Lumina Depths specific assets."""
    from procgen.core.textures import generate_voronoi_texture
    from procgen.lib.sfx import generate_game_sfx

    if asset_type in ("all", "textures"):
        print("\n--- Textures ---")
        textures_dir = output_dir / "textures"
        textures_dir.mkdir(exist_ok=True)

        # Bioluminescent pattern
        bio = generate_voronoi_texture(
            256, 256, cell_count=15,
            color_low=(0, 30, 60), color_high=(0, 200, 255)
        )
        export_texture_ppm(bio, textures_dir / "bioluminescent.ppm")

    if asset_type in ("all", "audio"):
        print("\n--- Audio ---")
        audio_dir = output_dir / "audio"
        audio_dir.mkdir(exist_ok=True)

        sfx = generate_game_sfx("lumina-depths")
        for name, wave in sfx.items():
            export_audio_wav(wave, audio_dir / f"{name}.wav")


def _generate_prism_survivors(style, output_dir: Path, asset_type: str):
    """Generate Prism Survivors specific assets."""
    from procgen.core.meshes import (
        create_humanoid_mesh, HumanoidParams,
        create_gem_pickup, create_shard_projectile,
    )
    from procgen.lib.sfx import generate_game_sfx

    if asset_type in ("all", "meshes", "heroes"):
        print("\n--- Heroes ---")
        heroes_dir = output_dir / "heroes"
        heroes_dir.mkdir(exist_ok=True)

        for hero_style in ["blocky", "rounded", "angular"]:
            mesh = create_humanoid_mesh(HumanoidParams(), style=hero_style)
            export_mesh_obj(mesh, heroes_dir / f"hero_{hero_style}.obj")

    if asset_type in ("all", "meshes", "pickups"):
        print("\n--- Pickups ---")
        pickups_dir = output_dir / "pickups"
        pickups_dir.mkdir(exist_ok=True)

        for gem_type in ["diamond", "emerald", "ruby"]:
            gem = create_gem_pickup(gem_type=gem_type)
            export_mesh_obj(gem, pickups_dir / f"gem_{gem_type}.obj")

    if asset_type in ("all", "meshes", "projectiles"):
        print("\n--- Projectiles ---")
        proj_dir = output_dir / "projectiles"
        proj_dir.mkdir(exist_ok=True)

        for shard_type in ["crystal", "glass", "ice"]:
            shard = create_shard_projectile(shard_type=shard_type)
            export_mesh_obj(shard, proj_dir / f"shard_{shard_type}.obj")

    if asset_type in ("all", "audio"):
        print("\n--- Audio ---")
        audio_dir = output_dir / "audio"
        audio_dir.mkdir(exist_ok=True)

        sfx = generate_game_sfx("prism-survivors")
        for name, wave in sfx.items():
            export_audio_wav(wave, audio_dir / f"{name}.wav")


def _generate_override(style, output_dir: Path, asset_type: str):
    """Generate Override specific assets using the new modular pipeline."""
    from procgen.games.override import generate_all

    # Use the new modular Override generator
    counts = generate_all(output_dir, asset_type)

    total = sum(counts.values())
    print(f"\nOverride: Generated {total} assets ({counts})")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="ZX Showcase Procedural Asset Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run.py --core --all              Generate all core assets
    python run.py --core --meshes           Generate core mesh primitives
    python run.py --game neon-drift --all   Generate all Neon Drift assets
    python run.py --game override --audio   Generate Override audio only
    python run.py --game prism-survivors --full  Core + game assets
        """
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--core", action="store_true",
                            help="Generate core/shared assets")
    mode_group.add_argument("--game", type=str,
                            choices=["neon-drift", "lumina-depths", "prism-survivors", "override"],
                            help="Generate game-specific assets")

    # Asset type selection
    parser.add_argument("--all", action="store_true", help="Generate all assets")
    parser.add_argument("--meshes", action="store_true", help="Generate meshes only")
    parser.add_argument("--textures", action="store_true", help="Generate textures only")
    parser.add_argument("--audio", action="store_true", help="Generate audio only")
    parser.add_argument("--full", action="store_true",
                        help="Generate core + game-specific assets (requires --game)")

    # Options
    parser.add_argument("--output", type=str, help="Custom output directory")
    parser.add_argument("--preview", action="store_true", help="Open in Blender for preview")

    args = parser.parse_args()

    # Determine output directory
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
    elif args.core:
        output_dir = get_core_output_dir()
    else:
        output_dir = get_output_dir(args.game)

    print("=" * 60)
    print("ZX Showcase Procedural Asset Generator v2.0")
    print("=" * 60)

    if args.core:
        print(f"Mode: Core Assets")
        print(f"Output: {output_dir}")

        if args.all or not (args.meshes or args.textures or args.audio):
            generate_core_all(output_dir)
        else:
            if args.meshes:
                generate_core_meshes(output_dir)
            if args.textures:
                generate_core_textures(output_dir)
            if args.audio:
                generate_core_audio(output_dir)

    elif args.game:
        print(f"Mode: Game Assets - {args.game}")
        print(f"Output: {output_dir}")

        # Determine asset type
        if args.all:
            asset_type = "all"
        elif args.meshes:
            asset_type = "meshes"
        elif args.textures:
            asset_type = "textures"
        elif args.audio:
            asset_type = "audio"
        else:
            asset_type = "all"

        if args.full:
            # Generate core first, then game-specific
            core_dir = get_core_output_dir()
            generate_core_all(core_dir)

        generate_game_assets(args.game, output_dir, asset_type)

    print("\n" + "=" * 60)
    print("Generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
