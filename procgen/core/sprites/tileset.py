"""
Tileset generation for 2D games.

Generates 8x8 pixel tiles for floors and walls.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from ..base_params import UniversalStyleParams


@dataclass
class TileData:
    """Raw tile pixel data."""
    width: int
    height: int
    pixels: List[List[Tuple[int, int, int, int]]]  # RGBA
    name: str = ""


def hex_to_rgba(hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    """Convert hex color to RGBA tuple."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b, alpha)


def blend(c1: Tuple[int, int, int, int], c2: Tuple[int, int, int, int], t: float) -> Tuple[int, int, int, int]:
    """Blend two colors."""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] * (1 - t) + c2[0] * t),
        int(c1[1] * (1 - t) + c2[1] * t),
        int(c1[2] * (1 - t) + c2[2] * t),
        int(c1[3] * (1 - t) + c2[3] * t),
    )


def add_noise(c: Tuple[int, int, int, int], amount: int, seed: int) -> Tuple[int, int, int, int]:
    """Add deterministic noise to a color."""
    def hash_fn(s: int) -> int:
        x = (s * 0x5851f42d4c957f2d) & 0xFFFFFFFFFFFFFFFF
        return ((x >> 32) % (amount * 2 + 1)) - amount

    return (
        max(0, min(255, c[0] + hash_fn(seed))),
        max(0, min(255, c[1] + hash_fn(seed + 1))),
        max(0, min(255, c[2] + hash_fn(seed + 2))),
        c[3],
    )


def create_tile(width: int = 8, height: int = 8, fill: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> TileData:
    """Create an empty tile with a fill color."""
    pixels = [[fill for _ in range(width)] for _ in range(height)]
    return TileData(width=width, height=height, pixels=pixels)


def generate_floor_tile(
    tile_type: str,
    palette: Dict[str, str],
    size: int = 8,
) -> TileData:
    """
    Generate a floor tile.

    Args:
        tile_type: Type of floor (metal, grate, panel, damaged)
        palette: Color palette dict with hex colors
        size: Tile size in pixels

    Returns:
        TileData with generated tile
    """
    # Get colors from palette
    metal = hex_to_rgba(palette.get("metal", "#343E4E"))
    dark_metal = hex_to_rgba(palette.get("dark_metal", "#232A34"))
    light_metal = hex_to_rgba(palette.get("light_metal", "#485569"))
    shadow = hex_to_rgba(palette.get("shadow", "#191E26"))
    highlight = hex_to_rgba(palette.get("highlight", "#5F7087"))
    dark_bg = hex_to_rgba(palette.get("dark_bg", "#12161C"))
    rust = hex_to_rgba(palette.get("rust", "#553426"))
    rust_dark = hex_to_rgba(palette.get("rust_dark", "#342016"))
    black = hex_to_rgba(palette.get("black", "#0A0C0F"))

    tile = create_tile(size, size, metal)

    if tile_type == "metal":
        # Base gradient with noise
        for y in range(size):
            for x in range(size):
                t = (x + y) / (size * 2)
                color = blend(metal, dark_metal, t * 0.3)
                seed = (y * size + x) * 12345
                tile.pixels[y][x] = add_noise(color, 3, seed)

        # Panel lines
        for x in range(size):
            tile.pixels[0][x] = shadow
            tile.pixels[size - 1][x] = light_metal
        for y in range(size):
            tile.pixels[y][0] = shadow

        # Rivets at corners
        tile.pixels[1][1] = highlight
        tile.pixels[1][size - 2] = highlight
        tile.pixels[size - 2][1] = highlight
        tile.pixels[size - 2][size - 2] = highlight

    elif tile_type == "grate":
        # Base metal
        for y in range(size):
            for x in range(size):
                seed = (y * size + x) * 54321
                tile.pixels[y][x] = add_noise(metal, 2, seed)

        # Grate holes
        for y in range(1, size - 1, 2):
            for x in range(1, size - 1, 2):
                tile.pixels[y][x] = dark_bg
                if x + 1 < size:
                    tile.pixels[y][x + 1] = dark_bg

        # Horizontal bars
        for x in range(size):
            tile.pixels[0][x] = light_metal
            if size > 3:
                tile.pixels[3][x] = light_metal
            if size > 6:
                tile.pixels[6][x] = light_metal

    elif tile_type == "panel":
        # Clean panel
        for y in range(size):
            for x in range(size):
                seed = (y * size + x) * 98765
                tile.pixels[y][x] = add_noise(light_metal, 2, seed)

        # Edge highlights
        for x in range(size):
            tile.pixels[0][x] = highlight
        for y in range(size):
            tile.pixels[y][0] = highlight

    elif tile_type == "damaged":
        # Start with metal base
        tile = generate_floor_tile("metal", palette, size)

        # Rust patches
        rust_positions = [(2, 3), (5, 5), (3, 6)]
        for rx, ry in rust_positions:
            if 0 <= rx < size and 0 <= ry < size:
                tile.pixels[ry][rx] = rust_dark
                # Spread rust
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = rx + dx, ry + dy
                    if 0 <= nx < size and 0 <= ny < size:
                        tile.pixels[ny][nx] = rust

        # Diagonal crack
        for i in range(size):
            if 0 <= i < size:
                tile.pixels[i][i] = black

    tile.name = f"floor_{tile_type}"
    return tile


def generate_wall_tile(
    tile_type: str,
    palette: Dict[str, str],
    size: int = 8,
) -> TileData:
    """
    Generate a wall tile.

    Args:
        tile_type: Type of wall (solid, window, vent, pipe, screen, doorframe)
        palette: Color palette dict with hex colors
        size: Tile size in pixels

    Returns:
        TileData with generated tile
    """
    dark_metal = hex_to_rgba(palette.get("dark_metal", "#232A34"))
    metal = hex_to_rgba(palette.get("metal", "#343E4E"))
    light_metal = hex_to_rgba(palette.get("light_metal", "#485569"))
    shadow = hex_to_rgba(palette.get("shadow", "#191E26"))
    glass_dark = hex_to_rgba(palette.get("glass_dark", "#2D3744"))
    cyan_dark = hex_to_rgba(palette.get("cyan_dark", "#0F2D37"))
    cyan = hex_to_rgba(palette.get("cyan", "#2D7D91"))
    yellow_dark = hex_to_rgba(palette.get("yellow_dark", "#372D0F"))

    tile = create_tile(size, size, dark_metal)

    if tile_type == "solid":
        # Vertical gradient
        for y in range(size):
            for x in range(size):
                t = y / size
                color = blend(dark_metal, metal, t * 0.3)
                seed = (y * size + x) * 11111
                tile.pixels[y][x] = add_noise(color, 2, seed)

    elif tile_type == "window":
        # Dark metal frame
        for y in range(size):
            for x in range(size):
                tile.pixels[y][x] = dark_metal

        # Glass center
        for y in range(2, size - 2):
            for x in range(2, size - 2):
                tile.pixels[y][x] = glass_dark

        # Frame edges
        for x in range(size):
            tile.pixels[1][x] = metal
            tile.pixels[size - 2][x] = metal
        for y in range(size):
            tile.pixels[y][1] = metal
            tile.pixels[y][size - 2] = metal

    elif tile_type == "vent":
        # Horizontal slats
        for y in range(size):
            for x in range(size):
                if y % 2 == 0:
                    tile.pixels[y][x] = dark_metal
                else:
                    tile.pixels[y][x] = shadow

    elif tile_type == "pipe":
        # Background
        for y in range(size):
            for x in range(size):
                tile.pixels[y][x] = dark_metal

        # Vertical pipe in center
        pipe_x = size // 2
        for y in range(size):
            if pipe_x - 1 >= 0:
                tile.pixels[y][pipe_x - 1] = metal
            tile.pixels[y][pipe_x] = light_metal
            if pipe_x + 1 < size:
                tile.pixels[y][pipe_x + 1] = metal

    elif tile_type == "screen":
        # Background
        for y in range(size):
            for x in range(size):
                tile.pixels[y][x] = dark_metal

        # Screen area
        for y in range(1, size - 1):
            for x in range(1, size - 1):
                tile.pixels[y][x] = cyan_dark

        # Glow center
        center = size // 2
        if 0 <= center < size:
            tile.pixels[center][center] = cyan

    elif tile_type == "doorframe":
        # Background
        for y in range(size):
            for x in range(size):
                tile.pixels[y][x] = dark_metal

        # Yellow warning frame
        tile.pixels[0][0] = yellow_dark
        tile.pixels[0][size - 1] = yellow_dark
        tile.pixels[size - 1][0] = yellow_dark
        tile.pixels[size - 1][size - 1] = yellow_dark

    tile.name = f"wall_{tile_type}"
    return tile


def generate_tileset(
    style: UniversalStyleParams,
    tile_types: Optional[List[str]] = None,
) -> Dict[str, TileData]:
    """
    Generate a complete tileset for a game.

    Args:
        style: Universal style parameters
        tile_types: Optional list of tile types to generate

    Returns:
        Dict mapping tile names to TileData
    """
    # Extract palette from style
    palette = {}
    if hasattr(style, 'palette'):
        # Map primary colors to named palette entries
        if style.palette.primary:
            palette["metal"] = style.palette.primary[0] if len(style.palette.primary) > 0 else "#343E4E"
            palette["dark_metal"] = style.palette.primary[1] if len(style.palette.primary) > 1 else "#232A34"
            palette["light_metal"] = style.palette.primary[2] if len(style.palette.primary) > 2 else "#485569"
            palette["shadow"] = style.palette.primary[3] if len(style.palette.primary) > 3 else "#191E26"
        if style.palette.neutral:
            palette["black"] = style.palette.neutral[0] if len(style.palette.neutral) > 0 else "#0A0C0F"
            palette["dark_bg"] = style.palette.neutral[1] if len(style.palette.neutral) > 1 else "#12161C"
            palette["highlight"] = style.palette.neutral[2] if len(style.palette.neutral) > 2 else "#5F7087"
        if style.palette.accent:
            palette["cyan"] = style.palette.accent[0] if len(style.palette.accent) > 0 else "#2D7D91"
            palette["cyan_dark"] = "#0F2D37"
            palette["yellow_dark"] = "#372D0F"

    # Default palette values
    palette.setdefault("metal", "#343E4E")
    palette.setdefault("dark_metal", "#232A34")
    palette.setdefault("light_metal", "#485569")
    palette.setdefault("shadow", "#191E26")
    palette.setdefault("highlight", "#5F7087")
    palette.setdefault("dark_bg", "#12161C")
    palette.setdefault("black", "#0A0C0F")
    palette.setdefault("rust", "#553426")
    palette.setdefault("rust_dark", "#342016")
    palette.setdefault("cyan", "#2D7D91")
    palette.setdefault("cyan_dark", "#0F2D37")
    palette.setdefault("glass_dark", "#2D3744")
    palette.setdefault("yellow_dark", "#372D0F")

    # Get resolution from style
    size = style.textures.resolution if hasattr(style, 'textures') else 8

    # Default tile types
    if tile_types is None:
        tile_types = [
            "floor_metal", "floor_grate", "floor_panel", "floor_damaged",
            "wall_solid", "wall_window", "wall_vent", "wall_pipe",
            "wall_screen", "wall_doorframe",
        ]

    tiles = {}
    for tile_name in tile_types:
        if tile_name.startswith("floor_"):
            tile_type = tile_name[6:]  # Remove "floor_" prefix
            tiles[tile_name] = generate_floor_tile(tile_type, palette, size)
        elif tile_name.startswith("wall_"):
            tile_type = tile_name[5:]  # Remove "wall_" prefix
            tiles[tile_name] = generate_wall_tile(tile_type, palette, size)

    return tiles
