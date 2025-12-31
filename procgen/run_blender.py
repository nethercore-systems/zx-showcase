#!/usr/bin/env python3
"""
ZX Showcase - Blender Asset Generation Runner

Usage:
    blender --background --python run_blender.py -- --game prism-survivors --all
    blender --background --python run_blender.py -- --game prism-survivors --asset hero_knight
    blender --background --python run_blender.py -- --game prism-survivors --heroes
    blender --background --python run_blender.py -- --game prism-survivors --enemies
    blender --background --python run_blender.py -- --game prism-survivors --pickups
    blender --background --python run_blender.py -- --game prism-survivors --textures
    blender --background --python run_blender.py -- --game prism-survivors --audio

Note: Arguments after '--' are passed to the script.
"""

import argparse
import sys
from pathlib import Path

# Add procgen to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR.parent))

# Import Blender modules
try:
    import bpy
    from procgen.core.blender_export import (
        MeshData, TextureData, clear_scene,
        export_mesh_glb, export_texture_png,
        create_material_with_texture,
    )
except ImportError as e:
    print(f"Error: Must run from Blender. Use:")
    print(f"  blender --background --python {__file__} -- --game prism-survivors --all")
    sys.exit(1)

from procgen.core import UniversalStyleParams
from procgen.configs import get_style_tokens
from procgen.meshes import generate_humanoid, generate_crystal, MeshData as PrimitiveMeshData
from procgen.meshes.humanoid import generate_enemy
from procgen.meshes.crystals import generate_xp_gem, generate_projectile
from procgen.meshes.environment import generate_health_pickup, generate_powerup
from procgen.textures import generate_albedo, generate_emission, generate_roughness
from procgen.textures.glow_effects import generate_prismatic_glow
from procgen.textures.noise_patterns import TextureData as NoiseTextureData


def get_output_dir(game_name: str) -> Path:
    """Get output directory for game assets."""
    showcase_root = SCRIPT_DIR.parent
    # Output to assets/models/ to match nether.toml paths
    game_dir = game_name.replace("-", "-")
    output_dir = showcase_root / "games" / game_dir / "assets" / "models"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def convert_mesh_data(mesh: PrimitiveMeshData) -> MeshData:
    """Convert primitives MeshData to blender_export MeshData."""
    return MeshData(
        vertices=mesh.vertices,
        faces=mesh.faces,
        normals=mesh.normals,
        uvs=mesh.uvs,
    )


def convert_texture_data(tex: NoiseTextureData) -> TextureData:
    """Convert noise TextureData to blender_export TextureData."""
    return TextureData(
        pixels=tex.pixels,
        width=tex.width,
        height=tex.height,
    )


def generate_prism_survivors_heroes(style: UniversalStyleParams, output_dir: Path):
    """Generate all hero meshes and textures for Prism Survivors."""
    from procgen.configs.prism_survivors import HERO_PRESETS

    print("\n=== Generating Heroes ===")

    meshes_dir = output_dir / "meshes"
    textures_dir = output_dir / "textures"
    meshes_dir.mkdir(parents=True, exist_ok=True)
    textures_dir.mkdir(parents=True, exist_ok=True)

    for hero_name, preset in HERO_PRESETS.items():
        print(f"\n--- {hero_name.title()} ---")

        # Generate mesh
        mesh = generate_humanoid(style, preset=preset, size_class="medium")
        mesh_data = convert_mesh_data(mesh)
        mesh_data.name = hero_name

        # Generate textures
        color = preset.get("color_primary", [0.5, 0.5, 0.5])
        rgb = tuple(int(c * 255) for c in color)

        albedo = generate_albedo(style, base_color=rgb, pattern="noisy", width=256, height=256)
        albedo_data = convert_texture_data(albedo)
        albedo_data.name = f"{hero_name}_albedo"

        accent = preset.get("color_accent", [1.0, 1.0, 1.0])
        accent_rgb = tuple(int(c * 255) for c in accent)
        emission = generate_emission(style, emission_color=accent_rgb, pattern="outline", width=256, height=256)
        emission_data = convert_texture_data(emission)
        emission_data.name = f"{hero_name}_emission"

        # Export textures first
        albedo_path = textures_dir / f"{hero_name}.png"
        emission_path = textures_dir / f"{hero_name}_emission.png"
        export_texture_png(albedo_data, albedo_path)
        export_texture_png(emission_data, emission_path)

        # Export mesh with material (create material inside export to avoid scene clearing issues)
        mesh_path = meshes_dir / f"{hero_name}.glb"
        export_mesh_glb(
            mesh_data, mesh_path,
            albedo_path=albedo_path,
            emission_path=emission_path,
            roughness=0.3,
            emission_strength=1.0,
        )

    print(f"\nHeroes exported to: {output_dir}")


def generate_prism_survivors_enemies(style: UniversalStyleParams, output_dir: Path):
    """Generate all enemy meshes and textures for Prism Survivors."""
    from procgen.configs.prism_survivors import ENEMY_PRESETS

    # Add missing enemies from GDD
    ALL_ENEMY_PRESETS = {
        **ENEMY_PRESETS,
        # Add missing basic enemies
        "shade": {
            "tier": "basic",
            "scale": 0.7,
            "hp": 20,
            "xp": 2,
            "vertices": 5,
            "symmetry": 2,
            "color_base": [0.1, 0.05, 0.15],
            "color_glow": [0.3, 0.2, 0.4],
        },
        "berserker": {
            "tier": "basic",
            "scale": 1.0,
            "hp": 40,
            "xp": 4,
            "vertices": 6,
            "symmetry": 2,
            "color_base": [0.5, 0.15, 0.1],
            "color_glow": [0.9, 0.3, 0.2],
        },
        "arcane_sentinel": {
            "tier": "basic",
            "scale": 0.9,
            "hp": 35,
            "xp": 3,
            "vertices": 8,
            "symmetry": 4,
            "color_base": [0.2, 0.3, 0.5],
            "color_glow": [0.4, 0.6, 1.0],
        },
        # Add missing elite enemies
        "golem_titan": {
            "tier": "elite",
            "scale": 1.6,
            "hp": 250,
            "xp": 20,
            "vertices": 8,
            "symmetry": 2,
            "color_base": [0.35, 0.3, 0.25],
            "color_glow": [0.6, 0.5, 0.4],
        },
        "specter_lord": {
            "tier": "elite",
            "scale": 1.2,
            "hp": 120,
            "xp": 15,
            "vertices": 6,
            "symmetry": 3,
            "color_base": [0.15, 0.15, 0.2],
            "color_glow": [0.5, 0.5, 0.8],
        },
    }

    print("\n=== Generating Enemies ===")

    meshes_dir = output_dir / "meshes"
    textures_dir = output_dir / "textures"
    meshes_dir.mkdir(parents=True, exist_ok=True)
    textures_dir.mkdir(parents=True, exist_ok=True)

    for enemy_name, preset in ALL_ENEMY_PRESETS.items():
        print(f"\n--- {enemy_name.replace('_', ' ').title()} ({preset['tier']}) ---")

        tier = preset.get("tier", "basic")

        # Generate mesh
        mesh = generate_enemy(style, preset=preset, tier=tier)
        mesh_data = convert_mesh_data(mesh)
        mesh_data.name = enemy_name

        # Generate textures based on tier
        base_color = preset.get("color_base", [0.3, 0.3, 0.3])
        base_rgb = tuple(int(c * 255) for c in base_color)

        glow_color = preset.get("color_glow", [0.5, 0.5, 0.5])
        glow_rgb = tuple(int(c * 255) for c in glow_color)

        # Texture size based on tier
        tex_size = 128 if tier == "basic" else (256 if tier == "elite" else 512)

        albedo = generate_albedo(style, base_color=base_rgb, pattern="noisy", width=tex_size, height=tex_size)
        albedo_data = convert_texture_data(albedo)

        # Emission pattern based on tier
        emission_pattern = "spots" if tier == "basic" else ("outline" if tier == "elite" else "glow")
        emission_strength = 0.5 if tier == "basic" else (1.0 if tier == "elite" else 2.0)

        emission = generate_emission(
            style,
            emission_color=glow_rgb,
            pattern=emission_pattern,
            strength=emission_strength,
            width=tex_size,
            height=tex_size,
        )
        emission_data = convert_texture_data(emission)

        # Export textures
        albedo_path = textures_dir / f"{enemy_name}.png"
        emission_path = textures_dir / f"{enemy_name}_emission.png"
        export_texture_png(albedo_data, albedo_path)
        export_texture_png(emission_data, emission_path)

        # Export mesh with material
        mesh_path = meshes_dir / f"{enemy_name}.glb"
        export_mesh_glb(
            mesh_data, mesh_path,
            albedo_path=albedo_path,
            emission_path=emission_path,
            roughness=0.4,
            emission_strength=emission_strength,
        )

    print(f"\nEnemies exported to: {output_dir}")


def generate_prism_survivors_pickups(style: UniversalStyleParams, output_dir: Path):
    """Generate pickups and projectiles for Prism Survivors."""
    print("\n=== Generating Pickups & Projectiles ===")

    meshes_dir = output_dir / "meshes"
    textures_dir = output_dir / "textures"
    meshes_dir.mkdir(parents=True, exist_ok=True)
    textures_dir.mkdir(parents=True, exist_ok=True)

    # XP Gem
    print("\n--- XP Gem ---")
    xp_mesh = generate_xp_gem(size=0.2)
    xp_data = convert_mesh_data(xp_mesh)
    xp_data.name = "xp_gem"

    xp_albedo = generate_albedo(style, base_color=(64, 255, 64), pattern="solid", width=64, height=64)
    xp_emission = generate_emission(style, emission_color=(128, 255, 128), pattern="glow", width=64, height=64)

    xp_albedo_path = textures_dir / "xp_gem.png"
    xp_emission_path = textures_dir / "xp_gem_emission.png"
    export_texture_png(convert_texture_data(xp_albedo), xp_albedo_path)
    export_texture_png(convert_texture_data(xp_emission), xp_emission_path)

    export_mesh_glb(
        xp_data, meshes_dir / "xp_gem.glb",
        albedo_path=xp_albedo_path,
        emission_path=xp_emission_path,
        emission_strength=2.0,
    )

    # Coin
    print("\n--- Coin ---")
    from procgen.meshes.primitives import create_cylinder
    coin_prim = create_cylinder(radius=0.15, height=0.05, segments=12)
    coin_data = convert_mesh_data(coin_prim)
    coin_data.name = "coin"

    coin_albedo = generate_albedo(style, base_color=(255, 200, 50), pattern="metallic", width=64, height=64)
    coin_albedo_path = textures_dir / "coin.png"
    export_texture_png(convert_texture_data(coin_albedo), coin_albedo_path)

    export_mesh_glb(
        coin_data, meshes_dir / "coin.glb",
        albedo_path=coin_albedo_path,
        roughness=0.2,
    )

    # Powerup Orb
    print("\n--- Powerup Orb ---")
    from procgen.meshes.primitives import create_sphere
    orb_prim = create_sphere(radius=0.15, segments=8, rings=6)
    orb_data = convert_mesh_data(orb_prim)
    orb_data.name = "powerup_orb"

    orb_albedo = generate_albedo(style, base_color=(200, 100, 255), pattern="solid", width=64, height=64)
    orb_emission = generate_emission(style, emission_color=(220, 150, 255), pattern="glow", width=64, height=64)

    orb_albedo_path = textures_dir / "powerup_orb.png"
    orb_emission_path = textures_dir / "powerup_orb_emission.png"
    export_texture_png(convert_texture_data(orb_albedo), orb_albedo_path)
    export_texture_png(convert_texture_data(orb_emission), orb_emission_path)

    export_mesh_glb(
        orb_data, meshes_dir / "powerup_orb.glb",
        albedo_path=orb_albedo_path,
        emission_path=orb_emission_path,
        emission_strength=1.5,
    )

    # Projectiles
    projectile_configs = [
        ("frost_shard", "shard", (100, 200, 255), (150, 220, 255)),
        ("void_orb", "orb", (80, 40, 120), (150, 80, 200)),
        ("lightning_bolt", "beam", (255, 255, 100), (255, 255, 200)),
    ]

    for proj_name, proj_type, base_rgb, glow_rgb in projectile_configs:
        print(f"\n--- {proj_name.replace('_', ' ').title()} ---")

        proj_mesh = generate_projectile(projectile_type=proj_type, size=0.15)
        proj_data = convert_mesh_data(proj_mesh)
        proj_data.name = proj_name

        proj_albedo = generate_albedo(style, base_color=base_rgb, pattern="solid", width=32, height=32)
        proj_emission = generate_emission(style, emission_color=glow_rgb, pattern="glow", width=32, height=32)

        proj_albedo_path = textures_dir / f"{proj_name}.png"
        proj_emission_path = textures_dir / f"{proj_name}_emission.png"
        export_texture_png(convert_texture_data(proj_albedo), proj_albedo_path)
        export_texture_png(convert_texture_data(proj_emission), proj_emission_path)

        export_mesh_glb(
            proj_data, meshes_dir / f"{proj_name}.glb",
            albedo_path=proj_albedo_path,
            emission_path=proj_emission_path,
            emission_strength=2.0,
        )

    print(f"\nPickups exported to: {output_dir}")


def generate_prism_survivors_arena(style: UniversalStyleParams, output_dir: Path):
    """Generate arena floor mesh and stage textures."""
    from procgen.configs.prism_survivors import STAGE_PRESETS

    print("\n=== Generating Arena & Stage Textures ===")

    meshes_dir = output_dir / "meshes"
    textures_dir = output_dir / "textures"
    meshes_dir.mkdir(parents=True, exist_ok=True)
    textures_dir.mkdir(parents=True, exist_ok=True)

    # Arena floor mesh (simple quad)
    print("\n--- Arena Floor Mesh ---")
    from procgen.meshes.primitives import create_box
    arena_prim = create_box(width=20.0, depth=20.0, height=0.1, center=(0, 0, -0.05))
    arena_data = convert_mesh_data(arena_prim)
    arena_data.name = "arena_floor"

    # Generate default arena texture
    arena_albedo = generate_albedo(style, base_color=(30, 30, 50), pattern="noisy", width=256, height=256)
    arena_albedo_path = textures_dir / "arena_floor.png"
    export_texture_png(convert_texture_data(arena_albedo), arena_albedo_path)

    export_mesh_glb(
        arena_data, meshes_dir / "arena_floor.glb",
        albedo_path=arena_albedo_path,
        roughness=0.7,
    )

    # Stage-specific floor textures
    for stage_name, preset in STAGE_PRESETS.items():
        print(f"\n--- {stage_name.replace('_', ' ').title()} Floor ---")

        # Parse floor color
        floor_hex = preset.get("floor_color", "#1A1A2A")
        floor_rgb = tuple(int(floor_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

        # Generate stage floor texture with pattern
        floor_tex = generate_albedo(style, base_color=floor_rgb, pattern="noisy", width=256, height=256, seed=hash(stage_name) % 10000)
        floor_path = textures_dir / f"{stage_name}_floor.png"
        export_texture_png(convert_texture_data(floor_tex), floor_path)

        # Generate hazard glow texture
        hazard_hex = preset.get("hazard_color", "#FF0000")
        hazard_rgb = tuple(int(hazard_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

        hazard_tex = generate_emission(style, emission_color=hazard_rgb, pattern="spots", width=128, height=128, seed=hash(stage_name) % 10000)
        hazard_path = textures_dir / f"{stage_name}_hazard.png"
        export_texture_png(convert_texture_data(hazard_tex), hazard_path)

    print(f"\nArena exported to: {output_dir}")


def generate_prism_survivors_font(output_dir: Path):
    """Generate a simple bitmap font texture."""
    print("\n=== Generating Font Texture ===")

    textures_dir = output_dir / "textures"
    textures_dir.mkdir(parents=True, exist_ok=True)

    # Create a simple 8x12 pixel font atlas (96 characters, 16x6 grid)
    # Characters 32-127 (space to DEL)
    char_width = 8
    char_height = 12
    chars_per_row = 16
    num_rows = 6
    tex_width = char_width * chars_per_row  # 128
    tex_height = char_height * num_rows  # 72

    # Simple pixel font data (very basic, just for testing)
    # Real implementation would load a proper bitmap font
    pixels = [[(0, 0, 0, 0) for _ in range(tex_width)] for _ in range(tex_height)]

    # Draw simple placeholder characters
    for char_idx in range(96):
        char_x = (char_idx % chars_per_row) * char_width
        char_y = (char_idx // chars_per_row) * char_height

        # Draw a simple box for each character position
        for y in range(char_height):
            for x in range(char_width):
                px = char_x + x
                py = char_y + y

                # Border
                if x == 0 or x == char_width - 1 or y == 0 or y == char_height - 1:
                    pixels[py][px] = (255, 255, 255, 255)
                # Fill
                elif (x + y) % 2 == 0:
                    pixels[py][px] = (200, 200, 200, 255)

    font_data = TextureData(pixels=pixels, width=tex_width, height=tex_height, name="prism_font")
    font_path = textures_dir / "prism_font.png"
    export_texture_png(font_data, font_path)

    print(f"Font texture exported to: {font_path}")
    print("NOTE: Replace with proper bitmap font for production!")


def generate_prism_survivors_audio(output_dir: Path):
    """Generate SFX using scipy/numpy synthesis."""
    print("\n=== Generating Audio (SFX) ===")

    audio_dir = output_dir.parent / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    # Check if we have scipy/numpy
    try:
        import numpy as np
        from scipy.io import wavfile
        HAS_AUDIO_DEPS = True
    except ImportError:
        print("WARNING: scipy/numpy not available in Blender Python.")
        print("Run the standalone audio generator instead:")
        print("  python procgen/audio/generate_sfx.py --game prism-survivors")
        HAS_AUDIO_DEPS = False
        return

    sample_rate = 22050

    def generate_sine_wave(freq: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
        """Generate a sine wave."""
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = amplitude * np.sin(2 * np.pi * freq * t)
        return wave

    def generate_noise(duration: float, amplitude: float = 0.3) -> np.ndarray:
        """Generate white noise."""
        samples = int(sample_rate * duration)
        return amplitude * (np.random.random(samples) * 2 - 1)

    def apply_envelope(wave: np.ndarray, attack: float, decay: float, sustain: float, release: float) -> np.ndarray:
        """Apply ADSR envelope."""
        total_samples = len(wave)
        attack_samples = int(attack * sample_rate)
        decay_samples = int(decay * sample_rate)
        release_samples = int(release * sample_rate)
        sustain_samples = max(0, total_samples - attack_samples - decay_samples - release_samples)

        envelope = np.zeros(total_samples)

        # Attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        # Decay
        decay_start = attack_samples
        decay_end = decay_start + decay_samples
        if decay_samples > 0:
            envelope[decay_start:decay_end] = np.linspace(1, sustain, decay_samples)

        # Sustain
        sustain_start = decay_end
        sustain_end = sustain_start + sustain_samples
        envelope[sustain_start:sustain_end] = sustain

        # Release
        release_start = sustain_end
        if release_samples > 0 and release_start < total_samples:
            envelope[release_start:] = np.linspace(sustain, 0, total_samples - release_start)

        return wave * envelope

    def save_wav(filename: str, wave: np.ndarray):
        """Save wave to WAV file."""
        # Normalize and convert to 16-bit
        wave = wave / np.max(np.abs(wave)) if np.max(np.abs(wave)) > 0 else wave
        wave_int = (wave * 32767).astype(np.int16)
        wavfile.write(audio_dir / filename, sample_rate, wave_int)
        print(f"  {filename}")

    # Generate SFX
    print("Generating SFX...")

    # Shoot - quick blip
    shoot = generate_sine_wave(880, 0.1) + generate_sine_wave(1320, 0.08) * 0.5
    shoot = apply_envelope(shoot[:int(sample_rate * 0.1)], 0.01, 0.02, 0.3, 0.05)
    save_wav("shoot.wav", shoot)

    # Hit - impact thud
    hit = generate_noise(0.1) * 0.5 + generate_sine_wave(200, 0.1)
    hit = apply_envelope(hit, 0.005, 0.03, 0.2, 0.05)
    save_wav("hit.wav", hit)

    # Death - glass shatter
    death_base = generate_noise(0.3) * 0.4
    death_tone = generate_sine_wave(440, 0.3) * 0.3 + generate_sine_wave(660, 0.25) * 0.2
    death = death_base + death_tone
    death = apply_envelope(death, 0.01, 0.1, 0.3, 0.15)
    save_wav("death.wav", death)

    # XP pickup - bright chime
    xp = generate_sine_wave(1200, 0.15) + generate_sine_wave(1800, 0.12) * 0.6
    xp = apply_envelope(xp[:int(sample_rate * 0.15)], 0.01, 0.02, 0.5, 0.1)
    save_wav("xp.wav", xp)

    # Level up - triumphant chord
    levelup = (
        generate_sine_wave(440, 0.8) * 0.3 +
        generate_sine_wave(554, 0.7) * 0.25 +
        generate_sine_wave(659, 0.6) * 0.2 +
        generate_sine_wave(880, 0.5) * 0.15
    )
    levelup = apply_envelope(levelup, 0.05, 0.15, 0.6, 0.3)
    save_wav("level_up.wav", levelup)

    # Hurt - pain grunt
    hurt = generate_noise(0.15) * 0.3 + generate_sine_wave(300, 0.15) * 0.4
    hurt = apply_envelope(hurt, 0.01, 0.05, 0.3, 0.08)
    save_wav("hurt.wav", hurt)

    # Select - UI click
    select = generate_sine_wave(600, 0.08) + generate_sine_wave(800, 0.06) * 0.5
    select = apply_envelope(select[:int(sample_rate * 0.08)], 0.005, 0.02, 0.4, 0.03)
    save_wav("select.wav", select)

    # Menu - soft tone
    menu = generate_sine_wave(500, 0.12)
    menu = apply_envelope(menu, 0.01, 0.03, 0.4, 0.06)
    save_wav("menu.wav", menu)

    # Back - descending tone
    back = generate_sine_wave(600, 0.1) + generate_sine_wave(400, 0.1) * 0.7
    back = apply_envelope(back, 0.01, 0.03, 0.3, 0.05)
    save_wav("back.wav", back)

    # Dash - whoosh
    dash = generate_noise(0.2) * 0.4
    dash = apply_envelope(dash, 0.02, 0.05, 0.2, 0.12)
    save_wav("dash.wav", dash)

    # Coin - metallic clink
    coin = generate_sine_wave(1500, 0.12) + generate_sine_wave(2000, 0.08) * 0.4
    coin = apply_envelope(coin[:int(sample_rate * 0.12)], 0.005, 0.02, 0.4, 0.08)
    save_wav("coin.wav", coin)

    # Powerup - ascending arpeggio
    powerup = np.zeros(int(sample_rate * 0.4))
    for i, freq in enumerate([400, 500, 600, 800]):
        start = int(i * sample_rate * 0.1)
        tone = generate_sine_wave(freq, 0.15) * 0.3
        tone = apply_envelope(tone, 0.01, 0.02, 0.5, 0.1)
        end = min(start + len(tone), len(powerup))
        powerup[start:end] += tone[:end - start]
    save_wav("powerup.wav", powerup)

    print(f"\nAudio exported to: {audio_dir}")


def generate_all_prism_survivors(style: UniversalStyleParams, output_dir: Path):
    """Generate all assets for Prism Survivors."""
    print("\n" + "=" * 60)
    print("  PRISM SURVIVORS - FULL ASSET GENERATION")
    print("=" * 60)

    generate_prism_survivors_heroes(style, output_dir)
    generate_prism_survivors_enemies(style, output_dir)
    generate_prism_survivors_pickups(style, output_dir)
    generate_prism_survivors_arena(style, output_dir)
    generate_prism_survivors_font(output_dir)
    generate_prism_survivors_audio(output_dir)

    print("\n" + "=" * 60)
    print(f"  ALL ASSETS EXPORTED TO: {output_dir}")
    print("=" * 60)


def generate_lumina_depths_creatures(output_dir: Path):
    """Generate all creature meshes for Lumina Depths using metaballs."""
    from procgen.games.lumina_depths.blender_creatures import generate_all_creatures

    print("\n" + "=" * 60)
    print("  LUMINA DEPTHS - CREATURE GENERATION (METABALLS)")
    print("=" * 60)

    meshes_dir = output_dir / "meshes"
    meshes_dir.mkdir(parents=True, exist_ok=True)

    count = generate_all_creatures(meshes_dir)

    print("\n" + "=" * 60)
    print(f"  Generated {count} creatures to: {meshes_dir}")
    print("=" * 60)


def generate_lumina_depths_asset(asset_name: str, output_dir: Path):
    """Generate a single Lumina Depths asset by name."""
    from procgen.games.lumina_depths.blender_creatures import CREATURE_GENERATORS

    meshes_dir = output_dir / "meshes"
    meshes_dir.mkdir(parents=True, exist_ok=True)

    if asset_name not in CREATURE_GENERATORS:
        print(f"Error: Unknown asset '{asset_name}'")
        print(f"Available assets: {', '.join(CREATURE_GENERATORS.keys())}")
        return

    generator = CREATURE_GENERATORS[asset_name]
    generator(meshes_dir)
    print(f"Generated: {asset_name}")


def generate_lumina_depths_zone(zone: str, output_dir: Path):
    """Generate all creatures for a specific zone."""
    from procgen.games.lumina_depths.blender_creatures import (
        generate_all_zone1, generate_all_zone2,
        generate_all_zone3, generate_all_zone4, generate_all_epic,
    )

    meshes_dir = output_dir / "meshes"
    meshes_dir.mkdir(parents=True, exist_ok=True)

    zone_map = {
        "zone1": generate_all_zone1,
        "zone2": generate_all_zone2,
        "zone3": generate_all_zone3,
        "zone4": generate_all_zone4,
        "epic": generate_all_epic,
    }

    if zone not in zone_map:
        print(f"Error: Unknown zone '{zone}'")
        print(f"Available zones: {', '.join(zone_map.keys())}")
        return

    count = zone_map[zone](meshes_dir)
    print(f"Generated {count} creatures for {zone}")


def generate_all_lumina_depths(output_dir: Path):
    """Generate all assets for Lumina Depths."""
    print("\n" + "=" * 60)
    print("  LUMINA DEPTHS - FULL ASSET GENERATION")
    print("=" * 60)

    generate_lumina_depths_creatures(output_dir)
    # TODO: Add flora, terrain, audio generation when implemented

    print("\n" + "=" * 60)
    print(f"  ALL ASSETS EXPORTED TO: {output_dir}")
    print("=" * 60)


def main():
    # Parse arguments after '--'
    argv = sys.argv
    if '--' in argv:
        argv = argv[argv.index('--') + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="ZX Showcase Blender Asset Generator")
    parser.add_argument("--game", required=True, choices=["neon-drift", "lumina-depths", "prism-survivors"],
                        help="Target game")
    parser.add_argument("--all", action="store_true", help="Generate all assets")
    parser.add_argument("--heroes", action="store_true", help="Generate hero assets only (prism-survivors)")
    parser.add_argument("--enemies", action="store_true", help="Generate enemy assets only (prism-survivors)")
    parser.add_argument("--pickups", action="store_true", help="Generate pickup/projectile assets (prism-survivors)")
    parser.add_argument("--arena", action="store_true", help="Generate arena and stage textures (prism-survivors)")
    parser.add_argument("--font", action="store_true", help="Generate font texture (prism-survivors)")
    parser.add_argument("--audio", action="store_true", help="Generate audio SFX")
    parser.add_argument("--creatures", action="store_true", help="Generate creature meshes (lumina-depths)")
    parser.add_argument("--zone", type=str, help="Generate specific zone (zone1, zone2, zone3, zone4, epic)")
    parser.add_argument("--asset", type=str, help="Generate specific asset by name")
    parser.add_argument("--output", type=str, help="Custom output directory")

    args = parser.parse_args(argv)

    # Get output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = get_output_dir(args.game)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Game: {args.game}")
    print(f"Output: {output_dir}")

    # Generate based on game and flags
    if args.game == "prism-survivors":
        # Get style tokens for prism-survivors
        style = get_style_tokens(args.game)
        if style is None:
            print(f"Error: No style tokens found for game '{args.game}'")
            sys.exit(1)
        print(f"Style: {style.style_name}")

        if args.all:
            generate_all_prism_survivors(style, output_dir)
        elif args.heroes:
            generate_prism_survivors_heroes(style, output_dir)
        elif args.enemies:
            generate_prism_survivors_enemies(style, output_dir)
        elif args.pickups:
            generate_prism_survivors_pickups(style, output_dir)
        elif args.arena:
            generate_prism_survivors_arena(style, output_dir)
        elif args.font:
            generate_prism_survivors_font(output_dir)
        elif args.audio:
            generate_prism_survivors_audio(output_dir)
        else:
            print("No generation flag specified. Use --all, --heroes, --enemies, etc.")
            parser.print_help()

    elif args.game == "lumina-depths":
        if args.all:
            generate_all_lumina_depths(output_dir)
        elif args.creatures:
            generate_lumina_depths_creatures(output_dir)
        elif args.zone:
            generate_lumina_depths_zone(args.zone, output_dir)
        elif args.asset:
            generate_lumina_depths_asset(args.asset, output_dir)
        else:
            print("No generation flag specified. Use --all, --creatures, --zone <zone>, or --asset <name>")
            parser.print_help()

    else:
        print(f"Game '{args.game}' not fully implemented yet in Blender pipeline.")


if __name__ == "__main__":
    main()
