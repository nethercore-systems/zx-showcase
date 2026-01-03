//! Build orchestration for games

use crate::asset_gen::find_python;
use crate::config::{discover_games, AssetStrategy, GameConfig};
use anyhow::{bail, Context, Result};
use colored::Colorize;
use rayon::prelude::*;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::atomic::{AtomicUsize, Ordering};

/// Find the nether CLI executable
fn find_nether_cli() -> Result<PathBuf> {
    // First check if it's in PATH
    if let Ok(path) = which::which("nether") {
        return Ok(path);
    }

    // Check in the parent nethercore project
    let root = crate::project_root();

    #[cfg(windows)]
    let possible_paths = [
        "../nethercore/target/release/nether.exe",
        "../nethercore/target/debug/nether.exe",
    ];

    #[cfg(not(windows))]
    let possible_paths = [
        "../nethercore/target/release/nether",
        "../nethercore/target/debug/nether",
    ];

    for rel_path in &possible_paths {
        let path = root.join(rel_path);
        if path.exists() {
            return Ok(path.canonicalize()?);
        }
    }

    bail!(
        "nether CLI not found. Please either:\n\
         1. Build it: cd ../nethercore && cargo build -p nether-cli --release\n\
         2. Add it to PATH\n\
         3. Install from: https://github.com/nethercore-systems/nethercore"
    )
}

/// Build all games
pub fn build_all(skip_assets: bool, parallel: bool) -> Result<()> {
    let root = crate::project_root();
    let games = discover_games(&root)?;
    let nether_exe = find_nether_cli()?;

    println!("{}", "ZX-Showcase Build".bold());
    println!("{}", "=================".dimmed());
    println!();
    println!("Found {} games to build", games.len());
    println!("Using nether CLI: {}", nether_exe.display());
    println!();

    // Asset generation phase
    if !skip_assets {
        println!("{}", "Phase 1: Asset Generation".bold());
        println!("{}", "-------------------------".dimmed());
        let python = find_python().ok();
        for game in &games {
            print!("  {} ... ", game.id);
            if let Some(ref python_path) = python {
                match crate::asset_gen::generate_for_game(game, python_path) {
                    Ok(_) => println!("{}", "OK".green()),
                    Err(e) => println!("{} - {}", "WARN".yellow(), e),
                }
            } else {
                println!("{} - Python not found", "SKIP".yellow());
            }
        }
        println!();
    }

    // Build phase
    println!("{}", "Phase 2: Build".bold());
    println!("{}", "--------------".dimmed());

    let success_count = AtomicUsize::new(0);
    let fail_count = AtomicUsize::new(0);
    let skip_count = AtomicUsize::new(0);

    let build_game_fn = |game: &GameConfig| {
        // Skip games without assets (unless they use build.rs which generates on build)
        if !matches!(game.asset_strategy, AssetStrategy::BuildRs) && !game.has_assets() {
            println!(
                "  {} {} (no assets)",
                "SKIP".yellow(),
                game.id
            );
            skip_count.fetch_add(1, Ordering::Relaxed);
            return;
        }

        match build_single_game(game, &nether_exe) {
            Ok(_) => {
                println!("  {} {}", "OK".green(), game.id);
                success_count.fetch_add(1, Ordering::Relaxed);
            }
            Err(e) => {
                println!("  {} {} - {}", "FAILED".red(), game.id, e);
                fail_count.fetch_add(1, Ordering::Relaxed);
            }
        }
    };

    if parallel {
        games.par_iter().for_each(build_game_fn);
    } else {
        games.iter().for_each(build_game_fn);
    }

    let success = success_count.load(Ordering::Relaxed);
    let failed = fail_count.load(Ordering::Relaxed);
    let skipped = skip_count.load(Ordering::Relaxed);

    println!();
    println!("{}", "Build Results".bold());
    println!("  Success: {}", success.to_string().green());
    if skipped > 0 {
        println!("  Skipped: {}", skipped.to_string().yellow());
    }
    if failed > 0 {
        println!("  Failed: {}", failed.to_string().red());
    }

    // Installation phase
    if success > 0 {
        println!();
        println!("{}", "Phase 3: Installation".bold());
        println!("{}", "---------------------".dimmed());
        crate::install::install_games(None)?;
    }

    if failed > 0 {
        bail!("{} game(s) failed to build", failed);
    }

    println!();
    println!("{}", "Build complete!".green().bold());

    Ok(())
}

/// Build a specific game
pub fn build_game(game_id: &str, skip_assets: bool) -> Result<()> {
    let root = crate::project_root();
    let games = discover_games(&root)?;
    let nether_exe = find_nether_cli()?;

    let game = games
        .iter()
        .find(|g| g.id == game_id)
        .context(format!("Game '{}' not found", game_id))?;

    println!("Building {}...", game.id.bold());

    if !skip_assets {
        println!("  Generating assets...");
        let python = find_python()?;
        crate::asset_gen::generate_for_game(game, &python)?;
    }

    println!("  Compiling and packing...");
    build_single_game(game, &nether_exe)?;

    println!("  Installing...");
    crate::install::install_single_game(game)?;

    println!("{}", "Done!".green());

    Ok(())
}

fn build_single_game(game: &GameConfig, nether_exe: &Path) -> Result<()> {
    if !game.nether_toml_path.exists() {
        bail!(
            "nether.toml not found at {}",
            game.nether_toml_path.display()
        );
    }

    // nether build compiles WASM and packs ROM
    let output = Command::new(nether_exe)
        .args(["build", "--manifest", "nether.toml"])
        .current_dir(&game.path)
        .output()
        .context("Failed to run nether build")?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        let stdout = String::from_utf8_lossy(&output.stdout);
        bail!("Build failed:\n{}\n{}", stdout, stderr);
    }

    // Verify {game_id}.nczx was created
    let rom_filename = format!("{}.nczx", game.id);
    let rom_path = game.path.join(&rom_filename);
    if !rom_path.exists() {
        bail!("Expected {} not found after build", rom_filename);
    }

    Ok(())
}

/// Clean all build artifacts
pub fn clean_all(clean_assets: bool) -> Result<()> {
    let root = crate::project_root();
    let games = discover_games(&root)?;

    println!("{}", "Cleaning ZX-Showcase".bold());
    println!("{}", "====================".dimmed());
    println!();

    for game in &games {
        print!("  {} ... ", game.id);

        // Clean cargo target
        let target_dir = game.path.join("target");
        if target_dir.exists() {
            std::fs::remove_dir_all(&target_dir).context("Failed to remove target dir")?;
        }

        // Clean ROM file ({game_id}.nczx)
        let rom_path = game.path.join(format!("{}.nczx", game.id));
        if rom_path.exists() {
            std::fs::remove_file(&rom_path)?;
        }

        // Optionally clean generated assets
        if clean_assets {
            match &game.asset_strategy {
                AssetStrategy::BuildRs => {
                    // build.rs generates to assets/
                    let assets_dir = game.path.join("assets");
                    if assets_dir.exists() {
                        std::fs::remove_dir_all(&assets_dir)?;
                    }
                }
                AssetStrategy::BlenderPipeline | AssetStrategy::StandaloneTool { .. } => {
                    // Blender/standalone generates to assets/models/
                    let models_dir = game.path.join("assets").join("models");
                    if models_dir.exists() {
                        std::fs::remove_dir_all(&models_dir)?;
                    }
                }
                AssetStrategy::None => {
                    // Don't clean manually created/procgen assets
                }
            }
        }

        println!("{}", "OK".green());
    }

    println!();
    println!("{}", "Clean complete!".green());

    Ok(())
}
