"""
Override - Asset Quality Validation

Validates all generated Override assets against quality standards.
Aligned with zx-procgen creative-orchestrator workflow.

Usage:
    python run.py --game override --validate
"""

from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from procgen.core.quality import (
    QualityReport, TextureQuality, SpriteQuality, AudioQuality,
    analyze_texture, analyze_sprite, analyze_audio,
    QUALITY_THRESHOLDS,
)
from procgen.configs.override import TILESET_DEFS, SPRITE_DEFS, VFX_DEFS, UI_DEFS, SFX_DEFS


# Override-specific quality targets
OVERRIDE_QUALITY = {
    "tilesets": {
        "max_colors": 8,      # 8x8 tiles should be limited
        "target_size": 8,     # 8x8 pixels
    },
    "sprites": {
        "max_colors": 16,     # Sprite palette limit
        "sizes": [(8, 8), (16, 16), (16, 24), (32, 4)],
    },
    "vfx": {
        "max_colors": 8,
        "allow_alpha": True,
    },
    "audio": {
        "sample_rate": 22050,  # ZX audio sample rate
        "max_duration_ms": 1000,
    },
}


def validate_tilesets(assets_dir: Path, report: QualityReport) -> int:
    """Validate tileset assets."""
    tiles_dir = assets_dir / "tilesets"
    if not tiles_dir.exists():
        print(f"  Warning: {tiles_dir} not found")
        return 0

    count = 0
    for png_file in tiles_dir.glob("*.png"):
        try:
            quality = analyze_sprite(png_file, max_palette=OVERRIDE_QUALITY["tilesets"]["max_colors"])
            report.sprites[f"tileset:{png_file.stem}"] = quality
            count += 1

            status = "PASS" if quality.passes_minimum() else "FAIL"
            print(f"  {png_file.stem}: {status} (colors: {quality.palette_colors})")
        except Exception as e:
            print(f"  {png_file.stem}: ERROR - {e}")

    return count


def validate_sprites(assets_dir: Path, report: QualityReport) -> int:
    """Validate sprite assets."""
    sprites_dir = assets_dir / "sprites"
    if not sprites_dir.exists():
        print(f"  Warning: {sprites_dir} not found")
        return 0

    count = 0
    for subdir in ["doors", "traps", "characters"]:
        subpath = sprites_dir / subdir
        if not subpath.exists():
            continue
        for png_file in subpath.glob("*.png"):
            try:
                quality = analyze_sprite(png_file, max_palette=OVERRIDE_QUALITY["sprites"]["max_colors"])
                report.sprites[f"sprite:{subdir}/{png_file.stem}"] = quality
                count += 1

                status = "PASS" if quality.passes_minimum() else "FAIL"
                print(f"  {subdir}/{png_file.stem}: {status} ({quality.width}x{quality.height}, {quality.palette_colors} colors)")
            except Exception as e:
                print(f"  {subdir}/{png_file.stem}: ERROR - {e}")

    return count


def validate_vfx(assets_dir: Path, report: QualityReport) -> int:
    """Validate VFX assets."""
    vfx_dir = assets_dir / "vfx"
    if not vfx_dir.exists():
        print(f"  Warning: {vfx_dir} not found")
        return 0

    count = 0
    for png_file in vfx_dir.glob("*.png"):
        try:
            quality = analyze_sprite(png_file, max_palette=OVERRIDE_QUALITY["vfx"]["max_colors"])
            report.sprites[f"vfx:{png_file.stem}"] = quality
            count += 1

            status = "PASS" if quality.passes_minimum() else "FAIL"
            print(f"  {png_file.stem}: {status} ({quality.width}x{quality.height})")
        except Exception as e:
            print(f"  {png_file.stem}: ERROR - {e}")

    return count


def validate_ui(assets_dir: Path, report: QualityReport) -> int:
    """Validate UI assets."""
    ui_dir = assets_dir / "ui"
    if not ui_dir.exists():
        print(f"  Warning: {ui_dir} not found")
        return 0

    count = 0
    for png_file in ui_dir.glob("*.png"):
        try:
            quality = analyze_sprite(png_file, max_palette=16)
            report.sprites[f"ui:{png_file.stem}"] = quality
            count += 1

            status = "PASS" if quality.passes_minimum() else "FAIL"
            print(f"  {png_file.stem}: {status}")
        except Exception as e:
            print(f"  {png_file.stem}: ERROR - {e}")

    return count


def validate_audio(assets_dir: Path, report: QualityReport) -> int:
    """Validate audio assets."""
    audio_dir = assets_dir / "audio"
    if not audio_dir.exists():
        print(f"  Warning: {audio_dir} not found")
        return 0

    count = 0
    for wav_file in audio_dir.glob("*.wav"):
        try:
            quality = analyze_audio(wav_file)
            report.audio[wav_file.stem] = quality
            count += 1

            status = "PASS" if quality.passes_minimum() else "FAIL"
            print(f"  {wav_file.stem}: {status} ({quality.duration_ms}ms, peak: {quality.peak_level:.2f})")
        except Exception as e:
            print(f"  {wav_file.stem}: ERROR - {e}")

    return count


def validate_all(assets_dir: Path, quality_target: str = "development") -> QualityReport:
    """
    Validate all Override assets.

    Args:
        assets_dir: Directory containing generated assets
        quality_target: Quality threshold (prototype, development, production, release)

    Returns:
        QualityReport with all validation results
    """
    report = QualityReport()
    threshold = QUALITY_THRESHOLDS.get(quality_target, QUALITY_THRESHOLDS["development"])

    print(f"\n{'='*60}")
    print(f"Override Asset Validation")
    print(f"Target: {quality_target} (min score: {threshold['min_score']})")
    print(f"{'='*60}")

    print("\n--- Tilesets ---")
    tileset_count = validate_tilesets(assets_dir, report)

    print("\n--- Sprites ---")
    sprite_count = validate_sprites(assets_dir, report)

    print("\n--- VFX ---")
    vfx_count = validate_vfx(assets_dir, report)

    print("\n--- UI ---")
    ui_count = validate_ui(assets_dir, report)

    print("\n--- Audio ---")
    audio_count = validate_audio(assets_dir, report)

    # Summary
    total = tileset_count + sprite_count + vfx_count + ui_count + audio_count
    score = report.overall_score()
    passed = score >= threshold["min_score"]

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total Assets: {total}")
    print(f"  Tilesets: {tileset_count}")
    print(f"  Sprites:  {sprite_count}")
    print(f"  VFX:      {vfx_count}")
    print(f"  UI:       {ui_count}")
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

    parser = argparse.ArgumentParser(description="Validate Override assets")
    parser.add_argument("--assets-dir", type=Path,
                        default=Path(__file__).parent.parent.parent.parent / "games" / "override" / "assets",
                        help="Assets directory")
    parser.add_argument("--quality", choices=["prototype", "development", "production", "release"],
                        default="development", help="Quality target")
    args = parser.parse_args()

    report = validate_all(args.assets_dir, args.quality)
    sys.exit(0 if report.all_pass() else 1)


if __name__ == "__main__":
    main()
