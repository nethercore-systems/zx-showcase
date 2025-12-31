"""
Neon Drift - Asset Quality Validation

Validates all generated Neon Drift assets against quality standards.
Aligned with zx-procgen creative-orchestrator workflow.

Usage:
    python run.py --game neon-drift --validate
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


# Neon Drift-specific quality targets
NEON_QUALITY = {
    "vehicles": {
        "min_tris": 800,
        "max_tris": 1200,
    },
    "tracks": {
        "min_tris": 100,
        "max_tris": 2000,
    },
    "props": {
        "min_tris": 50,
        "max_tris": 800,
    },
    "textures": {
        "max_size": 256,
        "max_colors": 64,
    },
    "audio": {
        "sample_rate": 22050,
        "max_duration_ms": 1000,  # SFX should be short
    },
}

# Asset categorization
VEHICLE_NAMES = ["speedster", "muscle", "racer", "drift", "phantom", "titan", "viper"]
TRACK_NAMES = ["track_straight", "track_curve_left", "track_curve_right",
               "track_tunnel", "track_jump", "track_checkpoint"]
PROP_NAMES = ["prop_barrier", "prop_boost_pad", "prop_billboard",
              "prop_building", "crystal_formation"]


def categorize_mesh(name: str) -> str:
    """Determine mesh category from name."""
    if name in VEHICLE_NAMES:
        return "vehicles"
    elif name in TRACK_NAMES or name.startswith("track_"):
        return "tracks"
    elif name in PROP_NAMES or name.startswith("prop_"):
        return "props"
    return "props"  # Default


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
            limits = NEON_QUALITY.get(category, {"min_tris": 50, "max_tris": 1000})

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
    limits = NEON_QUALITY["textures"]

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
    limits = NEON_QUALITY["audio"]

    for wav_file in audio_dir.glob("*.wav"):
        try:
            quality = analyze_audio(wav_file)
            report.audio[wav_file.stem] = quality

            # Synth samples can be longer
            is_synth = wav_file.stem.startswith("synth_")
            max_duration = 2000 if is_synth else limits["max_duration_ms"]

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
    """
    Validate all Neon Drift assets.

    Args:
        assets_dir: Directory containing generated assets
        quality_target: Quality threshold (prototype, development, production, release)

    Returns:
        QualityReport with all validation results
    """
    report = QualityReport()
    threshold = QUALITY_THRESHOLDS.get(quality_target, QUALITY_THRESHOLDS["development"])

    print(f"\n{'='*60}")
    print(f"Neon Drift Asset Validation")
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

    parser = argparse.ArgumentParser(description="Validate Neon Drift assets")
    parser.add_argument("--assets-dir", type=Path,
                        default=Path(__file__).parent.parent.parent.parent / "games" / "neon-drift" / "assets",
                        help="Assets directory")
    parser.add_argument("--quality", choices=["prototype", "development", "production", "release"],
                        default="development", help="Quality target")
    args = parser.parse_args()

    report = validate_all(args.assets_dir, args.quality)
    sys.exit(0 if report.all_pass() else 1)


if __name__ == "__main__":
    main()
