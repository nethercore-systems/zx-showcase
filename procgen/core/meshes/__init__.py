"""
Core mesh generators for ZX games.

Provides reusable mesh primitives, humanoid bases, vehicles, pickups,
and projectiles that can be customized with style tokens.
"""

from .primitives import (
    create_box,
    create_sphere,
    create_cylinder,
    create_torus,
    create_cone,
    create_prism,
    create_pyramid,
    create_capsule,
)

from .humanoid_base import (
    create_humanoid_skeleton,
    create_humanoid_mesh,
    HumanoidParams,
)

from .vehicle_base import (
    create_vehicle_chassis,
    create_wheel,
    VehicleParams,
)

from .pickup import (
    create_gem_pickup,
    create_health_pickup,
    create_xp_orb,
    create_powerup_cube,
    create_ammo_pickup,
    PickupParams,
)

from .projectile import (
    create_shard_projectile,
    create_orb_projectile,
    create_beam_projectile,
    create_bullet_projectile,
    create_missile_projectile,
    ProjectileParams,
)

__all__ = [
    # Primitives
    "create_box",
    "create_sphere",
    "create_cylinder",
    "create_torus",
    "create_cone",
    "create_prism",
    "create_pyramid",
    "create_capsule",
    # Humanoid
    "create_humanoid_skeleton",
    "create_humanoid_mesh",
    "HumanoidParams",
    # Vehicle
    "create_vehicle_chassis",
    "create_wheel",
    "VehicleParams",
    # Pickup
    "create_gem_pickup",
    "create_health_pickup",
    "create_xp_orb",
    "create_powerup_cube",
    "create_ammo_pickup",
    "PickupParams",
    # Projectile
    "create_shard_projectile",
    "create_orb_projectile",
    "create_beam_projectile",
    "create_bullet_projectile",
    "create_missile_projectile",
    "ProjectileParams",
]
