"""
Prop Geometry Generator
Creates 3D meshes for NEON DRIFT props (barriers, boost pads, etc.)
"""

import bpy
import bmesh
import math


class PropGeometry:
    """Handles prop mesh generation"""

    @staticmethod
    def clear_scene():
        """Clear all objects from scene"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

    @staticmethod
    def generate_barrier(width=2.0, height=0.5, thickness=0.1):
        """Generate barrier prop"""
        PropGeometry.clear_scene()

        bm = bmesh.new()

        # Main body
        v1 = bm.verts.new((-width/2, -thickness/2, 0))
        v2 = bm.verts.new((width/2, -thickness/2, 0))
        v3 = bm.verts.new((width/2, thickness/2, 0))
        v4 = bm.verts.new((-width/2, thickness/2, 0))

        v5 = bm.verts.new((-width/2, -thickness/2, height))
        v6 = bm.verts.new((width/2, -thickness/2, height))
        v7 = bm.verts.new((width/2, thickness/2, height))
        v8 = bm.verts.new((-width/2, thickness/2, height))

        # Faces
        bm.faces.new([v1, v2, v6, v5])  # Front
        bm.faces.new([v2, v3, v7, v6])  # Right
        bm.faces.new([v3, v4, v8, v7])  # Back
        bm.faces.new([v4, v1, v5, v8])  # Left
        bm.faces.new([v5, v6, v7, v8])  # Top
        bm.faces.new([v1, v2, v3, v4])  # Bottom

        mesh = bpy.data.meshes.new("prop_barrier")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("prop_barrier", mesh)
        bpy.context.collection.objects.link(obj)

        return obj

    @staticmethod
    def generate_boost_pad(width=2.0, length=1.5, height=0.05):
        """Generate boost pad prop"""
        PropGeometry.clear_scene()

        bm = bmesh.new()

        # Base pad
        v1 = bm.verts.new((-width/2, -length/2, 0))
        v2 = bm.verts.new((width/2, -length/2, 0))
        v3 = bm.verts.new((width/2, length/2, 0))
        v4 = bm.verts.new((-width/2, length/2, 0))

        v5 = bm.verts.new((-width/2, -length/2, height))
        v6 = bm.verts.new((width/2, -length/2, height))
        v7 = bm.verts.new((width/2, length/2, height))
        v8 = bm.verts.new((-width/2, length/2, height))

        bm.faces.new([v1, v2, v6, v5])
        bm.faces.new([v2, v3, v7, v6])
        bm.faces.new([v3, v4, v8, v7])
        bm.faces.new([v4, v1, v5, v8])
        bm.faces.new([v5, v6, v7, v8])

        mesh = bpy.data.meshes.new("prop_boost_pad")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("prop_boost_pad", mesh)
        bpy.context.collection.objects.link(obj)

        return obj

    @staticmethod
    def generate_billboard(width=3.0, height=2.0, thickness=0.1):
        """Generate billboard prop"""
        PropGeometry.clear_scene()

        bm = bmesh.new()

        # Screen panel
        v1 = bm.verts.new((-width/2, -thickness/2, 0))
        v2 = bm.verts.new((width/2, -thickness/2, 0))
        v3 = bm.verts.new((width/2, -thickness/2, height))
        v4 = bm.verts.new((-width/2, -thickness/2, height))

        v5 = bm.verts.new((-width/2, thickness/2, 0))
        v6 = bm.verts.new((width/2, thickness/2, 0))
        v7 = bm.verts.new((width/2, thickness/2, height))
        v8 = bm.verts.new((-width/2, thickness/2, height))

        bm.faces.new([v1, v2, v3, v4])  # Front (screen)
        bm.faces.new([v5, v6, v7, v8])  # Back
        bm.faces.new([v1, v2, v6, v5])  # Bottom
        bm.faces.new([v4, v3, v7, v8])  # Top
        bm.faces.new([v1, v4, v8, v5])  # Left
        bm.faces.new([v2, v3, v7, v6])  # Right

        # Support pole
        pole_radius = 0.1
        pole_height = height * 1.5
        segments = 8

        for i in range(segments):
            angle1 = (i / segments) * 2 * math.pi
            angle2 = ((i + 1) / segments) * 2 * math.pi

            x1 = pole_radius * math.cos(angle1)
            y1 = pole_radius * math.sin(angle1)
            x2 = pole_radius * math.cos(angle2)
            y2 = pole_radius * math.sin(angle2)

            v1 = bm.verts.new((x1, y1, -pole_height))
            v2 = bm.verts.new((x2, y2, -pole_height))
            v3 = bm.verts.new((x2, y2, 0))
            v4 = bm.verts.new((x1, y1, 0))

            bm.faces.new([v1, v2, v3, v4])

        mesh = bpy.data.meshes.new("prop_billboard")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("prop_billboard", mesh)
        bpy.context.collection.objects.link(obj)

        return obj

    @staticmethod
    def generate_building(width=4.0, depth=4.0, height=6.0):
        """Generate building prop"""
        PropGeometry.clear_scene()

        bm = bmesh.new()

        # Main building body
        v1 = bm.verts.new((-width/2, -depth/2, 0))
        v2 = bm.verts.new((width/2, -depth/2, 0))
        v3 = bm.verts.new((width/2, depth/2, 0))
        v4 = bm.verts.new((-width/2, depth/2, 0))

        v5 = bm.verts.new((-width/2, -depth/2, height))
        v6 = bm.verts.new((width/2, -depth/2, height))
        v7 = bm.verts.new((width/2, depth/2, height))
        v8 = bm.verts.new((-width/2, depth/2, height))

        bm.faces.new([v1, v2, v6, v5])  # Front
        bm.faces.new([v2, v3, v7, v6])  # Right
        bm.faces.new([v3, v4, v8, v7])  # Back
        bm.faces.new([v4, v1, v5, v8])  # Left
        bm.faces.new([v5, v6, v7, v8])  # Top

        mesh = bpy.data.meshes.new("prop_building")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("prop_building", mesh)
        bpy.context.collection.objects.link(obj)

        return obj

    @staticmethod
    def generate_crystal(size=0.8, height=1.5):
        """Generate crystal formation prop"""
        PropGeometry.clear_scene()

        bm = bmesh.new()

        # Create faceted crystal
        segments = 6
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = size * math.cos(angle)
            y = size * math.sin(angle)

            # Bottom
            bm.verts.new((x, y, 0))

        # Middle (wider)
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = size * 1.2 * math.cos(angle)
            y = size * 1.2 * math.sin(angle)

            bm.verts.new((x, y, height * 0.5))

        # Top point
        top_vert = bm.verts.new((0, 0, height))

        bm.verts.ensure_lookup_table()

        # Create faces
        for i in range(segments):
            # Bottom to middle
            v1 = i
            v2 = (i + 1) % segments
            v3 = segments + (i + 1) % segments
            v4 = segments + i

            bm.faces.new([bm.verts[v1], bm.verts[v2], bm.verts[v3], bm.verts[v4]])

            # Middle to top
            v1 = segments + i
            v2 = segments + (i + 1) % segments

            bm.faces.new([bm.verts[v1], bm.verts[v2], top_vert])

        mesh = bpy.data.meshes.new("prop_crystal_formation")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("prop_crystal_formation", mesh)
        bpy.context.collection.objects.link(obj)

        return obj
