"""Elite tier enemies (700-1000 tris)"""

from .crystal_knight import build_crystal_knight, CRYSTAL_KNIGHT_SPEC
from .void_mage import build_void_mage, VOID_MAGE_SPEC
from .golem_titan import build_golem_titan, GOLEM_TITAN_SPEC
from .specter_lord import build_specter_lord, SPECTER_LORD_SPEC

ALL_ELITE_ENEMIES = {
    "crystal_knight": (build_crystal_knight, CRYSTAL_KNIGHT_SPEC),
    "void_mage": (build_void_mage, VOID_MAGE_SPEC),
    "golem_titan": (build_golem_titan, GOLEM_TITAN_SPEC),
    "specter_lord": (build_specter_lord, SPECTER_LORD_SPEC),
}
