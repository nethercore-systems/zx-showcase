"""PRISM SURVIVORS - Hero Generators

Each hero has its own module with a dedicated builder function.
Import individual heroes or use generate_all_heroes().
"""

from .knight import build_knight, KNIGHT_SPEC
from .mage import build_mage, MAGE_SPEC
from .ranger import build_ranger, RANGER_SPEC
from .cleric import build_cleric, CLERIC_SPEC
from .necromancer import build_necromancer, NECROMANCER_SPEC
from .paladin import build_paladin, PALADIN_SPEC

ALL_HEROES = {
    "knight": (build_knight, KNIGHT_SPEC),
    "mage": (build_mage, MAGE_SPEC),
    "ranger": (build_ranger, RANGER_SPEC),
    "cleric": (build_cleric, CLERIC_SPEC),
    "necromancer": (build_necromancer, NECROMANCER_SPEC),
    "paladin": (build_paladin, PALADIN_SPEC),
}

def generate_hero(name: str, output_path: str):
    """Generate a single hero mesh."""
    if name not in ALL_HEROES:
        raise ValueError(f"Unknown hero: {name}")

    builder, spec = ALL_HEROES[name]
    mesh = builder(spec)
    mesh.export(output_path)
    return mesh

def generate_all_heroes(output_dir: str):
    """Generate all hero meshes."""
    from pathlib import Path
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for name, (builder, spec) in ALL_HEROES.items():
        output_path = f"{output_dir}/{name}.glb"
        mesh = builder(spec)
        mesh.export(output_path)
        print(f"Generated {name}: {mesh.tri_count} tris -> {output_path}")
