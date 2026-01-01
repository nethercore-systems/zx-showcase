#!/usr/bin/env python3
"""
NEON DRIFT Car Generator
Main entry point for generating all car meshes and textures

Run with: blender --background --python generate_cars.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import bpy
    from generators.car_geometry import CarGeometry, CAR_DIMENSIONS
    from generators.car_textures import CarTextures
except ImportError as e:
    print(f"Error: {e}")
    print("Must run from Blender with generators module available")
    print("Usage: blender --background --python generate_cars.py")
    sys.exit(1)

# Add procgen configs to path
REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "zx-showcase" / "procgen" / "configs"))

from neon_drift import CAR_PRESETS

# Output paths
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "models"
MESH_DIR = OUTPUT_DIR / "meshes"
TEXTURE_DIR = OUTPUT_DIR / "textures"
MESH_DIR.mkdir(parents=True, exist_ok=True)
TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
            ["curved_hood", "low_roof", "streamlined", "small_spoiler"]),

    CarSpec("muscle", (0.15, 0.25, 0.85), (0.0, 0.6, 1.0),
            4.5, 2.1, 1.25, 0.48, "boxy",
            ["hood_scoop", "wide_stance", "chunky_wheels", "squared_fenders"]),

    CarSpec("racer", (0.12, 0.85, 0.35), (0.0, 1.0, 0.5),
            4.3, 1.7, 0.85, 0.32, "technical",
            ["rear_wing", "aero_nose", "low_cockpit", "side_pods"]),

    CarSpec("drift", (0.95, 0.55, 0.12), (1.0, 0.4, 0.0),
            3.9, 2.0, 1.1, 0.42, "japanese",
            ["wide_fenders", "side_skirts", "drift_spoiler", "vented_hood"]),

    CarSpec("phantom", (0.2, 0.12, 0.28), (0.7, 0.0, 1.0),
            4.6, 1.85, 0.98, 0.4, "stealth",
            ["wedge_nose", "hidden_lights", "smooth_panels", "integrated_spoiler"]),

    CarSpec("titan", (0.55, 0.65, 0.7), (0.0, 1.0, 1.0),
            4.8, 2.3, 1.45, 0.52, "truck",
            ["boxy_cab", "roof_lights", "heavy_bumper", "high_clearance"]),

    CarSpec("viper", (0.92, 0.9, 0.15), (1.0, 1.0, 0.0),
            3.6, 1.65, 0.88, 0.35, "compact",
            ["tight_curves", "small_spoiler", "aggressive_lights", "sport_stance"]),
]


def clear_scene():
    """Remove all objects from scene and clean up orphan data."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def create_beveled_box(sx: float, sy: float, sz: float,
                       bevel: float = 0.02, segments: int = 1) -> bpy.types.Object:
    """Create a box with beveled edges for smooth transitions."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)

    # Add bevel modifier for smooth edges (1 segment to save tris)
    bevel_mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel_mod.width = bevel
    bevel_mod.segments = segments
    bevel_mod.limit_method = 'ANGLE'
    bevel_mod.angle_limit = math.radians(30)

    # Apply modifier
    bpy.ops.object.modifier_apply(modifier="Bevel")

    return obj


def create_tapered_box(sx: float, sy: float, sz: float,
                       front_taper: float = 0.8, top_taper: float = 0.9) -> bpy.types.Object:
    """Create a tapered box for aerodynamic shapes."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)

    # Enter edit mode to taper
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)

    # Taper front vertices
    for v in bm.verts:
        if v.co.x > 0:  # Front
            v.co.y *= front_taper
            v.co.z *= (0.9 + 0.1 * front_taper)
        if v.co.z > 0:  # Top
            v.co.y *= top_taper

    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    return obj


def create_wheel(radius: float = 0.15, width: float = 0.08,
                 vertices: int = 16) -> bpy.types.Object:
    """Create a detailed wheel with rim suggestion."""
    # Outer tire
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=width, vertices=vertices,
        rotation=(math.pi/2, 0, 0)
    )
    wheel = bpy.context.active_object

    # Add inner rim (smaller cylinder)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius * 0.65, depth=width * 1.1, vertices=8,
        rotation=(math.pi/2, 0, 0)
    )
    rim = bpy.context.active_object

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    wheel.select_set(True)
    rim.select_set(True)
    bpy.context.view_layer.objects.active = wheel
    bpy.ops.object.join()

    return wheel


def create_headlight(size: float = 0.06, style: str = "round") -> bpy.types.Object:
    """Create headlight geometry."""
    if style == "round":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size, segments=8, ring_count=6)
        light = bpy.context.active_object
        # Flatten front
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.transform.resize(value=(0.5, 1, 1))
        bpy.ops.object.mode_set(mode='OBJECT')
    else:  # rectangular
        light = create_beveled_box(size * 0.5, size, size * 0.6, bevel=0.01)

    return light


def create_taillight(width: float = 0.08, height: float = 0.04) -> bpy.types.Object:
    """Create taillight geometry."""
    light = create_beveled_box(0.02, width, height, bevel=0.005)
    return light


def create_windshield(width: float, height: float,
                      angle: float = 30) -> bpy.types.Object:
    """Create angled windshield panel."""
    bpy.ops.mesh.primitive_plane_add(size=1)
    obj = bpy.context.active_object
    obj.scale = (height * 0.5, width * 0.5, 1)
    bpy.ops.object.transform_apply(scale=True)

    # Rotate to angle
    obj.rotation_euler.y = math.radians(angle)
    bpy.ops.object.transform_apply(rotation=True)

    # Add slight curve
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=2)
    bm = bmesh.from_edit_mesh(obj.data)
    for v in bm.verts:
        # Curve slightly outward
        curve = 0.02 * (1 - (v.co.x ** 2) * 4)
        v.co.z += curve
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    return obj


def create_spoiler(width: float, height: float, depth: float,
                   style: str = "wing") -> bpy.types.Object:
    """Create rear spoiler/wing."""
    if style == "wing":
        spoiler_parts = []

        # Main wing element
        wing = create_beveled_box(depth, width, height * 0.3, bevel=0.01)
        wing.location.z = height * 0.7
        spoiler_parts.append(wing)

        # Supports
        for y_offset in [width * 0.35, -width * 0.35]:
            bpy.ops.mesh.primitive_cube_add(size=1)
            support = bpy.context.active_object
            support.scale = (depth * 0.3, 0.02, height * 0.5)
            bpy.ops.object.transform_apply(scale=True)
            support.location = (0, y_offset, height * 0.35)
            spoiler_parts.append(support)

        # Join spoiler parts only
        bpy.ops.object.select_all(action='DESELECT')
        for p in spoiler_parts:
            p.select_set(True)
        bpy.context.view_layer.objects.active = wing
        bpy.ops.object.join()
        return bpy.context.active_object
    else:  # lip
        return create_beveled_box(depth, width, height, bevel=0.01)


# === CAR-SPECIFIC BUILDERS ===

def create_speedster(spec: CarSpec) -> bpy.types.Object:
    """Create sleek magenta speedster - beginner-friendly."""
    L, W, H = spec.length, spec.width, spec.height
    parts = []

    # Main body - long, low, tapered
    body = create_tapered_box(L * 0.48, W * 0.46, H * 0.35,
                              front_taper=0.75, top_taper=0.88)
    body.location = (0, 0, H * 0.38)
    parts.append(body)

    # Hood - curved, flows forward
    hood = create_tapered_box(L * 0.22, W * 0.42, H * 0.18,
                              front_taper=0.6, top_taper=0.85)
    hood.location = (L * 0.28, 0, H * 0.45)
    parts.append(hood)

    # Cabin - low, streamlined bubble
    cabin = create_beveled_box(L * 0.28, W * 0.4, H * 0.28, bevel=0.03)
    cabin.location = (-L * 0.05, 0, H * 0.62)
    parts.append(cabin)

    # Windshield
    ws = create_windshield(W * 0.38, H * 0.25, angle=25)
    ws.location = (L * 0.08, 0, H * 0.72)
    parts.append(ws)

    # Rear deck - tapers down
    rear = create_tapered_box(L * 0.18, W * 0.4, H * 0.2,
                              front_taper=1.0, top_taper=0.7)
    rear.location = (-L * 0.32, 0, H * 0.48)
    parts.append(rear)

    # Small integrated spoiler
    spoiler = create_beveled_box(L * 0.04, W * 0.42, H * 0.03, bevel=0.008)
    spoiler.location = (-L * 0.42, 0, H * 0.52)
    parts.append(spoiler)

    # Wheels
    wheel_r = H * 0.28
    for x, y in [(L * 0.28, W * 0.48), (L * 0.28, -W * 0.48),
                 (-L * 0.28, W * 0.48), (-L * 0.28, -W * 0.48)]:
        wheel = create_wheel(wheel_r, W * 0.08)
        wheel.location = (x, y, wheel_r)
        parts.append(wheel)

    # Headlights
    for y in [W * 0.32, -W * 0.32]:
        hl = create_headlight(H * 0.06, "round")
        hl.location = (L * 0.44, y, H * 0.4)
        parts.append(hl)

    # Taillights
    for y in [W * 0.28, -W * 0.28]:
        tl = create_taillight(H * 0.08, H * 0.04)
        tl.location = (-L * 0.46, y, H * 0.45)
        parts.append(tl)

    return join_car_parts(parts, spec.name)


def create_muscle(spec: CarSpec) -> bpy.types.Object:
    """Create boxy blue muscle car - powerful American style."""
    L, W, H = spec.length, spec.width, spec.height
    parts = []

    # Main body - wide, aggressive, boxy (includes fenders)
    body = create_beveled_box(L * 0.48, W * 0.5, H * 0.34, bevel=0.02)
    body.location = (0, 0, H * 0.36)
    parts.append(body)

    # Hood - long, flat with integrated scoop shape
    hood = create_beveled_box(L * 0.26, W * 0.46, H * 0.14, bevel=0.015)
    hood.location = (L * 0.26, 0, H * 0.52)
    parts.append(hood)

    # Cabin - squared, sits high
    cabin = create_beveled_box(L * 0.26, W * 0.44, H * 0.3, bevel=0.02)
    cabin.location = (-L * 0.05, 0, H * 0.62)
    parts.append(cabin)

    # Windshield
    ws = create_windshield(W * 0.42, H * 0.28, angle=38)
    ws.location = (L * 0.08, 0, H * 0.72)
    parts.append(ws)

    # Trunk - squared
    trunk = create_beveled_box(L * 0.16, W * 0.44, H * 0.2, bevel=0.015)
    trunk.location = (-L * 0.34, 0, H * 0.44)
    parts.append(trunk)

    # Chunky wheels
    wheel_r = H * 0.3
    for x, y in [(L * 0.28, W * 0.52), (L * 0.28, -W * 0.52),
                 (-L * 0.28, W * 0.52), (-L * 0.28, -W * 0.52)]:
        wheel = create_wheel(wheel_r, W * 0.1, vertices=14)
        wheel.location = (x, y, wheel_r)
        parts.append(wheel)

    # Rectangular headlights
    for y in [W * 0.34, -W * 0.34]:
        hl = create_headlight(H * 0.07, "rectangular")
        hl.location = (L * 0.44, y, H * 0.44)
        parts.append(hl)

    # Wide taillights
    for y in [W * 0.32, -W * 0.32]:
        tl = create_taillight(H * 0.1, H * 0.045)
        tl.location = (-L * 0.45, y, H * 0.48)
        parts.append(tl)

    return join_car_parts(parts, spec.name)


def create_racer(spec: CarSpec) -> bpy.types.Object:
    """Create green F1-inspired technical racer."""
    L, W, H = spec.length, spec.width, spec.height
    parts = []

    # Main body - very low, very long
    body = create_tapered_box(L * 0.5, W * 0.42, H * 0.28,
                              front_taper=0.5, top_taper=0.75)
    body.location = (0, 0, H * 0.32)
    parts.append(body)

    # Aero nose cone
    nose = create_tapered_box(L * 0.18, W * 0.3, H * 0.15,
                              front_taper=0.3, top_taper=0.6)
    nose.location = (L * 0.38, 0, H * 0.28)
    parts.append(nose)

    # Low cockpit
    cabin = create_beveled_box(L * 0.18, W * 0.32, H * 0.22, bevel=0.02)
    cabin.location = (-L * 0.12, 0, H * 0.48)
    parts.append(cabin)

    # Windshield - very angled
    ws = create_windshield(W * 0.3, H * 0.18, angle=18)
    ws.location = (-L * 0.02, 0, H * 0.55)
    parts.append(ws)

    # Side pods (aero)
    for y in [W * 0.38, -W * 0.38]:
        pod = create_tapered_box(L * 0.22, W * 0.12, H * 0.12,
                                 front_taper=0.6, top_taper=0.8)
        pod.location = (L * 0.05, y, H * 0.32)
        parts.append(pod)

    # High rear wing
    wing = create_spoiler(W * 0.48, H * 0.2, L * 0.08, style="wing")
    wing.location = (-L * 0.42, 0, H * 0.5)
    parts.append(wing)

    # Low profile wheels
    wheel_r = H * 0.26
    for x, y in [(L * 0.32, W * 0.48), (L * 0.32, -W * 0.48),
                 (-L * 0.28, W * 0.48), (-L * 0.28, -W * 0.48)]:
        wheel = create_wheel(wheel_r, W * 0.09, vertices=18)
        wheel.location = (x, y, wheel_r)
        parts.append(wheel)

    # Small LED headlights
    for y in [W * 0.22, -W * 0.22]:
        hl = create_headlight(H * 0.04, "round")
        hl.location = (L * 0.48, y, H * 0.28)
        parts.append(hl)

    # Strip taillights
    for y in [W * 0.2, -W * 0.2]:
        tl = create_taillight(H * 0.06, H * 0.025)
        tl.location = (-L * 0.48, y, H * 0.38)
        parts.append(tl)

    return join_car_parts(parts, spec.name)


def create_drift(spec: CarSpec) -> bpy.types.Object:
    """Create orange Japanese drift car."""
    L, W, H = spec.length, spec.width, spec.height
    parts = []

    # Main body - medium profile (combines body + fenders)
    body = create_beveled_box(L * 0.48, W * 0.52, H * 0.32, bevel=0.02)
    body.location = (0, 0, H * 0.35)
    parts.append(body)

    # Hood with vents integrated
    hood = create_beveled_box(L * 0.22, W * 0.48, H * 0.14, bevel=0.015)
    hood.location = (L * 0.26, 0, H * 0.5)
    parts.append(hood)

    # Cabin
    cabin = create_beveled_box(L * 0.24, W * 0.42, H * 0.28, bevel=0.02)
    cabin.location = (-L * 0.06, 0, H * 0.58)
    parts.append(cabin)

    # Windshield
    ws = create_windshield(W * 0.4, H * 0.26, angle=32)
    ws.location = (L * 0.06, 0, H * 0.68)
    parts.append(ws)

    # Rear deck with integrated spoiler
    rear = create_beveled_box(L * 0.16, W * 0.46, H * 0.18, bevel=0.015)
    rear.location = (-L * 0.34, 0, H * 0.48)
    parts.append(rear)

    # Simple lip spoiler (no wing supports to save tris)
    spoiler = create_spoiler(W * 0.44, H * 0.08, L * 0.04, style="lip")
    spoiler.location = (-L * 0.42, 0, H * 0.58)
    parts.append(spoiler)

    # Wheels with wide stance
    wheel_r = H * 0.28
    for x, y in [(L * 0.26, W * 0.52), (L * 0.26, -W * 0.52),
                 (-L * 0.26, W * 0.52), (-L * 0.26, -W * 0.52)]:
        wheel = create_wheel(wheel_r, W * 0.1, vertices=14)
        wheel.location = (x, y, wheel_r)
        parts.append(wheel)

    # Angular headlights
    for y in [W * 0.32, -W * 0.32]:
        hl = create_headlight(H * 0.06, "rectangular")
        hl.location = (L * 0.44, y, H * 0.42)
        parts.append(hl)

    # Taillights
    for y in [W * 0.28, -W * 0.28]:
        tl = create_taillight(H * 0.08, H * 0.04)
        tl.location = (-L * 0.45, y, H * 0.48)
        parts.append(tl)

    return join_car_parts(parts, spec.name)


def create_phantom(spec: CarSpec) -> bpy.types.Object:
    """Create purple stealth wedge car."""
    L, W, H = spec.length, spec.width, spec.height
    parts = []

    # Wedge body - smooth, mysterious
    body = create_tapered_box(L * 0.5, W * 0.45, H * 0.3,
                              front_taper=0.55, top_taper=0.8)
    body.location = (0, 0, H * 0.35)
    parts.append(body)

    # Wedge nose - very low, pointed
    nose = create_tapered_box(L * 0.2, W * 0.38, H * 0.14,
                              front_taper=0.35, top_taper=0.6)
    nose.location = (L * 0.32, 0, H * 0.3)
    parts.append(nose)

    # Low smooth cabin
    cabin = create_beveled_box(L * 0.26, W * 0.38, H * 0.24, bevel=0.03)
    cabin.location = (-L * 0.08, 0, H * 0.55)
    parts.append(cabin)

    # Angled windshield - very low angle
    ws = create_windshield(W * 0.36, H * 0.22, angle=22)
    ws.location = (L * 0.04, 0, H * 0.62)
    parts.append(ws)

    # Smooth rear deck
    rear = create_tapered_box(L * 0.18, W * 0.42, H * 0.18,
                              front_taper=1.0, top_taper=0.75)
    rear.location = (-L * 0.34, 0, H * 0.45)
    parts.append(rear)

    # Integrated lip spoiler
    spoiler = create_beveled_box(L * 0.05, W * 0.4, H * 0.025, bevel=0.008)
    spoiler.location = (-L * 0.45, 0, H * 0.5)
    parts.append(spoiler)

    # Sleek wheels
    wheel_r = H * 0.27
    for x, y in [(L * 0.3, W * 0.46), (L * 0.3, -W * 0.46),
                 (-L * 0.28, W * 0.46), (-L * 0.28, -W * 0.46)]:
        wheel = create_wheel(wheel_r, W * 0.08, vertices=16)
        wheel.location = (x, y, wheel_r)
        parts.append(wheel)

    # Hidden/recessed headlights
    for y in [W * 0.28, -W * 0.28]:
        hl = create_headlight(H * 0.04, "round")
        hl.location = (L * 0.46, y, H * 0.28)
        parts.append(hl)

    # Minimal strip taillights
    for y in [W * 0.25, -W * 0.25]:
        tl = create_taillight(H * 0.06, H * 0.02)
        tl.location = (-L * 0.48, y, H * 0.42)
        parts.append(tl)

    return join_car_parts(parts, spec.name)


def create_titan(spec: CarSpec) -> bpy.types.Object:
    """Create cyan/silver heavy truck."""
    L, W, H = spec.length, spec.width, spec.height
    parts = []

    # Boxy main body - heavy, high (includes bumper/grille)
    body = create_beveled_box(L * 0.48, W * 0.5, H * 0.38, bevel=0.02)
    body.location = (0, 0, H * 0.4)
    parts.append(body)

    # Truck cab - tall, boxy
    cabin = create_beveled_box(L * 0.28, W * 0.46, H * 0.36, bevel=0.02)
    cabin.location = (-L * 0.02, 0, H * 0.64)
    parts.append(cabin)

    # Windshield - more upright
    ws = create_windshield(W * 0.44, H * 0.3, angle=48)
    ws.location = (L * 0.12, 0, H * 0.78)
    parts.append(ws)

    # Hood - short, high
    hood = create_beveled_box(L * 0.16, W * 0.46, H * 0.12, bevel=0.015)
    hood.location = (L * 0.28, 0, H * 0.56)
    parts.append(hood)

    # Bed/cargo area
    bed = create_beveled_box(L * 0.2, W * 0.48, H * 0.16, bevel=0.015)
    bed.location = (-L * 0.34, 0, H * 0.4)
    parts.append(bed)

    # Large wheels with high clearance
    wheel_r = H * 0.26
    for x, y in [(L * 0.28, W * 0.54), (L * 0.28, -W * 0.54),
                 (-L * 0.28, W * 0.54), (-L * 0.28, -W * 0.54)]:
        wheel = create_wheel(wheel_r, W * 0.12, vertices=14)
        wheel.location = (x, y, wheel_r)
        parts.append(wheel)

    # Large round headlights
    for y in [W * 0.36, -W * 0.36]:
        hl = create_headlight(H * 0.07, "round")
        hl.location = (L * 0.44, y, H * 0.48)
        parts.append(hl)

    # Big rectangular taillights
    for y in [W * 0.34, -W * 0.34]:
        tl = create_taillight(H * 0.1, H * 0.05)
        tl.location = (-L * 0.46, y, H * 0.45)
        parts.append(tl)

    return join_car_parts(parts, spec.name)


def create_viper(spec: CarSpec) -> bpy.types.Object:
    """Create yellow compact sports car - agile."""
    L, W, H = spec.length, spec.width, spec.height
    parts = []

    # Compact body
    body = create_tapered_box(L * 0.48, W * 0.44, H * 0.32,
                              front_taper=0.7, top_taper=0.85)
    body.location = (0, 0, H * 0.36)
    parts.append(body)

    # Compact curved hood
    hood = create_tapered_box(L * 0.2, W * 0.4, H * 0.14,
                              front_taper=0.6, top_taper=0.8)
    hood.location = (L * 0.28, 0, H * 0.45)
    parts.append(hood)

    # Tight cabin
    cabin = create_beveled_box(L * 0.22, W * 0.38, H * 0.26, bevel=0.025)
    cabin.location = (-L * 0.04, 0, H * 0.58)
    parts.append(cabin)

    # Windshield
    ws = create_windshield(W * 0.36, H * 0.24, angle=28)
    ws.location = (L * 0.08, 0, H * 0.68)
    parts.append(ws)

    # Compact rear
    rear = create_tapered_box(L * 0.15, W * 0.38, H * 0.18,
                              front_taper=1.0, top_taper=0.75)
    rear.location = (-L * 0.3, 0, H * 0.45)
    parts.append(rear)

    # Small sporty spoiler
    spoiler = create_spoiler(W * 0.38, H * 0.1, L * 0.05, style="lip")
    spoiler.location = (-L * 0.4, 0, H * 0.55)
    parts.append(spoiler)

    # Compact wheels
    wheel_r = H * 0.27
    for x, y in [(L * 0.28, W * 0.46), (L * 0.28, -W * 0.46),
                 (-L * 0.26, W * 0.46), (-L * 0.26, -W * 0.46)]:
        wheel = create_wheel(wheel_r, W * 0.08, vertices=16)
        wheel.location = (x, y, wheel_r)
        parts.append(wheel)

    # Aggressive angular headlights
    for y in [W * 0.28, -W * 0.28]:
        hl = create_headlight(H * 0.055, "rectangular")
        hl.location = (L * 0.42, y, H * 0.4)
        parts.append(hl)

    # Sport taillights
    for y in [W * 0.25, -W * 0.25]:
        tl = create_taillight(H * 0.07, H * 0.035)
        tl.location = (-L * 0.44, y, H * 0.48)
        parts.append(tl)

    return join_car_parts(parts, spec.name)


def join_car_parts(parts: List[bpy.types.Object], name: str) -> bpy.types.Object:
    """Join all parts into single mesh with proper UVs."""
    if not parts:
        return None

    # Select all parts
    bpy.ops.object.select_all(action='DESELECT')
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]

    # Join
    bpy.ops.object.join()
    car = bpy.context.active_object
    car.name = name

    # UV unwrap
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Smooth shading for curves
    bpy.ops.object.shade_smooth()

    return car


def create_car_mesh(spec: CarSpec) -> bpy.types.Object:
    """Create car mesh based on style."""
    clear_scene()

    builders = {
        "sleek": create_speedster,
        "boxy": create_muscle,
        "technical": create_racer,
        "japanese": create_drift,
        "stealth": create_phantom,
        "truck": create_titan,
        "compact": create_viper,
    }

    builder = builders.get(spec.style)
    if builder:
        return builder(spec)
    else:
        print(f"Warning: Unknown style '{spec.style}', using sleek")
        return create_speedster(spec)


def generate_metallic_texture(spec: CarSpec, size: int = 256) -> 'bpy.types.Image':
    """Generate metallic paint texture with gradients and panel lines."""
    img = bpy.data.images.new(name=f"{spec.name}_albedo",
                               width=size, height=size, alpha=False)

    pixels = []
    r, g, b = spec.body_color

    for y in range(size):
        for x in range(size):
            # Base gradient (lighter on top)
            gradient = 1.0 - (y / size) * 0.25

            # Metallic sheen variation
            sheen = 1.0 + 0.08 * math.sin(x * 0.15) * math.cos(y * 0.12)

            # Subtle noise for paint texture
            noise = ((x * 17 + y * 31) % 100) / 1000.0 - 0.05

            # Panel lines (darker horizontal/vertical lines)
            panel_dark = 1.0
            if y == size // 4 or y == size // 2 or y == 3 * size // 4:
                panel_dark = 0.7
            if x == size // 3 or x == 2 * size // 3:
                panel_dark = 0.7

            # Window tint region (dark in upper middle)
            window_tint = 1.0
            if size // 3 < y < size // 2 and size // 6 < x < 5 * size // 6:
                window_tint = 0.15

            # Calculate final color
            pr = max(0, min(1, r * gradient * sheen * panel_dark * window_tint + noise))
            pg = max(0, min(1, g * gradient * sheen * panel_dark * window_tint + noise))
            pb = max(0, min(1, b * gradient * sheen * panel_dark * window_tint + noise))

            pixels.extend([pr, pg, pb, 1.0])

    img.pixels = pixels
    return img


def generate_emissive_texture(spec: CarSpec, size: int = 256) -> 'bpy.types.Image':
    """Generate strategic neon emissive texture."""
    img = bpy.data.images.new(name=f"{spec.name}_emissive",
                               width=size, height=size, alpha=False)

    pixels = [0.0] * (size * size * 4)  # Start with black
    r, g, b = spec.accent_color

    def set_pixel(x: int, y: int, intensity: float = 1.0):
        if 0 <= x < size and 0 <= y < size:
            idx = (y * size + x) * 4
            pixels[idx] = r * intensity
            pixels[idx + 1] = g * intensity
            pixels[idx + 2] = b * intensity
            pixels[idx + 3] = 1.0

    def draw_line_h(y: int, x1: int, x2: int, intensity: float = 1.0, width: int = 2):
        for dy in range(-width//2, width//2 + 1):
            for x in range(x1, x2):
                set_pixel(x, y + dy, intensity)

    def draw_line_v(x: int, y1: int, y2: int, intensity: float = 1.0, width: int = 2):
        for dx in range(-width//2, width//2 + 1):
            for y in range(y1, y2):
                set_pixel(x + dx, y, intensity)

    def draw_circle(cx: int, cy: int, radius: int, intensity: float = 1.0):
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx*dx + dy*dy <= radius*radius:
                    set_pixel(cx + dx, cy + dy, intensity)

    # Edge trim (neon outline)
    edge_y_top = size // 4
    edge_y_bot = 3 * size // 4
    edge_x_left = size // 6
    edge_x_right = 5 * size // 6

    draw_line_h(edge_y_top, edge_x_left, edge_x_right, 0.9)
    draw_line_h(edge_y_bot, edge_x_left, edge_x_right, 0.9)
    draw_line_v(edge_x_left, edge_y_top, edge_y_bot, 0.9)
    draw_line_v(edge_x_right, edge_y_top, edge_y_bot, 0.9)

    # Headlights (bright spots)
    hl_y = int(size * 0.38)
    draw_circle(size // 4, hl_y, 8, 1.0)
    draw_circle(3 * size // 4, hl_y, 8, 1.0)

    # Taillights
    tl_y = int(size * 0.55)
    draw_circle(size // 8, tl_y, 6, 0.95)
    draw_circle(7 * size // 8, tl_y, 6, 0.95)

    # Underglow gradient
    for y in range(7 * size // 8, size):
        intensity = (y - 7 * size // 8) / (size // 8) * 0.5
        for x in range(size):
            set_pixel(x, y, intensity)

    # Style-specific patterns
    if spec.style == "technical":
        # Aero stripes
        draw_line_h(size // 3, size // 4, 3 * size // 4, 0.7)
        draw_line_h(2 * size // 3, size // 4, 3 * size // 4, 0.7)

    elif spec.style == "boxy":
        # Hood stripe lights
        draw_line_v(size // 3, size // 5, size // 2, 0.8)
        draw_line_v(2 * size // 3, size // 5, size // 2, 0.8)

    elif spec.style == "japanese":
        # Side underglow emphasis
        for y in range(2 * size // 3, 7 * size // 8):
            intensity = 0.6 * (y - 2 * size // 3) / (7 * size // 24)
            set_pixel(size // 5, y, intensity)
            set_pixel(4 * size // 5, y, intensity)

    elif spec.style == "truck":
        # Roof light bar
        roof_y = size // 6
        for x in range(size // 4, 3 * size // 4, size // 8):
            draw_circle(x, roof_y, 5, 1.0)

    img.pixels = pixels
    return img


def create_material(name: str, color: Tuple[float, float, float]) -> bpy.types.Material:
    """Create PBR material for car."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    # Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['Roughness'].default_value = 0.25

    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat


def save_texture(img: bpy.types.Image, filepath: Path):
    """Save texture to PNG file."""
    img.filepath_raw = str(filepath)
    img.file_format = 'PNG'
    img.save()


def export_glb(obj: bpy.types.Object, filepath: Path):
    """Export mesh to GLB format."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    filepath.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(filepath),
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
        export_normals=True,
        export_texcoords=True,
    )


def count_triangles(obj: bpy.types.Object) -> int:
    """Count triangles in mesh."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    count = len(bm.faces)
    bm.free()
    return count


def main():
    print("\n" + "=" * 60)
    print("  NEON DRIFT - Enhanced Car Generator")
    print("  Synthwave Racing Cars with Curved Bodies & Neon")
    print("=" * 60)

    script_dir = Path(__file__).parent
    output_base = script_dir.parent / "assets" / "models"
    meshes_dir = output_base / "meshes"
    textures_dir = output_base / "textures"
    meshes_dir.mkdir(parents=True, exist_ok=True)
    textures_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nOutput: {output_base}")

    for spec in CARS:
        print(f"\n--- {spec.name.upper()} ({spec.style}) ---")

        # Create mesh
        car = create_car_mesh(spec)
        tri_count = count_triangles(car)
        print(f"  Triangles: {tri_count}")

        # Create material
        mat = create_material(f"{spec.name}_mat", spec.body_color)
        car.data.materials.append(mat)

        # Generate textures
        albedo = generate_metallic_texture(spec)
        save_texture(albedo, textures_dir / f"{spec.name}.png")
        print(f"  Albedo: {spec.name}.png")
        bpy.data.images.remove(albedo)

        emissive = generate_emissive_texture(spec)
        save_texture(emissive, textures_dir / f"{spec.name}_emissive.png")
        print(f"  Emissive: {spec.name}_emissive.png")
        bpy.data.images.remove(emissive)

        # Export mesh
        export_glb(car, meshes_dir / f"{spec.name}.glb")
        print(f"  Mesh: {spec.name}.glb")

        # Budget check
        if tri_count > 1200:
            print(f"  WARNING: Exceeds 1200 tri budget!")
        elif tri_count < 800:
            print(f"  Note: Under 800 tris, could add more detail")

    print("\n" + "=" * 60)
    print(f"  Generated {len(CARS)} enhanced cars")
    print("  - Curved aerodynamic bodies")
    print("  - Distinct silhouettes per type")
    print("  - Metallic paint with gradients")
    print("  - Strategic neon placement")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
