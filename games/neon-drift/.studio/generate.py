#!/usr/bin/env python3
"""
Unified Asset Generator - Discovers specs and routes to parsers.

Scans .studio/specs/ for .spec.py files and generates assets using the
appropriate parser based on the containing folder.

Usage:
    python .studio/generate.py                    # Generate all assets
    python .studio/generate.py --only textures    # Generate only textures
    python .studio/generate.py --spec hero.spec.py # Generate specific spec
    python .studio/generate.py --dry-run          # Show what would generate
    python .studio/generate.py --clean            # Remove generated assets

Output goes to generated/ directory (parallel to .studio/).
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, Callable, Dict, List

# Ensure parsers module is importable
STUDIO_ROOT = Path(__file__).parent
sys.path.insert(0, str(STUDIO_ROOT))

from parsers import (
    texture,
    sound,
    normal,
)

# Try to import optional parsers
try:
    from parsers import character, animation
    HAS_CHARACTER = True
except ImportError:
    HAS_CHARACTER = False
    character = None
    animation = None

try:
    from parsers import music
    HAS_MUSIC = True
except ImportError:
    HAS_MUSIC = False


# =============================================================================
# CONFIGURATION
# =============================================================================

SPEC_ROOT = STUDIO_ROOT.parent / "specs"  # Read from ../specs/
ASSET_ROOT = STUDIO_ROOT.parent / "generated"

# Category -> (parser_module, output_extension)
PARSERS: Dict[str, tuple] = {
    "textures": (texture, ".png"),
    "sounds": (sound, ".wav"),
    "instruments": (sound, ".wav"),  # Uses sound parser with instrument mode
    "characters": (character, ".glb"),
    "animations": (animation, ".glb"),
    "normals": (normal, ".png"),
    "meshes": (None, ".glb"),  # TODO: Add mesh parser
}

if HAS_MUSIC:
    PARSERS["music"] = (music, ".xm")


# =============================================================================
# DISCOVERY
# =============================================================================

def discover_specs(only: Optional[str] = None) -> List[Path]:
    """Find all .spec.py files, optionally filtered by category."""
    if only:
        category_dir = SPEC_ROOT / only
        if not category_dir.exists():
            print(f"Warning: Category '{only}' not found at {category_dir}")
            return []
        return sorted(category_dir.glob("*.spec.py"))

    # Find all specs across all categories
    specs = []
    for category in PARSERS.keys():
        category_dir = SPEC_ROOT / category
        if category_dir.exists():
            specs.extend(category_dir.glob("*.spec.py"))

    return sorted(specs)


def get_parser(spec_path: Path) -> Optional[tuple]:
    """Get parser module and extension for a spec based on its folder."""
    category = spec_path.parent.name
    return PARSERS.get(category)


def get_output_path(spec_path: Path, extension: str) -> Path:
    """Determine output path for a spec."""
    category = spec_path.parent.name
    name = spec_path.stem.replace(".spec", "")
    return ASSET_ROOT / category / f"{name}{extension}"


# =============================================================================
# GENERATION
# =============================================================================

def generate_spec(spec_path: Path, dry_run: bool = False) -> bool:
    """Generate asset from a single spec file."""
    parser_info = get_parser(spec_path)

    if not parser_info:
        print(f"  [SKIP] No parser for: {spec_path}")
        return False

    parser_module, extension = parser_info

    if parser_module is None:
        print(f"  [SKIP] Parser not implemented: {spec_path.parent.name}")
        return False

    output_path = get_output_path(spec_path, extension)

    if dry_run:
        print(f"  [DRY] {spec_path.name} -> {output_path}")
        return True

    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Load spec
        spec = parser_module.load_spec(str(spec_path))

        # Generate based on category
        category = spec_path.parent.name

        if category == "textures":
            result = parser_module.generate_texture(spec)
            parser_module.write_png(str(output_path), result)

        elif category == "sounds":
            result = parser_module.generate_sfx(spec)
            sample_rate = spec.get('sound', {}).get('sample_rate', 22050)
            parser_module.write_wav(str(output_path), result, sample_rate)

        elif category == "instruments":
            result = parser_module.generate_instrument(spec)
            sample_rate = spec.get('instrument', {}).get('sample_rate', 22050)
            parser_module.write_wav(str(output_path), result, sample_rate)

        elif category == "characters":
            parser_module.generate_character(spec, str(output_path))

        elif category == "animations":
            parser_module.generate_animation(spec, str(output_path))

        elif category == "normals":
            result = parser_module.generate_normal_map(spec)
            parser_module.write_png(str(output_path), result)

        elif category == "music" and HAS_MUSIC:
            parser_module.generate_song(spec, str(output_path))

        print(f"  [OK] {spec_path.name} -> {output_path.relative_to(ASSET_ROOT.parent)}")
        return True

    except Exception as e:
        print(f"  [ERR] {spec_path.name}: {e}")
        return False


def generate_all(
    only: Optional[str] = None,
    spec_file: Optional[str] = None,
    dry_run: bool = False
) -> tuple[int, int]:
    """Generate all specs, returning (success_count, error_count)."""

    if spec_file:
        # Single spec mode
        spec_path = Path(spec_file)
        if not spec_path.is_absolute():
            spec_path = SPEC_ROOT / spec_file

        if not spec_path.exists():
            print(f"Error: Spec file not found: {spec_path}")
            return 0, 1

        specs = [spec_path]
    else:
        specs = discover_specs(only)

    if not specs:
        print("No specs found.")
        return 0, 0

    # Group by category for nicer output
    by_category: Dict[str, List[Path]] = {}
    for spec in specs:
        category = spec.parent.name
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(spec)

    success = 0
    errors = 0

    for category, category_specs in sorted(by_category.items()):
        print(f"\n=== {category.upper()} ({len(category_specs)} specs) ===")

        for spec_path in category_specs:
            if generate_spec(spec_path, dry_run):
                success += 1
            else:
                errors += 1

    return success, errors


def clean_generated(only: Optional[str] = None):
    """Remove generated assets."""
    if only:
        target = ASSET_ROOT / only
        if target.exists():
            import shutil
            shutil.rmtree(target)
            print(f"Cleaned: {target}")
    else:
        if ASSET_ROOT.exists():
            import shutil
            shutil.rmtree(ASSET_ROOT)
            print(f"Cleaned: {ASSET_ROOT}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Unified asset generator for Nethercore ZX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python .studio/generate.py                     Generate all assets
  python .studio/generate.py --only textures     Generate only textures
  python .studio/generate.py --only sounds       Generate only sounds
  python .studio/generate.py --spec hero.spec.py Generate specific spec
  python .studio/generate.py --dry-run           Preview without generating
  python .studio/generate.py --clean             Remove all generated assets
        """
    )

    parser.add_argument(
        "--only",
        choices=list(PARSERS.keys()),
        help="Only generate assets of this type"
    )
    parser.add_argument(
        "--spec",
        help="Generate a specific spec file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without actually generating"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove generated assets"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_specs",
        help="List all discovered specs"
    )

    args = parser.parse_args()

    print("=" * 50)
    print("  Nethercore ZX - Unified Asset Generator")
    print("=" * 50)
    print(f"Specs:  {SPEC_ROOT}")
    print(f"Output: {ASSET_ROOT}")

    if args.clean:
        clean_generated(args.only)
        return

    if args.list_specs:
        specs = discover_specs(args.only)
        print(f"\nDiscovered {len(specs)} spec(s):")
        for spec in specs:
            print(f"  {spec.relative_to(SPEC_ROOT)}")
        return

    success, errors = generate_all(
        only=args.only,
        spec_file=args.spec,
        dry_run=args.dry_run
    )

    print("\n" + "=" * 50)
    if args.dry_run:
        print(f"Dry run complete: {success} would generate, {errors} would skip")
    else:
        print(f"Generation complete: {success} succeeded, {errors} failed")

    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
