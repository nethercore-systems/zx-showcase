"""
Core audio generators for ZX games.

Provides reusable SFX and musical elements that can be customized
with style tokens.
"""

from .ui_sfx import (
    generate_menu_click,
    generate_menu_hover,
    generate_menu_confirm,
    generate_menu_cancel,
    generate_menu_error,
    generate_notification,
)

from .impact_sfx import (
    generate_hit,
    generate_explosion,
    generate_impact,
    generate_crunch,
    generate_shatter,
)

from .ambient_sfx import (
    generate_hum,
    generate_drone,
    generate_wind,
    generate_water,
    generate_machinery,
)

from .musical import (
    generate_bass_sample,
    generate_lead_sample,
    generate_pad_sample,
    generate_arp_sample,
    generate_drum_kit,
)

__all__ = [
    # UI SFX
    "generate_menu_click",
    "generate_menu_hover",
    "generate_menu_confirm",
    "generate_menu_cancel",
    "generate_menu_error",
    "generate_notification",
    # Impact SFX
    "generate_hit",
    "generate_explosion",
    "generate_impact",
    "generate_crunch",
    "generate_shatter",
    # Ambient SFX
    "generate_hum",
    "generate_drone",
    "generate_wind",
    "generate_water",
    "generate_machinery",
    # Musical
    "generate_bass_sample",
    "generate_lead_sample",
    "generate_pad_sample",
    "generate_arp_sample",
    "generate_drum_kit",
]
