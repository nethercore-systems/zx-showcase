"""
Character sprite generation for 2D games.

Generates animated character sprites (runners, drones, NPCs).
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from ..base_params import UniversalStyleParams


@dataclass
class SpriteData:
    """Raw sprite pixel data."""
    width: int
    height: int
    pixels: List[List[Tuple[int, int, int, int]]]  # RGBA
    name: str = ""


@dataclass
class AnimationData:
    """Animation sequence data."""
    frames: List[SpriteData]
    frame_duration_ms: int = 100
    loop: bool = True
    name: str = ""


def hex_to_rgba(hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    """Convert hex color to RGBA tuple."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b, alpha)


def create_sprite(width: int, height: int, fill: Tuple[int, int, int, int] = (0, 0, 0, 0)) -> SpriteData:
    """Create an empty sprite with a fill color."""
    pixels = [[fill for _ in range(width)] for _ in range(height)]
    return SpriteData(width=width, height=height, pixels=pixels)


def draw_rect(
    sprite: SpriteData,
    x: int, y: int,
    w: int, h: int,
    color: Tuple[int, int, int, int],
) -> None:
    """Draw a filled rectangle on a sprite."""
    for py in range(max(0, y), min(sprite.height, y + h)):
        for px in range(max(0, x), min(sprite.width, x + w)):
            sprite.pixels[py][px] = color


def generate_character_sprite(
    char_type: str,
    palette: Dict[str, str],
    size: Tuple[int, int] = (16, 24),
) -> SpriteData:
    """
    Generate a character sprite.

    Args:
        char_type: Type of character (runner, drone)
        palette: Color palette dict with hex colors
        size: Sprite size (width, height)

    Returns:
        SpriteData with generated sprite
    """
    width, height = size
    transparent = (0, 0, 0, 0)
    sprite = create_sprite(width, height, transparent)

    # Get colors from palette
    body_color = hex_to_rgba(palette.get("cyan", "#2D7D91"))
    dark_color = hex_to_rgba(palette.get("cyan_dark", "#0F2D37"))
    highlight = hex_to_rgba(palette.get("cyan_bright", "#55B9D7"))
    metal = hex_to_rgba(palette.get("metal", "#343E4E"))

    if char_type == "runner":
        # Simple humanoid shape
        # Head (4x4 at center top)
        head_x = (width - 4) // 2
        draw_rect(sprite, head_x, 0, 4, 4, body_color)
        # Eyes
        sprite.pixels[1][head_x + 1] = highlight
        sprite.pixels[1][head_x + 2] = highlight

        # Body (6x8)
        body_x = (width - 6) // 2
        draw_rect(sprite, body_x, 4, 6, 8, body_color)
        # Body detail
        draw_rect(sprite, body_x + 2, 5, 2, 4, dark_color)

        # Arms (2x6 on each side)
        draw_rect(sprite, body_x - 2, 4, 2, 6, body_color)
        draw_rect(sprite, body_x + 6, 4, 2, 6, body_color)

        # Legs (2x10 each)
        leg_y = 12
        draw_rect(sprite, body_x, leg_y, 2, 10, body_color)
        draw_rect(sprite, body_x + 4, leg_y, 2, 10, body_color)

        # Feet
        draw_rect(sprite, body_x - 1, height - 2, 3, 2, metal)
        draw_rect(sprite, body_x + 4, height - 2, 3, 2, metal)

    elif char_type == "drone":
        # Circular/oval drone
        center_x, center_y = width // 2, height // 2

        # Main body (oval)
        for y in range(height):
            for x in range(width):
                dx = (x - center_x) / (width / 2)
                dy = (y - center_y) / (height / 2)
                dist = dx * dx + dy * dy
                if dist < 0.8:
                    if dist < 0.4:
                        sprite.pixels[y][x] = highlight
                    elif dist < 0.6:
                        sprite.pixels[y][x] = body_color
                    else:
                        sprite.pixels[y][x] = dark_color

        # Eye (center)
        sprite.pixels[center_y][center_x] = hex_to_rgba(palette.get("red_bright", "#E14141"))

    sprite.name = char_type
    return sprite


def generate_character_animation(
    char_type: str,
    animation_type: str,
    palette: Dict[str, str],
    size: Tuple[int, int] = (16, 24),
) -> AnimationData:
    """
    Generate an animated character sprite sequence.

    Args:
        char_type: Type of character (runner, drone)
        animation_type: Type of animation (idle, walk, run, death)
        palette: Color palette dict with hex colors
        size: Sprite size (width, height)

    Returns:
        AnimationData with animation frames
    """
    frames = []

    # Frame counts per animation type
    frame_counts = {
        "idle": 4,
        "walk": 8,
        "run": 6,
        "death": 4,
    }
    num_frames = frame_counts.get(animation_type, 4)

    # Frame duration (ms)
    durations = {
        "idle": 200,
        "walk": 100,
        "run": 80,
        "death": 150,
    }
    duration = durations.get(animation_type, 100)

    for i in range(num_frames):
        # Generate base sprite
        frame = generate_character_sprite(char_type, palette, size)

        # Apply animation offsets
        if animation_type == "idle":
            # Subtle breathing/bobbing
            if i in [1, 2]:
                # Shift all pixels down by 1
                new_pixels = [[(0, 0, 0, 0) for _ in range(frame.width)] for _ in range(frame.height)]
                for y in range(frame.height - 1):
                    for x in range(frame.width):
                        new_pixels[y + 1][x] = frame.pixels[y][x]
                frame.pixels = new_pixels

        elif animation_type == "walk":
            # Alternating leg positions
            # This is a simplified version - real implementation would be more complex
            pass

        elif animation_type == "death":
            # Fade out / collapse
            if i > 0:
                # Reduce alpha
                alpha_mult = 1.0 - (i / num_frames)
                for y in range(frame.height):
                    for x in range(frame.width):
                        r, g, b, a = frame.pixels[y][x]
                        frame.pixels[y][x] = (r, g, b, int(a * alpha_mult))

        frame.name = f"{char_type}_{animation_type}_{i}"
        frames.append(frame)

    return AnimationData(
        frames=frames,
        frame_duration_ms=duration,
        loop=(animation_type != "death"),
        name=f"{char_type}_{animation_type}",
    )


def generate_door_sprites(
    palette: Dict[str, str],
    size: Tuple[int, int] = (16, 16),
) -> Dict[str, SpriteData]:
    """
    Generate door state sprites.

    Args:
        palette: Color palette dict with hex colors
        size: Sprite size (width, height)

    Returns:
        Dict of door state sprites (closed, opening, open)
    """
    width, height = size
    transparent = (0, 0, 0, 0)

    dark_metal = hex_to_rgba(palette.get("dark_metal", "#232A34"))
    metal = hex_to_rgba(palette.get("metal", "#343E4E"))
    red_dark = hex_to_rgba(palette.get("red_dark", "#370F0F"))
    yellow = hex_to_rgba(palette.get("yellow", "#C3A52D"))
    green = hex_to_rgba(palette.get("green", "#2D874B"))

    doors = {}

    # Closed door
    closed = create_sprite(width, height, transparent)
    draw_rect(closed, 0, 0, width, height, dark_metal)
    draw_rect(closed, 2, 2, width - 4, height - 4, metal)
    # Red indicator
    draw_rect(closed, width // 2 - 1, 2, 2, 2, red_dark)
    closed.name = "door_closed"
    doors["closed"] = closed

    # Opening door
    opening = create_sprite(width, height, transparent)
    draw_rect(opening, 0, 0, width, height, dark_metal)
    # Gap in middle
    gap = width // 4
    draw_rect(opening, 2, 2, gap - 2, height - 4, metal)
    draw_rect(opening, width - gap, 2, gap - 2, height - 4, metal)
    # Yellow indicator
    draw_rect(opening, width // 2 - 1, 2, 2, 2, yellow)
    opening.name = "door_opening"
    doors["opening"] = opening

    # Open door
    open_door = create_sprite(width, height, transparent)
    draw_rect(open_door, 0, 0, width, height, dark_metal)
    # Open center
    draw_rect(open_door, 4, 0, width - 8, height, transparent)
    # Green indicator
    draw_rect(open_door, 2, 2, 2, 2, green)
    draw_rect(open_door, width - 4, 2, 2, 2, green)
    open_door.name = "door_open"
    doors["open"] = open_door

    return doors


def generate_trap_sprites(
    palette: Dict[str, str],
    size: Tuple[int, int] = (8, 8),
) -> Dict[str, SpriteData]:
    """
    Generate trap sprites.

    Args:
        palette: Color palette dict with hex colors
        size: Sprite size (width, height)

    Returns:
        Dict of trap sprites (spike, gas, laser)
    """
    width, height = size
    transparent = (0, 0, 0, 0)

    metal = hex_to_rgba(palette.get("metal", "#343E4E"))
    red = hex_to_rgba(palette.get("red", "#A52323"))
    red_bright = hex_to_rgba(palette.get("red_bright", "#E14141"))
    green_dark = hex_to_rgba(palette.get("green_dark", "#0F2D19"))
    green = hex_to_rgba(palette.get("green", "#2D874B"))

    traps = {}

    # Spike trap
    spike = create_sprite(width, height, transparent)
    # Metal base
    draw_rect(spike, 0, height - 2, width, 2, metal)
    # Spikes
    for x in range(1, width - 1, 2):
        spike.pixels[height - 3][x] = red
        spike.pixels[height - 4][x] = red_bright
        spike.pixels[height - 5][x] = red_bright
    spike.name = "trap_spike"
    traps["spike"] = spike

    # Gas trap
    gas = create_sprite(width, height, transparent)
    # Gas cloud
    for y in range(height):
        for x in range(width):
            # Create cloud shape
            dist = abs(x - width // 2) + abs(y - height // 2)
            if dist < width // 2:
                alpha = int(200 * (1 - dist / (width // 2)))
                if y < height // 2:
                    gas.pixels[y][x] = (*green[:3], alpha)
                else:
                    gas.pixels[y][x] = (*green_dark[:3], alpha)
    gas.name = "trap_gas"
    traps["gas"] = gas

    # Laser trap
    laser = create_sprite(width, height, transparent)
    # Horizontal laser beam
    beam_y = height // 2
    for x in range(width):
        laser.pixels[beam_y - 1][x] = red
        laser.pixels[beam_y][x] = red_bright
        laser.pixels[beam_y + 1][x] = red
    laser.name = "trap_laser"
    traps["laser"] = laser

    return traps
