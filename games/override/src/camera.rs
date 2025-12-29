//! Camera system for OVERRIDE - dual perspective handling
//!
//! Runner cameras: Low-angle third-person chase cam
//! Overseer camera: Elevated orthographic god-view

use crate::ffi::*;

// =============================================================================
// CAMERA CONFIGURATION
// =============================================================================

/// Runner camera: 8 units behind, 3 above, looking at chest height
const RUNNER_OFFSET_BACK: f32 = 8.0;
const RUNNER_OFFSET_UP: f32 = 3.0;
const RUNNER_LOOK_HEIGHT: f32 = 1.0;
const RUNNER_FOV: f32 = 70.0;

/// Smooth follow lerp rates (per frame at 60fps)
const POS_LERP: f32 = 0.15;
const ROT_LERP: f32 = 0.08;

/// Overseer camera: 60 units above, orthographic
const OVERSEER_HEIGHT: f32 = 60.0;
const OVERSEER_ORTHO_WIDTH: f32 = 60.0;

/// Fog for runner view limiting (20-40 unit fade)
const FOG_NEAR: f32 = 20.0;
const FOG_FAR: f32 = 40.0;
const FOG_COLOR: u32 = 0x0A0C0FFF; // Match clear color

// =============================================================================
// CAMERA STATE (Render-only, NOT part of rollback state)
// =============================================================================

/// Camera interpolation state - uses floats for smooth rendering
/// This is NOT serialized for rollback - it's purely visual
#[derive(Clone, Copy)]
pub struct CameraState {
    // Current interpolated values
    pub pos_x: f32,
    pub pos_y: f32,
    pub pos_z: f32,
    pub target_x: f32,
    pub target_y: f32,
    pub target_z: f32,
}

impl CameraState {
    pub const fn new() -> Self {
        Self {
            pos_x: 0.0,
            pos_y: 10.0,
            pos_z: -20.0,
            target_x: 0.0,
            target_y: 0.0,
            target_z: 0.0,
        }
    }

    /// Smoothly interpolate position toward target
    fn lerp_toward(&mut self,
        target_pos_x: f32, target_pos_y: f32, target_pos_z: f32,
        target_look_x: f32, target_look_y: f32, target_look_z: f32,
        pos_rate: f32, rot_rate: f32
    ) {
        // Position lerp
        self.pos_x += (target_pos_x - self.pos_x) * pos_rate;
        self.pos_y += (target_pos_y - self.pos_y) * pos_rate;
        self.pos_z += (target_pos_z - self.pos_z) * pos_rate;

        // Target lerp
        self.target_x += (target_look_x - self.target_x) * rot_rate;
        self.target_y += (target_look_y - self.target_y) * rot_rate;
        self.target_z += (target_look_z - self.target_z) * rot_rate;
    }

    /// Apply camera to ZX graphics system
    fn apply(&self, fov: f32) {
        unsafe {
            camera_set(
                self.pos_x, self.pos_y, self.pos_z,
                self.target_x, self.target_y, self.target_z
            );
            camera_fov(fov);
        }
    }
}

// =============================================================================
// CAMERA SETUP FUNCTIONS
// =============================================================================

/// Tile size in game pixels
const TILE_SIZE: i32 = 8;

/// Convert fixed-point pixel position to world-space coordinates
/// Runner positions are in Q24.8 fixed-point pixels
/// 1 tile = 8 pixels = 1 world unit in 3D
fn fixed_to_world(fixed_pos: i32) -> f32 {
    // Q24.8 fixed point: value = fixed_pos / 256.0 (in pixels)
    // World unit = pixels / TILE_SIZE
    let pixels = fixed_pos as f32 / 256.0;
    pixels / TILE_SIZE as f32
}

/// Setup runner third-person camera
///
/// Positioned behind and above the runner, smoothly following.
/// FOV 70°, with fog limiting view distance.
pub fn setup_runner_camera(
    camera: &mut CameraState,
    runner_x: i32,      // Q24.8 fixed-point X position
    runner_y: i32,      // Q24.8 fixed-point Y position
    facing_x: i8,       // Facing direction -1/0/1
    facing_y: i8,       // Facing direction -1/0/1
) {
    // Convert runner position to world space
    let world_x = fixed_to_world(runner_x);
    let world_z = fixed_to_world(runner_y); // Y in 2D = Z in 3D (depth)

    // Calculate camera offset based on facing direction
    // Camera positioned behind the runner
    // Use sign-based offset since facing is just -1/0/1
    let (offset_x, offset_z) = match (facing_x, facing_y) {
        (0, 0) => (0.0, -RUNNER_OFFSET_BACK), // Default: camera behind (negative Z)
        (fx, 0) => (-(fx as f32) * RUNNER_OFFSET_BACK, 0.0), // Pure X facing
        (0, fy) => (0.0, -(fy as f32) * RUNNER_OFFSET_BACK), // Pure Y facing
        (fx, fy) => {
            // Diagonal - split offset between both axes (approximate 45°)
            let half_offset = RUNNER_OFFSET_BACK * 0.707; // ~1/sqrt(2)
            (-(fx as f32) * half_offset, -(fy as f32) * half_offset)
        }
    };

    // Target camera position: behind and above runner
    let target_pos_x = world_x + offset_x;
    let target_pos_y = RUNNER_OFFSET_UP;
    let target_pos_z = world_z + offset_z;

    // Look at runner's chest
    let target_look_x = world_x;
    let target_look_y = RUNNER_LOOK_HEIGHT;
    let target_look_z = world_z;

    // Smooth interpolation
    camera.lerp_toward(
        target_pos_x, target_pos_y, target_pos_z,
        target_look_x, target_look_y, target_look_z,
        POS_LERP, ROT_LERP
    );

    // Apply camera
    camera.apply(RUNNER_FOV);

    // Setup fog for view limiting
    // Note: Using env_room for atmospheric fog effect
    unsafe {
        // Configure room environment to create fog effect
        // This gives us distance-based visibility limiting
        env_room(
            0,                    // layer 0 (base)
            0x0A0C0F00,          // ceiling color (dark)
            0x0A0C0F00,          // floor color (dark)
            0x1A1A2E00,          // wall color (slightly lighter)
            10.0,                 // panel size
            8,                    // panel gap
            0.0, -1.0, 0.0,      // light direction (from above)
            64,                   // light intensity
            128,                  // corner darkening
            100.0,               // room scale (large)
            0, 0, 0              // viewer at center
        );
    }
}

/// Setup overseer orthographic camera
///
/// High above the facility looking straight down.
/// Orthographic projection to see the whole map.
pub fn setup_overseer_camera(camera: &mut CameraState, facility_center_x: f32, facility_center_z: f32) {
    // Position directly above facility center
    let target_pos_x = facility_center_x;
    let target_pos_y = OVERSEER_HEIGHT;
    let target_pos_z = facility_center_z;

    // Look straight down at facility
    let target_look_x = facility_center_x;
    let target_look_y = 0.0;
    let target_look_z = facility_center_z;

    // Instant positioning for overseer (no lerp)
    camera.pos_x = target_pos_x;
    camera.pos_y = target_pos_y;
    camera.pos_z = target_pos_z;
    camera.target_x = target_look_x;
    camera.target_y = target_look_y;
    camera.target_z = target_look_z;

    // Apply perspective camera but with very low FOV for near-ortho effect
    // True ortho would need push_projection_matrix
    camera.apply(15.0); // Low FOV approximates orthographic

    // No fog for overseer - they see everything
    unsafe {
        // Use simple gradient environment (no fog)
        env_gradient(
            0,                    // layer 0
            0x0A0C0FFF,          // zenith (dark)
            0x1A1A2EFF,          // sky horizon
            0x1A1A2EFF,          // ground horizon
            0x0A0C0FFF,          // nadir (dark)
            0.0,                  // no rotation
            0.0                   // horizon at center
        );
    }
}

/// Get the local player's role and runner index
/// Returns (is_overseer, runner_index)
pub fn get_local_role(local_player_mask: u32, overseer_player: u32) -> (bool, usize) {
    // Check each player bit in mask
    for player in 0..4u32 {
        if (local_player_mask & (1 << player)) != 0 {
            if player == overseer_player {
                return (true, 0); // This local player is overseer
            } else {
                // Runner index: player 0 is overseer, so runner indices are player-1
                // But if overseer is player 0, runners are 1,2,3 → indices 0,1,2
                // If overseer is player 2, runners are 0,1,3 → need to remap
                let runner_idx = if player < overseer_player {
                    player as usize
                } else {
                    (player - 1) as usize
                };
                return (false, runner_idx.min(2));
            }
        }
    }
    // Default to runner 0 if nothing found
    (false, 0)
}
