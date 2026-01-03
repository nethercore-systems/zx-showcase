"""Prism Survivors - Arena Generator.

Generates the arena floor mesh:
- Hexagonal tiled floor
- Crystal border pillars
- Subtle glow patterns

~500-1000 triangles for arena.
Requires Blender to run.
"""

import math
from pathlib import Path

try:
    import bpy
    import bmesh
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False
    bpy = None
    bmesh = None


if BLENDER_AVAILABLE:

    def clear_scene():
        """Remove all objects from scene."""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)

    def create_hexagon(radius: float, height: float):
        """Create hexagonal prism."""
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, vertices=6)
        return bpy.context.active_object

    def build_arena_floor():
        """Build the arena floor mesh."""
        parts = []

        # Main floor (large hexagon)
        floor = create_hexagon(radius=10.0, height=0.2)
        floor.location.z = -0.1
        parts.append(floor)

        # Border ring
        bpy.ops.mesh.primitive_torus_add(major_radius=10.5, minor_radius=0.3,
                                          major_segments=6, minor_segments=8)
        border = bpy.context.active_object
        border.location.z = 0.1
        parts.append(border)

        # Corner pillars (6)
        for i in range(6):
            angle = i * (math.pi / 3) + (math.pi / 6)
            x = math.cos(angle) * 10.0
            y = math.sin(angle) * 10.0

            pillar = create_hexagon(radius=0.4, height=1.5)
            pillar.location = (x, y, 0.75)
            parts.append(pillar)

            # Crystal top
            bpy.ops.mesh.primitive_cone_add(radius1=0.35, radius2=0.05, depth=0.8, vertices=6)
            crystal = bpy.context.active_object
            crystal.location = (x, y, 1.9)
            parts.append(crystal)

        # Center glow pattern (decorative)
        bpy.ops.mesh.primitive_circle_add(radius=2.0, vertices=6, fill_type='NGON')
        center = bpy.context.active_object
        center.location.z = 0.02
        parts.append(center)

        # Join all parts
        bpy.ops.object.select_all(action='DESELECT')
        for part in parts:
            part.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]
        bpy.ops.object.join()

        arena = bpy.context.active_object
        arena.name = "arena_floor"

        # UV unwrap
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.shade_smooth()

        return arena

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
        )

    def generate_arena(meshes_dir: Path, textures_dir: Path = None) -> int:
        """Generate the arena floor mesh."""
        clear_scene()

        arena = build_arena_floor()

        tri_count = count_triangles(arena)
        status = "OK" if tri_count <= 1500 else "WARN"
        print(f"  arena_floor: {tri_count} tris [{status}]")

        export_glb(arena, meshes_dir / "arena_floor.glb")

        return 1


if not BLENDER_AVAILABLE:
    def generate_arena(meshes_dir: Path, textures_dir: Path = None) -> int:
        """Stub when Blender not available."""
        print("Warning: Blender not available, skipping arena generation")
        return 0


__all__ = [
    "generate_arena",
    "BLENDER_AVAILABLE",
]


if __name__ == "__main__" and BLENDER_AVAILABLE:
    script_dir = Path(__file__).parent
    meshes_dir = script_dir.parent.parent / "generated" / "meshes"

    print("\n" + "=" * 60)
    print("  PRISM SURVIVORS - Arena Generator")
    print("=" * 60)

    count = generate_arena(meshes_dir)

    print(f"\nGenerated {count} arena")
    print("=" * 60)
