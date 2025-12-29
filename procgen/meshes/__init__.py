"""
ZX Showcase - Procedural Mesh Generators

Generates low-poly meshes optimized for ZX console constraints.
All generators accept style tokens to parameterize the output.
"""

from .primitives import (
    MeshData,
    create_box,
    create_sphere,
    create_cylinder,
    create_prism,
    create_torus,
)
from .humanoid import generate_humanoid
from .vehicles import generate_vehicle
from .crystals import generate_crystal
from .creatures import generate_creature
from .environment import generate_prop


__all__ = [
    # Data types
    "MeshData",
    # Primitives
    "create_box",
    "create_sphere",
    "create_cylinder",
    "create_prism",
    "create_torus",
    # Complex generators
    "generate_humanoid",
    "generate_vehicle",
    "generate_crystal",
    "generate_creature",
    "generate_prop",
]
