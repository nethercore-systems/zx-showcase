"""
Car Geometry Generator
Creates 3D meshes for NEON DRIFT vehicles with enhanced detail
"""

import bpy
import bmesh
import math
from mathutils import Vector


class CarGeometry:
    """Handles car mesh generation with enhanced quality"""

    @staticmethod
    def clear_scene():
        """Clear all mesh objects from scene"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

    @staticmethod
    def create_wheel_with_spokes(radius=0.3, width=0.15, spokes=5):
        """Create a wheel with detailed spoke pattern"""
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=24,
            radius=radius,
            depth=width,
            location=(0, 0, 0),
            rotation=(math.pi/2, 0, 0)
        )
        wheel = bpy.context.active_object

        # Add bevel for tire edge
        bevel_mod = wheel.modifiers.new(name="Bevel", type='BEVEL')
        bevel_mod.width = 0.02
        bevel_mod.segments = 1
        bevel_mod.limit_method = 'ANGLE'
        bevel_mod.angle_limit = math.radians(30)

        # Create spoke geometry
        bm = bmesh.new()
        bm.from_mesh(wheel.data)

        # Add hub cap (center circle)
        hub_radius = radius * 0.3
        hub_verts = []
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            x = hub_radius * math.cos(angle)
            z = hub_radius * math.sin(angle)
            v = bm.verts.new((x, 0, z))
            hub_verts.append(v)

        # Create spokes radiating from hub
        outer_radius = radius * 0.85
        for i in range(spokes):
            angle = (i / spokes) * 2 * math.pi

            # Inner spoke point (at hub)
            inner_x = hub_radius * math.cos(angle)
            inner_z = hub_radius * math.sin(angle)

            # Outer spoke point
            outer_x = outer_radius * math.cos(angle)
            outer_z = outer_radius * math.sin(angle)

            # Create spoke quad (narrow strip)
            spoke_width = 0.04

            v1 = bm.verts.new((inner_x, 0.02, inner_z))
            v2 = bm.verts.new((outer_x, 0.02, outer_z))
            v3 = bm.verts.new((outer_x, -0.02, outer_z))
            v4 = bm.verts.new((inner_x, -0.02, inner_z))

            bm.faces.new([v1, v2, v3, v4])

        bm.to_mesh(wheel.data)
        bm.free()

        return wheel

    @staticmethod
    def create_side_mirror(side='left'):
        """Create a simple side mirror stub"""
        # Mirror stalk
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=6,
            radius=0.02,
            depth=0.15,
            location=(0, 0, 0),
            rotation=(0, math.radians(45), 0)
        )
        stalk = bpy.context.active_object

        # Mirror head
        bpy.ops.mesh.primitive_cube_add(
            size=0.08,
            location=(0.1, 0, 0)
        )
        head = bpy.context.active_object
        head.scale = (1.2, 0.4, 0.7)

        # Join
        stalk.select_set(True)
        head.select_set(True)
        bpy.context.view_layer.objects.active = head
        bpy.ops.object.join()

        mirror = bpy.context.active_object
        mirror.name = f"Mirror_{side}"

        return mirror

    @staticmethod
    def create_rear_diffuser(width=1.5):
        """Create rear diffuser element"""
        bpy.ops.mesh.primitive_cube_add(size=1)
        diffuser = bpy.context.active_object
        diffuser.scale = (width * 0.8, 0.15, 0.08)
        diffuser.location = (0, -0.9, -0.15)

        # Add fins using array modifier
        bpy.ops.mesh.primitive_cube_add(size=1)
        fin = bpy.context.active_object
        fin.scale = (0.02, 0.15, 0.06)
        fin.location = (-width * 0.3, -0.9, -0.15)

        # Array for multiple fins
        array_mod = fin.modifiers.new(name="Array", type='ARRAY')
        array_mod.count = 5
        array_mod.relative_offset_displace = (2.0, 0, 0)

        # Join fins to diffuser
        diffuser.select_set(True)
        fin.select_set(True)
        bpy.context.view_layer.objects.active = diffuser
        bpy.ops.object.join()

        return diffuser

    @staticmethod
    def create_body_base(length=2.0, width=1.2, height=0.5):
        """Create main body capsule with aggressive angles"""
        # Main body
        bpy.ops.mesh.primitive_cube_add(size=1)
        body = bpy.context.active_object
        body.scale = (length, width, height)

        # Add more aggressive taper for sporty look
        bm = bmesh.new()
        bm.from_mesh(body.data)

        # Taper front and rear
        for v in bm.verts:
            # Front taper (nose down)
            if v.co.y > 0.4:
                v.co.z -= (v.co.y - 0.4) * 0.3
                v.co.x *= 0.8  # Narrow front

            # Rear taper (tail up slightly)
            if v.co.y < -0.4:
                v.co.z += abs(v.co.y + 0.4) * 0.15
                v.co.x *= 0.85  # Narrow rear

            # Lower overall (racing stance)
            v.co.z -= 0.1

        bm.to_mesh(body.data)
        bm.free()

        # Add edge bevel for light catch
        bevel_mod = body.modifiers.new(name="Bevel", type='BEVEL')
        bevel_mod.width = 0.015
        bevel_mod.segments = 1
        bevel_mod.limit_method = 'ANGLE'
        bevel_mod.angle_limit = math.radians(45)

        return body

    @staticmethod
    def create_windshield(car_type):
        """Create windshield with subtle tinting"""
        angle = 25 if car_type in ['speedster', 'racer'] else 35

        bpy.ops.mesh.primitive_cube_add(size=1)
        windshield = bpy.context.active_object
        windshield.scale = (0.8, 0.4, 0.3)
        windshield.location = (0, 0.3, 0.35)
        windshield.rotation_euler = (math.radians(angle), 0, 0)

        # Add slight bevel
        bevel_mod = windshield.modifiers.new(name="Bevel", type='BEVEL')
        bevel_mod.width = 0.01
        bevel_mod.segments = 1

        return windshield

    @staticmethod
    def create_neon_accent_strips(car_type):
        """Create consistent neon light strip geometry"""
        strips = []

        # Side strips (along body line)
        for side in [-1, 1]:
            bpy.ops.mesh.primitive_cube_add(size=1)
            strip = bpy.context.active_object
            strip.scale = (1.6, 0.02, 0.015)
            strip.location = (side * 0.62, 0, 0.1)
            strips.append(strip)

        # Front neon strip
        if car_type in ['speedster', 'phantom', 'racer']:
            bpy.ops.mesh.primitive_cube_add(size=1)
            strip = bpy.context.active_object
            strip.scale = (0.8, 0.02, 0.015)
            strip.location = (0, 0.98, 0.05)
            strips.append(strip)

        # Rear neon strip
        bpy.ops.mesh.primitive_cube_add(size=1)
        strip = bpy.context.active_object
        strip.scale = (0.9, 0.02, 0.015)
        strip.location = (0, -0.95, 0.2)
        strips.append(strip)

        # Underglow strip
        if car_type in ['drift', 'phantom']:
            bpy.ops.mesh.primitive_cube_add(size=1)
            strip = bpy.context.active_object
            strip.scale = (1.4, 0.8, 0.01)
            strip.location = (0, 0, -0.25)
            strips.append(strip)

        return strips

    @staticmethod
    def assemble_car(car_type, dimensions):
        """Assemble complete car from components"""
        length, width, height, wheel_radius, spoke_count = dimensions

        # Create body
        body = CarGeometry.create_body_base(length, width, height)
        body.name = "Body"

        # Create wheels
        wheels = []
        wheel_positions = [
            (width * 0.45, length * 0.35, -height * 0.3),   # Front left
            (-width * 0.45, length * 0.35, -height * 0.3),  # Front right
            (width * 0.45, -length * 0.35, -height * 0.3),  # Rear left
            (-width * 0.45, -length * 0.35, -height * 0.3), # Rear right
        ]

        for i, pos in enumerate(wheel_positions):
            wheel = CarGeometry.create_wheel_with_spokes(wheel_radius, 0.12, spoke_count)
            wheel.location = pos
            wheel.name = f"Wheel_{i}"
            wheels.append(wheel)

        # Create windshield
        windshield = CarGeometry.create_windshield(car_type)
        windshield.name = "Windshield"

        # Create neon accent strips
        neon_strips = CarGeometry.create_neon_accent_strips(car_type)
        for i, strip in enumerate(neon_strips):
            strip.name = f"NeonStrip_{i}"

        # Create side mirrors
        mirror_left = CarGeometry.create_side_mirror('left')
        mirror_left.location = (width * 0.5, length * 0.2, height * 0.3)
        mirror_left.name = "Mirror_L"

        mirror_right = CarGeometry.create_side_mirror('right')
        mirror_right.location = (-width * 0.5, length * 0.2, height * 0.3)
        mirror_right.scale.x *= -1
        mirror_right.name = "Mirror_R"

        # Create rear diffuser (except for speedster and phantom)
        diffuser = None
        if car_type not in ['speedster', 'phantom']:
            diffuser = CarGeometry.create_rear_diffuser(width)
            diffuser.name = "Diffuser"

        # Join all parts
        all_parts = [body] + wheels + [windshield] + neon_strips + [mirror_left, mirror_right]
        if diffuser:
            all_parts.append(diffuser)

        for obj in all_parts:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = body
        bpy.ops.object.join()

        car = bpy.context.active_object
        car.name = f"Car_{car_type}"

        # Apply all modifiers
        for modifier in car.modifiers:
            bpy.ops.object.modifier_apply(modifier=modifier.name)

        # Calculate normals
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Generate UVs
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
        bpy.ops.object.mode_set(mode='OBJECT')

        return car


# Car type dimensions: (length, width, height, wheel_radius, spoke_count)
CAR_DIMENSIONS = {
    'speedster': (2.2, 1.0, 0.45, 0.28, 5),
    'muscle': (2.4, 1.4, 0.55, 0.35, 6),
    'racer': (2.0, 1.1, 0.4, 0.26, 5),
    'drift': (2.1, 1.3, 0.48, 0.30, 6),
    'phantom': (2.3, 1.2, 0.42, 0.29, 5),
    'titan': (2.6, 1.5, 0.65, 0.38, 6),
    'viper': (2.1, 1.15, 0.43, 0.27, 5),
}
