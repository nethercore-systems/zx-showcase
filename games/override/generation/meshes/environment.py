#!/usr/bin/env python3
"""Generate 3D environment meshes for Override.

Environment tiles (8x8 grid):
- Floors: metal, grate, panel, damaged
- Walls: solid, window, vent, pipe, screen, doorframe
- Doors: open, closed, locked
- Traps: spike, gas, laser

All meshes are 1 unit cubes/planes designed for tile-based level building.
"""

import bpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from bpy_utils import setup_scene, export_glb, get_output_dir, create_dark_industrial_material


def generate_floor_metal():
    """Generate metal floor tile."""
    setup_scene()

    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "floor_metal"

    # Add subdivision for detail
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=2)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Panel grooves (boolean cuts)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.02))
    groove = bpy.context.active_object
    groove.scale = (0.02, 0.9, 0.02)
    bpy.ops.object.transform_apply(scale=True)

    # Boolean modifier
    mod = floor.modifiers.new(name='Groove', type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = groove
    bpy.ops.object.modifier_apply(modifier='Groove')
    bpy.data.objects.remove(groove)

    mat = create_dark_industrial_material("floor_metal_mat")
    floor.data.materials.append(mat)

    output_path = get_output_dir() / "floor_metal.glb"
    export_glb(floor, output_path)
    print(f"✓ floor_metal")


def generate_floor_grate():
    """Generate grate floor tile (with holes)."""
    setup_scene()

    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "floor_grate"

    # Subdivide
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=4)

    # Inset for grate pattern
    bpy.ops.mesh.inset(thickness=0.05, depth=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

    mat = create_dark_industrial_material("floor_grate_mat")
    floor.data.materials.append(mat)

    output_path = get_output_dir() / "floor_grate.glb"
    export_glb(floor, output_path)
    print(f"✓ floor_grate")


def generate_wall_solid():
    """Generate solid wall tile."""
    setup_scene()

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
    wall = bpy.context.active_object
    wall.name = "wall_solid"
    wall.scale = (1, 0.1, 1)
    bpy.ops.object.transform_apply(scale=True)

    mat = create_dark_industrial_material("wall_solid_mat")
    wall.data.materials.append(mat)

    output_path = get_output_dir() / "wall_solid.glb"
    export_glb(wall, output_path)
    print(f"✓ wall_solid")


def generate_wall_window():
    """Generate wall with window cutout."""
    setup_scene()

    # Base wall
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
    wall = bpy.context.active_object
    wall.name = "wall_window"
    wall.scale = (1, 0.1, 1)
    bpy.ops.object.transform_apply(scale=True)

    # Window cutout
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.6))
    window = bpy.context.active_object
    window.scale = (0.6, 0.2, 0.4)
    bpy.ops.object.transform_apply(scale=True)

    # Boolean
    mod = wall.modifiers.new(name='Window', type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = window
    bpy.ops.object.modifier_apply(modifier='Window')
    bpy.data.objects.remove(window)

    mat = create_dark_industrial_material("wall_window_mat")
    wall.data.materials.append(mat)

    output_path = get_output_dir() / "wall_window.glb"
    export_glb(wall, output_path)
    print(f"✓ wall_window")


def generate_door_closed():
    """Generate closed door."""
    setup_scene()

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
    door = bpy.context.active_object
    door.name = "door_closed"
    door.scale = (0.8, 0.1, 0.95)
    bpy.ops.object.transform_apply(scale=True)

    mat = create_dark_industrial_material("door_closed_mat")
    door.data.materials.append(mat)

    output_path = get_output_dir() / "door_closed.glb"
    export_glb(door, output_path)
    print(f"✓ door_closed")


def generate_door_open():
    """Generate open door (slid to side)."""
    setup_scene()

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.45, 0, 0.5))
    door = bpy.context.active_object
    door.name = "door_open"
    door.scale = (0.1, 0.1, 0.95)
    bpy.ops.object.transform_apply(scale=True)

    mat = create_dark_industrial_material("door_open_mat")
    door.data.materials.append(mat)

    output_path = get_output_dir() / "door_open.glb"
    export_glb(door, output_path)
    print(f"✓ door_open")


def generate_trap_spike():
    """Generate spike trap (retractable spikes)."""
    setup_scene()

    parts = []

    # Base plate
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.02))
    base = bpy.context.active_object
    base.name = "Base"
    base.scale = (1, 1, 0.02)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(base)

    # Spikes (3x3 grid)
    for x in [-0.3, 0, 0.3]:
        for y in [-0.3, 0, 0.3]:
            bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.08, depth=0.4, location=(x, y, 0.25))
            spike = bpy.context.active_object
            spike.name = f"Spike_{x}_{y}"
            parts.append(spike)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()

    trap = bpy.context.active_object
    trap.name = "trap_spike"

    mat = create_dark_industrial_material("trap_spike_mat")
    trap.data.materials.append(mat)

    output_path = get_output_dir() / "trap_spike.glb"
    export_glb(trap, output_path)
    print(f"✓ trap_spike")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("OVERRIDE - Environment Generation")
    print("="*60 + "\n")

    print("Floors:")
    generate_floor_metal()
    generate_floor_grate()

    print("\nWalls:")
    generate_wall_solid()
    generate_wall_window()

    print("\nDoors:")
    generate_door_closed()
    generate_door_open()

    print("\nTraps:")
    generate_trap_spike()

    print("\n" + "="*60)
    print("✓ All environment tiles generated!")
    print("="*60)
