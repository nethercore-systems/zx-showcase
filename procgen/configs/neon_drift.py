"""
Neon Drift - Style Token Configuration

Aesthetic: Synthwave, neon glows, speed lines, retro-futuristic racing
"""

from procgen.core.base_params import (
    UniversalStyleParams, ColorPalette, PolyBudget, GeometrySettings,
    TextureSettings, MaterialSettings, AnimationSettings, EffectSettings,
    AudioSettings, AudioEnvelope, Waveform, FilterType, SymmetryMode
)


STYLE_TOKENS = UniversalStyleParams(
    game_name="neon_drift",
    style_name="synthwave_racing",

    # Color Palette - Neon synthwave
    palette=ColorPalette(
        primary=[
            "#FF00FF",  # Magenta
            "#00FFFF",  # Cyan
            "#FF6B35",  # Orange
            "#F72585",  # Pink
        ],
        accent=[
            "#FFFF00",  # Yellow (boost)
            "#00FF00",  # Green (speed)
            "#FF0000",  # Red (danger)
            "#FFFFFF",  # White (headlights)
        ],
        neutral=[
            "#0D0221",  # Deep purple (void)
            "#1A0533",  # Dark purple
            "#190A3D",  # Night sky
            "#2D1B4E",  # Building base
        ]
    ),
    saturation_range=(0.7, 1.0),  # Vibrant neon
    value_range=(0.6, 1.0),        # Bright but not washed out
    color_temperature=0.2,         # Slightly warm (sunset vibes)

    # Geometry - Clean, angular vehicles
    poly_budget=PolyBudget(
        vehicle=1000,
        prop_small=100,
        prop_medium=300,
        prop_large=600,
        environment_tile=500,
    ),
    geometry=GeometrySettings(
        curvature_bias=0.4,  # More angular than smooth
        symmetry_mode=SymmetryMode.BILATERAL,
        detail_scale=1.2,
        bevel_enabled=True,
        bevel_width=0.015,
    ),

    # Textures - Metallic with neon strips
    textures=TextureSettings(
        resolution=256,
        roughness_range=(0.2, 0.5),  # Glossy metallic
        metallic_range=(0.6, 0.9),   # High metallic
        normal_strength=0.4,
        use_emission=True,
        emission_strength=(1.5, 3.0),  # Strong neon glow
    ),

    # Materials - Metallic cars with emissive strips
    materials=MaterialSettings(
        base_roughness=0.3,
        base_metallic=0.8,
        emissive_enabled=True,
        emissive_strength=2.5,
        translucency_enabled=False,
        fresnel_intensity=0.7,
    ),

    # Animation - Speed and drift
    animation=AnimationSettings(
        idle_rotation_speed=0.0,  # Cars don't rotate idle
        pulse_frequency=2.0,      # Faster pulse for energy
        bob_amplitude=0.0,
        bob_frequency=0.0,
    ),

    # Effects - Heavy bloom, speed trails
    effects=EffectSettings(
        bloom_intensity=2.5,
        bloom_threshold=0.7,
        chromatic_aberration=0.015,
        motion_blur=False,  # ZX constraint
        trail_enabled=True,
        trail_decay=0.15,
        particle_density="high",  # Sparks, exhaust
    ),

    # Audio - Synthwave
    audio=AudioSettings(
        primary_waveform=Waveform.SAWTOOTH,
        secondary_waveform=Waveform.SQUARE,
        detune_cents=8.0,
        envelope=AudioEnvelope(
            attack_ms=5,
            decay_ms=300,
            sustain_level=0.7,
            release_ms=100,
        ),
        filter_type=FilterType.LOW_PASS,
        filter_cutoff=3000.0,
        filter_resonance=0.4,
        reverb_wet=0.25,
        reverb_decay=1.2,
    ),
)


# Car type presets
CAR_PRESETS = {
    "speedster": {
        "color_primary": "#00FFFF",
        "color_emissive": "#00FFFF",
        "silhouette": "classic_sports",
    },
    "muscle": {
        "color_primary": "#FF6B35",
        "color_emissive": "#FF6B35",
        "silhouette": "muscle_car",
    },
    "racer": {
        "color_primary": "#FF00FF",
        "color_emissive": "#FF00FF",
        "silhouette": "formula",
    },
    "drift": {
        "color_primary": "#F72585",
        "color_emissive": "#00FFFF",
        "silhouette": "jdm_hatch",
    },
    "phantom": {
        "color_primary": "#282D33",
        "color_emissive": "#00FF64",
        "silhouette": "stealth_supercar",
    },
    "titan": {
        "color_primary": "#646973",
        "color_emissive": "#FFFFFF",
        "silhouette": "luxury_gt",
    },
    "viper": {
        "color_primary": "#B41424",
        "color_emissive": "#FFC800",
        "silhouette": "hypercar",
    },
}


# Track environment presets
TRACK_PRESETS = {
    "sunset_strip": {
        "sky_colors": ["#FF6B35", "#F72585", "#7209B7", "#1A0533"],
        "road_color": "#2A1520",
        "lane_color": "#FF6B35",
    },
    "neon_city": {
        "sky_colors": ["#0D0221", "#0D0221", "#190A3D", "#000000"],
        "road_color": "#1A1A2E",
        "lane_color": "#00FFFF",
    },
    "void_tunnel": {
        "sky_colors": ["#000000", "#000000", "#000000", "#000000"],
        "road_color": "#0A0A0A",
        "lane_color": "#FF00FF",
    },
    "crystal_cavern": {
        "sky_colors": ["#1A0533", "#2D1B4E", "#0D0221", "#000000"],
        "road_color": "#1A2030",
        "lane_color": "#8B5CF6",
    },
    "solar_highway": {
        "sky_colors": ["#FFFFFF", "#FFAA00", "#FF4400", "#330000"],
        "road_color": "#2A2010",
        "lane_color": "#FFAA00",
    },
}
