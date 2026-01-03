"""
Track Texture Generator
Creates textures for NEON DRIFT track segments and props
"""

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


class TrackTextures:
    """Handles track and prop texture generation"""

    @staticmethod
    def generate_road_texture(texture_type='straight', width=256, height=256):
        """Generate road surface texture"""
        # Base asphalt
        img = Image.new('RGB', (width, height), color=(40, 45, 50))
        pixels = np.array(img)

        # Add noise
        noise = np.random.normal(0, 8, (height, width, 3))
        pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(pixels)

        # Boost contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)

        draw = ImageDraw.Draw(img)

        # Add road markings based on type
        if texture_type == 'straight':
            # Centerline dashes
            dash_length = int(height * 0.15)
            gap_length = int(height * 0.08)
            y = 0
            while y < height:
                draw.rectangle([width//2 - 2, y, width//2 + 2, y + dash_length],
                              fill=(220, 220, 180))
                y += dash_length + gap_length

        elif texture_type == 'checkpoint':
            # Finish line checkered
            checker_size = height // 16
            finish_y = int(height * 0.8)

            for x_i in range(16):
                for y_i in range(2):
                    if (x_i + y_i) % 2 == 0:
                        x = x_i * checker_size
                        y = finish_y + y_i * checker_size
                        draw.rectangle([x, y, x + checker_size, y + checker_size],
                                      fill=(240, 240, 240))

        return img

    @staticmethod
    def generate_tunnel_texture(width=256, height=256):
        """Generate tunnel texture"""
        img = Image.new('RGB', (width, height), color=(30, 35, 45))

        draw = ImageDraw.Draw(img)

        # Panel lines
        for i in range(0, height, 32):
            draw.line([(0, i), (width, i)], fill=(50, 60, 70), width=2)

        for i in range(0, width, 32):
            draw.line([(i, 0), (i, height)], fill=(50, 60, 70), width=2)

        return img

    @staticmethod
    def generate_prop_texture(prop_type, width=256, height=256):
        """Generate prop texture"""
        if prop_type == 'barrier':
            img = Image.new('RGB', (width, height), color=(80, 85, 90))
            draw = ImageDraw.Draw(img)

            # Reflective strip
            strip_y = height // 2 - 20
            draw.rectangle([0, strip_y, width, strip_y + 40], fill=(200, 180, 50))

        elif prop_type == 'boost_pad':
            img = Image.new('RGB', (width, height))
            pixels = np.array(img)

            for y in range(height):
                intensity = int(100 + (y / height) * 155)
                pixels[y, :] = [intensity, intensity // 2, 255]

            img = Image.fromarray(pixels)

        elif prop_type == 'billboard':
            img = Image.new('RGB', (width, height), color=(100, 150, 255))
            draw = ImageDraw.Draw(img)

            # Scanlines
            for y in range(0, height, 4):
                draw.line([(0, y), (width, y)], fill=(80, 120, 200))

        elif prop_type == 'building':
            img = Image.new('RGB', (width, height), color=(60, 65, 70))
            draw = ImageDraw.Draw(img)

            # Window grid
            window_size = 20
            window_spacing = 30

            for x in range(20, width - 20, window_spacing):
                for y in range(20, height - 20, window_spacing):
                    # Random lit/unlit windows
                    if np.random.random() > 0.3:
                        color = (150, 180, 200)  # Lit
                    else:
                        color = (20, 25, 30)  # Dark

                    draw.rectangle([x, y, x + window_size, y + window_size], fill=color)

        elif prop_type == 'crystal':
            img = Image.new('RGB', (width, height), color=(80, 50, 120))

            # Add glow variation
            pixels = np.array(img)
            for y in range(height):
                for x in range(width):
                    dist_from_center = abs(x - width/2) + abs(y - height/2)
                    glow = max(0, 100 - int(dist_from_center * 0.5))
                    pixels[y, x] = pixels[y, x] + glow

            img = Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8))

        else:
            img = Image.new('RGB', (width, height), color=(128, 128, 128))

        # Add noise
        pixels = np.array(img)
        noise = np.random.normal(0, 5, (height, width, 3))
        pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(pixels)

        return img
