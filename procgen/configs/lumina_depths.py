"""
Lumina Depths - Style Token Configuration

Aesthetic: Underwater bioluminescence, alien beauty, subaquatic dreamscape
"""

from procgen.core.base_params import (
    UniversalStyleParams, ColorPalette, PolyBudget, GeometrySettings,
    TextureSettings, MaterialSettings, AnimationSettings, EffectSettings,
    AudioSettings, AudioEnvelope, Waveform, FilterType, SymmetryMode
)


STYLE_TOKENS = UniversalStyleParams(
    game_name="lumina_depths",
    style_name="bioluminescent_underwater",

    # Color Palette - Deep ocean with bioluminescent accents
    palette=ColorPalette(
        primary=[
            "#00FFCC",  # Electric Teal (primary bioluminescence)
            "#00D9FF",  # Neon Cyan (jellyfish)
            "#6B46C1",  # Deep Purple (rare flora)
            "#4DD4E8",  # Ambient Cyan
        ],
        accent=[
            "#C0F0FF",  # Aqua White (brightest points)
            "#FF6B9D",  # Coral Pink
            "#40E0D0",  # Turquoise
            "#8B008B",  # Dark Magenta (danger)
        ],
        neutral=[
            "#0A0E1A",  # Abyssal Black
            "#1A2A4A",  # Deep Indigo
            "#2D4A7C",  # Ocean Blue
            "#101828",  # Near-black blue
        ]
    ),
    saturation_range=(0.6, 1.0),
    value_range=(0.2, 0.9),
    color_temperature=-0.4,  # Cool blue bias

    # Geometry - Organic, flowing curves
    poly_budget=PolyBudget(
        character_small=600,
        character_medium=1000,
        enemy_small=300,
        enemy_medium=600,
        enemy_large=1200,
        prop_small=150,
        prop_medium=400,
        environment_tile=500,
    ),
    geometry=GeometrySettings(
        curvature_bias=0.75,  # Organic curves
        symmetry_mode=SymmetryMode.BILATERAL,
        detail_scale=1.2,
        bevel_enabled=False,  # Soft organic forms
        bevel_width=0.0,
    ),

    # Textures - Translucent with glow patterns
    textures=TextureSettings(
        resolution=512,
        roughness_range=(0.3, 0.95),
        metallic_range=(0.0, 0.2),  # Non-metallic organic
        normal_strength=0.4,
        use_emission=True,
        emission_strength=(0.5, 2.0),
    ),

    # Materials - Translucent bioluminescence
    materials=MaterialSettings(
        base_roughness=0.5,
        base_metallic=0.0,
        emissive_enabled=True,
        emissive_strength=1.5,
        translucency_enabled=True,
        translucency_depth=0.3,
        fresnel_intensity=0.6,
        subsurface_enabled=True,
    ),

    # Animation - Slow, flowing movement
    animation=AnimationSettings(
        idle_rotation_speed=0.2,  # Gentle drift
        pulse_frequency=0.8,      # Slow bio-pulse
        bob_amplitude=0.15,       # Floating motion
        bob_frequency=0.5,        # Slow bob
    ),

    # Effects - Subtle glow, underwater caustics
    effects=EffectSettings(
        bloom_intensity=1.8,
        bloom_threshold=0.6,
        chromatic_aberration=0.0,
        motion_blur=False,
        trail_enabled=True,
        trail_decay=0.4,  # Longer trails (water)
        particle_density="medium",  # Bubbles, plankton
    ),

    # Audio - Subaquatic ambience
    audio=AudioSettings(
        primary_waveform=Waveform.SINE,
        secondary_waveform=Waveform.TRIANGLE,
        detune_cents=5.0,
        envelope=AudioEnvelope(
            attack_ms=200,
            decay_ms=500,
            sustain_level=0.6,
            release_ms=800,
        ),
        filter_type=FilterType.LOW_PASS,
        filter_cutoff=2000.0,  # Underwater muffling
        filter_resonance=0.3,
        reverb_wet=0.5,
        reverb_decay=2.5,
    ),
)


# Creature family presets
CREATURE_PRESETS = {
    "lantern_jelly": {
        "color_primary": "#00FFCC",
        "color_glow": "#C0F0FF",
        "body_type": "bell_translucent",
        "limb_count": 12,
        "movement_style": "float",
        "behavior": "guide",
    },
    "void_swimmer": {
        "color_primary": "#4DD4E8",
        "color_glow": "#6B46C1",
        "body_type": "eel_elongated",
        "limb_count": 0,
        "movement_style": "swim_fast",
        "behavior": "neutral",
    },
    "light_eater": {
        "color_primary": "#8B008B",
        "color_glow": "#FF6B9D",
        "body_type": "angular_predator",
        "limb_count": 6,
        "movement_style": "dart_erratic",
        "behavior": "hazard",
    },
    "abyssal_leviathan": {
        "color_primary": "#0A0E1A",
        "color_glow": "#FF0000",
        "body_type": "massive_silhouette",
        "limb_count": 0,
        "movement_style": "background_drift",
        "behavior": "environmental",
    },
}


# Depth zone presets
DEPTH_ZONES = {
    "twilight": {
        "depth_range": (0, 100),
        "background_color": "#2D4A7C",
        "visibility": 30,
        "caustics_strength": 0.8,
        "fog_density": 0.05,
    },
    "midnight": {
        "depth_range": (100, 500),
        "background_color": "#1A2A4A",
        "visibility": 15,
        "caustics_strength": 0.2,
        "fog_density": 0.15,
    },
    "abyssal": {
        "depth_range": (500, 1000),
        "background_color": "#0A0E1A",
        "visibility": 8,
        "caustics_strength": 0.0,
        "fog_density": 0.3,
    },
}


# Environment presets
ENVIRONMENT_PRESETS = {
    "coral_cluster": {
        "pattern": "fractal_branching",
        "colors": ["#FF6B9D", "#00FFCC", "#6B46C1"],
        "scale_range": (0.5, 2.0),
        "glow_zones": 3,
    },
    "kelp_forest": {
        "pattern": "ribbon_vertical",
        "colors": ["#2D5A3D", "#40E0D0"],
        "scale_range": (2.0, 5.0),
        "sway_amount": 0.3,
    },
    "ancient_ruin": {
        "pattern": "geometric_eroded",
        "colors": ["#1A2A4A", "#00FFCC"],
        "scale_range": (3.0, 10.0),
        "rune_glow": True,
    },
}
