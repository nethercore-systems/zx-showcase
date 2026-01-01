"""Override - Trap Sprite Generators"""

from .trap_spike import generate_trap_spike
from .trap_gas import generate_trap_gas
from .trap_laser import generate_trap_laser

__all__ = [
    "generate_trap_spike",
    "generate_trap_gas",
    "generate_trap_laser",
]
