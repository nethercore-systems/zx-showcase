"""
Nethercore ZX Asset Parsers

This module contains all parsers for the spec-driven asset pipeline.
Each parser reads .spec.py files and generates corresponding assets.

Parsers:
    texture  - Procedural textures (albedo, patterns)
    sound    - SFX and instrument synthesis
    character - Character meshes with rigs (Blender bpy)
    animation - Skeletal animations (Blender bpy)
    normal   - Normal map generation
    music    - Tracker music (XM/IT format)
"""

from . import texture
from . import sound
from . import normal

# Optional: character/animation parsers (require Blender bpy)
try:
    from . import character
    from . import animation
except ImportError:
    pass

# Optional: music parser (requires xm_writer/it_writer)
try:
    from . import music
except ImportError:
    pass

__all__ = [
    'texture',
    'sound',
    'character',
    'animation',
    'normal',
    'music',
]
