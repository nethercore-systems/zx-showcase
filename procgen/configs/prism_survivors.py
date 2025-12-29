"""
Prism Survivors - Style Token Configuration

Aesthetic: Prismatic violence, crystalline chaos, geometric elegance
"""

from procgen.core.base_params import (
    UniversalStyleParams, ColorPalette, PolyBudget, GeometrySettings,
    TextureSettings, MaterialSettings, AnimationSettings, EffectSettings,
    AudioSettings, AudioEnvelope, Waveform, FilterType, SymmetryMode
)


STYLE_TOKENS = UniversalStyleParams(
    game_name="prism_survivors",
    style_name="crystalline_chaos",

    # Color Palette - Full prismatic spectrum
    palette=ColorPalette(
        primary=[
            "#E63946",  # Refracted Red
            "#FF9500",  # Orange Beam
            "#FFD700",  # Yellow Radiance
            "#00FF7F",  # Green Crystal
            "#00E5FF",  # Cyan Shard
            "#0066FF",  # Blue Depth
            "#9D00FF",  # Violet Edge
        ],
        accent=[
            "#FFFFFF",  # White Light (source)
            "#FFFACD",  # Prismatic Glow
            "#FF1744",  # Danger Red
            "#40FF40",  # XP Green
        ],
        neutral=[
            "#0A0A0F",  # Black Void
            "#1A0F2E",  # Deep Purple (background)
            "#2D1B3D",  # Shadow Purple (UI)
            "#8B9DC3",  # Gray Crystal
        ]
    ),
    saturation_range=(0.8, 1.0),  # Vibrant crystals
    value_range=(0.5, 1.0),
    color_temperature=0.0,  # Neutral (full spectrum)

    # Geometry - Faceted crystals, sharp angles
    poly_budget=PolyBudget(
        character_small=800,
        character_medium=1200,
        character_large=1500,
        enemy_small=200,
        enemy_medium=500,
        enemy_large=1000,
        enemy_boss=2000,
        prop_small=50,
        prop_medium=150,
        projectile=50,
    ),
    geometry=GeometrySettings(
        curvature_bias=0.2,  # Angular, faceted
        symmetry_mode=SymmetryMode.RADIAL_6,  # Hexagonal bias
        detail_scale=0.8,
        bevel_enabled=True,
        bevel_width=0.02,
    ),

    # Textures - Glossy crystal with iridescence
    textures=TextureSettings(
        resolution=256,
        roughness_range=(0.1, 0.3),  # Very glossy
        metallic_range=(0.0, 0.1),
        normal_strength=0.3,
        use_emission=True,
        emission_strength=(0.3, 1.5),
    ),

    # Materials - Crystalline with fresnel
    materials=MaterialSettings(
        base_roughness=0.2,
        base_metallic=0.0,
        emissive_enabled=True,
        emissive_strength=1.0,
        translucency_enabled=False,
        fresnel_intensity=0.8,  # Strong rim glow
    ),

    # Animation - Rigid rotation
    animation=AnimationSettings(
        idle_rotation_speed=0.5,  # Constant spin
        pulse_frequency=1.5,
        bob_amplitude=0.05,
        bob_frequency=2.0,
    ),

    # Effects - Heavy bloom, prismatic
    effects=EffectSettings(
        bloom_intensity=2.0,
        bloom_threshold=0.5,
        chromatic_aberration=0.02,  # Prismatic edge
        motion_blur=False,
        trail_enabled=True,
        trail_decay=0.15,
        particle_density="high",  # Crystal shards
    ),

    # Audio - Synthesized, harmonic
    audio=AudioSettings(
        primary_waveform=Waveform.SQUARE,
        secondary_waveform=Waveform.TRIANGLE,
        detune_cents=0.0,
        envelope=AudioEnvelope(
            attack_ms=10,
            decay_ms=50,
            sustain_level=0.0,
            release_ms=100,
        ),
        filter_type=FilterType.BAND_PASS,
        filter_cutoff=1500.0,
        filter_resonance=0.5,
        reverb_wet=0.15,
        reverb_decay=0.8,
    ),
)


# Hero class presets
HERO_PRESETS = {
    "knight": {
        "color_primary": [0.35, 0.45, 0.6],  # Steel blue
        "color_accent": [0.85, 0.7, 0.2],    # Gold
        "armored": True,
        "hp": 150,
        "speed": 3.5,
        "damage_mult": 1.0,
        "armor": 0.1,
    },
    "mage": {
        "color_primary": [0.35, 0.15, 0.55],
        "color_accent": [0.3, 0.8, 0.95],
        "armored": False,
        "hp": 80,
        "speed": 4.0,
        "damage_mult": 1.3,
        "armor": 0.0,
    },
    "ranger": {
        "color_primary": [0.2, 0.45, 0.25],
        "color_accent": [0.55, 0.4, 0.25],
        "armored": False,
        "hp": 100,
        "speed": 5.0,
        "damage_mult": 1.0,
        "armor": 0.0,
    },
    "cleric": {
        "color_primary": [0.95, 0.92, 0.85],
        "color_accent": [1.0, 0.8, 0.3],
        "armored": False,
        "hp": 120,
        "speed": 3.8,
        "damage_mult": 1.0,
        "armor": 0.0,
    },
    "necromancer": {
        "color_primary": [0.15, 0.1, 0.2],
        "color_accent": [0.4, 0.9, 0.3],
        "armored": False,
        "hp": 90,
        "speed": 3.6,
        "damage_mult": 1.2,
        "armor": 0.0,
    },
    "paladin": {
        "color_primary": [0.9, 0.75, 0.25],
        "color_accent": [1.0, 0.95, 0.8],
        "armored": True,
        "hp": 180,
        "speed": 3.0,
        "damage_mult": 1.0,
        "armor": 0.2,
    },
}


# Enemy type presets - All 13 enemy types from GDD
ENEMY_PRESETS = {
    # === Basic Enemies (7) ===
    "crawler": {
        "tier": "basic",
        "scale": 0.6,
        "hp": 15,
        "xp": 1,
        "vertices": 6,
        "symmetry": 3,
        "color_base": [0.15, 0.1, 0.2],
        "color_glow": [0.3, 0.1, 0.35],
        "behavior": "swarm",
    },
    "skeleton": {
        "tier": "basic",
        "scale": 0.8,
        "hp": 25,
        "xp": 2,
        "vertices": 8,
        "symmetry": 2,
        "color_base": [0.9, 0.85, 0.75],
        "color_glow": [0.6, 0.55, 0.45],
        "behavior": "melee",
    },
    "wisp": {
        "tier": "basic",
        "scale": 0.5,
        "hp": 10,
        "xp": 2,
        "vertices": 4,
        "symmetry": 4,
        "color_base": [0.3, 0.6, 1.0],
        "color_glow": [0.8, 0.9, 1.0],
        "behavior": "erratic",
    },
    "golem": {
        "tier": "basic",
        "scale": 1.2,
        "hp": 60,
        "xp": 5,
        "vertices": 8,
        "symmetry": 2,
        "color_base": [0.4, 0.38, 0.35],
        "color_glow": [0.55, 0.5, 0.45],
        "behavior": "slow",
    },
    "shade": {
        "tier": "basic",
        "scale": 0.7,
        "hp": 20,
        "xp": 2,
        "vertices": 5,
        "symmetry": 2,
        "color_base": [0.1, 0.05, 0.15],
        "color_glow": [0.3, 0.2, 0.4],
        "behavior": "fast",
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
        "behavior": "aggressive",
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
        "behavior": "ranged",
    },
    # === Elite Enemies (4) ===
    "crystal_knight": {
        "tier": "elite",
        "scale": 1.3,
        "hp": 150,
        "xp": 15,
        "vertices": 8,
        "symmetry": 2,
        "color_base": [0.4, 0.2, 0.5],
        "color_glow": [0.8, 0.5, 1.0],
        "behavior": "tank",
    },
    "void_mage": {
        "tier": "elite",
        "scale": 1.1,
        "hp": 100,
        "xp": 12,
        "vertices": 6,
        "symmetry": 3,
        "color_base": [0.1, 0.05, 0.15],
        "color_glow": [0.4, 0.2, 0.6],
        "behavior": "caster",
    },
    "golem_titan": {
        "tier": "elite",
        "scale": 1.6,
        "hp": 250,
        "xp": 20,
        "vertices": 8,
        "symmetry": 2,
        "color_base": [0.35, 0.3, 0.25],
        "color_glow": [0.6, 0.5, 0.4],
        "behavior": "tank",
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
        "behavior": "caster",
    },
    # === Bosses (2) ===
    "prism_colossus": {
        "tier": "boss",
        "scale": 2.5,
        "hp": 1000,
        "xp": 100,
        "vertices": 8,
        "symmetry": 4,
        "color_base": [0.3, 0.4, 0.5],
        "color_glow": [1.0, 0.3, 0.3],
        "behavior": "boss",
    },
    "void_dragon": {
        "tier": "boss",
        "scale": 2.2,
        "hp": 1500,
        "xp": 100,
        "vertices": 8,
        "symmetry": 2,
        "color_base": [0.15, 0.05, 0.2],
        "color_glow": [0.8, 0.2, 0.3],
        "behavior": "boss",
    },
}


# Stage environment presets
STAGE_PRESETS = {
    "crystal_cavern": {
        "background_colors": ["#1A2A4A", "#2A3A5A", "#101828", "#080810"],
        "floor_color": "#1A2A4A",
        "hazard_color": "#8080FF",
        "hazard_type": "crystal_shards",
    },
    "enchanted_forest": {
        "background_colors": ["#102810", "#1A3A1A", "#081808", "#040804"],
        "floor_color": "#1A3A1A",
        "hazard_color": "#40FF40",
        "hazard_type": "poison_cloud",
    },
    "volcanic_depths": {
        "background_colors": ["#2A1010", "#4A2020", "#200808", "#100404"],
        "floor_color": "#2A1010",
        "hazard_color": "#FF4000",
        "hazard_type": "lava_pool",
    },
    "void_realm": {
        "background_colors": ["#0A0A1A", "#1A1A3A", "#050510", "#000008"],
        "floor_color": "#0A0A1A",
        "hazard_color": "#8000FF",
        "hazard_type": "void_rift",
    },
}
