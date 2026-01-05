#!/usr/bin/env python3
"""Generate all sounds from specs.

This is the spec-driven sound generator for Neon Drift.
It reads .spec.py files from .studio/sounds/ and generates WAV files.
"""
import sys
from pathlib import Path

# Add procgen lib to path
PROCGEN_LIB = Path(__file__).parents[4] / "procgen" / "lib"
sys.path.insert(0, str(PROCGEN_LIB))

from sound_parser import load_spec, generate_sfx, write_wav

SPEC_DIR = Path(__file__).parents[2] / "specs" / "sounds"
OUTPUT_DIR = Path(__file__).parents[2] / "generated" / "sounds"


def generate():
    """Generate all sounds from specs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    spec_files = list(SPEC_DIR.glob("*.spec.py"))
    if not spec_files:
        print(f"No spec files found in {SPEC_DIR}")
        return

    print(f"\nGenerating {len(spec_files)} sounds from specs...")
    print(f"Spec dir: {SPEC_DIR}")
    print(f"Output dir: {OUTPUT_DIR}\n")

    for spec_file in sorted(spec_files):
        try:
            spec = load_spec(str(spec_file))
            sound = spec.get('sound', spec)
            name = sound.get('name', spec_file.stem)
            signal = generate_sfx(spec)
            sample_rate = sound.get('sample_rate', 22050)
            output_path = OUTPUT_DIR / f"{name}.wav"
            write_wav(str(output_path), signal, sample_rate)
        except Exception as e:
            print(f"Error generating {spec_file.stem}: {e}")
            raise


if __name__ == "__main__":
    generate()
    print("\nDone!")
