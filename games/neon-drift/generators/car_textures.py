"""
Car Texture Generator
Creates albedo and emissive textures for NEON DRIFT vehicles
"""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


class CarTextures:
    """Handles car texture generation"""

    @staticmethod
    def hex_to_rgb(hex_color):
        """Convert hex color to RGB tuple (0-255 range)"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def generate_base_texture(body_color_hex, width=256, height=256):
        """Generate enhanced body texture with proper detail"""
        body_color = CarTextures.hex_to_rgb(body_color_hex)

        img = Image.new('RGB', (width, height), color=body_color)

        # Add noise for surface variation
        noise = np.random.normal(0, 8, (height, width, 3))
        img_array = np.array(img, dtype=float)
        img_array += noise
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        img = Image.fromarray(img_array)

        # Add panel lines (subtle darker lines)
        draw = ImageDraw.Draw(img)
        panel_color = tuple(int(c * 0.78) for c in body_color)  # 78% of base

        # Horizontal panel lines
        for y in [height // 4, height // 2, 3 * height // 4]:
            draw.line([(0, y), (width, y)], fill=panel_color, width=2)

        # Vertical panel lines
        for x in [width // 3, 2 * width // 3]:
            draw.line([(x, 0), (x, height)], fill=panel_color, width=2)

        # Add metallic flake (tiny bright pixels)
        flake_count = width * height // 50
        for _ in range(flake_count):
            x = np.random.randint(0, width)
            y = np.random.randint(0, height)
            brightness = np.random.randint(200, 255)
            img.putpixel((x, y), (brightness, brightness, brightness))

        # Slight blur to soften
        img = img.filter(ImageFilter.GaussianBlur(0.5))

        # Boost contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)

        return img

    @staticmethod
    def generate_emissive_map(car_name, emissive_color_hex, width=256, height=256):
        """Generate enhanced emissive map with proper neon patterns"""
        # Start black
        img = Image.new('RGB', (width, height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        emissive_rgb = CarTextures.hex_to_rgb(emissive_color_hex)

        # Side accent strips (horizontal lines at edges)
        strip_y_positions = [height // 6, 5 * height // 6]
        for y in strip_y_positions:
            for dy in range(-3, 4):
                draw.line([(0, y + dy), (width, y + dy)], fill=emissive_rgb, width=1)

        # Front strip (top edge)
        for y in range(5):
            draw.line([(width // 6, y), (5 * width // 6, y)], fill=emissive_rgb, width=1)

        # Rear strip (bottom edge)
        for y in range(height - 8, height):
            draw.line([(width // 6, y), (5 * width // 6, y)], fill=emissive_rgb, width=1)

        # Underglow pattern (for drift/phantom)
        if car_name in ['drift', 'phantom']:
            underglow_y = height // 2
            for x in range(0, width, 4):
                intensity = int(255 * (0.5 + 0.5 * math.sin(x * 0.1)))
                color = tuple(int(c * intensity / 255) for c in emissive_rgb)
                draw.rectangle([(x, underglow_y - 2), (x + 2, underglow_y + 2)], fill=color)

        # Add glow effect
        img = img.filter(ImageFilter.GaussianBlur(3))

        # Boost intensity
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.5)

        return img
