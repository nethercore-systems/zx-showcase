"""
ZX Showcase - Game Style Token Configurations

Each game has its own style tokens that configure the shared procedural
asset generation pipeline for their specific aesthetic.
"""

from .neon_drift import STYLE_TOKENS as NEON_DRIFT_TOKENS
from .lumina_depths import STYLE_TOKENS as LUMINA_DEPTHS_TOKENS
from .prism_survivors import STYLE_TOKENS as PRISM_SURVIVORS_TOKENS
from .override import STYLE_TOKENS as OVERRIDE_TOKENS


def get_style_tokens(game_name: str):
    """Get style tokens for a specific game."""
    tokens = {
        "neon_drift": NEON_DRIFT_TOKENS,
        "neon-drift": NEON_DRIFT_TOKENS,
        "lumina_depths": LUMINA_DEPTHS_TOKENS,
        "lumina-depths": LUMINA_DEPTHS_TOKENS,
        "prism_survivors": PRISM_SURVIVORS_TOKENS,
        "prism-survivors": PRISM_SURVIVORS_TOKENS,
        "override": OVERRIDE_TOKENS,
    }
    return tokens.get(game_name.lower())


__all__ = [
    "NEON_DRIFT_TOKENS",
    "LUMINA_DEPTHS_TOKENS",
    "PRISM_SURVIVORS_TOKENS",
    "OVERRIDE_TOKENS",
    "get_style_tokens",
]
