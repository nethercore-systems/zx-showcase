#!/usr/bin/env python3
"""Run all procedural generators for Override.

Spec-driven workflow:
- Sounds: Uses _generate.py wrapper with spec files from .studio/sounds/
- Meshes: Traditional Blender generators (unique geometry)

Usage:
    python generate_all.py           # Generate all
    python generate_all.py meshes    # Generate meshes only
    python generate_all.py sounds    # Generate sounds only
"""
import subprocess
import sys
from pathlib import Path

# Generator configurations
# For spec-driven categories, we run the _generate.py wrapper
# For traditional categories, we run each *.py file individually
GENERATORS = {
    "meshes": {
        "type": "traditional",
        "runner": ["blender", "--background", "--python"],
    },
    "sounds": {
        "type": "spec-driven",
        "runner": ["python"],
        "wrapper": "_generate.py",
    },
}


def run_spec_driven(folder: str, config: dict):
    """Run spec-driven generator wrapper."""
    folder_path = Path(__file__).parent / folder
    wrapper_path = folder_path / config["wrapper"]

    if not wrapper_path.exists():
        print(f"Warning: No wrapper found at {wrapper_path}")
        return

    print(f"\n{'='*60}")
    print(f"Generating {folder} from specs...")
    print('='*60)

    cmd = config["runner"] + [str(wrapper_path)]
    result = subprocess.run(cmd, capture_output=False)

    if result.returncode != 0:
        print(f"FAILED: {folder}")
        sys.exit(1)


def run_traditional(folder: str, config: dict):
    """Run traditional individual generators."""
    folder_path = Path(__file__).parent / folder
    if not folder_path.exists():
        return

    for file in sorted(folder_path.glob("*.py")):
        if file.name.startswith("_"):
            continue
        print(f"\n{'='*60}")
        print(f"Generating: {folder}/{file.name}")
        print('='*60)

        cmd = config["runner"] + [str(file)]
        result = subprocess.run(cmd, capture_output=False)

        if result.returncode != 0:
            print(f"FAILED: {file.name}")
            sys.exit(1)


def main():
    # Parse arguments
    if len(sys.argv) > 1:
        folders = sys.argv[1:]
    else:
        folders = list(GENERATORS.keys())

    # Run generators
    for folder in folders:
        if folder not in GENERATORS:
            print(f"Unknown folder: {folder}")
            continue

        config = GENERATORS[folder]
        if config["type"] == "spec-driven":
            run_spec_driven(folder, config)
        else:
            run_traditional(folder, config)

    print("\n" + "="*60)
    print("All generators completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()
