"""
Track Segment Geometry Generator
Creates 3D meshes for NEON DRIFT track segments
"""

import bpy
import bmesh
import math
from mathutils import Vector


class TrackGeometry:
    """Handles track segment mesh generation"""

    @staticmethod
    def clear_scene():
        """Clear all objects from scene"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

    @staticmethod
    def create_road_plane(length, width, segments=8):
        """Create a basic road surface with subdivisions"""
        bm = bmesh.new()

        # Create grid of vertices
        for i in range(segments + 1):
            for j in range(2):  # Left and right edge
                x = (j - 0.5) * width
                y = (i / segments) * length - length / 2
                bm.verts.new((x, y, 0))

        bm.verts.ensure_lookup_table()

        # Create faces
        for i in range(segments):
            v1 = i * 2
            v2 = i * 2 + 1
            v3 = (i + 1) * 2 + 1
            v4 = (i + 1) * 2
            bm.faces.new([bm.verts[v1], bm.verts[v2], bm.verts[v3], bm.verts[v4]])

        # Create mesh
        mesh = bpy.data.meshes.new("road")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("road", mesh)
        bpy.context.collection.objects.link(obj)

        return obj

    @staticmethod
    def add_barriers(road_obj, width, length, height=0.5):
        """Add barrier geometry on both sides"""
        bm = bmesh.new()
        bm.from_mesh(road_obj.data)

        barrier_thickness = 0.1
        offset = width / 2 + barrier_thickness

        for side in [-1, 1]:  # Left and right
            x = side * offset

            # Create barrier strip
            segments = 8
            for i in range(segments + 1):
                y = (i / segments) * length - length / 2

                # Bottom vertices
                v1 = bm.verts.new((x - side * barrier_thickness/2, y, 0))
                v2 = bm.verts.new((x + side * barrier_thickness/2, y, 0))

                # Top vertices
                v3 = bm.verts.new((x + side * barrier_thickness/2, y, height))
                v4 = bm.verts.new((x - side * barrier_thickness/2, y, height))

                if i > 0:
                    # Create faces connecting to previous segment
                    # Outer face
                    bm.faces.new([
                        bm.verts[-8], bm.verts[-7],
                        bm.verts[-3], bm.verts[-4]
                    ])
                    # Top face
                    bm.faces.new([
                        bm.verts[-7], bm.verts[-6],
                        bm.verts[-2], bm.verts[-3]
                    ])
                    # Inner face
                    bm.faces.new([
                        bm.verts[-6], bm.verts[-5],
                        bm.verts[-1], bm.verts[-2]
                    ])

        bm.to_mesh(road_obj.data)
        bm.free()

    @staticmethod
    def generate_straight(length=20.0, width=4.0):
        """Generate straight track segment"""
        TrackGeometry.clear_scene()

        road = TrackGeometry.create_road_plane(length, width)
        TrackGeometry.add_barriers(road, width, length)

        road.name = "track_straight"
        return road

    @staticmethod
    def generate_curve(length=15.0, width=4.0, angle=45, direction='left'):
        """Generate curved track segment"""
        TrackGeometry.clear_scene()

        # Create curved road using circle formula
        radius = length / (angle * math.pi / 180)
        segments = 16

        bm = bmesh.new()

        for i in range(segments + 1):
            a = (angle * i / segments) * math.pi / 180
            x_center = radius * math.sin(a)
            z = radius * (1 - math.cos(a))

            if direction == 'right':
                x_center *= -1

            # Left and right edges
            for j in range(2):
                x_offset = (j - 0.5) * width
                x = x_center + x_offset
                bm.verts.new((x, z, 0))

        bm.verts.ensure_lookup_table()

        # Create faces
        for i in range(segments):
            v1 = i * 2
            v2 = i * 2 + 1
            v3 = (i + 1) * 2 + 1
            v4 = (i + 1) * 2
            bm.faces.new([bm.verts[v1], bm.verts[v2], bm.verts[v3], bm.verts[v4]])

        # Create mesh
        mesh = bpy.data.meshes.new(f"track_curve_{direction}")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new(f"track_curve_{direction}", mesh)
        bpy.context.collection.objects.link(obj)

        # Add barriers
        TrackGeometry.add_barriers(obj, width, length)

        return obj

    @staticmethod
    def generate_tunnel(length=25.0, radius=3.0):
        """Generate tunnel segment"""
        TrackGeometry.clear_scene()

        segments = 16
        rings = 8

        bm = bmesh.new()

        for ring_idx in range(rings + 1):
            z = (ring_idx / rings) * length - length / 2

            for i in range(segments):
                angle = (i / segments) * 2 * math.pi
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)

                bm.verts.new((x, z, y))

        bm.verts.ensure_lookup_table()

        # Create faces
        for ring in range(rings):
            for i in range(segments):
                v1 = ring * segments + i
                v2 = ring * segments + (i + 1) % segments
                v3 = (ring + 1) * segments + (i + 1) % segments
                v4 = (ring + 1) * segments + i

                bm.faces.new([bm.verts[v1], bm.verts[v2], bm.verts[v3], bm.verts[v4]])

        mesh = bpy.data.meshes.new("track_tunnel")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("track_tunnel", mesh)
        bpy.context.collection.objects.link(obj)

        return obj

    @staticmethod
    def generate_jump(length=15.0, width=4.0, height=2.0):
        """Generate jump ramp segment"""
        TrackGeometry.clear_scene()

        road = TrackGeometry.create_road_plane(length, width, segments=16)

        # Deform into ramp
        bpy.context.view_layer.objects.active = road
        bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(road.data)

        for v in bm.verts:
            # Ramp up in first half
            if v.co.y < 0:
                progress = (v.co.y + length/2) / (length/2)
                v.co.z = progress * height

        bmesh.update_edit_mesh(road.data)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Add railings
        TrackGeometry.add_barriers(road, width, length, height=1.0)

        road.name = "track_jump"
        return road

    @staticmethod
    def generate_checkpoint(length=12.0, width=4.0):
        """Generate checkpoint/finish line segment"""
        TrackGeometry.clear_scene()

        road = TrackGeometry.create_road_plane(length, width)
        TrackGeometry.add_barriers(road, width, length)

        # Add timing gate
        bm = bmesh.new()
        bm.from_mesh(road.data)

        gate_height = 3.0
        gate_thickness = 0.2
        gate_y = length / 2 - 2.0

        # Left post
        for x_sign in [-1, 1]:
            x = x_sign * (width/2 + 0.5)

            v1 = bm.verts.new((x - gate_thickness/2, gate_y - gate_thickness/2, 0))
            v2 = bm.verts.new((x + gate_thickness/2, gate_y - gate_thickness/2, 0))
            v3 = bm.verts.new((x + gate_thickness/2, gate_y + gate_thickness/2, 0))
            v4 = bm.verts.new((x - gate_thickness/2, gate_y + gate_thickness/2, 0))

            v5 = bm.verts.new((x - gate_thickness/2, gate_y - gate_thickness/2, gate_height))
            v6 = bm.verts.new((x + gate_thickness/2, gate_y - gate_thickness/2, gate_height))
            v7 = bm.verts.new((x + gate_thickness/2, gate_y + gate_thickness/2, gate_height))
            v8 = bm.verts.new((x - gate_thickness/2, gate_y + gate_thickness/2, gate_height))

            # Post faces
            bm.faces.new([v1, v2, v6, v5])
            bm.faces.new([v2, v3, v7, v6])
            bm.faces.new([v3, v4, v8, v7])
            bm.faces.new([v4, v1, v5, v8])

        bm.to_mesh(road.data)
        bm.free()

        road.name = "track_checkpoint"
        return road
