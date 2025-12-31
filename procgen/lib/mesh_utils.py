"""
Mesh utilities for procedural mesh generation.

Provides the MeshData class and mesh manipulation functions.
"""

import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class MeshData:
    """Raw mesh data container."""
    vertices: List[Tuple[float, float, float]]
    faces: List[Tuple[int, ...]]
    normals: Optional[List[Tuple[float, float, float]]] = None
    uvs: Optional[List[Tuple[float, float]]] = None
    name: str = ""

    @property
    def triangle_count(self) -> int:
        """Count triangles (quads count as 2)."""
        return sum(len(f) - 2 for f in self.faces)

    @property
    def vertex_count(self) -> int:
        """Count vertices."""
        return len(self.vertices)

    def copy(self) -> "MeshData":
        """Create a deep copy of the mesh."""
        return MeshData(
            vertices=list(self.vertices),
            faces=[tuple(f) for f in self.faces],
            normals=list(self.normals) if self.normals else None,
            uvs=list(self.uvs) if self.uvs else None,
            name=self.name,
        )


def merge_meshes(meshes: List[MeshData]) -> MeshData:
    """Merge multiple meshes into one."""
    if not meshes:
        return MeshData(vertices=[], faces=[])

    vertices = []
    faces = []
    offset = 0

    for mesh in meshes:
        vertices.extend(mesh.vertices)
        for face in mesh.faces:
            faces.append(tuple(v + offset for v in face))
        offset += len(mesh.vertices)

    return MeshData(vertices=vertices, faces=faces)


def translate(mesh: MeshData, offset: Tuple[float, float, float]) -> MeshData:
    """Translate mesh by offset."""
    ox, oy, oz = offset
    new_vertices = [(x + ox, y + oy, z + oz) for x, y, z in mesh.vertices]
    return MeshData(
        vertices=new_vertices,
        faces=mesh.faces,
        normals=mesh.normals,
        uvs=mesh.uvs,
        name=mesh.name,
    )


def scale(
    mesh: MeshData,
    factor: float | Tuple[float, float, float],
    center: Tuple[float, float, float] = (0, 0, 0)
) -> MeshData:
    """Scale mesh by factor around center point."""
    if isinstance(factor, (int, float)):
        sx, sy, sz = factor, factor, factor
    else:
        sx, sy, sz = factor

    cx, cy, cz = center
    new_vertices = [
        (cx + (x - cx) * sx, cy + (y - cy) * sy, cz + (z - cz) * sz)
        for x, y, z in mesh.vertices
    ]

    return MeshData(
        vertices=new_vertices,
        faces=mesh.faces,
        normals=mesh.normals,
        uvs=mesh.uvs,
        name=mesh.name,
    )


def rotate(
    mesh: MeshData,
    axis: str,
    angle_rad: float,
    center: Tuple[float, float, float] = (0, 0, 0)
) -> MeshData:
    """
    Rotate mesh around axis.

    Args:
        mesh: Mesh to rotate
        axis: "x", "y", or "z"
        angle_rad: Rotation angle in radians
        center: Rotation center point
    """
    cx, cy, cz = center
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    new_vertices = []
    for x, y, z in mesh.vertices:
        # Translate to origin
        x -= cx
        y -= cy
        z -= cz

        # Rotate
        if axis == "x":
            ny = y * cos_a - z * sin_a
            nz = y * sin_a + z * cos_a
            x, y, z = x, ny, nz
        elif axis == "y":
            nx = x * cos_a + z * sin_a
            nz = -x * sin_a + z * cos_a
            x, y, z = nx, y, nz
        elif axis == "z":
            nx = x * cos_a - y * sin_a
            ny = x * sin_a + y * cos_a
            x, y, z = nx, ny, z

        # Translate back
        new_vertices.append((x + cx, y + cy, z + cz))

    return MeshData(
        vertices=new_vertices,
        faces=mesh.faces,
        normals=None,  # Normals need recalculation after rotation
        uvs=mesh.uvs,
        name=mesh.name,
    )


def apply_noise(mesh: MeshData, amplitude: float = 0.1, seed: int = 42) -> MeshData:
    """Apply random noise displacement to vertices."""
    import random
    random.seed(seed)

    new_vertices = []
    for x, y, z in mesh.vertices:
        nx = x + (random.random() - 0.5) * amplitude
        ny = y + (random.random() - 0.5) * amplitude
        nz = z + (random.random() - 0.5) * amplitude
        new_vertices.append((nx, ny, nz))

    return MeshData(
        vertices=new_vertices,
        faces=mesh.faces,
        normals=None,  # Normals need recalculation
        uvs=mesh.uvs,
        name=mesh.name,
    )


def compute_normals(mesh: MeshData) -> MeshData:
    """Compute per-vertex normals from face normals."""
    # Initialize vertex normals to zero
    normals = [[0.0, 0.0, 0.0] for _ in mesh.vertices]

    # Accumulate face normals for each vertex
    for face in mesh.faces:
        if len(face) < 3:
            continue

        # Get vertices for this face
        v0 = mesh.vertices[face[0]]
        v1 = mesh.vertices[face[1]]
        v2 = mesh.vertices[face[2]]

        # Calculate face normal using cross product
        e1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
        e2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])

        nx = e1[1] * e2[2] - e1[2] * e2[1]
        ny = e1[2] * e2[0] - e1[0] * e2[2]
        nz = e1[0] * e2[1] - e1[1] * e2[0]

        # Add to all vertices in face
        for vi in face:
            normals[vi][0] += nx
            normals[vi][1] += ny
            normals[vi][2] += nz

    # Normalize
    result_normals = []
    for n in normals:
        length = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
        if length > 0:
            result_normals.append((n[0] / length, n[1] / length, n[2] / length))
        else:
            result_normals.append((0.0, 1.0, 0.0))

    return MeshData(
        vertices=mesh.vertices,
        faces=mesh.faces,
        normals=result_normals,
        uvs=mesh.uvs,
        name=mesh.name,
    )


def generate_uvs_box(mesh: MeshData) -> MeshData:
    """Generate box-projected UVs."""
    uvs = []

    for x, y, z in mesh.vertices:
        # Simple box projection - use XY for now
        u = (x + 1) / 2  # Assuming -1 to 1 range
        v = (y + 1) / 2
        uvs.append((u, v))

    return MeshData(
        vertices=mesh.vertices,
        faces=mesh.faces,
        normals=mesh.normals,
        uvs=uvs,
        name=mesh.name,
    )


def triangulate(mesh: MeshData) -> MeshData:
    """Convert all faces to triangles (fan triangulation)."""
    new_faces = []

    for face in mesh.faces:
        if len(face) <= 3:
            new_faces.append(face)
        else:
            # Fan triangulation from first vertex
            for i in range(1, len(face) - 1):
                new_faces.append((face[0], face[i], face[i + 1]))

    return MeshData(
        vertices=mesh.vertices,
        faces=new_faces,
        normals=mesh.normals,
        uvs=mesh.uvs,
        name=mesh.name,
    )


def flip_normals(mesh: MeshData) -> MeshData:
    """Flip face winding order (reverses normals)."""
    new_faces = [tuple(reversed(face)) for face in mesh.faces]

    new_normals = None
    if mesh.normals:
        new_normals = [(-n[0], -n[1], -n[2]) for n in mesh.normals]

    return MeshData(
        vertices=mesh.vertices,
        faces=new_faces,
        normals=new_normals,
        uvs=mesh.uvs,
        name=mesh.name,
    )


def get_bounds(mesh: MeshData) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
    """Get bounding box (min, max) corners."""
    if not mesh.vertices:
        return ((0, 0, 0), (0, 0, 0))

    xs = [v[0] for v in mesh.vertices]
    ys = [v[1] for v in mesh.vertices]
    zs = [v[2] for v in mesh.vertices]

    return (
        (min(xs), min(ys), min(zs)),
        (max(xs), max(ys), max(zs))
    )


def center_mesh(mesh: MeshData) -> MeshData:
    """Center mesh at origin."""
    min_b, max_b = get_bounds(mesh)
    center = (
        (min_b[0] + max_b[0]) / 2,
        (min_b[1] + max_b[1]) / 2,
        (min_b[2] + max_b[2]) / 2,
    )
    return translate(mesh, (-center[0], -center[1], -center[2]))
