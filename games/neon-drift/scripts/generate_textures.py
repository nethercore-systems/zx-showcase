#!/usr/bin/env python3
"""Generate textures for Neon Drift track segments and props.

Creates synthwave-styled PNG textures for the ZX console.
"""

from pathlib import Path

try:
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("PIL not available. Install with: pip install Pillow")


def create_texture(size: tuple, fill: tuple) -> Image:
    """Create a base texture with solid fill."""
    return Image.new('RGB', size, fill)


def generate_track_texture(path: Path, base_color: tuple, line_color: tuple, size: int = 128):
    """Generate a track texture with lane lines."""
    img = create_texture((size, size), base_color)
    draw = ImageDraw.Draw(img)

    # Grid lines
    grid_step = size // 8
    for i in range(0, size, grid_step):
        # Horizontal lines (fainter)
        draw.line([(0, i), (size, i)], fill=line_color, width=1)
        # Vertical lines (brighter - lane markers)
        if i == size // 4 or i == 3 * size // 4:
            draw.line([(i, 0), (i, size)], fill=line_color, width=2)

    # Center line (dashed)
    center = size // 2
    dash_len = size // 16
    for y in range(0, size, dash_len * 2):
        draw.rectangle([center - 1, y, center + 1, y + dash_len], fill=line_color)

    img.save(path)
    print(f"  Generated: {path.name}")


def generate_barrier_texture(path: Path, base: tuple, stripe: tuple, size: int = 64):
    """Generate a barrier texture with hazard stripes."""
    img = create_texture((size, size), base)
    draw = ImageDraw.Draw(img)

    # Diagonal stripes
    stripe_width = size // 4
    for i in range(-size, size * 2, stripe_width * 2):
        draw.polygon([
            (i, 0),
            (i + stripe_width, 0),
            (i + stripe_width + size, size),
            (i + size, size)
        ], fill=stripe)

    # Neon edge highlight
    draw.rectangle([0, 0, size - 1, 2], fill=stripe)
    draw.rectangle([0, size - 3, size - 1, size - 1], fill=stripe)

    img.save(path)
    print(f"  Generated: {path.name}")


def generate_boost_pad_texture(path: Path, size: int = 64):
    """Generate a glowing boost pad texture."""
    img = create_texture((size, size), (20, 10, 30))
    draw = ImageDraw.Draw(img)

    # Glowing yellow/gold center
    center = size // 2
    for r in range(size // 2, 0, -4):
        intensity = int(255 * (1 - r / (size // 2)))
        color = (255, min(255, intensity + 150), 0)
        draw.ellipse([center - r, center - r, center + r, center + r], fill=color)

    # Arrow chevrons
    for y_offset in range(-size // 4, size // 3, size // 6):
        y = center + y_offset
        draw.polygon([
            (center - size // 3, y),
            (center, y - size // 6),
            (center + size // 3, y),
            (center, y + size // 6)
        ], fill=(255, 220, 0))

    img.save(path)
    print(f"  Generated: {path.name}")


def generate_building_texture(path: Path, size: int = 128):
    """Generate a building facade with windows."""
    img = create_texture((size, size), (30, 20, 50))  # Dark purple base
    draw = ImageDraw.Draw(img)

    # Window grid
    window_size = size // 8
    margin = window_size // 2
    colors = [(0, 255, 255), (255, 0, 255), (255, 200, 0), (100, 100, 120)]

    for row in range(4):
        for col in range(4):
            x = margin + col * (window_size + margin)
            y = margin + row * (window_size + margin)
            # Random-ish window colors (deterministic by position)
            color = colors[(row + col * 3) % len(colors)]
            draw.rectangle([x, y, x + window_size, y + window_size], fill=color)

    img.save(path)
    print(f"  Generated: {path.name}")


def generate_billboard_texture(path: Path, size: int = 128):
    """Generate a neon billboard texture."""
    img = create_texture((size, size), (10, 5, 20))
    draw = ImageDraw.Draw(img)

    # Neon border
    draw.rectangle([2, 2, size - 3, size - 3], outline=(255, 0, 255), width=3)

    # "NEON" text (simplified as rectangles)
    text_y = size // 3
    text_h = size // 3
    letter_w = size // 6
    margin = size // 8

    # N
    x = margin
    draw.rectangle([x, text_y, x + 4, text_y + text_h], fill=(0, 255, 255))
    draw.rectangle([x + letter_w - 4, text_y, x + letter_w, text_y + text_h], fill=(0, 255, 255))
    draw.polygon([(x + 4, text_y), (x + letter_w - 4, text_y + text_h - 4),
                  (x + letter_w - 4, text_y + text_h), (x + 4, text_y + 4)], fill=(0, 255, 255))

    # E
    x = margin + letter_w + 4
    draw.rectangle([x, text_y, x + 4, text_y + text_h], fill=(255, 0, 255))
    draw.rectangle([x, text_y, x + letter_w, text_y + 4], fill=(255, 0, 255))
    draw.rectangle([x, text_y + text_h // 2 - 2, x + letter_w - 4, text_y + text_h // 2 + 2], fill=(255, 0, 255))
    draw.rectangle([x, text_y + text_h - 4, x + letter_w, text_y + text_h], fill=(255, 0, 255))

    # O
    x = margin + (letter_w + 4) * 2
    draw.ellipse([x, text_y, x + letter_w, text_y + text_h], outline=(0, 255, 255), width=4)

    # N
    x = margin + (letter_w + 4) * 3
    draw.rectangle([x, text_y, x + 4, text_y + text_h], fill=(255, 0, 255))
    draw.rectangle([x + letter_w - 4, text_y, x + letter_w, text_y + text_h], fill=(255, 0, 255))

    img.save(path)
    print(f"  Generated: {path.name}")


def generate_crystal_texture(path: Path, size: int = 64):
    """Generate a glowing crystal texture."""
    img = create_texture((size, size), (20, 10, 40))
    draw = ImageDraw.Draw(img)

    # Gradient from dark to bright cyan
    for y in range(size):
        intensity = int(255 * (1 - y / size))
        color = (intensity // 2, intensity, intensity)
        draw.line([(0, y), (size, y)], fill=color)

    # Facet highlights
    draw.polygon([(0, 0), (size // 2, size // 3), (size, 0)], fill=(200, 255, 255))
    draw.line([(size // 2, 0), (size // 2, size)], fill=(255, 255, 255), width=2)

    img.save(path)
    print(f"  Generated: {path.name}")


def generate_emissive_texture(path: Path, color: tuple, size: int = 64):
    """Generate a solid emissive texture."""
    img = create_texture((size, size), color)
    img.save(path)
    print(f"  Generated: {path.name}")


def main():
    if not HAS_PIL:
        return

    base_dir = Path(__file__).parent.parent
    textures_dir = base_dir / "assets" / "models" / "textures"
    textures_dir.mkdir(parents=True, exist_ok=True)

    print("Generating track and prop textures...")

    # Track textures (dark base with neon lines)
    generate_track_texture(textures_dir / "track_curve_left.png", (30, 20, 40), (0, 255, 255))
    generate_track_texture(textures_dir / "track_curve_right.png", (30, 20, 40), (255, 0, 255))
    generate_track_texture(textures_dir / "track_tunnel.png", (20, 15, 35), (100, 100, 200))
    generate_track_texture(textures_dir / "track_jump.png", (40, 30, 20), (255, 150, 0))

    # Prop textures
    generate_barrier_texture(textures_dir / "prop_barrier.png", (50, 30, 60), (255, 0, 255))
    generate_boost_pad_texture(textures_dir / "prop_boost_pad.png")
    generate_building_texture(textures_dir / "prop_building.png")
    generate_billboard_texture(textures_dir / "prop_billboard.png")
    generate_crystal_texture(textures_dir / "crystal_formation.png")

    # Emissive textures (solid glow colors)
    generate_emissive_texture(textures_dir / "prop_barrier_emissive.png", (255, 0, 255))
    generate_emissive_texture(textures_dir / "prop_boost_pad_emissive.png", (255, 200, 0))
    generate_emissive_texture(textures_dir / "prop_billboard_emissive.png", (0, 255, 255))
    generate_emissive_texture(textures_dir / "crystal_formation_emissive.png", (0, 255, 200))

    print("\nDone! Generated 13 texture files.")


if __name__ == "__main__":
    main()
