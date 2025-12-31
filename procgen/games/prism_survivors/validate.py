"""Prism Survivors - Asset Quality Validation.

Validates all generated Prism Survivors assets against quality standards.
Aligned with zx-procgen creative-orchestrator workflow.

Usage:
    python run.py --game prism-survivors --validate
"""

from pathlib import Path
from typing import Dict, List
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from procgen.core.quality import (
    QualityReport, MeshQuality, SpriteQuality, AudioQuality,
    analyze_mesh, analyze_sprite, analyze_audio,
    QUALITY_THRESHOLDS,
)


# Prism Survivors-specific quality targets
PRISM_QUALITY = {
    "heroes": {
        "min_tris": 800,
        "max_tris": 1500,
    },
    "enemies_basic": {
        "min_tris": 200,
        "max_tris": 600,
    },
    "enemies_elite": {
        "min_tris": 500,
        "max_tris": 1000,
    },
    "enemies_boss": {
        "min_tris": 1500,
        "max_tris": 2000,
    },
    "pickups": {
        "min_tris": 50,
        "max_tris": 200,
    },
    "projectiles": {
        "min_tris": 20,
        "max_tris": 100,
    },
    "arena": {
        "min_tris": 500,
        "max_tris": 1500,
    },
    "textures": {
        "max_size": 256,
        "max_colors": 64,
    },
    "audio": {
        "sample_rate": 22050,
        "max_duration_ms": 1000,
    },
}

# Asset categorization
HERO_NAMES = ["knight", "mage", "ranger", "cleric", "necromancer", "paladin"]
BASIC_ENEMY_NAMES = ["crawler", "skeleton", "wisp", "golem", "shade", "berserker", "arcane_sentinel"]
ELITE_ENEMY_NAMES = ["crystal_knight", "void_mage", "golem_titan", "specter_lord"]
BOSS_NAMES = ["prism_colossus", "void_dragon"]
PICKUP_NAMES = ["xp_gem", "coin", "powerup_orb"]
PROJECTILE_NAMES = ["frost_shard", "void_orb", "lightning_bolt"]
ARENA_NAMES = ["arena_floor"]


def categorize_mesh(name: str) -> str:
    """Determine mesh category from name."""
    if name in HERO_NAMES:
        return "heroes"
    elif name in BASIC_ENEMY_NAMES:
        return "enemies_basic"
    elif name in ELITE_ENEMY_NAMES:
        return "enemies_elite"
    elif name in BOSS_NAMES:
        return "enemies_boss"
    elif name in PICKUP_NAMES:
        return "pickups"
    elif name in PROJECTILE_NAMES:
        return "projectiles"
    elif name in ARENA_NAMES:
        return "arena"
    return "pickups"  # Default to smallest budget


def validate_meshes(assets_dir: Path, report: QualityReport) -> int:
    """Validate mesh assets (GLB/OBJ files)."""
    meshes_dir = assets_dir / "models" / "meshes"
    if not meshes_dir.exists():
        meshes_dir = assets_dir / "meshes"
    if not meshes_dir.exists():
        print(f"  Warning: {meshes_dir} not found")
        return 0

    count = 0
    for mesh_file in list(meshes_dir.glob("*.glb")) + list(meshes_dir.glob("*.obj")):
        try:
            quality = analyze_mesh(mesh_file)
            report.meshes[mesh_file.stem] = quality

            # Get category-specific limits
            category = categorize_mesh(mesh_file.stem)
            limits = PRISM_QUALITY.get(category, {"min_tris": 50, "max_tris": 1000})

            # Check against limits
            in_budget = limits["min_tris"] <= quality.triangle_count <= limits["max_tris"]
            status = "PASS" if quality.passes_minimum() and in_budget else "FAIL"

            details = f"{quality.triangle_count} tris ({category})"
            if not in_budget:
                details += f" [target: {limits['min_tris']}-{limits['max_tris']}]"

            print(f"  {mesh_file.stem}: {status} ({details})")
            count += 1
        except Exception as e:
            print(f"  {mesh_file.stem}: ERROR - {e}")

    return count


def validate_textures(assets_dir: Path, report: QualityReport) -> int:
    """Validate texture assets (PNG files)."""
    textures_dir = assets_dir / "models" / "textures"
    if not textures_dir.exists():
        textures_dir = assets_dir / "textures"
    if not textures_dir.exists():
        print(f"  Warning: {textures_dir} not found")
        return 0

    count = 0
    limits = PRISM_QUALITY["textures"]

    for png_file in textures_dir.glob("*.png"):
        try:
            quality = analyze_sprite(png_file, max_palette=limits["max_colors"])
            report.sprites[f"texture:{png_file.stem}"] = quality

            # Check size limits
            max_dim = max(quality.width, quality.height)
            size_ok = max_dim <= limits["max_size"]
            colors_ok = quality.palette_colors <= limits["max_colors"]

            status = "PASS" if quality.passes_minimum() and size_ok else "FAIL"

            details = f"{quality.width}x{quality.height}, {quality.palette_colors} colors"
            if not size_ok:
                details += f" [max: {limits['max_size']}]"

            print(f"  {png_file.stem}: {status} ({details})")
            count += 1
        except Exception as e:
            print(f"  {png_file.stem}: ERROR - {e}")

    return count


def validate_audio(assets_dir: Path, report: QualityReport) -> int:
    """Validate audio assets (WAV files)."""
    audio_dir = assets_dir / "audio"
    if not audio_dir.exists():
        print(f"  Warning: {audio_dir} not found")
        return 0

    count = 0
    limits = PRISM_QUALITY["audio"]

    for wav_file in audio_dir.glob("*.wav"):
        try:
            quality = analyze_audio(wav_file)
            report.audio[wav_file.stem] = quality

            # Boss spawn can be longer
            is_long_sfx = wav_file.stem in ["boss_spawn", "level_up", "wave_complete"]
            max_duration = 2000 if is_long_sfx else limits["max_duration_ms"]

            duration_ok = quality.duration_ms <= max_duration

            status = "PASS" if quality.passes_minimum() and duration_ok else "FAIL"

            details = f"{quality.duration_ms}ms, peak: {quality.peak_level:.2f}"
            if not duration_ok:
                details += f" [max: {max_duration}ms]"

            print(f"  {wav_file.stem}: {status} ({details})")
            count += 1
        except Exception as e:
            print(f"  {wav_file.stem}: ERROR - {e}")

    return count


def validate_all(assets_dir: Path, quality_target: str = "development") -> QualityReport:
    """Validate all Prism Survivors assets.

    Args:
        assets_dir: Directory containing generated assets
        quality_target: Quality threshold (prototype, development, production, release)

    Returns:
        QualityReport with all validation results
    """
    report = QualityReport()
    threshold = QUALITY_THRESHOLDS.get(quality_target, QUALITY_THRESHOLDS["development"])

    print(f"\n{'='*60}")
    print(f"Prism Survivors Asset Validation")
    print(f"Target: {quality_target} (min score: {threshold['min_score']})")
    print(f"{'='*60}")

    print("\n--- Meshes ---")
    mesh_count = validate_meshes(assets_dir, report)

    print("\n--- Textures ---")
    texture_count = validate_textures(assets_dir, report)

    print("\n--- Audio ---")
    audio_count = validate_audio(assets_dir, report)

    # Summary
    total = mesh_count + texture_count + audio_count
    score = report.overall_score()
    passed = score >= threshold["min_score"]

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total Assets: {total}")
    print(f"  Meshes:   {mesh_count}")
    print(f"  Textures: {texture_count}")
    print(f"  Audio:    {audio_count}")
    print(f"")
    print(f"Overall Score: {score:.1f}/100")
    print(f"Target Score:  {threshold['min_score']}")
    print(f"Result:        {'PASS' if passed else 'FAIL'}")

    issues = report.all_issues()
    if issues:
        print(f"\n--- Issues ({len(issues)}) ---")
        for asset, issue_list in issues.items():
            print(f"  {asset}:")
            for issue in issue_list:
                print(f"    - {issue}")

    return report


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate Prism Survivors assets")
    parser.add_argument("--assets-dir", type=Path,
                        default=Path(__file__).parent.parent.parent.parent / "games" / "prism-survivors" / "assets",
                        help="Assets directory")
    parser.add_argument("--quality", choices=["prototype", "development", "production", "release"],
                        default="development", help="Quality target")
    args = parser.parse_args()

    report = validate_all(args.assets_dir, args.quality)
    sys.exit(0 if report.all_pass() else 1)


if __name__ == "__main__":
    main()
