"""Boss tier enemies (1500-2000 tris)"""

from .prism_colossus import build_prism_colossus, PRISM_COLOSSUS_SPEC
from .void_dragon import build_void_dragon, VOID_DRAGON_SPEC

ALL_BOSS_ENEMIES = {
    "prism_colossus": (build_prism_colossus, PRISM_COLOSSUS_SPEC),
    "void_dragon": (build_void_dragon, VOID_DRAGON_SPEC),
}
