"""
Vehicle mesh generator for ZX console.

Generates low-poly vehicles for racing games (Neon Drift).
"""

from typing import Optional
from .primitives import MeshData, create_box, create_cylinder, create_prism, merge_meshes
from procgen.core import UniversalStyleParams


def generate_vehicle(
    style: UniversalStyleParams,
    preset: Optional[dict] = None,
    vehicle_type: str = "speedster",
) -> MeshData:
    """
    Generate a vehicle mesh for racing games.

    Args:
        style: Style tokens from game config
        preset: Optional preset from CAR_PRESETS
        vehicle_type: Vehicle style identifier

    Returns:
        MeshData with combined vehicle mesh
    """
    # Get polygon budget
    max_tris = getattr(style.poly_budget, "vehicle", 1000)

    detail = _calculate_detail(max_tris)
    silhouette = preset.get("silhouette", "classic_sports") if preset else "classic_sports"

    parts = []

    # Body based on silhouette
    body = _generate_body(silhouette, detail)
    parts.append(body)

    # Wheels (4 wheels)
    wheels = _generate_wheels(silhouette, detail)
    parts.extend(wheels)

    # Cockpit/windshield
    cockpit = _generate_cockpit(silhouette, detail)
    parts.append(cockpit)

    # Details (spoiler, vents, etc) if budget allows
    if max_tris > 600:
        details = _generate_details(silhouette, detail)
        parts.extend(details)

    return merge_meshes(parts)


def _calculate_detail(max_tris: int) -> int:
    """Calculate detail level from triangle budget."""
    if max_tris < 400:
        return 1
    elif max_tris < 800:
        return 2
    else:
        return 3


def _generate_body(silhouette: str, detail: int) -> MeshData:
    """Generate vehicle body based on silhouette type."""
    # Base dimensions
    length = 4.0
    width = 2.0
    height = 0.8

    if silhouette == "formula":
        # Formula car - narrow, long, low
        return create_box(width * 0.7, length * 1.2, height * 0.6, center=(0, 0, height * 0.3))

    elif silhouette == "muscle_car":
        # Muscle car - wide, aggressive
        return create_box(width * 1.1, length, height * 1.1, center=(0, 0, height * 0.55))

    elif silhouette == "jdm_hatch":
        # JDM hatchback - compact, boxy
        return create_box(width * 0.9, length * 0.85, height * 1.2, center=(0, 0, height * 0.6))

    elif silhouette == "hypercar":
        # Hypercar - extremely low, wedge
        # Use tapered prism for wedge shape
        return create_prism(
            sides=4,
            radius=width * 0.7,
            height=height * 0.5,
            taper=0.6,
            center=(0, 0, height * 0.25),
        )

    elif silhouette == "stealth_supercar":
        # Stealth - angular facets
        return create_prism(
            sides=6,
            radius=width * 0.6,
            height=height * 0.7,
            taper=0.75,
            center=(0, 0, height * 0.35),
        )

    elif silhouette == "luxury_gt":
        # Grand tourer - elegant, long hood
        return create_box(width, length * 1.1, height * 0.9, center=(0, 0, height * 0.45))

    else:  # classic_sports (default)
        # Classic sports car
        return create_box(width, length, height, center=(0, 0, height * 0.5))


def _generate_wheels(silhouette: str, detail: int) -> list:
    """Generate four wheels."""
    wheels = []

    # Wheel dimensions
    wheel_radius = 0.3
    wheel_width = 0.15
    segments = max(6, 4 + detail * 2)

    # Wheel positions depend on silhouette
    if silhouette == "formula":
        wheel_x = 0.9
        front_y, rear_y = 1.5, -1.2
    elif silhouette == "jdm_hatch":
        wheel_x = 0.7
        front_y, rear_y = 0.9, -0.9
    else:
        wheel_x = 0.85
        front_y, rear_y = 1.3, -1.1

    wheel_z = wheel_radius

    positions = [
        (-wheel_x, front_y, wheel_z),  # Front left
        (wheel_x, front_y, wheel_z),   # Front right
        (-wheel_x, rear_y, wheel_z),   # Rear left
        (wheel_x, rear_y, wheel_z),    # Rear right
    ]

    for x, y, z in positions:
        wheel = create_cylinder(
            radius=wheel_radius,
            height=wheel_width,
            segments=segments,
            center=(x, y, z),
        )
        wheels.append(wheel)

    return wheels


def _generate_cockpit(silhouette: str, detail: int) -> MeshData:
    """Generate cockpit/windshield area."""
    if silhouette == "formula":
        # Open cockpit
        return create_prism(
            sides=4,
            radius=0.3,
            height=0.3,
            taper=0.8,
            center=(0, 0.2, 0.6),
        )
    else:
        # Enclosed cockpit
        return create_box(
            1.5, 1.2, 0.4,
            center=(0, 0.3, 0.9),
        )


def _generate_details(silhouette: str, detail: int) -> list:
    """Generate detail elements like spoiler, vents, etc."""
    details = []

    # Rear spoiler for some silhouettes
    if silhouette in ["jdm_hatch", "hypercar", "formula"]:
        spoiler = create_box(1.6, 0.1, 0.05, center=(0, -1.8, 1.0))
        spoiler_supports = [
            create_box(0.05, 0.1, 0.3, center=(-0.6, -1.8, 0.85)),
            create_box(0.05, 0.1, 0.3, center=(0.6, -1.8, 0.85)),
        ]
        details.append(spoiler)
        details.extend(spoiler_supports)

    # Side vents/intakes
    if silhouette in ["hypercar", "stealth_supercar", "muscle_car"]:
        left_vent = create_box(0.1, 0.3, 0.15, center=(-1.0, 0, 0.4))
        right_vent = create_box(0.1, 0.3, 0.15, center=(1.0, 0, 0.4))
        details.extend([left_vent, right_vent])

    return details


def generate_simple_vehicle(
    length: float = 4.0,
    width: float = 2.0,
    height: float = 0.8,
) -> MeshData:
    """Generate a simple placeholder vehicle for testing."""
    parts = []

    # Body
    body = create_box(width, length, height, center=(0, 0, height / 2 + 0.3))
    parts.append(body)

    # Wheels
    wheel_radius = 0.3
    wheel_width = 0.15
    wheel_z = wheel_radius
    wheel_x = width / 2 - 0.15
    front_y, rear_y = length / 2 - 0.5, -length / 2 + 0.5

    for x, y in [(wheel_x, front_y), (-wheel_x, front_y), (wheel_x, rear_y), (-wheel_x, rear_y)]:
        wheel = create_cylinder(wheel_radius, wheel_width, segments=6, center=(x, y, wheel_z))
        parts.append(wheel)

    return merge_meshes(parts)
