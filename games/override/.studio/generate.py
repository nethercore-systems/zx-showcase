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
    from parsers import music
    HAS_MUSIC = True
except ImportError:
    HAS_MUSIC = False

# Try to import Blender-dependent parsers
HAS_BLENDER = False
try:
    import bpy
    from parsers import character, animation
    HAS_BLENDER = True
except ImportError:
    character = None
    animation = None


# =============================================================================
# CONFIGURATION
# =============================================================================

SPEC_ROOT = STUDIO_ROOT / "specs"
ASSET_ROOT = STUDIO_ROOT.parent / "generated"

# Category -> (parser_module, output_extension)
PARSERS: Dict[str, tuple] = {
    "textures": (texture, ".png"),
    "sounds": (sound, ".wav"),
    "instruments": (sound, ".wav"),  # Uses sound parser with instrument mode
    "normals": (normal, ".png"),
    "meshes": (None, ".glb"),  # TODO: Add mesh parser
}

if HAS_BLENDER:
    PARSERS["characters"] = (character, ".glb")
    PARSERS["animations"] = (animation, ".glb")

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

    # Find all specs across all category folders (not just those with parsers)
    specs = []
    if SPEC_ROOT.exists():
        for category_dir in SPEC_ROOT.iterdir():
            if category_dir.is_dir():
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
# VALIDATION
# =============================================================================

def validate_animation_against_character_spec(anim_spec: dict, char_spec: dict, anim_path: Path) -> None:
    """
    Validate animation spec bones against character spec skeleton.

    This is an early check BEFORE any Blender work. Catches mismatches
    between animation and character specs at the spec level.

    Args:
        anim_spec: Loaded animation spec dict
        char_spec: Loaded character spec dict
        anim_path: Path to animation spec (for error messages)

    Raises:
        ValueError: If animation references bones not in character skeleton
    """
    # Import preset requirements from animation parser
    if HAS_BLENDER:
        from parsers.animation import PRESET_REQUIREMENTS, collect_referenced_bones
    else:
        # Can't validate without Blender - will be caught at runtime
        return

    # Get character skeleton bones
    skeleton = char_spec.get('character', char_spec).get('skeleton', [])
    char_bones = set()
    for bone_def in skeleton:
        bone_name = bone_def.get('bone')
        if bone_name:
            char_bones.add(bone_name)
        # Handle mirrored bones
        mirror = bone_def.get('mirror')
        if mirror:
            # Mirrored bones use opposite side naming
            if bone_name.endswith('_L'):
                char_bones.add(bone_name[:-2] + '_R')
            elif bone_name.endswith('_R'):
                char_bones.add(bone_name[:-2] + '_L')

    if not char_bones:
        print(f"  [WARN] No skeleton found in character spec")
        return

    # Get animation bone references
    referenced = collect_referenced_bones(anim_spec)

    # Get preset requirements
    anim = anim_spec.get('animation', anim_spec)
    rig_setup = anim.get('rig_setup', {})
    presets = rig_setup.get('presets', {})

    preset_required = {}
    for preset_name, enabled in presets.items():
        if not enabled:
            continue
        requirements = PRESET_REQUIREMENTS.get(preset_name, {})
        for bone in requirements.get('required', []):
            if bone not in preset_required:
                preset_required[bone] = []
            preset_required[bone].append(f"preset '{preset_name}'")

    # Find missing bones
    all_missing = {}

    for bone, locations in referenced.items():
        if bone not in char_bones:
            all_missing[bone] = locations

    for bone, sources in preset_required.items():
        if bone not in char_bones:
            if bone in all_missing:
                all_missing[bone].extend(sources)
            else:
                all_missing[bone] = sources

    if all_missing:
        lines = [
            f"Animation spec '{anim_path.name}' references bones not in character skeleton:",
            "",
            "Missing bones:"
        ]

        for bone, locations in sorted(all_missing.items()):
            loc_str = ", ".join(locations[:3])
            if len(locations) > 3:
                loc_str += f", ... ({len(locations)} total)"
            lines.append(f"  - {bone} (referenced in: {loc_str})")

        lines.extend([
            "",
            f"Character skeleton has {len(char_bones)} bones:",
            "  " + ", ".join(sorted(char_bones)),
            "",
            "Fix: Add missing bones to character spec, or remove references from animation spec."
        ])

        raise ValueError("\n".join(lines))


def get_character_spec_for_animation(anim_spec: dict, anim_path: Path) -> Optional[dict]:
    """
    Find and load the character spec referenced by an animation spec.

    Returns None if character spec not found or not specified.
    """
    anim = anim_spec.get('animation', anim_spec)

    # Check for character reference
    char_name = anim.get('character')
    input_armature = anim.get('input_armature', '')

    # Try to infer character name from input_armature path
    if not char_name and input_armature:
        # e.g., "generated/characters/knight.glb" -> "knight"
        # e.g., "../characters/knight.glb" -> "knight"
        from pathlib import Path as P
        armature_path = P(input_armature)
        char_name = armature_path.stem  # "knight.glb" -> "knight"

    if not char_name:
        return None

    # Look for character spec
    char_spec_path = SPEC_ROOT / "characters" / f"{char_name}.spec.py"
    if not char_spec_path.exists():
        print(f"  [WARN] Character spec not found: {char_spec_path}")
        return None

    # Load character spec
    try:
        if HAS_BLENDER:
            from parsers import character
            return character.load_spec(str(char_spec_path))
        else:
            # Simple exec-based loading
            with open(char_spec_path, 'r') as f:
                code = f.read()
            namespace = {}
            exec(code, namespace)
            return namespace.get('CHARACTER', namespace.get('character', {}))
    except Exception as e:
        print(f"  [WARN] Failed to load character spec: {e}")
        return None


# =============================================================================
# GENERATION
# =============================================================================

def generate_spec(spec_path: Path, dry_run: bool = False) -> bool:
    """Generate asset from a single spec file."""
    category = spec_path.parent.name
    parser_info = get_parser(spec_path)

    if not parser_info:
        # Check if this is a Blender-dependent category
        if category in ["characters", "animations"] and not HAS_BLENDER:
            print(f"  [SKIP] {spec_path.name}: Requires Blender (run via: blender --background --python .studio/generate.py)")
        else:
            print(f"  [SKIP] No parser for: {spec_path}")
        return False

    parser_module, extension = parser_info

    if parser_module is None:
        print(f"  [SKIP] Parser not implemented: {category}")
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

        # For music, determine format from spec and update output path
        category = spec_path.parent.name
        if category == "music" and HAS_MUSIC:
            song = spec.get('song', spec)
            fmt = song.get('format', 'xm')
            if not output_path.name.endswith(f'.{fmt}'):
                output_path = output_path.with_suffix(f'.{fmt}')

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
            armature, merged = parser_module.generate_character(spec)
            parser_module.export_character(armature, merged, str(output_path))

        elif category == "animations":
            # Early spec-to-spec validation (before any Blender work)
            char_spec = get_character_spec_for_animation(spec, spec_path)
            if char_spec:
                validate_animation_against_character_spec(spec, char_spec, spec_path)
            parser_module.generate_animation(spec, str(output_path))

        elif category == "normals":
            result = parser_module.generate_normal(spec)
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
