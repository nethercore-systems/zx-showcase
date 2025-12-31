"""
Override - Style Token Configuration

Aesthetic: Dark industrial sci-fi, high contrast, muted grays/blues with cyan/red accents
Game Type: 2D sprite-based asymmetric multiplayer (1v3)
Assets: 8x8 tilesets, animated sprites, UI elements
"""

from procgen.core.base_params import (
    UniversalStyleParams, ColorPalette, PolyBudget, GeometrySettings,
    TextureSettings, MaterialSettings, AnimationSettings, EffectSettings,
    AudioSettings, AudioEnvelope, Waveform, FilterType, SymmetryMode
)


# Raw palette values from original build.rs (RGBA)
PALETTE = {
    # Base palette - metals and shadows
    "black": "#0A0C0F",
    "dark_bg": "#12161C",
    "shadow": "#191E26",
    "dark_metal": "#232A34",
    "metal": "#343E4E",
    "light_metal": "#485569",
    "highlight": "#5F7087",
    "bright": "#7D91AC",

    # Accent palette - gameplay colors
    "cyan_dark": "#0F2D37",
    "cyan": "#2D7D91",
    "cyan_bright": "#55B9D7",
    "red_dark": "#370F0F",
    "red": "#A52323",
    "red_bright": "#E14141",
    "yellow_dark": "#372D0F",
    "yellow": "#C3A52D",
    "yellow_bright": "#F5D75F",
    "green_dark": "#0F2D19",
    "green": "#2D874B",
    "green_bright": "#55CD7D",

    # Material palette
    "rust": "#553426",
    "rust_dark": "#342016",
    "glow_core": "#91EBFF",
    "glass": "#55697D",
    "glass_dark": "#2D3744",
    "energy_blue": "#419BE1",
}


STYLE_TOKENS = UniversalStyleParams(
    game_name="override",
    style_name="industrial_dark",

    # Color Palette - Dark industrial with accent pops
    palette=ColorPalette(
        primary=[
            PALETTE["metal"],         # Base metal
            PALETTE["dark_metal"],    # Shadows
            PALETTE["light_metal"],   # Highlights
            PALETTE["shadow"],        # Deep shadow
        ],
        accent=[
            PALETTE["cyan"],          # Player/ally indicators
            PALETTE["cyan_bright"],   # Active elements
            PALETTE["red"],           # Danger/enemy
            PALETTE["red_bright"],    # Alerts
            PALETTE["yellow"],        # Collectibles
            PALETTE["green"],         # Success/health
        ],
        neutral=[
            PALETTE["black"],         # True black
            PALETTE["dark_bg"],       # Background
            PALETTE["highlight"],     # Subtle highlight
        ]
    ),
    saturation_range=(0.3, 0.6),  # Muted industrial
    value_range=(0.15, 0.7),      # Dark overall
    color_temperature=-0.4,       # Cool (blue-gray tones)

    # Geometry - 2D sprites, not 3D meshes
    # These values are mostly unused for Override but kept for compatibility
    poly_budget=PolyBudget(
        character_small=0,   # N/A - 2D sprites
        character_medium=0,
        character_large=0,
        enemy_small=0,
        enemy_medium=0,
        enemy_large=0,
        enemy_boss=0,
        vehicle=0,
        prop_small=0,
        prop_medium=0,
        prop_large=0,
        environment_tile=0,
        projectile=0,
    ),
    geometry=GeometrySettings(
        curvature_bias=0.0,  # Sharp pixels
        symmetry_mode=SymmetryMode.NONE,
        detail_scale=1.0,
        bevel_enabled=False,
        bevel_width=0.0,
    ),

    # Textures - 8x8 pixel tiles
    textures=TextureSettings(
        resolution=8,         # 8x8 tiles
        roughness_range=(0.4, 0.7),
        metallic_range=(0.5, 0.8),  # Industrial metal
        normal_strength=0.0,  # 2D - no normals
        use_emission=True,
        emission_strength=(0.8, 2.0),  # Glowing screens/indicators
    ),

    # Materials - Industrial metal with glow
    materials=MaterialSettings(
        base_roughness=0.5,
        base_metallic=0.7,
        emissive_enabled=True,
        emissive_strength=1.5,
        translucency_enabled=True,  # Glass panels
        translucency_depth=0.5,
        fresnel_intensity=0.0,  # 2D
        subsurface_enabled=False,
    ),

    # Animation - Industrial mechanical
    animation=AnimationSettings(
        idle_rotation_speed=0.0,   # No rotation
        pulse_frequency=1.0,       # Slow industrial pulse
        bob_amplitude=0.0,
        bob_frequency=0.0,
    ),

    # Effects - High contrast, minimal bloom
    effects=EffectSettings(
        bloom_intensity=0.8,       # Subtle glow
        bloom_threshold=0.85,
        chromatic_aberration=0.0,
        motion_blur=False,
        trail_enabled=False,       # No trails
        trail_decay=0.0,
        particle_density="low",    # Minimal particles
    ),

    # Audio - Industrial tension
    audio=AudioSettings(
        primary_waveform=Waveform.SQUARE,
        secondary_waveform=Waveform.NOISE,
        detune_cents=0.0,
        envelope=AudioEnvelope(
            attack_ms=2,
            decay_ms=50,
            sustain_level=0.5,
            release_ms=150,
        ),
        filter_type=FilterType.LOW_PASS,
        filter_cutoff=2500.0,
        filter_resonance=0.2,
        reverb_wet=0.35,      # Industrial reverb
        reverb_decay=1.8,
    ),
)


# Tileset definitions - 8x8 pixel tiles
TILESET_DEFS = {
    # Floor tiles
    "floor_metal": {
        "base_color": PALETTE["metal"],
        "highlight": PALETTE["light_metal"],
        "shadow": PALETTE["shadow"],
        "features": ["panel_lines", "rivets"],
    },
    "floor_grate": {
        "base_color": PALETTE["metal"],
        "hole_color": PALETTE["dark_bg"],
        "features": ["grate_pattern", "horizontal_bars"],
    },
    "floor_panel": {
        "base_color": PALETTE["light_metal"],
        "edge_color": PALETTE["highlight"],
        "features": ["clean_surface"],
    },
    "floor_damaged": {
        "base_color": PALETTE["metal"],
        "damage_colors": [PALETTE["rust"], PALETTE["rust_dark"], PALETTE["black"]],
        "features": ["rust_patches", "crack"],
    },

    # Wall tiles
    "wall_solid": {
        "base_color": PALETTE["dark_metal"],
        "highlight": PALETTE["metal"],
        "features": ["vertical_gradient"],
    },
    "wall_window": {
        "base_color": PALETTE["dark_metal"],
        "glass_color": PALETTE["glass_dark"],
        "frame_color": PALETTE["metal"],
        "features": ["window_frame"],
    },
    "wall_vent": {
        "base_color": PALETTE["dark_metal"],
        "vent_color": PALETTE["shadow"],
        "features": ["horizontal_slats"],
    },
    "wall_pipe": {
        "base_color": PALETTE["dark_metal"],
        "pipe_color": PALETTE["metal"],
        "highlight": PALETTE["light_metal"],
        "features": ["vertical_pipe"],
    },
    "wall_screen": {
        "base_color": PALETTE["dark_metal"],
        "screen_color": PALETTE["cyan_dark"],
        "glow_color": PALETTE["cyan"],
        "features": ["display_panel"],
    },
    "wall_doorframe": {
        "base_color": PALETTE["dark_metal"],
        "frame_color": PALETTE["yellow_dark"],
        "features": ["door_outline"],
    },
}


# Sprite definitions
SPRITE_DEFS = {
    # Door states (16x16)
    "door_closed": {"size": (16, 16), "colors": [PALETTE["dark_metal"], PALETTE["red_dark"]]},
    "door_opening": {"size": (16, 16), "colors": [PALETTE["metal"], PALETTE["yellow"]]},
    "door_open": {"size": (16, 16), "colors": [PALETTE["dark_bg"], PALETTE["green"]]},

    # Traps (8x8)
    "trap_spike": {"size": (8, 8), "colors": [PALETTE["metal"], PALETTE["red"]]},
    "trap_gas": {"size": (8, 8), "colors": [PALETTE["green_dark"], PALETTE["green"]]},
    "trap_laser": {"size": (8, 8), "colors": [PALETTE["red_dark"], PALETTE["red_bright"]]},

    # Runner animations (16x24, 20 frames)
    "runner_idle": {"size": (16, 24), "frames": 4},
    "runner_walk": {"size": (16, 24), "frames": 8},
    "runner_run": {"size": (16, 24), "frames": 6},
    "runner_death": {"size": (16, 24), "frames": 4},

    # Drone animations (16x16, 4 frames)
    "drone_idle": {"size": (16, 16), "frames": 4},
}


# VFX definitions
VFX_DEFS = {
    "gas_cloud": {
        "color": PALETTE["green"],
        "alpha_range": (0.3, 0.7),
        "size": (16, 16),
    },
    "laser_beam": {
        "color": PALETTE["red_bright"],
        "core_color": PALETTE["yellow_bright"],
        "size": (8, 8),
    },
    "core_glow": {
        "color": PALETTE["glow_core"],
        "pulse": True,
        "size": (8, 8),
    },
    "dust_particle": {
        "color": PALETTE["metal"],
        "size": (4, 4),
    },
    "flash": {
        "color": PALETTE["bright"],
        "size": (8, 8),
    },
}


# UI element definitions
UI_DEFS = {
    "energy_bar_bg": {"color": PALETTE["shadow"], "size": (32, 4)},
    "energy_bar_fill": {"color": PALETTE["cyan"], "glow": PALETTE["cyan_bright"]},
    "timer_digit": {"color": PALETTE["yellow"], "size": (8, 12)},
    "score_digit": {"color": PALETTE["bright"], "size": (6, 8)},
    "indicator_active": {"color": PALETTE["green_bright"]},
    "indicator_inactive": {"color": PALETTE["dark_metal"]},
    "button_normal": {"color": PALETTE["metal"], "border": PALETTE["highlight"]},
    "button_hover": {"color": PALETTE["light_metal"], "border": PALETTE["cyan"]},
    "button_pressed": {"color": PALETTE["dark_metal"], "border": PALETTE["cyan_bright"]},
}


# Audio SFX definitions
SFX_DEFS = {
    "footstep_metal": {"type": "noise_burst", "filter": 800, "duration_ms": 80},
    "footstep_grate": {"type": "noise_burst", "filter": 1200, "duration_ms": 60},
    "door_open": {"type": "sweep_down", "freq": (400, 100), "duration_ms": 300},
    "door_close": {"type": "sweep_up", "freq": (100, 400), "duration_ms": 250},
    "trap_spike": {"type": "noise_burst", "filter": 2000, "duration_ms": 100},
    "trap_gas": {"type": "noise_hiss", "filter": 3000, "duration_ms": 500},
    "trap_laser": {"type": "square_buzz", "freq": 440, "duration_ms": 200},
    "pickup_core": {"type": "sweep_up", "freq": (200, 800), "duration_ms": 150},
    "alert": {"type": "square_pulse", "freq": 880, "duration_ms": 400},
    "damage": {"type": "noise_burst", "filter": 1500, "duration_ms": 120},
    "death": {"type": "sweep_down", "freq": (600, 50), "duration_ms": 600},
    "drone_move": {"type": "square_buzz", "freq": 220, "duration_ms": 100},
    "ui_click": {"type": "square_blip", "freq": 1200, "duration_ms": 30},
    "ui_hover": {"type": "sine_blip", "freq": 800, "duration_ms": 20},
    "victory": {"type": "arpeggio", "notes": [523, 659, 784], "duration_ms": 600},
    "defeat": {"type": "sweep_down", "freq": (400, 100), "duration_ms": 800},
}


# Music definitions
MUSIC_DEFS = {
    "menu": {
        "tempo_bpm": 90,
        "key": "Am",
        "mood": "ominous",
        "layers": ["pad", "bass_pulse"],
    },
    "gameplay": {
        "tempo_bpm": 120,
        "key": "Dm",
        "mood": "tense",
        "layers": ["drums", "bass", "arp", "pad"],
    },
    "chase": {
        "tempo_bpm": 140,
        "key": "Em",
        "mood": "urgent",
        "layers": ["drums_fast", "bass_drive", "stab"],
    },
    "victory": {
        "tempo_bpm": 100,
        "key": "C",
        "mood": "triumphant",
        "layers": ["pad_major", "arp_bright"],
    },
    "defeat": {
        "tempo_bpm": 70,
        "key": "Fm",
        "mood": "somber",
        "layers": ["pad_minor", "bass_low"],
    },
}
