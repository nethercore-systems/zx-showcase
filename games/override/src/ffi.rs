// Nethercore ZX FFI Bindings (minimal subset for OVERRIDE)
// Updated to match canonical source: nethercore/include/zx.rs

#![allow(unused)]

// Button constants
pub const BTN_UP: u32 = 0;
pub const BTN_DOWN: u32 = 1;
pub const BTN_LEFT: u32 = 2;
pub const BTN_RIGHT: u32 = 3;
pub const BTN_A: u32 = 4;
pub const BTN_B: u32 = 5;
pub const BTN_X: u32 = 6;
pub const BTN_Y: u32 = 7;
pub const BTN_L1: u32 = 8;
pub const BTN_R1: u32 = 9;
pub const BTN_L3: u32 = 10;
pub const BTN_R3: u32 = 11;
pub const BTN_START: u32 = 12;
pub const BTN_SELECT: u32 = 13;

// Render mode constants
pub const RENDER_LAMBERT: u32 = 0;
pub const RENDER_MATCAP: u32 = 1;
pub const RENDER_PBR: u32 = 2;
pub const RENDER_HYBRID: u32 = 3;

#[link(wasm_import_module = "env")]
extern "C" {
    // =========================================================================
    // System Functions
    // =========================================================================
    pub fn delta_time() -> f32;
    pub fn elapsed_time() -> f32;
    pub fn tick_count() -> u64;
    pub fn log(ptr: *const u8, len: u32);
    pub fn quit();

    // Rollback-safe random
    pub fn random() -> u32;
    pub fn random_range(min: i32, max: i32) -> i32;
    pub fn random_f32() -> f32;

    // Session
    pub fn player_count() -> u32;
    pub fn local_player_mask() -> u32;

    // =========================================================================
    // Configuration (init-only)
    // =========================================================================
    pub fn set_tick_rate(rate: u32);
    pub fn set_clear_color(color: u32);
    pub fn render_mode(mode: u32);

    // =========================================================================
    // Input - Buttons
    // =========================================================================
    pub fn button_held(player: u32, button: u32) -> u32;
    pub fn button_pressed(player: u32, button: u32) -> u32;
    pub fn button_released(player: u32, button: u32) -> u32;
    pub fn buttons_held(player: u32) -> u32;
    pub fn buttons_pressed(player: u32) -> u32;

    // Input - analog
    pub fn left_stick_x(player: u32) -> f32;
    pub fn left_stick_y(player: u32) -> f32;
    pub fn right_stick_x(player: u32) -> f32;
    pub fn right_stick_y(player: u32) -> f32;

    // =========================================================================
    // Camera Functions
    // =========================================================================
    /// Set camera position and look-at target
    pub fn camera_set(x: f32, y: f32, z: f32, target_x: f32, target_y: f32, target_z: f32);
    /// Set field of view in degrees
    pub fn camera_fov(fov_degrees: f32);
    /// Push custom projection matrix (16 floats, column-major)
    pub fn push_projection_matrix(
        m0: f32, m1: f32, m2: f32, m3: f32,
        m4: f32, m5: f32, m6: f32, m7: f32,
        m8: f32, m9: f32, m10: f32, m11: f32,
        m12: f32, m13: f32, m14: f32, m15: f32,
    );

    // =========================================================================
    // Transform Functions
    // =========================================================================
    pub fn push_identity();
    pub fn push_translate(x: f32, y: f32, z: f32);
    pub fn push_rotate_x(angle_deg: f32);
    pub fn push_rotate_y(angle_deg: f32);
    pub fn push_rotate_z(angle_deg: f32);
    pub fn push_rotate(angle_deg: f32, axis_x: f32, axis_y: f32, axis_z: f32);
    pub fn push_scale(x: f32, y: f32, z: f32);
    pub fn push_scale_uniform(s: f32);

    // =========================================================================
    // Render State
    // =========================================================================
    pub fn set_color(color: u32);
    pub fn depth_test(enabled: u32);
    pub fn cull_mode(mode: u32);
    pub fn texture_filter(filter: u32);
    pub fn uniform_alpha(level: u32);
    pub fn layer(n: u32);

    // =========================================================================
    // Environment Rendering (EPU)
    // =========================================================================
    pub fn draw_env();

    /// Gradient environment (sky/ground)
    pub fn env_gradient(layer: u32, zenith: u32, sky_horizon: u32, ground_horizon: u32, nadir: u32, rotation: f32, shift: f32);

    /// Room environment (interior with lighting)
    pub fn env_room(layer: u32, color_ceiling: u32, color_floor: u32, color_walls: u32, panel_size: f32, panel_gap: u32,
                    light_dir_x: f32, light_dir_y: f32, light_dir_z: f32, light_intensity: u32,
                    corner_darken: u32, room_scale: f32, viewer_x: i32, viewer_y: i32, viewer_z: i32);

    // =========================================================================
    // Texture Functions
    // =========================================================================
    pub fn load_texture(width: u32, height: u32, pixels_ptr: *const u8) -> u32;
    pub fn texture_bind(handle: u32);
    // Alias for legacy code
    #[link_name = "texture_bind"]
    pub fn bind_texture(handle: u32);

    // =========================================================================
    // Mesh Functions
    // =========================================================================
    pub fn load_mesh(data_ptr: *const f32, vertex_count: u32, format: u32) -> u32;
    pub fn draw_mesh(handle: u32);

    // Procedural meshes (init-only)
    pub fn cube(size_x: f32, size_y: f32, size_z: f32) -> u32;
    pub fn sphere(radius: f32, segments: u32, rings: u32) -> u32;
    pub fn cylinder(radius_bottom: f32, radius_top: f32, height: f32, segments: u32) -> u32;
    pub fn plane(size_x: f32, size_z: f32, subdivisions_x: u32, subdivisions_z: u32) -> u32;
    pub fn capsule(radius: f32, height: f32, segments: u32, rings: u32) -> u32;

    // UV variants
    pub fn cube_uv(size_x: f32, size_y: f32, size_z: f32) -> u32;
    pub fn plane_uv(size_x: f32, size_z: f32, subdivisions_x: u32, subdivisions_z: u32) -> u32;
    pub fn capsule_uv(radius: f32, height: f32, segments: u32, rings: u32) -> u32;

    // =========================================================================
    // 2D Drawing
    // =========================================================================
    pub fn draw_sprite(x: f32, y: f32, w: f32, h: f32, color: u32);
    pub fn draw_sprite_region(
        x: f32, y: f32, w: f32, h: f32,
        src_x: f32, src_y: f32, src_w: f32, src_h: f32,
        color: u32
    );
    pub fn draw_rect(x: f32, y: f32, w: f32, h: f32, color: u32);
    pub fn draw_text(ptr: *const u8, len: u32, x: f32, y: f32, size: f32, color: u32);
    pub fn draw_line(x1: f32, y1: f32, x2: f32, y2: f32, thickness: f32, color: u32);
    pub fn draw_circle(x: f32, y: f32, radius: f32, color: u32);

    // =========================================================================
    // Billboard Drawing
    // =========================================================================
    pub fn draw_billboard(w: f32, h: f32, mode: u32, color: u32);

    // =========================================================================
    // Audio
    // =========================================================================
    pub fn load_sound(data_ptr: *const i16, byte_len: u32) -> u32;
    pub fn play_sound(sound: u32, volume: f32, pan: f32);
    pub fn music_play(handle: u32, volume: f32, looping: u32);
    pub fn music_stop();
    pub fn music_set_volume(volume: f32);

    // =========================================================================
    // ROM Loading (init-only)
    // =========================================================================
    pub fn rom_texture(id_ptr: u32, id_len: u32) -> u32;
    pub fn rom_mesh(id_ptr: u32, id_len: u32) -> u32;
    pub fn rom_sound(id_ptr: u32, id_len: u32) -> u32;
}

// =========================================================================
// Helper Functions
// =========================================================================

/// Helper to draw text from a string slice
#[inline]
pub fn draw_text_str(s: &str, x: f32, y: f32, size: f32, color: u32) {
    unsafe {
        draw_text(s.as_ptr(), s.len() as u32, x, y, size, color);
    }
}

/// Helper to log a string slice
#[inline]
pub fn log_str(s: &str) {
    unsafe {
        log(s.as_ptr(), s.len() as u32);
    }
}
