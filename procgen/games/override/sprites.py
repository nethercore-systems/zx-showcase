"""
Override - Sprite Generation

Generates sprites for doors, traps, and characters.
"""

from pathlib import Path
from typing import Dict, List, Tuple

from procgen.lib.pixel_art import (
    hex_to_rgba, blend, add_noise, export_png,
    RGBA, PixelGrid,
)


def create_sprite(width: int, height: int, fill: RGBA = (0, 0, 0, 0)) -> PixelGrid:
    """Create an empty sprite with a fill color."""
    return [[fill for _ in range(width)] for _ in range(height)]


def draw_rect(
    sprite: PixelGrid,
    x: int, y: int,
    w: int, h: int,
    color: RGBA,
) -> None:
    """Draw a filled rectangle on a sprite."""
    height = len(sprite)
    width = len(sprite[0]) if height > 0 else 0
    for py in range(max(0, y), min(height, y + h)):
        for px in range(max(0, x), min(width, x + w)):
            sprite[py][px] = color


# =============================================================================
# DOOR SPRITES (8x16)
# =============================================================================

def generate_door_closed(palette: Dict[str, str]) -> PixelGrid:
    """Generate closed door sprite (8x16)."""
    dark_metal = hex_to_rgba(palette["dark_metal"])
    shadow = hex_to_rgba(palette["shadow"])
    light_metal = hex_to_rgba(palette["light_metal"])
    yellow = hex_to_rgba(palette["yellow"])

    sprite = create_sprite(8, 16)

    # Base metal
    for y in range(16):
        for x in range(8):
            seed = (y * 8 + x) * 22222
            sprite[y][x] = add_noise(dark_metal, 2, seed)

    # Panel lines
    for y in [0, 5, 10, 15]:
        for x in range(8):
            sprite[y][x] = shadow

    # Center line
    for y in range(16):
        sprite[y][4] = shadow

    # Highlights
    for y in [1, 6, 11]:
        for x in range(8):
            sprite[y][x] = light_metal

    # Lock indicator
    sprite[8][6] = yellow
    sprite[8][5] = shadow

    return sprite


def generate_door_open(palette: Dict[str, str]) -> PixelGrid:
    """Generate open door sprite (8x16)."""
    dark_metal = hex_to_rgba(palette["dark_metal"])
    shadow = hex_to_rgba(palette["shadow"])
    transparent = (0, 0, 0, 0)

    sprite = create_sprite(8, 16, transparent)

    # Door compressed to left side
    for y in range(16):
        for x in range(3):
            seed = (y * 8 + x) * 33333
            sprite[y][x] = add_noise(dark_metal, 2, seed)

    # Panel lines on compressed part
    for y in [0, 5, 10, 15]:
        for x in range(3):
            sprite[y][x] = shadow

    return sprite


def generate_door_locked(palette: Dict[str, str]) -> PixelGrid:
    """Generate locked door sprite (8x16)."""
    red_bright = hex_to_rgba(palette["red_bright"])
    yellow = hex_to_rgba(palette["yellow"])

    sprite = generate_door_closed(palette)

    # Red lock indicator
    for y in range(7, 10):
        for x in range(5, 7):
            sprite[y][x] = red_bright

    # Warning stripes
    for i in range(16):
        x = (i // 2) % 8
        if i % 4 < 2:
            sprite[i][x] = yellow

    return sprite


# =============================================================================
# TRAP SPRITES (8x8)
# =============================================================================

def generate_trap_spike(palette: Dict[str, str]) -> PixelGrid:
    """Generate spike trap sprite (8x8)."""
    dark_bg = hex_to_rgba(palette["dark_bg"])
    light_metal = hex_to_rgba(palette["light_metal"])
    bright = hex_to_rgba(palette["bright"])
    shadow = hex_to_rgba(palette["shadow"])

    sprite = create_sprite(8, 8, dark_bg)

    # Spike triangle
    center_x = 4
    for y in range(4, 8):
        width = (8 - y) // 2
        for x in range(center_x - width, center_x + width + 1):
            if 0 <= x < 8:
                sprite[y][x] = light_metal

    # Tip
    sprite[4][4] = bright

    # Base plate
    for x in range(8):
        sprite[7][x] = shadow

    return sprite


def generate_trap_gas(palette: Dict[str, str]) -> PixelGrid:
    """Generate gas trap sprite (8x8)."""
    dark_metal = hex_to_rgba(palette["dark_metal"])
    shadow = hex_to_rgba(palette["shadow"])
    yellow = hex_to_rgba(palette["yellow"])

    sprite = create_sprite(8, 8, dark_metal)

    # Add noise
    for y in range(8):
        for x in range(8):
            seed = (y * 8 + x) * 44444
            sprite[y][x] = add_noise(dark_metal, 2, seed)

    # Vent holes
    for y in range(1, 7, 2):
        for x in range(1, 7, 2):
            sprite[y][x] = shadow

    # Hazard stripes
    for x in range(8):
        sprite[0][x] = yellow
        sprite[7][x] = yellow

    return sprite


def generate_trap_laser(palette: Dict[str, str]) -> PixelGrid:
    """Generate laser trap sprite (8x8)."""
    dark_metal = hex_to_rgba(palette["dark_metal"])
    glass = hex_to_rgba(palette.get("glass", "#55697D"))
    red_bright = hex_to_rgba(palette["red_bright"])
    shadow = hex_to_rgba(palette["shadow"])
    light_metal = hex_to_rgba(palette["light_metal"])

    sprite = create_sprite(8, 8, dark_metal)

    # Lens (center glow)
    import math
    center = 4.0
    for y in range(8):
        for x in range(8):
            dist = math.sqrt((x - center) ** 2 + (y - center) ** 2)
            if dist < 2.0:
                sprite[y][x] = glass
            if dist < 1.5:
                sprite[y][x] = red_bright

    # Edge details
    for x in range(8):
        sprite[0][x] = shadow
        sprite[7][x] = light_metal

    return sprite


# =============================================================================
# CHARACTER SPRITES (8x12)
# =============================================================================

def generate_runner_idle(palette: Dict[str, str], frame: int = 0) -> PixelGrid:
    """Generate runner idle frame (8x12)."""
    cyan = hex_to_rgba(palette["cyan"])
    cyan_bright = hex_to_rgba(palette["cyan_bright"])
    metal = hex_to_rgba(palette["metal"])
    light_metal = hex_to_rgba(palette["light_metal"])
    transparent = (0, 0, 0, 0)

    sprite = create_sprite(8, 12, transparent)
    cx = 4

    # Head (3x3)
    for y in range(3):
        for x in range(cx - 1, cx + 2):
            if 0 <= x < 8:
                sprite[y][x] = cyan

    # Eyes
    sprite[1][cx - 1] = cyan_bright
    sprite[1][cx + 1] = cyan_bright

    # Body (4x5)
    for y in range(3, 8):
        for x in range(cx - 2, cx + 2):
            if 0 <= x < 8:
                sprite[y][x] = cyan

    # Belt/detail
    for x in range(cx - 2, cx + 2):
        if 0 <= x < 8:
            sprite[5][x] = metal

    # Legs (2x4 each)
    for y in range(8, 12):
        sprite[y][cx - 2] = cyan
        sprite[y][cx - 1] = cyan
        sprite[y][cx] = cyan
        sprite[y][cx + 1] = cyan

    # Feet
    sprite[11][cx - 2] = light_metal
    sprite[11][cx + 1] = light_metal

    # Breathing animation (slight offset for frames 1,2)
    if frame in [1, 2]:
        # Shift body down slightly (simulated by just changing colors)
        sprite[2][cx] = cyan_bright

    return sprite


def generate_drone_idle(palette: Dict[str, str], frame: int = 0) -> PixelGrid:
    """Generate drone idle frame (8x8)."""
    red = hex_to_rgba(palette["red"])
    red_bright = hex_to_rgba(palette["red_bright"])
    metal = hex_to_rgba(palette["metal"])
    dark_metal = hex_to_rgba(palette["dark_metal"])
    transparent = (0, 0, 0, 0)

    sprite = create_sprite(8, 8, transparent)

    # Oval body
    import math
    center_x, center_y = 4, 4
    for y in range(8):
        for x in range(8):
            dx = (x - center_x) / 3.5
            dy = (y - center_y) / 3.5
            dist = dx * dx + dy * dy
            if dist < 0.9:
                if dist < 0.3:
                    sprite[y][x] = metal
                elif dist < 0.6:
                    sprite[y][x] = dark_metal
                else:
                    sprite[y][x] = dark_metal

    # Eye (center, pulses with frame)
    eye_color = red_bright if frame % 2 == 0 else red
    sprite[center_y][center_x] = eye_color

    return sprite


def generate_all_sprites(output_dir: Path, palette: Dict[str, str]) -> int:
    """
    Generate all sprites and save to output directory.

    Args:
        output_dir: Output directory
        palette: Color palette

    Returns:
        Number of sprites generated
    """
    count = 0

    # Doors
    doors_dir = output_dir / "doors"
    doors_dir.mkdir(exist_ok=True)

    door_sprites = {
        "door_closed": generate_door_closed(palette),
        "door_open": generate_door_open(palette),
        "door_locked": generate_door_locked(palette),
    }
    for name, pixels in door_sprites.items():
        export_png(pixels, doors_dir / f"{name}.png")
        print(f"  Exported: doors/{name}.png")
        count += 1

    # Traps
    traps_dir = output_dir / "traps"
    traps_dir.mkdir(exist_ok=True)

    trap_sprites = {
        "trap_spike": generate_trap_spike(palette),
        "trap_gas": generate_trap_gas(palette),
        "trap_laser": generate_trap_laser(palette),
    }
    for name, pixels in trap_sprites.items():
        export_png(pixels, traps_dir / f"{name}.png")
        print(f"  Exported: traps/{name}.png")
        count += 1

    # Characters
    chars_dir = output_dir / "characters"
    chars_dir.mkdir(exist_ok=True)

    # Runner idle frames
    for frame in range(4):
        pixels = generate_runner_idle(palette, frame)
        export_png(pixels, chars_dir / f"runner_idle_{frame}.png")
        print(f"  Exported: characters/runner_idle_{frame}.png")
        count += 1

    # Drone idle frames
    for frame in range(4):
        pixels = generate_drone_idle(palette, frame)
        export_png(pixels, chars_dir / f"drone_idle_{frame}.png")
        print(f"  Exported: characters/drone_idle_{frame}.png")
        count += 1

    return count
