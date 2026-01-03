"""Prism Survivors - Projectile Generators.

Generates 3 projectile types:
- Frost Shard: Icy crystal spike
- Void Orb: Dark energy sphere
- Lightning Bolt: Electrical streak

~50 triangles per projectile (many on screen).
Requires Blender to run.
"""

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

try:
    import bpy
    import bmesh
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False
    bpy = None
    bmesh = None


@dataclass
class ProjectileSpec:
    """Projectile specification."""
    name: str
    color: Tuple[float, float, float]
    glow_color: Tuple[float, float, float]
    shape: str  # shard, orb, bolt
    length: float
    width: float


PROJECTILES = [
    ProjectileSpec("frost_shard", (0.6, 0.85, 0.95), (0.8, 0.95, 1.0),
                   "shard", 0.2, 0.04),
    ProjectileSpec("void_orb", (0.2, 0.1, 0.3), (0.5, 0.2, 0.6),
                   "orb", 0.12, 0.12),
    ProjectileSpec("lightning_bolt", (1.0, 0.95, 0.5), (1.0, 1.0, 0.8),
                   "bolt", 0.25, 0.03),
]


if BLENDER_AVAILABLE:

    def clear_scene():
        """Remove all objects from scene."""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)

    def build_shard(spec: ProjectileSpec):
        """Build ice shard projectile."""
        # Elongated diamond shape
        bpy.ops.mesh.primitive_cone_add(radius1=spec.width, radius2=0,
                                         depth=spec.length * 0.7, vertices=4)
        front = bpy.context.active_object
        front.location.z = spec.length * 0.15

        bpy.ops.mesh.primitive_cone_add(radius1=spec.width, radius2=0,
                                         depth=spec.length * 0.3, vertices=4)
        back = bpy.context.active_object
        back.rotation_euler.x = math.pi
        back.location.z = -spec.length * 0.2
        bpy.ops.object.transform_apply(rotation=True)

        # Join
        bpy.ops.object.select_all(action='DESELECT')
        front.select_set(True)
        back.select_set(True)
        bpy.context.view_layer.objects.active = front
        bpy.ops.object.join()

        shard = bpy.context.active_object
        shard.name = spec.name

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66)
        bpy.ops.object.mode_set(mode='OBJECT')

        return shard

    def build_projectile_orb(spec: ProjectileSpec):
        """Build energy orb projectile."""
        bpy.ops.mesh.primitive_uv_sphere_add(radius=spec.width, segments=8, ring_count=6)
        orb = bpy.context.active_object
        orb.name = spec.name

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.shade_smooth()

        return orb

    def build_bolt(spec: ProjectileSpec):
        """Build lightning bolt projectile."""
        # Simple elongated shape with zigzag
        bpy.ops.mesh.primitive_cylinder_add(radius=spec.width, depth=spec.length, vertices=6)
        bolt = bpy.context.active_object
        bolt.name = spec.name

        # Deform slightly for lightning effect
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(bolt.data)
        for v in bm.verts:
            if abs(v.co.z) > spec.length * 0.2:
                v.co.x += 0.01 * math.sin(v.co.z * 20)
                v.co.y += 0.01 * math.cos(v.co.z * 20)
        bmesh.update_edit_mesh(bolt.data)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66)
        bpy.ops.object.mode_set(mode='OBJECT')

        return bolt

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

    def generate_projectile(spec: ProjectileSpec, meshes_dir: Path, textures_dir: Path) -> int:
        """Generate a single projectile."""
        clear_scene()

        builders = {
            "shard": build_shard,
            "orb": build_projectile_orb,
            "bolt": build_bolt,
        }

        builder = builders.get(spec.shape, build_shard)
        proj = builder(spec)

        tri_count = count_triangles(proj)
        status = "OK" if tri_count <= 100 else "WARN"
        print(f"  {spec.name}: {tri_count} tris [{status}]")

        export_glb(proj, meshes_dir / f"{spec.name}.glb")

        return 1

    def generate_all_projectiles(meshes_dir: Path, textures_dir: Path = None) -> int:
        """Generate all projectile meshes."""
        if textures_dir is None:
            textures_dir = meshes_dir.parent / "textures"

        meshes_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for spec in PROJECTILES:
            count += generate_projectile(spec, meshes_dir, textures_dir)

        return count


if not BLENDER_AVAILABLE:
    def generate_all_projectiles(meshes_dir: Path, textures_dir: Path = None) -> int:
        """Stub when Blender not available."""
        print("Warning: Blender not available, skipping projectile generation")
        return 0


__all__ = [
    "PROJECTILES",
    "ProjectileSpec",
    "generate_all_projectiles",
    "BLENDER_AVAILABLE",
]


if __name__ == "__main__" and BLENDER_AVAILABLE:
    script_dir = Path(__file__).parent
    meshes_dir = script_dir.parent.parent / "generated" / "meshes"
    # meshes_dir set above

    print("\n" + "=" * 60)
    print("  PRISM SURVIVORS - Projectile Generator")
    print("=" * 60)

    count = generate_all_projectiles(meshes_dir)

    print(f"\nGenerated {count} projectiles")
    print("=" * 60)
