"""
Lumina Depths - Procedural Asset Generation Module

Generates all assets for the Lumina Depths game using Blender metaballs:
- Submersible (player vehicle)
- Whales (epic encounters)
- Zone creatures (16+ creatures across 4 zones)

Usage:
    blender --background --python run_blender.py -- --game lumina-depths --all

The metaball-based generators are in blender_creatures.py.
Legacy OBJ-based generators are deprecated but still present in other files.
"""

# Note: blender_creatures.py is imported dynamically when running in Blender
# to avoid import errors when Blender's bpy module is not available.

__all__ = [
    # Main entry point for Blender-based generation is in blender_creatures.py
    # Imported dynamically from run_blender.py
]
