"""Generate submersible mesh for Lumina Depths.

Design specs:
- Industrial but not military
- Glass canopy for visibility
- Warm interior lighting (amber/yellow)
- Orange accent panels
- Visible propulsion system

Output: ~1200 triangles
"""

from pathlib import Path

from procgen.lib.mesh_primitives import (
    generate_sphere, generate_cylinder, generate_cone,
    merge_meshes, write_obj
)


def generate_submersible_mesh():
    """Generate complete submersible mesh."""
    meshes = []

    # Main hull (elongated cylinder)
    hull_verts, hull_faces = generate_cylinder(0, 0, 0, 0.4, 2.0, segments=20)
    meshes.append((hull_verts, hull_faces))

    # Glass canopy (sphere at front)
    canopy_verts, canopy_faces = generate_sphere(0, 0, 1.2, 0.5, lat_segments=10, lon_segments=16)
    meshes.append((canopy_verts, canopy_faces))

    # Rear thruster housing (cylinder)
    thruster_main = generate_cylinder(0, 0, -1.3, 0.3, 0.5, segments=12)
    meshes.append(thruster_main)

    # Thruster nozzle (cone)
    nozzle = generate_cone(0, 0, -1.55, 0.25, -0.3, segments=12)
    meshes.append(nozzle)

    # Left stabilizer fin
    left_fin = generate_cylinder(-0.6, 0, -0.5, 0.08, 0.8, segments=8)
    meshes.append(left_fin)

    # Right stabilizer fin
    right_fin = generate_cylinder(0.6, 0, -0.5, 0.08, 0.8, segments=8)
    meshes.append(right_fin)

    # Top dorsal fin
    dorsal = generate_cylinder(0, 0.5, -0.3, 0.06, 0.6, segments=8)
    meshes.append(dorsal)

    # Bottom skid
    skid = generate_cylinder(0, -0.45, 0, 0.1, 1.5, segments=8)
    meshes.append(skid)

    # Left thruster pod
    left_pod = generate_sphere(-0.55, -0.2, -0.8, 0.15, lat_segments=8, lon_segments=10)
    meshes.append(left_pod)

    # Right thruster pod
    right_pod = generate_sphere(0.55, -0.2, -0.8, 0.15, lat_segments=8, lon_segments=10)
    meshes.append(right_pod)

    # Headlight housing (front)
    headlight = generate_cylinder(0, -0.35, 0.9, 0.12, 0.15, segments=10)
    meshes.append(headlight)

    return merge_meshes(meshes)


def generate_submersible(output_dir: Path) -> None:
    """Generate and save submersible mesh."""
    print("Generating submersible mesh...")

    vertices, faces = generate_submersible_mesh()
    output_path = output_dir / "submersible.obj"

    write_obj(
        str(output_path),
        vertices, faces,
        name="Submersible",
        comment="Lumina Depths - Player Vehicle"
    )

    print(f"  -> {output_path.name}")
    print(f"     Vertices: {len(vertices)}, Faces: {len(faces)}")
