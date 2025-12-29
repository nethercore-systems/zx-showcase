//! OVERRIDE - Asymmetric 1v3 Multiplayer for Nethercore ZX
//!
//! One Overseer with god-view controls the facility.
//! Three Runners with limited view must collect cores and escape.

#![no_std]
#![allow(dead_code)]

// Pull in the ZX FFI bindings (local copy to avoid include! doc comment issues)
mod ffi;
use ffi::*;

// Camera system for dual-perspective rendering
mod camera;
use camera::{CameraState, setup_runner_camera, setup_overseer_camera, get_local_role};

// AI module for single-player mode
mod ai;
use ai::{RunnerAI, RunnerInput, update_runner_ai};

use core::mem::MaybeUninit;

// ============================================================================
// CONSTANTS
// ============================================================================

/// Pixel scale factor (960/320 = 3)
const SCALE: i32 = 3;

/// Game resolution (scaled to 960x540)
const GAME_WIDTH: i32 = 320;
const GAME_HEIGHT: i32 = 180;

/// Tile size in game pixels
const TILE_SIZE: i32 = 8;

/// Facility grid size
const FACILITY_WIDTH: usize = 40;  // 320 / 8
const FACILITY_HEIGHT: usize = 22; // 176 / 8 (4 pixels for HUD)

/// Maximum entities
const MAX_RUNNERS: usize = 3;
const MAX_DRONES: usize = 4;
const MAX_TRAPS: usize = 20;
const MAX_DOORS: usize = 30;
const MAX_CORES: usize = 3;

/// Game timing
const ROUND_DURATION_TICKS: u32 = 60 * 60 * 4; // 4 minutes at 60fps

/// Overseer energy
const MAX_ENERGY: i32 = 100;
const ENERGY_REGEN_PER_TICK: i32 = 1; // Regenerates ~1 per tick at 60fps / 60 = ~1/sec, so 5/sec = 5

// ============================================================================
// FIXED POINT MATH (for deterministic rollback)
// ============================================================================

/// Fixed point with 8 fractional bits (Q24.8)
type Fixed = i32;

const FIXED_SHIFT: i32 = 8;
const FIXED_ONE: Fixed = 1 << FIXED_SHIFT;

fn fixed_from_int(x: i32) -> Fixed {
    x << FIXED_SHIFT
}

fn fixed_to_int(x: Fixed) -> i32 {
    x >> FIXED_SHIFT
}

fn fixed_mul(a: Fixed, b: Fixed) -> Fixed {
    ((a as i64 * b as i64) >> FIXED_SHIFT) as Fixed
}

// ============================================================================
// GAME TYPES
// ============================================================================

#[derive(Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
enum TileType {
    Floor = 0,
    Wall = 1,
    Door = 2,
    Trap = 3,
    Core = 4,
    Entry = 5,
    Extract = 6,
}

#[derive(Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
enum FloorVariant {
    Metal = 0,
    Grate = 1,
    Panel = 2,
    Damaged = 3,
}

#[derive(Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
enum WallVariant {
    Solid = 0,
    Window = 1,
    Vent = 2,
    Pipe = 3,
    Screen = 4,
    Doorframe = 5,
}

#[derive(Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
enum TrapType {
    Spike = 0,
    Gas = 1,
    Laser = 2,
}

#[derive(Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
enum DoorState {
    Open = 0,
    Closed = 1,
    Locked = 2,
}

#[derive(Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
enum RunnerState {
    Idle = 0,
    Walking = 1,
    Sprinting = 2,
    Crouching = 3,
    Dead = 4,
}

#[derive(Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
enum GamePhase {
    Menu = 0,
    Playing = 1,
    RoundEnd = 2,
}

#[derive(Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
enum Role {
    Overseer = 0,
    Runner = 1,
}

// ============================================================================
// ENTITY STRUCTURES
// ============================================================================

#[derive(Clone, Copy)]
struct Runner {
    x: Fixed,
    y: Fixed,
    state: RunnerState,
    anim_tick: u8,
    facing_x: i8, // -1, 0, 1
    facing_y: i8, // -1, 0, 1
}

impl Runner {
    const fn new() -> Self {
        Self {
            x: 0,
            y: 0,
            state: RunnerState::Idle,
            anim_tick: 0,
            facing_x: 0,
            facing_y: 1,
        }
    }
}

#[derive(Clone, Copy)]
struct Drone {
    x: Fixed,
    y: Fixed,
    target_x: Fixed,
    target_y: Fixed,
    anim_tick: u8,
    active: bool,
    lifetime: u16,
}

impl Drone {
    const fn new() -> Self {
        Self {
            x: 0,
            y: 0,
            target_x: 0,
            target_y: 0,
            anim_tick: 0,
            active: false,
            lifetime: 0,
        }
    }
}

#[derive(Clone, Copy)]
struct Trap {
    x: u8,
    y: u8,
    trap_type: TrapType,
    active: bool,
    cooldown: u16,
}

impl Trap {
    const fn new() -> Self {
        Self {
            x: 0,
            y: 0,
            trap_type: TrapType::Spike,
            active: false,
            cooldown: 0,
        }
    }
}

#[derive(Clone, Copy)]
struct Door {
    x: u8,
    y: u8,
    state: DoorState,
    timer: u16, // For locked doors
}

impl Door {
    const fn new() -> Self {
        Self {
            x: 0,
            y: 0,
            state: DoorState::Open,
            timer: 0,
        }
    }
}

#[derive(Clone, Copy)]
struct Core {
    x: u8,
    y: u8,
    collected: bool,
}

impl Core {
    const fn new() -> Self {
        Self {
            x: 0,
            y: 0,
            collected: false,
        }
    }
}

// ============================================================================
// FACILITY MAP
// ============================================================================

#[derive(Clone, Copy)]
struct Tile {
    tile_type: TileType,
    variant: u8,
}

impl Tile {
    const fn floor(variant: FloorVariant) -> Self {
        Self {
            tile_type: TileType::Floor,
            variant: variant as u8,
        }
    }

    const fn wall(variant: WallVariant) -> Self {
        Self {
            tile_type: TileType::Wall,
            variant: variant as u8,
        }
    }
}

// ============================================================================
// GAME STATE (must be fully deterministic for rollback)
// ============================================================================

struct GameState {
    // Phase
    phase: GamePhase,
    round_timer: u32,

    // Facility
    seed: u64,
    tiles: [[Tile; FACILITY_WIDTH]; FACILITY_HEIGHT],

    // Entry/Exit positions
    entry_x: u8,
    entry_y: u8,
    extract_x: u8,
    extract_y: u8,

    // Entities
    runners: [Runner; MAX_RUNNERS],
    runners_alive: u8,

    drones: [Drone; MAX_DRONES],
    drone_count: u8,

    traps: [Trap; MAX_TRAPS],
    trap_count: u8,

    doors: [Door; MAX_DOORS],
    door_count: u8,

    cores: [Core; MAX_CORES],
    cores_collected: u8,

    // Overseer
    overseer_energy: i32,
    overseer_cursor_x: i32,
    overseer_cursor_y: i32,

    // Roles (player 0 is overseer, 1-3 are runners)
    overseer_player: u32,

    // AI state for runners (used in single-player mode)
    runner_ai: [RunnerAI; MAX_RUNNERS],

    // Round results
    runners_win: bool,
}

impl GameState {
    const fn new() -> Self {
        Self {
            phase: GamePhase::Menu,
            round_timer: ROUND_DURATION_TICKS,
            seed: 12345,
            tiles: [[Tile::floor(FloorVariant::Metal); FACILITY_WIDTH]; FACILITY_HEIGHT],
            entry_x: 1,
            entry_y: 10,
            extract_x: 38,
            extract_y: 10,
            runners: [Runner::new(); MAX_RUNNERS],
            runners_alive: 3,
            drones: [Drone::new(); MAX_DRONES],
            drone_count: 0,
            traps: [Trap::new(); MAX_TRAPS],
            trap_count: 0,
            doors: [Door::new(); MAX_DOORS],
            door_count: 0,
            cores: [Core::new(); MAX_CORES],
            cores_collected: 0,
            overseer_energy: MAX_ENERGY,
            overseer_cursor_x: GAME_WIDTH / 2,
            overseer_cursor_y: GAME_HEIGHT / 2,
            overseer_player: 0,
            runner_ai: [RunnerAI::new(); MAX_RUNNERS],
            runners_win: false,
        }
    }
}

// ============================================================================
// ASSET HANDLES
// ============================================================================

struct Assets {
    // 3D Meshes (procedural, created in init)
    mesh_floor: u32,      // Flat plane for floor tiles
    mesh_wall: u32,       // Cube for walls
    mesh_door: u32,       // Thin cube for doors
    mesh_runner: u32,     // Capsule for runner (placeholder)
    mesh_drone: u32,      // Sphere for drone (placeholder)
    mesh_core: u32,       // Cube for data core (placeholder)
    mesh_trap_spike: u32, // Cylinder for spike trap
    mesh_trap_gas: u32,   // Flat plane for gas trap
    mesh_trap_laser: u32, // Thin cube for laser trap

    // Tilesets (textures for 3D meshes)
    floor_metal: u32,
    floor_grate: u32,
    floor_panel: u32,
    floor_damaged: u32,
    wall_solid: u32,
    wall_window: u32,
    wall_vent: u32,
    wall_pipe: u32,
    wall_screen: u32,
    wall_doorframe: u32,

    // Sprites (still used for UI and some effects)
    door_closed: u32,
    door_open: u32,
    door_locked: u32,
    trap_spike: u32,
    trap_gas: u32,
    trap_laser: u32,

    // Characters (arrays for frames)
    runner_idle: [u32; 4],
    runner_walk: [u32; 4],
    runner_sprint: [u32; 4],
    runner_crouch: [u32; 4],
    runner_death: [u32; 4],
    drone_hover: [u32; 4],

    // VFX
    core_glow: [u32; 4],
    gas_cloud: [u32; 8],

    // UI
    energy_bar: [u32; 5],
    core_indicator_active: u32,
    core_indicator_inactive: u32,
    timer_digits: [u32; 10],

    // Audio
    sfx_footstep: u32,
    sfx_door_open: u32,
    sfx_door_close: u32,
    sfx_trap_spike: u32,
    sfx_core_pickup: u32,
    sfx_drone_hover: u32,
    sfx_runner_death: u32,
    sfx_alarm: u32,
    sfx_extraction_open: u32,

    mus_menu: u32,
    mus_gameplay: u32,
    mus_victory: u32,
    mus_defeat: u32,
}

impl Assets {
    const fn new() -> Self {
        Self {
            // Meshes (initialized to 0, created in init)
            mesh_floor: 0,
            mesh_wall: 0,
            mesh_door: 0,
            mesh_runner: 0,
            mesh_drone: 0,
            mesh_core: 0,
            mesh_trap_spike: 0,
            mesh_trap_gas: 0,
            mesh_trap_laser: 0,
            // Textures
            floor_metal: 0,
            floor_grate: 0,
            floor_panel: 0,
            floor_damaged: 0,
            wall_solid: 0,
            wall_window: 0,
            wall_vent: 0,
            wall_pipe: 0,
            wall_screen: 0,
            wall_doorframe: 0,
            door_closed: 0,
            door_open: 0,
            door_locked: 0,
            trap_spike: 0,
            trap_gas: 0,
            trap_laser: 0,
            runner_idle: [0; 4],
            runner_walk: [0; 4],
            runner_sprint: [0; 4],
            runner_crouch: [0; 4],
            runner_death: [0; 4],
            drone_hover: [0; 4],
            core_glow: [0; 4],
            gas_cloud: [0; 8],
            energy_bar: [0; 5],
            core_indicator_active: 0,
            core_indicator_inactive: 0,
            timer_digits: [0; 10],
            sfx_footstep: 0,
            sfx_door_open: 0,
            sfx_door_close: 0,
            sfx_trap_spike: 0,
            sfx_core_pickup: 0,
            sfx_drone_hover: 0,
            sfx_runner_death: 0,
            sfx_alarm: 0,
            sfx_extraction_open: 0,
            mus_menu: 0,
            mus_gameplay: 0,
            mus_victory: 0,
            mus_defeat: 0,
        }
    }
}

// ============================================================================
// GLOBAL STATE
// ============================================================================

static mut GAME: MaybeUninit<GameState> = MaybeUninit::uninit();
static mut ASSETS: MaybeUninit<Assets> = MaybeUninit::uninit();

/// Camera state - render-only, NOT part of rollback state
/// Stored separately from GameState because it uses floats for smooth interpolation
static mut CAMERA: CameraState = CameraState::new();

fn game() -> &'static mut GameState {
    unsafe { GAME.assume_init_mut() }
}

fn assets() -> &'static Assets {
    unsafe { ASSETS.assume_init_ref() }
}

fn assets_mut() -> &'static mut Assets {
    unsafe { ASSETS.assume_init_mut() }
}

fn camera() -> &'static mut CameraState {
    unsafe { &mut CAMERA }
}

// ============================================================================
// PROCEDURAL FACILITY GENERATION
// ============================================================================

/// Simple deterministic RNG
fn lcg_next(seed: &mut u64) -> u32 {
    *seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1);
    (*seed >> 32) as u32
}

fn generate_facility(state: &mut GameState) {
    let seed = &mut state.seed;

    // Fill with walls first
    for y in 0..FACILITY_HEIGHT {
        for x in 0..FACILITY_WIDTH {
            state.tiles[y][x] = Tile::wall(WallVariant::Solid);
        }
    }

    // Carve out rooms using simple cellular automata
    // Start with random floor placement
    for y in 1..(FACILITY_HEIGHT - 1) {
        for x in 1..(FACILITY_WIDTH - 1) {
            let r = lcg_next(seed) % 100;
            if r < 45 {
                let variant = match lcg_next(seed) % 4 {
                    0 => FloorVariant::Metal,
                    1 => FloorVariant::Grate,
                    2 => FloorVariant::Panel,
                    _ => FloorVariant::Damaged,
                };
                state.tiles[y][x] = Tile::floor(variant);
            }
        }
    }

    // Apply cellular automata rules a few times
    for _ in 0..4 {
        let mut new_tiles = state.tiles;

        for y in 1..(FACILITY_HEIGHT - 1) {
            for x in 1..(FACILITY_WIDTH - 1) {
                let mut floor_count = 0;

                // Count floor neighbors
                for dy in -1i32..=1 {
                    for dx in -1i32..=1 {
                        let ny = (y as i32 + dy) as usize;
                        let nx = (x as i32 + dx) as usize;
                        if state.tiles[ny][nx].tile_type == TileType::Floor {
                            floor_count += 1;
                        }
                    }
                }

                // Apply rules
                if state.tiles[y][x].tile_type == TileType::Floor {
                    if floor_count < 4 {
                        new_tiles[y][x] = Tile::wall(WallVariant::Solid);
                    }
                } else {
                    if floor_count > 5 {
                        let variant = match lcg_next(seed) % 4 {
                            0 => FloorVariant::Metal,
                            1 => FloorVariant::Grate,
                            2 => FloorVariant::Panel,
                            _ => FloorVariant::Damaged,
                        };
                        new_tiles[y][x] = Tile::floor(variant);
                    }
                }
            }
        }

        state.tiles = new_tiles;
    }

    // Ensure entry point on left side
    state.entry_x = 2;
    state.entry_y = (FACILITY_HEIGHT / 2) as u8;
    for y in (state.entry_y as usize - 1)..=(state.entry_y as usize + 1) {
        for x in 1..5 {
            state.tiles[y][x] = Tile::floor(FloorVariant::Panel);
        }
    }
    state.tiles[state.entry_y as usize][state.entry_x as usize].tile_type = TileType::Entry;

    // Ensure extraction point on right side
    state.extract_x = (FACILITY_WIDTH - 3) as u8;
    state.extract_y = (FACILITY_HEIGHT / 2) as u8;
    for y in (state.extract_y as usize - 1)..=(state.extract_y as usize + 1) {
        for x in (FACILITY_WIDTH - 5)..(FACILITY_WIDTH - 1) {
            state.tiles[y][x] = Tile::floor(FloorVariant::Panel);
        }
    }
    state.tiles[state.extract_y as usize][state.extract_x as usize].tile_type = TileType::Extract;

    // Place cores in scattered locations
    let core_positions = [
        (FACILITY_WIDTH / 4, FACILITY_HEIGHT / 3),
        (FACILITY_WIDTH / 2, FACILITY_HEIGHT * 2 / 3),
        (FACILITY_WIDTH * 3 / 4, FACILITY_HEIGHT / 2),
    ];

    for (i, &(cx, cy)) in core_positions.iter().enumerate() {
        // Ensure area is floor
        for y in (cy.saturating_sub(1))..=(cy + 1).min(FACILITY_HEIGHT - 1) {
            for x in (cx.saturating_sub(1))..=(cx + 1).min(FACILITY_WIDTH - 1) {
                if state.tiles[y][x].tile_type == TileType::Wall {
                    state.tiles[y][x] = Tile::floor(FloorVariant::Metal);
                }
            }
        }

        state.cores[i] = Core {
            x: cx as u8,
            y: cy as u8,
            collected: false,
        };
        state.tiles[cy][cx].tile_type = TileType::Core;
    }

    // Add some wall variations
    for y in 0..FACILITY_HEIGHT {
        for x in 0..FACILITY_WIDTH {
            if state.tiles[y][x].tile_type == TileType::Wall {
                let variant = match lcg_next(seed) % 10 {
                    0 => WallVariant::Window,
                    1 => WallVariant::Vent,
                    2 => WallVariant::Pipe,
                    3 => WallVariant::Screen,
                    _ => WallVariant::Solid,
                };
                state.tiles[y][x] = Tile::wall(variant);
            }
        }
    }

    // Place traps in security areas
    state.trap_count = 0;
    for _ in 0..8 {
        let tx = (lcg_next(seed) % (FACILITY_WIDTH as u32 - 4) + 2) as usize;
        let ty = (lcg_next(seed) % (FACILITY_HEIGHT as u32 - 4) + 2) as usize;

        if state.tiles[ty][tx].tile_type == TileType::Floor {
            let idx = state.trap_count as usize;
            if idx < MAX_TRAPS {
                state.traps[idx] = Trap {
                    x: tx as u8,
                    y: ty as u8,
                    trap_type: match lcg_next(seed) % 3 {
                        0 => TrapType::Spike,
                        1 => TrapType::Gas,
                        _ => TrapType::Laser,
                    },
                    active: false,
                    cooldown: 0,
                };
                state.tiles[ty][tx].tile_type = TileType::Trap;
                state.trap_count += 1;
            }
        }
    }
}

// ============================================================================
// GAME LOGIC
// ============================================================================

fn start_round(state: &mut GameState) {
    state.phase = GamePhase::Playing;
    state.round_timer = ROUND_DURATION_TICKS;
    state.runners_alive = 3;
    state.cores_collected = 0;
    state.overseer_energy = MAX_ENERGY;
    state.drone_count = 0;

    // Reset cores
    for core in state.cores.iter_mut() {
        core.collected = false;
    }

    // Reset traps
    for trap in state.traps.iter_mut() {
        trap.active = false;
        trap.cooldown = 0;
    }

    // Generate new facility
    state.seed = unsafe { tick_count() as u64 * 12345 + 67890 };
    generate_facility(state);

    // Spawn runners at entry and reset AI
    for (i, runner) in state.runners.iter_mut().enumerate() {
        runner.x = fixed_from_int((state.entry_x as i32) * TILE_SIZE + 4);
        runner.y = fixed_from_int((state.entry_y as i32 + i as i32 - 1) * TILE_SIZE + 6);
        runner.state = RunnerState::Idle;
        runner.anim_tick = 0;
    }

    // Reset AI state
    for ai in state.runner_ai.iter_mut() {
        *ai = RunnerAI::new();
    }

    // Play gameplay music
    unsafe {
        music_play(assets().mus_gameplay, 0.6, true as u32);
    }
}

/// Get input from a human player
fn get_player_input(player: u32) -> RunnerInput {
    unsafe {
        RunnerInput {
            move_x: if button_held(player, BTN_RIGHT) != 0 { 1 }
                    else if button_held(player, BTN_LEFT) != 0 { -1 }
                    else { 0 },
            move_y: if button_held(player, BTN_DOWN) != 0 { 1 }
                    else if button_held(player, BTN_UP) != 0 { -1 }
                    else { 0 },
            sprint: button_held(player, BTN_B) != 0,
            crouch: button_held(player, BTN_X) != 0,
        }
    }
}

fn update_runner(runner: &mut Runner, input: &RunnerInput, tiles: &[[Tile; FACILITY_WIDTH]; FACILITY_HEIGHT]) {
    if runner.state == RunnerState::Dead {
        return;
    }

    // Get input from parameter
    let move_x = input.move_x;
    let move_y = input.move_y;
    let sprint = input.sprint;
    let crouch = input.crouch;

    // Determine movement speed
    let speed = if crouch {
        FIXED_ONE / 4  // Slow crouch
    } else if sprint {
        FIXED_ONE      // Fast sprint
    } else {
        FIXED_ONE / 2  // Normal walk
    };

    // Apply movement
    if move_x != 0 || move_y != 0 {
        let dx = fixed_mul(fixed_from_int(move_x), speed);
        let dy = fixed_mul(fixed_from_int(move_y), speed);

        let new_x = runner.x + dx;
        let new_y = runner.y + dy;

        // Collision check
        let tile_x = (fixed_to_int(new_x) / TILE_SIZE) as usize;
        let tile_y = (fixed_to_int(new_y) / TILE_SIZE) as usize;

        if tile_x < FACILITY_WIDTH && tile_y < FACILITY_HEIGHT {
            let tile = &tiles[tile_y][tile_x];
            if tile.tile_type != TileType::Wall {
                runner.x = new_x;
                runner.y = new_y;
            }
        }

        // Update facing
        runner.facing_x = move_x as i8;
        runner.facing_y = move_y as i8;

        // Update state
        runner.state = if crouch {
            RunnerState::Crouching
        } else if sprint {
            RunnerState::Sprinting
        } else {
            RunnerState::Walking
        };
    } else {
        runner.state = if crouch {
            RunnerState::Crouching
        } else {
            RunnerState::Idle
        };
    }

    // Animate
    runner.anim_tick = runner.anim_tick.wrapping_add(1);
}

fn update_overseer(state: &mut GameState) {
    let player = state.overseer_player;

    // Cursor movement
    unsafe {
        let stick_x = left_stick_x(player);
        let stick_y = left_stick_y(player);

        state.overseer_cursor_x = (state.overseer_cursor_x + (stick_x * 4.0) as i32)
            .clamp(0, GAME_WIDTH - 1);
        state.overseer_cursor_y = (state.overseer_cursor_y + (stick_y * 4.0) as i32)
            .clamp(0, GAME_HEIGHT - 1);

        // Energy regeneration
        if state.overseer_energy < MAX_ENERGY {
            state.overseer_energy = (state.overseer_energy + 1).min(MAX_ENERGY);
        }

        // Get tile under cursor
        let tile_x = (state.overseer_cursor_x / TILE_SIZE) as usize;
        let tile_y = (state.overseer_cursor_y / TILE_SIZE) as usize;

        // Powers
        if button_pressed(player, BTN_A) != 0 {
            // Lock door (cost 10)
            if state.overseer_energy >= 10 {
                for door in state.doors.iter_mut() {
                    if door.x as usize == tile_x && door.y as usize == tile_y {
                        if door.state != DoorState::Locked {
                            door.state = DoorState::Locked;
                            door.timer = 60 * 5; // 5 seconds
                            state.overseer_energy -= 10;
                            break;
                        }
                    }
                }
            }
        }

        if button_pressed(player, BTN_B) != 0 {
            // Activate trap (cost 20)
            if state.overseer_energy >= 20 {
                for trap in state.traps.iter_mut() {
                    if trap.x as usize == tile_x && trap.y as usize == tile_y {
                        if !trap.active && trap.cooldown == 0 {
                            trap.active = true;
                            trap.cooldown = 60 * 10; // 10 second cooldown
                            state.overseer_energy -= 20;
                            play_sound(assets().sfx_trap_spike, 0.7, 0.0);
                            break;
                        }
                    }
                }
            }
        }

        if button_pressed(player, BTN_Y) != 0 {
            // Spawn drone (cost 30)
            if state.overseer_energy >= 30 && state.drone_count < MAX_DRONES as u8 {
                let idx = state.drone_count as usize;
                state.drones[idx] = Drone {
                    x: fixed_from_int(state.overseer_cursor_x),
                    y: fixed_from_int(state.overseer_cursor_y),
                    target_x: 0,
                    target_y: 0,
                    anim_tick: 0,
                    active: true,
                    lifetime: 60 * 15, // 15 seconds
                };
                state.drone_count += 1;
                state.overseer_energy -= 30;
            }
        }
    }
}

fn update_drones(state: &mut GameState) {
    for drone in state.drones.iter_mut() {
        if !drone.active {
            continue;
        }

        // Decrease lifetime
        if drone.lifetime > 0 {
            drone.lifetime -= 1;
            if drone.lifetime == 0 {
                drone.active = false;
                continue;
            }
        }

        // Find nearest alive runner
        let mut nearest_dist = i32::MAX;
        let mut nearest_x = drone.x;
        let mut nearest_y = drone.y;

        for runner in state.runners.iter() {
            if runner.state != RunnerState::Dead {
                let dx = fixed_to_int(runner.x - drone.x);
                let dy = fixed_to_int(runner.y - drone.y);
                let dist = dx * dx + dy * dy;
                if dist < nearest_dist {
                    nearest_dist = dist;
                    nearest_x = runner.x;
                    nearest_y = runner.y;
                }
            }
        }

        // Move toward nearest runner
        let dx = nearest_x - drone.x;
        let dy = nearest_y - drone.y;

        if dx != 0 || dy != 0 {
            let speed = FIXED_ONE / 3; // Slower than runners

            if dx.abs() > dy.abs() {
                drone.x += if dx > 0 { speed } else { -speed };
            } else {
                drone.y += if dy > 0 { speed } else { -speed };
            }
        }

        drone.anim_tick = drone.anim_tick.wrapping_add(1);
    }
}

fn check_collisions(state: &mut GameState) {
    // Check runner-drone collisions
    for runner_idx in 0..MAX_RUNNERS {
        let runner_state = state.runners[runner_idx].state;
        let runner_x = state.runners[runner_idx].x;
        let runner_y = state.runners[runner_idx].y;

        if runner_state == RunnerState::Dead {
            continue;
        }

        for drone in state.drones.iter() {
            if !drone.active {
                continue;
            }

            let dx = fixed_to_int(runner_x - drone.x).abs();
            let dy = fixed_to_int(runner_y - drone.y).abs();

            if dx < 6 && dy < 6 {
                // Collision! Eliminate runner
                state.runners[runner_idx].state = RunnerState::Dead;
                state.runners_alive -= 1;
                unsafe {
                    play_sound(assets().sfx_runner_death, 0.8, 0.0);
                }
                break; // Can only die once
            }
        }
    }

    // Check runner-trap collisions
    for runner_idx in 0..MAX_RUNNERS {
        let runner_state = state.runners[runner_idx].state;
        let runner_x = state.runners[runner_idx].x;
        let runner_y = state.runners[runner_idx].y;

        if runner_state == RunnerState::Dead {
            continue;
        }

        let runner_tile_x = (fixed_to_int(runner_x) / TILE_SIZE) as u8;
        let runner_tile_y = (fixed_to_int(runner_y) / TILE_SIZE) as u8;

        for trap in state.traps.iter() {
            if trap.active && trap.x == runner_tile_x && trap.y == runner_tile_y {
                state.runners[runner_idx].state = RunnerState::Dead;
                state.runners_alive -= 1;
                unsafe {
                    play_sound(assets().sfx_runner_death, 0.8, 0.0);
                }
                break; // Can only die once
            }
        }
    }

    // Check runner-core collection
    for runner in state.runners.iter() {
        if runner.state == RunnerState::Dead {
            continue;
        }

        let runner_tile_x = (fixed_to_int(runner.x) / TILE_SIZE) as u8;
        let runner_tile_y = (fixed_to_int(runner.y) / TILE_SIZE) as u8;

        for core in state.cores.iter_mut() {
            if !core.collected && core.x == runner_tile_x && core.y == runner_tile_y {
                core.collected = true;
                state.cores_collected += 1;
                unsafe {
                    play_sound(assets().sfx_core_pickup, 0.8, 0.0);
                }
            }
        }
    }

    // Check extraction
    if state.cores_collected >= 3 {
        for runner in state.runners.iter() {
            if runner.state == RunnerState::Dead {
                continue;
            }

            let runner_tile_x = (fixed_to_int(runner.x) / TILE_SIZE) as u8;
            let runner_tile_y = (fixed_to_int(runner.y) / TILE_SIZE) as u8;

            if runner_tile_x == state.extract_x && runner_tile_y == state.extract_y {
                // Runners win!
                state.phase = GamePhase::RoundEnd;
                state.runners_win = true;
                unsafe {
                    music_stop();
                    play_sound(assets().mus_victory, 0.8, 0.0);
                }
            }
        }
    }
}

fn update_traps(state: &mut GameState) {
    for trap in state.traps.iter_mut() {
        // Active traps deactivate after a short time
        if trap.active {
            // Spike traps stay active briefly
            if trap.trap_type == TrapType::Spike {
                trap.active = false;
            }
        }

        // Cooldown
        if trap.cooldown > 0 {
            trap.cooldown -= 1;
        }
    }
}

fn update_doors(state: &mut GameState) {
    for door in state.doors.iter_mut() {
        if door.state == DoorState::Locked {
            if door.timer > 0 {
                door.timer -= 1;
                if door.timer == 0 {
                    door.state = DoorState::Closed;
                }
            }
        }
    }
}

// ============================================================================
// RENDERING
// ============================================================================

fn render_facility(state: &GameState) {
    let a = assets();

    unsafe {
        // Enable depth testing for 3D
        depth_test(1);
        cull_mode(1); // Back-face culling

        for y in 0..FACILITY_HEIGHT {
            for x in 0..FACILITY_WIDTH {
                let tile = &state.tiles[y][x];

                // Convert tile position to 3D world coordinates
                // Tile (0,0) is at world origin, each tile is 1 unit
                let world_x = x as f32 + 0.5; // Center of tile
                let world_z = y as f32 + 0.5; // Y in 2D = Z in 3D

                match tile.tile_type {
                    TileType::Floor | TileType::Entry | TileType::Extract | TileType::Trap | TileType::Core => {
                        // Bind floor texture based on variant
                        let tex = match tile.variant {
                            0 => a.floor_metal,
                            1 => a.floor_grate,
                            2 => a.floor_panel,
                            _ => a.floor_damaged,
                        };
                        texture_bind(tex);

                        // Set color based on special tiles
                        let color = match tile.tile_type {
                            TileType::Entry => 0x44FF44FF,    // Green tint for entry
                            TileType::Extract => 0xFF4444FF,  // Red tint for extract
                            TileType::Core => 0x44FFFFFF,     // Cyan tint for core spots
                            TileType::Trap => 0xFF8800FF,     // Orange for traps
                            _ => 0xFFFFFFFF,                  // White (no tint)
                        };
                        set_color(color);

                        // Draw floor plane at Y=0
                        push_identity();
                        push_translate(world_x, 0.0, world_z);
                        draw_mesh(a.mesh_floor);
                    }

                    TileType::Wall => {
                        // Bind wall texture based on variant
                        let tex = match tile.variant {
                            0 => a.wall_solid,
                            1 => a.wall_window,
                            2 => a.wall_vent,
                            3 => a.wall_pipe,
                            4 => a.wall_screen,
                            _ => a.wall_doorframe,
                        };
                        texture_bind(tex);
                        set_color(0xFFFFFFFF);

                        // Draw wall cube, centered at Y=0.5 (bottom at Y=0)
                        push_identity();
                        push_translate(world_x, 0.5, world_z);
                        draw_mesh(a.mesh_wall);
                    }

                    TileType::Door => {
                        // Check if door is open/closed
                        let door = state.doors.iter()
                            .find(|d| d.x as usize == x && d.y as usize == y);

                        if let Some(d) = door {
                            if d.state != DoorState::Open {
                                // Draw closed/locked door
                                let tex = if d.state == DoorState::Locked {
                                    a.door_locked
                                } else {
                                    a.door_closed
                                };
                                texture_bind(tex);
                                set_color(0xFFFFFFFF);

                                push_identity();
                                push_translate(world_x, 0.5, world_z);
                                draw_mesh(a.mesh_door);
                            }
                        }

                        // Also draw floor under door
                        texture_bind(a.floor_metal);
                        set_color(0xFFFFFFFF);
                        push_identity();
                        push_translate(world_x, 0.0, world_z);
                        draw_mesh(a.mesh_floor);
                    }
                }
            }
        }

        // Reset color
        set_color(0xFFFFFFFF);
    }
}

fn render_cores(state: &GameState) {
    let a = assets();

    unsafe {
        let tick = tick_count() as u32;

        for core in state.cores.iter() {
            if !core.collected {
                // Core position is in tile coordinates
                let world_x = core.x as f32 + 0.5;
                let world_z = core.y as f32 + 0.5;

                // Simple bobbing using triangle wave (tick % 60 gives 0-59, /30 gives 0-1-0)
                let phase = (tick % 60) as i32;
                let bob_offset = if phase < 30 { phase } else { 60 - phase } as f32 / 100.0;
                let world_y = 0.3 + bob_offset;

                // Cyan glow color
                set_color(0x00FFFFFF);
                push_identity();
                push_translate(world_x, world_y, world_z);

                // Rotate slowly (3 degrees per tick = 180 degrees per second at 60fps)
                push_rotate_y((tick * 3 % 360) as f32);

                draw_mesh(a.mesh_core);
            }
        }

        set_color(0xFFFFFFFF);
    }
}

fn render_runners(state: &GameState) {
    let a = assets();

    unsafe {
        for (idx, runner) in state.runners.iter().enumerate() {
            if runner.state == RunnerState::Dead {
                continue;
            }

            // Convert fixed-point pixel position to world coordinates
            // 1 tile = 8 pixels = 1 world unit
            let world_x = fixed_to_int(runner.x) as f32 / TILE_SIZE as f32;
            let world_z = fixed_to_int(runner.y) as f32 / TILE_SIZE as f32;

            // Runner color based on index (distinguishes players)
            let color = match idx {
                0 => 0x44FF44FF, // Green for runner 1
                1 => 0x4444FFFF, // Blue for runner 2
                _ => 0xFFFF44FF, // Yellow for runner 3
            };

            // Height based on state
            let height = match runner.state {
                RunnerState::Crouching => 0.3,
                _ => 0.5,
            };

            set_color(color);
            push_identity();
            push_translate(world_x, height, world_z);

            // Rotate runner to face direction
            let angle = match (runner.facing_x, runner.facing_y) {
                (1, 0) => 90.0,   // Facing right
                (-1, 0) => -90.0, // Facing left
                (0, -1) => 180.0, // Facing up (toward camera)
                _ => 0.0,         // Facing down (default)
            };
            push_rotate_y(angle);

            draw_mesh(a.mesh_runner);
        }

        set_color(0xFFFFFFFF);
    }
}

fn render_drones(state: &GameState) {
    let a = assets();

    unsafe {
        let tick = tick_count() as u32;

        for drone in state.drones.iter() {
            if !drone.active {
                continue;
            }

            // Convert fixed-point pixel position to world coordinates
            let world_x = fixed_to_int(drone.x) as f32 / TILE_SIZE as f32;
            let world_z = fixed_to_int(drone.y) as f32 / TILE_SIZE as f32;

            // Hovering animation (bobbing)
            let phase = ((tick + drone.anim_tick as u32 * 17) % 40) as i32;
            let bob = if phase < 20 { phase } else { 40 - phase } as f32 / 100.0;
            let world_y = 0.6 + bob;

            // Red menacing glow for drones
            set_color(0xFF4444FF);
            push_identity();
            push_translate(world_x, world_y, world_z);

            // Slow rotation
            push_rotate_y((tick * 5 % 360) as f32);

            draw_mesh(a.mesh_drone);
        }

        set_color(0xFFFFFFFF);
    }
}

fn render_traps(state: &GameState) {
    let a = assets();

    unsafe {
        let tick = tick_count() as u32;

        for trap in state.traps.iter() {
            // Trap position is in tile coordinates
            let world_x = trap.x as f32 + 0.5;
            let world_z = trap.y as f32 + 0.5;

            // Color and mesh based on type and activation state
            let (mesh, color, height) = match trap.trap_type {
                TrapType::Spike => {
                    // Spikes extend when active
                    let h = if trap.active { 0.4 } else { 0.1 };
                    let c = if trap.active { 0xFF8888FF } else { 0x888888FF };
                    (a.mesh_trap_spike, c, h)
                }
                TrapType::Gas => {
                    // Gas cloud hovers when active
                    let h = if trap.active { 0.3 } else { 0.0 };
                    let c = if trap.active { 0x88FF88AA } else { 0x448844FF }; // Semi-transparent green
                    (a.mesh_trap_gas, c, h)
                }
                TrapType::Laser => {
                    // Laser beam appears when active
                    if !trap.active {
                        continue; // Don't render inactive lasers
                    }
                    (a.mesh_trap_laser, 0xFF0000FF, 0.5) // Bright red laser
                }
            };

            set_color(color);
            push_identity();
            push_translate(world_x, height, world_z);

            // Spike trap animation - rotate when extending
            if trap.trap_type == TrapType::Spike && trap.active {
                push_rotate_y((tick * 15 % 360) as f32);
            }

            draw_mesh(mesh);
        }

        set_color(0xFFFFFFFF);
    }
}

fn render_ui(state: &GameState) {
    unsafe {
        // Timer (top center)
        let seconds = state.round_timer / 60;
        let minutes = seconds / 60;
        let secs = seconds % 60;

        let timer_x = 430.0;
        let timer_y = 10.0;
        let digit_w = 15.0;
        let digit_h = 21.0;

        // Minutes
        bind_texture(assets().timer_digits[(minutes / 10) as usize % 10]);
        draw_sprite(timer_x, timer_y, digit_w, digit_h, 0xFFFFFFFF);
        bind_texture(assets().timer_digits[(minutes % 10) as usize]);
        draw_sprite(timer_x + digit_w, timer_y, digit_w, digit_h, 0xFFFFFFFF);

        // Colon (just a gap)

        // Seconds
        bind_texture(assets().timer_digits[(secs / 10) as usize]);
        draw_sprite(timer_x + digit_w * 2.5, timer_y, digit_w, digit_h, 0xFFFFFFFF);
        bind_texture(assets().timer_digits[(secs % 10) as usize]);
        draw_sprite(timer_x + digit_w * 3.5, timer_y, digit_w, digit_h, 0xFFFFFFFF);

        // Core indicators (top left)
        for i in 0..3 {
            let core_x = 10.0 + i as f32 * 30.0;
            let core_y = 10.0;
            let collected = state.cores_collected > i as u8;

            let tex = if collected {
                assets().core_indicator_active
            } else {
                assets().core_indicator_inactive
            };

            bind_texture(tex);
            draw_sprite(core_x, core_y, 24.0, 24.0, 0xFFFFFFFF);
        }

        // Energy bar (top right, for overseer)
        let energy_pct = (state.overseer_energy * 100 / MAX_ENERGY) as usize;
        let energy_idx = match energy_pct {
            0..=24 => 0,
            25..=49 => 1,
            50..=74 => 2,
            75..=99 => 3,
            _ => 4,
        };

        bind_texture(assets().energy_bar[energy_idx]);
        draw_sprite(800.0, 10.0, 96.0, 12.0, 0xFFFFFFFF);

        // Overseer cursor (if local player is overseer)
        let cursor_x = (state.overseer_cursor_x * SCALE) as f32;
        let cursor_y = (state.overseer_cursor_y * SCALE) as f32;
        draw_rect(cursor_x - 5.0, cursor_y - 1.0, 10.0, 2.0, 0xFFFF0000);
        draw_rect(cursor_x - 1.0, cursor_y - 5.0, 2.0, 10.0, 0xFFFF0000);
    }
}

// ============================================================================
// ENTRY POINTS
// ============================================================================

#[no_mangle]
pub extern "C" fn init() {
    // Initialize state
    unsafe {
        GAME.write(GameState::new());
        ASSETS.write(Assets::new());
    }

    // Configure console
    unsafe {
        set_clear_color(0x0A0C0FFF); // Dark background (RRGGBBAA format)
        set_tick_rate(2); // 60fps
        texture_filter(0); // Nearest neighbor (pixelated)
        render_mode(RENDER_LAMBERT); // Mode 0: Lambert shading for flat-shaded 3D
    }

    // Create procedural meshes (must be done in init)
    // Each tile is 1 world unit (8 game pixels)
    let a = assets_mut();
    unsafe {
        // Floor: 1x1 plane on XZ, at Y=0
        a.mesh_floor = plane_uv(0.5, 0.5, 1, 1);

        // Wall: 1x1x1 cube (half-extent 0.5)
        a.mesh_wall = cube_uv(0.5, 0.5, 0.5);

        // Door: thin cube (0.8 wide, 1 tall, 0.1 deep)
        a.mesh_door = cube_uv(0.4, 0.5, 0.05);

        // Runner placeholder: capsule (will be replaced with proper mesh)
        a.mesh_runner = capsule(0.3, 0.8, 8, 4);

        // Drone placeholder: sphere
        a.mesh_drone = sphere(0.4, 12, 8);

        // Core placeholder: small cube
        a.mesh_core = cube_uv(0.25, 0.25, 0.25);

        // Trap meshes
        a.mesh_trap_spike = cylinder(0.1, 0.0, 0.6, 6); // Cone for spike
        a.mesh_trap_gas = plane_uv(0.5, 0.5, 1, 1);     // Flat for gas vent
        a.mesh_trap_laser = cube_uv(0.02, 0.5, 0.02);   // Thin beam for laser
    }

    // Load assets from ROM
    // Note: In a real build, these would use rom_texture() with asset IDs
    // For now, we'll leave handles as 0 (default texture)

    // Start at menu
    let state = game();
    state.phase = GamePhase::Menu;
}

#[no_mangle]
pub extern "C" fn update() {
    let state = game();

    match state.phase {
        GamePhase::Menu => {
            // Press A to start
            unsafe {
                if button_pressed(0, BTN_A) != 0 || button_pressed(1, BTN_A) != 0 {
                    start_round(state);
                }
            }
        }

        GamePhase::Playing => {
            // Update timer
            if state.round_timer > 0 {
                state.round_timer -= 1;

                if state.round_timer == 0 {
                    // Time's up - Overseer wins
                    state.phase = GamePhase::RoundEnd;
                    state.runners_win = false;
                    unsafe {
                        music_stop();
                        play_sound(assets().mus_defeat, 0.8, 0.0);
                    }
                }
            }

            // Update overseer
            update_overseer(state);

            // Get player count for AI decision
            let num_players = unsafe { player_count() };

            // Update runners (players 1, 2, 3 control runners)
            // If fewer than 4 players, AI controls the remaining runners
            for i in 0..MAX_RUNNERS {
                let player = (i + 1) as u32;

                // Determine input source: human or AI
                let input = if player < num_players {
                    // Human player controls this runner
                    get_player_input(player)
                } else {
                    // AI controls this runner
                    update_runner_ai(
                        &mut state.runner_ai[i],
                        &state.runners[i],
                        &state.tiles,
                        &state.traps[..state.trap_count as usize],
                        &state.cores,
                        state.cores_collected,
                        state.extract_x,
                        state.extract_y,
                    )
                };

                update_runner(&mut state.runners[i], &input, &state.tiles);
            }

            // Update drones
            update_drones(state);

            // Update traps
            update_traps(state);

            // Update doors
            update_doors(state);

            // Check collisions and win conditions
            check_collisions(state);

            // Check if all runners dead
            if state.runners_alive == 0 {
                state.phase = GamePhase::RoundEnd;
                state.runners_win = false;
                unsafe {
                    music_stop();
                    play_sound(assets().mus_defeat, 0.8, 0.0);
                }
            }
        }

        GamePhase::RoundEnd => {
            // Press A to restart
            unsafe {
                if button_pressed(0, BTN_A) != 0 || button_pressed(1, BTN_A) != 0 {
                    start_round(state);
                }
            }
        }
    }
}

#[no_mangle]
pub extern "C" fn render() {
    let state = game();
    let cam = camera();

    match state.phase {
        GamePhase::Menu => {
            // Title screen - use 2D rendering
            draw_text_str("OVERRIDE", 380.0, 200.0, 48.0, 0xFFFFFFFF);
            draw_text_str("PRESS A TO START", 340.0, 300.0, 24.0, 0x888888FF);
        }

        GamePhase::Playing => {
            // Determine local player's role
            let local_mask = unsafe { local_player_mask() };
            let (is_overseer, runner_idx) = get_local_role(local_mask, state.overseer_player);

            // Setup camera based on role
            if is_overseer {
                // Overseer: god-view from above
                let facility_center_x = (FACILITY_WIDTH as f32 / 2.0) * (TILE_SIZE as f32 / 8.0);
                let facility_center_z = (FACILITY_HEIGHT as f32 / 2.0) * (TILE_SIZE as f32 / 8.0);
                setup_overseer_camera(cam, facility_center_x, facility_center_z);
            } else {
                // Runner: third-person chase cam
                let runner = &state.runners[runner_idx];
                if runner.state != RunnerState::Dead {
                    setup_runner_camera(cam, runner.x, runner.y, runner.facing_x, runner.facing_y);
                } else {
                    // Dead runners: spectate another runner or overseer view
                    // Find first alive runner to spectate
                    let mut found = false;
                    for (i, r) in state.runners.iter().enumerate() {
                        if r.state != RunnerState::Dead {
                            setup_runner_camera(cam, r.x, r.y, r.facing_x, r.facing_y);
                            found = true;
                            break;
                        }
                    }
                    if !found {
                        // All dead - show overseer view
                        let facility_center_x = (FACILITY_WIDTH as f32 / 2.0) * (TILE_SIZE as f32 / 8.0);
                        let facility_center_z = (FACILITY_HEIGHT as f32 / 2.0) * (TILE_SIZE as f32 / 8.0);
                        setup_overseer_camera(cam, facility_center_x, facility_center_z);
                    }
                }
            }

            // Draw environment (sets up atmosphere/fog)
            unsafe { draw_env(); }

            // Render game world (currently 2D sprites, will become 3D meshes)
            render_facility(state);
            render_traps(state);
            render_cores(state);
            render_runners(state);
            render_drones(state);

            // Render UI overlay (2D, rendered last)
            unsafe { layer(100); } // UI on top layer
            render_ui(state);
        }

        GamePhase::RoundEnd => {
            // Show results - reuse playing camera
            let local_mask = unsafe { local_player_mask() };
            let (is_overseer, _) = get_local_role(local_mask, state.overseer_player);

            if is_overseer {
                let facility_center_x = (FACILITY_WIDTH as f32 / 2.0) * (TILE_SIZE as f32 / 8.0);
                let facility_center_z = (FACILITY_HEIGHT as f32 / 2.0) * (TILE_SIZE as f32 / 8.0);
                setup_overseer_camera(cam, facility_center_x, facility_center_z);
            }

            unsafe { draw_env(); }

            render_facility(state);
            render_traps(state);
            render_cores(state);
            render_runners(state);
            render_drones(state);

            // Victory/defeat overlay
            unsafe { layer(100); }
            if state.runners_win {
                draw_text_str("RUNNERS WIN!", 340.0, 250.0, 36.0, 0x00FF88FF);
            } else {
                draw_text_str("OVERSEER WINS!", 320.0, 250.0, 36.0, 0xFF3333FF);
            }
            draw_text_str("PRESS A TO PLAY AGAIN", 300.0, 320.0, 24.0, 0x888888FF);
        }
    }
}

// ============================================================================
// PANIC HANDLER (required for no_std)
// ============================================================================

#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}
