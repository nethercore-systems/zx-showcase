//! Asset generation using per-game generation/ directories
//!
//! Each game has its own generation/generate_all.py script

use crate::config::{discover_games, AssetStrategy, GameConfig};
use anyhow::{bail, Context, Result};
use colored::Colorize;
use std::path::PathBuf;
use std::process::Command;

/// Find Python executable
pub fn find_python() -> Result<PathBuf> {
    // Try python3 first (Unix/macOS), then python (Windows)
    for cmd in ["python", "python3"] {
        if let Ok(path) = which::which(cmd) {
            return Ok(path);
        }
    }
    bail!("Python not found. Install Python 3.8+ and add to PATH.")
}

/// Find Blender executable (still needed for some generators)
pub fn find_blender() -> Result<PathBuf> {
    // Try which first
    if let Ok(path) = which::which("blender") {
        return Ok(path);
    }

    #[cfg(windows)]
    let candidates = [
        "C:\\Program Files\\Blender Foundation\\Blender 5.0\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.3\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.1\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe",
    ];

    #[cfg(not(windows))]
    let candidates = [
        "/usr/bin/blender",
        "/usr/local/bin/blender",
        "/Applications/Blender.app/Contents/MacOS/Blender",
    ];

    for candidate in candidates {
        let path = PathBuf::from(candidate);
        if path.exists() {
            return Ok(path);
        }
    }

    bail!(
        "Blender not found. Install Blender 4.0+ and add to PATH.\n\
         Download: https://www.blender.org/download/"
    )
}

/// Generate assets for a specific game or all games
pub fn generate_assets(game_filter: Option<&str>) -> Result<()> {
    let root = crate::project_root();
    let games = discover_games(&root)?;
    let python = find_python()?;
    let blender_result = find_blender();

    println!("{}", "Asset Generation (Per-Game)".bold());
    println!("{}", "===========================".dimmed());
    println!("Using Python: {}", python.display());
    if let Ok(blender) = &blender_result {
        println!("Using Blender: {}", blender.display());
    } else {
        println!("{}", "Warning: Blender not found (needed for mesh generation)".yellow());
    }
    println!();

    let mut success_count = 0;
    let mut skip_count = 0;
    let mut fail_count = 0;

    for game in &games {
        if let Some(filter) = game_filter {
            if game.id != filter {
                continue;
            }
        }

        print!("  {} ... ", game.id.bold());

        match generate_for_game(game, &python) {
            Ok(GenerateResult::Generated) => {
                println!("{}", "OK".green());
                success_count += 1;
            }
            Ok(GenerateResult::Skipped(reason)) => {
                println!("{} ({})", "SKIPPED".yellow(), reason);
                skip_count += 1;
            }
            Ok(GenerateResult::NeedsManual(msg)) => {
                println!("{}", "NEEDS SETUP".yellow().bold());
                println!("      {}", msg.dimmed());
                skip_count += 1;
            }
            Err(e) => {
                println!("{} - {}", "FAILED".red(), e);
                fail_count += 1;
            }
        }
    }

    println!();
    println!("{}", "Summary".bold());
    println!("  Generated: {}", success_count.to_string().green());
    println!("  Skipped: {}", skip_count.to_string().yellow());
    if fail_count > 0 {
        println!("  Failed: {}", fail_count.to_string().red());
    }

    Ok(())
}

pub enum GenerateResult {
    Generated,
    Skipped(String),
    NeedsManual(String),
}

pub fn generate_for_game(game: &GameConfig, python: &PathBuf) -> Result<GenerateResult> {
    match &game.asset_strategy {
        AssetStrategy::BuildRs => {
            // build.rs generates assets during cargo build - nothing to do here
            Ok(GenerateResult::Skipped(
                "build.rs handles asset generation".to_string(),
            ))
        }

        AssetStrategy::BlenderPipeline => run_game_generator(game, python),

        AssetStrategy::StandaloneTool { .. } => run_game_generator(game, python),

        AssetStrategy::None => {
            // Check if game has generation/generate_all.py
            let generate_all = game.path.join("generation").join("generate_all.py");
            if generate_all.exists() {
                run_game_generator(game, python)
            } else if game.has_assets() {
                Ok(GenerateResult::Skipped("assets already exist".to_string()))
            } else {
                Ok(GenerateResult::NeedsManual(
                    "Add generation/generate_all.py script".to_string(),
                ))
            }
        }
    }
}

/// Run the game's generation/generate_all.py script
fn run_game_generator(game: &GameConfig, python: &PathBuf) -> Result<GenerateResult> {
    let generate_all = game.path.join("generation").join("generate_all.py");

    if !generate_all.exists() {
        return Ok(GenerateResult::NeedsManual(format!(
            "Game '{}' missing generation/generate_all.py",
            game.id
        )));
    }

    println!();
    println!("      Running: python generation/generate_all.py");

    let output = Command::new(python)
        .arg(generate_all.to_str().unwrap())
        .current_dir(&game.path)
        .output()
        .context("Failed to run Python generator")?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    // Print output for visibility
    if !stdout.is_empty() {
        for line in stdout.lines().take(20) {
            println!("      {}", line.dimmed());
        }
        if stdout.lines().count() > 20 {
            println!("      ... ({} more lines)", stdout.lines().count() - 20);
        }
    }

    if !output.status.success() {
        // Check if it's a "not implemented" error vs actual failure
        if stderr.contains("not fully implemented") || stdout.contains("not fully implemented") {
            return Ok(GenerateResult::NeedsManual(format!(
                "Game '{}' generator not yet implemented",
                game.id
            )));
        }

        bail!(
            "Asset generation failed:\nstdout: {}\nstderr: {}",
            stdout,
            stderr
        );
    }

    Ok(GenerateResult::Generated)
}
