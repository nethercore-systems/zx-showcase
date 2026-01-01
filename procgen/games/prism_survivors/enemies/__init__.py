"""PRISM SURVIVORS - Enemy Generators

Enemies organized by tier:
- basic/: 200-600 tris (7 enemies)
- elite/: 700-1000 tris (4 enemies)
- boss/: 1500-2000 tris (2 enemies)
"""

from .basic import ALL_BASIC_ENEMIES
from .elite import ALL_ELITE_ENEMIES
from .boss import ALL_BOSS_ENEMIES

ALL_ENEMIES = {
    **ALL_BASIC_ENEMIES,
    **ALL_ELITE_ENEMIES,
    **ALL_BOSS_ENEMIES,
}

def generate_enemy(name: str, output_path: str):
    """Generate a single enemy mesh."""
    if name not in ALL_ENEMIES:
        raise ValueError(f"Unknown enemy: {name}")

    builder, spec = ALL_ENEMIES[name]
    mesh = builder(spec)
    mesh.export(output_path)
    return mesh

def generate_all_enemies(output_dir: str):
    """Generate all enemy meshes."""
    from pathlib import Path
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for name, (builder, spec) in ALL_ENEMIES.items():
        output_path = f"{output_dir}/{name}.glb"
        mesh = builder(spec)
        mesh.export(output_path)
        print(f"Generated {name}: {mesh.tri_count} tris -> {output_path}")
