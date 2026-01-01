"""Override - Damaged Floor Tile (8x8)"""

from typing import Dict
from procgen.lib.pixel_art import hex_to_rgba, PixelGrid
from .floor_metal import generate_floor_metal


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
