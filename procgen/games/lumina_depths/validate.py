"""
Lumina Depths - Asset Quality Validation

Validates all generated Lumina Depths assets against quality standards.
Aligned with zx-procgen creative-orchestrator workflow.

Usage:
    python run.py --game lumina_depths --validate
"""

from pathlib import Path
from typing import Dict, List
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from procgen.core.quality import (
    QualityReport, MeshQuality, AudioQuality,
    analyze_mesh, analyze_audio,
    QUALITY_THRESHOLDS,
)


# Lumina Depths-specific quality targets
LUMINA_QUALITY = {
    "meshes": {
        # Poly budgets by category
        "submersible": {"min_tris": 200, "max_tris": 800},
        "whale": {"min_tris": 400, "max_tris": 1500},
        "large_creature": {"min_tris": 200, "max_tris": 1000},  # manta ray, sea turtle
        "small_creature": {"min_tris": 50, "max_tris": 400},   # reef fish, coral crab
        "deep_creature": {"min_tris": 100, "max_tris": 600},   # anglerfish, jellyfish
        "colony": {"min_tris": 200, "max_tris": 800},          # tube worms (multiple instances)
    },
    "audio": {
        "ambient": {
            "sample_rate": 44100,
            "min_duration_s": 30,
            "max_duration_s": 150,
        },
        "creature": {
            "sample_rate": 44100,
            "min_duration_s": 2,
            "max_duration_s": 15,
        },
    },
}

# Map creature names to size categories
CREATURE_CATEGORIES = {
    "submersible": "submersible",
    "blue_whale": "whale",
    "sperm_whale": "whale",
    "manta_ray": "large_creature",
    "sea_turtle": "large_creature",
    "reef_fish": "small_creature",
    "coral_crab": "small_creature",
    "moon_jelly": "deep_creature",
    "lanternfish": "small_creature",
    "anglerfish": "deep_creature",
    "tube_worms": "colony",
}


def validate_meshes(assets_dir: Path, report: QualityReport) -> int:
    """Validate mesh assets (OBJ files)."""
    meshes_dir = assets_dir / "meshes"
    if not meshes_dir.exists():
        print(f"  Warning: {meshes_dir} not found")
        return 0

    count = 0
    for obj_file in meshes_dir.glob("*.obj"):
        try:
            quality = analyze_mesh(obj_file)
            report.meshes[obj_file.stem] = quality

            # Get category-specific limits
            category = CREATURE_CATEGORIES.get(obj_file.stem, "small_creature")
            limits = LUMINA_QUALITY["meshes"].get(category, {"min_tris": 50, "max_tris": 500})

            # Check against limits
            in_budget = limits["min_tris"] <= quality.triangle_count <= limits["max_tris"]
            status = "PASS" if quality.passes_minimum() and in_budget else "FAIL"

            details = f"{quality.triangle_count} tris"
            if not in_budget:
                details += f" (target: {limits['min_tris']}-{limits['max_tris']})"

            print(f"  {obj_file.stem}: {status} ({details})")
            count += 1
        except Exception as e:
            print(f"  {obj_file.stem}: ERROR - {e}")

    return count


def validate_audio(assets_dir: Path, report: QualityReport) -> int:
    """Validate audio assets (WAV files)."""
    audio_dir = assets_dir / "audio"
    if not audio_dir.exists():
        print(f"  Warning: {audio_dir} not found")
        return 0

    count = 0
    for wav_file in audio_dir.glob("*.wav"):
        try:
            quality = analyze_audio(wav_file)
            report.audio[wav_file.stem] = quality

            # Determine audio type
            is_ambient = wav_file.stem.startswith("ambient_")
            audio_type = "ambient" if is_ambient else "creature"
            limits = LUMINA_QUALITY["audio"][audio_type]

            duration_s = quality.duration_ms / 1000
            in_range = limits["min_duration_s"] <= duration_s <= limits["max_duration_s"]

            status = "PASS" if quality.passes_minimum() and in_range else "FAIL"

            details = f"{duration_s:.1f}s, peak: {quality.peak_level:.2f}"
            if not in_range:
                details += f" (target: {limits['min_duration_s']}-{limits['max_duration_s']}s)"

            print(f"  {wav_file.stem}: {status} ({details})")
            count += 1
        except Exception as e:
            print(f"  {wav_file.stem}: ERROR - {e}")

    return count


def validate_all(assets_dir: Path, quality_target: str = "development") -> QualityReport:
    """
    Validate all Lumina Depths assets.

    Args:
        assets_dir: Directory containing generated assets
        quality_target: Quality threshold (prototype, development, production, release)

    Returns:
        QualityReport with all validation results
    """
    report = QualityReport()
    threshold = QUALITY_THRESHOLDS.get(quality_target, QUALITY_THRESHOLDS["development"])

    print(f"\n{'='*60}")
    print(f"Lumina Depths Asset Validation")
    print(f"Target: {quality_target} (min score: {threshold['min_score']})")
    print(f"{'='*60}")

    print("\n--- Meshes ---")
    mesh_count = validate_meshes(assets_dir, report)

    print("\n--- Audio ---")
    audio_count = validate_audio(assets_dir, report)

    # Summary
    total = mesh_count + audio_count
    score = report.overall_score()
    passed = score >= threshold["min_score"]

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total Assets: {total}")
    print(f"  Meshes: {mesh_count}")
    print(f"  Audio:  {audio_count}")
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

    parser = argparse.ArgumentParser(description="Validate Lumina Depths assets")
    parser.add_argument("--assets-dir", type=Path,
                        default=Path(__file__).parent.parent.parent.parent / "games" / "lumina-depths" / "assets",
                        help="Assets directory")
    parser.add_argument("--quality", choices=["prototype", "development", "production", "release"],
                        default="development", help="Quality target")
    args = parser.parse_args()

    report = validate_all(args.assets_dir, args.quality)
    sys.exit(0 if report.all_pass() else 1)


if __name__ == "__main__":
    main()
