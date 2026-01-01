"""Basic tier enemies (200-600 tris)"""

from .crawler import build_crawler, CRAWLER_SPEC
from .skeleton import build_skeleton, SKELETON_SPEC
from .wisp import build_wisp, WISP_SPEC
from .shade import build_shade, SHADE_SPEC
from .golem import build_golem, GOLEM_SPEC
from .berserker import build_berserker, BERSERKER_SPEC
from .arcane_sentinel import build_arcane_sentinel, ARCANE_SENTINEL_SPEC

ALL_BASIC_ENEMIES = {
    "crawler": (build_crawler, CRAWLER_SPEC),
    "skeleton": (build_skeleton, SKELETON_SPEC),
    "wisp": (build_wisp, WISP_SPEC),
    "shade": (build_shade, SHADE_SPEC),
    "golem": (build_golem, GOLEM_SPEC),
    "berserker": (build_berserker, BERSERKER_SPEC),
    "arcane_sentinel": (build_arcane_sentinel, ARCANE_SENTINEL_SPEC),
}
