#!/usr/bin/env python3
"""Run all procedural generators for Override.

Usage:
    python generate_all.py           # Generate all
    python generate_all.py meshes    # Generate meshes only
    python generate_all.py sounds    # Generate sounds only
"""
import subprocess
import sys
from pathlib import Path

# Map folder to runner command
RUNNERS = {
    "meshes": ["blender", "--background", "--python"],  # HEADLESS Blender
    "sounds": ["python"],  # Audio generation
}

def run_generators(folder: str, runner: list[str]):
    """Run all generators in a folder."""
    folder_path = Path(__file__).parent / folder
    if not folder_path.exists():
        return

    for file in sorted(folder_path.glob("*.py")):
        if file.name.startswith("_"):
            continue
        print(f"\n{'='*60}")
        print(f"Generating: {folder}/{file.name}")
        print('='*60)

        cmd = runner + [str(file)]
        result = subprocess.run(cmd, capture_output=False)

        if result.returncode != 0:
            print(f"FAILED: {file.name}")
            sys.exit(1)

def main():
    # Parse arguments
    if len(sys.argv) > 1:
        folders = sys.argv[1:]
    else:
        folders = list(RUNNERS.keys())

    # Run generators
    for folder in folders:
        if folder not in RUNNERS:
            print(f"Unknown folder: {folder}")
            continue
        run_generators(folder, RUNNERS[folder])

    print("\n" + "="*60)
    print("All generators completed successfully!")
    print("="*60)

if __name__ == "__main__":
    main()
