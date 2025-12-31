"""
Override - Tileset Generation

Generates 8x8 pixel tiles for floors and walls.
Ported from build.rs tileset generators.
"""

from pathlib import Path
from typing import Dict, List, Tuple

from procgen.lib.pixel_art import (
    hex_to_rgba, blend, add_noise, export_png,
    RGBA, PixelGrid,
)


def create_tile(width: int = 8, height: int = 8, fill: RGBA = (0, 0, 0, 255)) -> PixelGrid:
    """Create an empty tile with a fill color."""
    return [[fill for _ in range(width)] for _ in range(height)]


def generate_floor_metal(palette: Dict[str, str]) -> PixelGrid:
    """Generate metal floor tile (8x8)."""
    metal = hex_to_rgba(palette["metal"])
    dark_metal = hex_to_rgba(palette["dark_metal"])
    shadow = hex_to_rgba(palette["shadow"])
    light_metal = hex_to_rgba(palette["light_metal"])
    highlight = hex_to_rgba(palette["highlight"])

    tile = create_tile(8, 8, metal)

    # Base gradient with noise
    for y in range(8):
        for x in range(8):
            t = (x + y) / 16.0
            color = blend(metal, dark_metal, t * 0.3)
            seed = (y * 8 + x) * 12345
            tile[y][x] = add_noise(color, 3, seed)

    # Panel lines
    for x in range(8):
        tile[0][x] = shadow
        tile[7][x] = light_metal
    for y in range(8):
        tile[y][0] = shadow

    # Rivets
    tile[1][1] = highlight
    tile[1][6] = highlight
    tile[6][1] = highlight
    tile[6][6] = highlight

    return tile


def generate_floor_grate(palette: Dict[str, str]) -> PixelGrid:
    """Generate grate floor tile (8x8)."""
    metal = hex_to_rgba(palette["metal"])
    dark_bg = hex_to_rgba(palette["dark_bg"])
    light_metal = hex_to_rgba(palette["light_metal"])

    tile = create_tile(8, 8, metal)

    # Base metal with noise
    for y in range(8):
        for x in range(8):
            seed = (y * 8 + x) * 54321
            tile[y][x] = add_noise(metal, 2, seed)

    # Grate holes
    for y in range(1, 7, 2):
        for x in range(1, 7, 2):
            tile[y][x] = dark_bg
            if x + 1 < 8:
                tile[y][x + 1] = dark_bg

    # Horizontal bars
    for x in range(8):
        tile[0][x] = light_metal
        tile[3][x] = light_metal
        tile[6][x] = light_metal

    return tile


def generate_floor_panel(palette: Dict[str, str]) -> PixelGrid:
    """Generate clean panel floor tile (8x8)."""
    light_metal = hex_to_rgba(palette["light_metal"])
    highlight = hex_to_rgba(palette["highlight"])

    tile = create_tile(8, 8, light_metal)

    # Noise
    for y in range(8):
        for x in range(8):
            seed = (y * 8 + x) * 98765
            tile[y][x] = add_noise(light_metal, 2, seed)

    # Edge highlights
    for x in range(8):
        tile[0][x] = highlight
    for y in range(8):
        tile[y][0] = highlight

    return tile


def generate_floor_damaged(palette: Dict[str, str]) -> PixelGrid:
    """Generate damaged floor tile with rust and cracks (8x8)."""
    rust = hex_to_rgba(palette["rust"])
    rust_dark = hex_to_rgba(palette["rust_dark"])
    black = hex_to_rgba(palette["black"])

    # Start with metal base
    tile = generate_floor_metal(palette)

    # Rust patches
    rust_positions = [(2, 3), (5, 5), (3, 6)]
    for rx, ry in rust_positions:
        if 0 <= rx < 8 and 0 <= ry < 8:
            tile[ry][rx] = rust_dark
            # Spread rust
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = rx + dx, ry + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    tile[ny][nx] = rust

    # Diagonal crack
    for i in range(8):
        tile[i][i] = black

    return tile


def generate_wall_solid(palette: Dict[str, str]) -> PixelGrid:
    """Generate solid wall tile (8x8)."""
    dark_metal = hex_to_rgba(palette["dark_metal"])
    shadow = hex_to_rgba(palette["shadow"])
    metal = hex_to_rgba(palette["metal"])

    tile = create_tile(8, 8, dark_metal)

    # Vertical gradient with noise
    for y in range(8):
        for x in range(8):
            t = y / 8.0
            color = blend(dark_metal, shadow, t * 0.3)
            seed = (y * 8 + x) * 11111
            tile[y][x] = add_noise(color, 3, seed)

    # Horizontal details
    for x in range(8):
        tile[0][x] = metal
        tile[4][x] = shadow

    return tile


def generate_wall_window(palette: Dict[str, str]) -> PixelGrid:
    """Generate wall tile with window (8x8)."""
    glass = hex_to_rgba(palette.get("glass", "#55697D"))
    glass_dark = hex_to_rgba(palette.get("glass_dark", "#2D3744"))
    light_metal = hex_to_rgba(palette["light_metal"])

    tile = generate_wall_solid(palette)

    # Window glass
    for y in range(2, 6):
        for x in range(2, 6):
            t = (y - 2) / 4.0
            tile[y][x] = blend(glass, glass_dark, t)

    # Frame
    for x in range(1, 7):
        tile[1][x] = light_metal
        tile[6][x] = light_metal
    for y in range(1, 7):
        tile[y][1] = light_metal
        tile[y][6] = light_metal

    return tile


def generate_wall_vent(palette: Dict[str, str]) -> PixelGrid:
    """Generate wall tile with vent (8x8)."""
    black = hex_to_rgba(palette["black"])
    light_metal = hex_to_rgba(palette["light_metal"])
    shadow = hex_to_rgba(palette["shadow"])

    tile = generate_wall_solid(palette)

    # Vent opening
    for y in range(2, 6):
        for x in range(2, 6):
            tile[y][x] = black
        tile[y][1] = light_metal
        tile[y][6] = shadow

    return tile


def generate_wall_pipe(palette: Dict[str, str]) -> PixelGrid:
    """Generate wall tile with pipe (8x8)."""
    shadow = hex_to_rgba(palette["shadow"])
    metal = hex_to_rgba(palette["metal"])
    light_metal = hex_to_rgba(palette["light_metal"])

    tile = generate_wall_solid(palette)

    # Vertical pipe
    for y in range(8):
        tile[y][2] = shadow
        tile[y][3] = metal
        tile[y][4] = light_metal

    # Pipe joint
    for x in range(2, 5):
        tile[4][x] = metal

    return tile


def generate_wall_screen(palette: Dict[str, str]) -> PixelGrid:
    """Generate wall tile with screen (8x8)."""
    black = hex_to_rgba(palette["black"])
    cyan = hex_to_rgba(palette["cyan"])
    metal = hex_to_rgba(palette["metal"])

    tile = generate_wall_solid(palette)

    # Screen background
    for y in range(2, 6):
        for x in range(2, 6):
            tile[y][x] = black

    # Glowing elements
    tile[3][3] = cyan
    tile[3][4] = cyan
    tile[4][3] = cyan

    # Frame
    for x in range(1, 7):
        tile[1][x] = metal
        tile[6][x] = metal
    for y in range(1, 7):
        tile[y][1] = metal
        tile[y][6] = metal

    return tile


def generate_wall_doorframe(palette: Dict[str, str]) -> PixelGrid:
    """Generate wall tile with door frame (8x8)."""
    black = hex_to_rgba(palette["black"])
    light_metal = hex_to_rgba(palette["light_metal"])

    tile = generate_wall_solid(palette)

    # Door opening
    for y in range(8):
        tile[y][0] = light_metal
        tile[y][7] = light_metal
        for x in range(2, 6):
            tile[y][x] = black

    return tile


def generate_all_tilesets(output_dir: Path, palette: Dict[str, str]) -> int:
    """
    Generate all tilesets and save to output directory.

    Args:
        output_dir: Output directory
        palette: Color palette

    Returns:
        Number of tiles generated
    """
    tiles = {
        "floor_metal": generate_floor_metal(palette),
        "floor_grate": generate_floor_grate(palette),
        "floor_panel": generate_floor_panel(palette),
        "floor_damaged": generate_floor_damaged(palette),
        "wall_solid": generate_wall_solid(palette),
        "wall_window": generate_wall_window(palette),
        "wall_vent": generate_wall_vent(palette),
        "wall_pipe": generate_wall_pipe(palette),
        "wall_screen": generate_wall_screen(palette),
        "wall_doorframe": generate_wall_doorframe(palette),
    }

    for name, pixels in tiles.items():
        filepath = output_dir / f"{name}.png"
        export_png(pixels, filepath)
        print(f"  Exported: {name}.png")

    return len(tiles)
