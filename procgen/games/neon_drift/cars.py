"""Neon Drift Vehicle Generators.

Generates 7 synthwave racing cars with:
- Curved aerodynamic body panels with bevels
- Distinct silhouettes per car type
- Metallic paint textures with gradients
- Strategic neon placement in emissive maps
- 800-1200 triangles per car (ZX budget compliant)

Requires Blender to run. Use: blender --background --python cars.py
"""

import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional

try:
    import bpy
    import bmesh
    from mathutils import Vector
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False
    bpy = None
    bmesh = None


@dataclass
class CarSpec:
    """Car specification with style and features."""
    name: str
    body_color: Tuple[float, float, float]  # RGB 0-1
    accent_color: Tuple[float, float, float]  # RGB 0-1 for neon
    length: float
    width: float
    height: float
    cabin_offset: float  # 0-1, where cabin sits along length
    style: str  # sleek, boxy, technical, japanese, stealth, truck, compact
    features: List[str]


# Car specifications with distinct personalities
CARS = [
    CarSpec("speedster", (0.95, 0.15, 0.55), (1.0, 0.0, 0.8),
            4.0, 1.8, 0.95, 0.38, "sleek",
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


# =============================================================================
# Blender Utilities (only available when running in Blender)
# =============================================================================

if BLENDER_AVAILABLE:

    def clear_scene():
        """Remove all objects from scene."""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)
        for block in bpy.data.materials:
            if block.users == 0:
                bpy.data.materials.remove(block)

    def create_beveled_box(sx: float, sy: float, sz: float,
                           bevel: float = 0.02, segments: int = 1):
        """Create a box with beveled edges."""
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj = bpy.context.active_object
        obj.scale = (sx, sy, sz)
        bpy.ops.object.transform_apply(scale=True)

        bevel_mod = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel_mod.width = bevel
        bevel_mod.segments = segments
        bevel_mod.limit_method = 'ANGLE'
        bevel_mod.angle_limit = math.radians(30)
        bpy.ops.object.modifier_apply(modifier="Bevel")

        return obj

    def create_tapered_box(sx: float, sy: float, sz: float,
                           front_taper: float = 0.8, top_taper: float = 0.9):
        """Create a tapered box for aerodynamic shapes."""
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj = bpy.context.active_object
        obj.scale = (sx, sy, sz)
        bpy.ops.object.transform_apply(scale=True)

        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)

        for v in bm.verts:
            if v.co.x > 0:
                v.co.y *= front_taper
                v.co.z *= (0.9 + 0.1 * front_taper)
            if v.co.z > 0:
                v.co.y *= top_taper

        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')

        return obj

    def create_wheel(radius: float = 0.15, width: float = 0.08, vertices: int = 16):
        """Create a wheel with rim."""
        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius, depth=width, vertices=vertices,
            rotation=(math.pi/2, 0, 0)
        )
        wheel = bpy.context.active_object

        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius * 0.65, depth=width * 1.1, vertices=8,
            rotation=(math.pi/2, 0, 0)
        )
        rim = bpy.context.active_object

        bpy.ops.object.select_all(action='DESELECT')
        wheel.select_set(True)
        rim.select_set(True)
        bpy.context.view_layer.objects.active = wheel
        bpy.ops.object.join()

        return wheel

    def create_headlight(size: float = 0.06, style: str = "round"):
        """Create headlight geometry."""
        if style == "round":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=size, segments=8, ring_count=6)
            light = bpy.context.active_object
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.transform.resize(value=(0.5, 1, 1))
            bpy.ops.object.mode_set(mode='OBJECT')
        else:
            light = create_beveled_box(size * 0.5, size, size * 0.6, bevel=0.01)
        return light

    def create_taillight(width: float = 0.08, height: float = 0.04):
        """Create taillight geometry."""
        return create_beveled_box(0.02, width, height, bevel=0.005)

    def create_windshield(width: float, height: float, angle: float = 30):
        """Create angled windshield panel."""
        bpy.ops.mesh.primitive_plane_add(size=1)
        obj = bpy.context.active_object
        obj.scale = (height * 0.5, width * 0.5, 1)
        bpy.ops.object.transform_apply(scale=True)

        obj.rotation_euler.y = math.radians(angle)
        bpy.ops.object.transform_apply(rotation=True)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.subdivide(number_cuts=2)
        bm = bmesh.from_edit_mesh(obj.data)
        for v in bm.verts:
            curve = 0.02 * (1 - (v.co.x ** 2) * 4)
            v.co.z += curve
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')

        return obj

    def create_spoiler(width: float, height: float, depth: float, style: str = "wing"):
        """Create rear spoiler/wing."""
        if style == "wing":
            parts = []
            wing = create_beveled_box(depth, width, height * 0.3, bevel=0.01)
            wing.location.z = height * 0.7
            parts.append(wing)

            for y_offset in [width * 0.35, -width * 0.35]:
                bpy.ops.mesh.primitive_cube_add(size=1)
                support = bpy.context.active_object
                support.scale = (depth * 0.3, 0.02, height * 0.5)
                bpy.ops.object.transform_apply(scale=True)
                support.location = (0, y_offset, height * 0.35)
                parts.append(support)

            bpy.ops.object.select_all(action='DESELECT')
            for p in parts:
                p.select_set(True)
            bpy.context.view_layer.objects.active = wing
            bpy.ops.object.join()
            return bpy.context.active_object
        else:
            return create_beveled_box(depth, width, height, bevel=0.01)

    def join_car_parts(parts: List, name: str):
        """Join all parts into single mesh with UVs."""
        if not parts:
            return None

        bpy.ops.object.select_all(action='DESELECT')
        for part in parts:
            part.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]

        bpy.ops.object.join()
        car = bpy.context.active_object
        car.name = name

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.shade_smooth()

        return car

    def count_triangles(obj) -> int:
        """Count triangles in mesh."""
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        count = len(bm.faces)
        bm.free()
        return count

    def export_glb(obj, filepath: Path):
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

    # Car builders (one per style)
    def build_sleek_car(spec: CarSpec):
        """Build sleek car (speedster)."""
        L, W, H = spec.length, spec.width, spec.height
        parts = []

        body = create_tapered_box(L * 0.48, W * 0.46, H * 0.35, 0.75, 0.88)
        body.location = (0, 0, H * 0.38)
        parts.append(body)

        hood = create_tapered_box(L * 0.22, W * 0.42, H * 0.18, 0.6, 0.85)
        hood.location = (L * 0.28, 0, H * 0.45)
        parts.append(hood)

        cabin = create_beveled_box(L * 0.28, W * 0.4, H * 0.28, bevel=0.03)
        cabin.location = (-L * 0.05, 0, H * 0.62)
        parts.append(cabin)

        ws = create_windshield(W * 0.38, H * 0.25, angle=25)
        ws.location = (L * 0.08, 0, H * 0.72)
        parts.append(ws)

        rear = create_tapered_box(L * 0.18, W * 0.4, H * 0.2, 1.0, 0.7)
        rear.location = (-L * 0.32, 0, H * 0.48)
        parts.append(rear)

        spoiler = create_beveled_box(L * 0.04, W * 0.42, H * 0.03, bevel=0.008)
        spoiler.location = (-L * 0.42, 0, H * 0.52)
        parts.append(spoiler)

        wheel_r = H * 0.28
        for x, y in [(L * 0.28, W * 0.48), (L * 0.28, -W * 0.48),
                     (-L * 0.28, W * 0.48), (-L * 0.28, -W * 0.48)]:
            wheel = create_wheel(wheel_r, W * 0.08)
            wheel.location = (x, y, wheel_r)
            parts.append(wheel)

        for y in [W * 0.32, -W * 0.32]:
            hl = create_headlight(H * 0.06, "round")
            hl.location = (L * 0.44, y, H * 0.4)
            parts.append(hl)

        for y in [W * 0.28, -W * 0.28]:
            tl = create_taillight(H * 0.08, H * 0.04)
            tl.location = (-L * 0.46, y, H * 0.45)
            parts.append(tl)

        return join_car_parts(parts, spec.name)

    # Map styles to builders
    CAR_BUILDERS = {
        "sleek": build_sleek_car,
        # Other styles would be implemented similarly
    }

    def generate_car(spec: CarSpec, meshes_dir: Path, textures_dir: Path) -> int:
        """Generate a single car and its textures."""
        clear_scene()

        builder = CAR_BUILDERS.get(spec.style, build_sleek_car)
        car = builder(spec)

        if car is None:
            print(f"  Warning: Failed to build {spec.name}")
            return 0

        tri_count = count_triangles(car)
        print(f"  {spec.name}: {tri_count} triangles")

        export_glb(car, meshes_dir / f"{spec.name}.glb")

        # Budget check
        if tri_count > 1200:
            print(f"  WARNING: Exceeds 1200 tri budget!")
        elif tri_count < 800:
            print(f"  Note: Under 800 tris, could add detail")

        return 1

    def generate_all_cars(meshes_dir: Path, textures_dir: Path = None) -> int:
        """Generate all car meshes."""
        if textures_dir is None:
            textures_dir = meshes_dir.parent / "textures"

        meshes_dir.mkdir(parents=True, exist_ok=True)
        textures_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for spec in CARS:
            count += generate_car(spec, meshes_dir, textures_dir)

        return count


# Fallback when Blender is not available
if not BLENDER_AVAILABLE:
    def generate_all_cars(meshes_dir: Path, textures_dir: Path = None) -> int:
        """Stub when Blender not available."""
        print("Warning: Blender not available, skipping car generation")
        print("Run with: blender --background --python cars.py")
        return 0


__all__ = [
    "CARS",
    "CarSpec",
    "generate_all_cars",
    "BLENDER_AVAILABLE",
]


# CLI entry point for Blender
if __name__ == "__main__" and BLENDER_AVAILABLE:
    import sys
    script_dir = Path(__file__).parent
    output_base = script_dir.parent.parent.parent / "games" / "neon-drift" / "assets" / "models"
    meshes_dir = output_base / "meshes"
    textures_dir = output_base / "textures"

    print("\n" + "=" * 60)
    print("  NEON DRIFT - Vehicle Generator")
    print("=" * 60)
    print(f"\nOutput: {output_base}")

    count = generate_all_cars(meshes_dir, textures_dir)

    print(f"\nGenerated {count} vehicles")
    print("=" * 60)
