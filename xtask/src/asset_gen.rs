//! Asset generation using unified Blender + Python pipeline
//!
//! All asset generation uses: blender --background --python run_blender.py -- --game <game> --all
//! This ensures GLB output, metaball support for organics, and consistent pipeline.

use crate::config::{discover_games, AssetStrategy, GameConfig};
use anyhow::{bail, Context, Result};
use colored::Colorize;
use std::path::PathBuf;
use std::process::Command;

/// Find Blender executable
pub fn find_blender() -> Result<PathBuf> {
    // Try which first
    if let Ok(path) = which::which("blender") {
        return Ok(path);
    }

    #[cfg(windows)]
    let candidates = [
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
    let blender = find_blender()?;

    println!("{}", "Asset Generation (Blender + Python)".bold());
    println!("{}", "====================================".dimmed());
    println!("Using Blender: {}", blender.display());
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

        match generate_for_game(game, &blender) {
            Ok(GenerateResult::Generated) => {
                println!("{}", "OK".green());
                success_count += 1;
            }
            Ok(GenerateResult::Skipped(reason)) => {
                println!("{} ({})", "SKIPPED".yellow(), reason);
                skip_count += 1;
            }
            Ok(GenerateResult::NeedsManual(msg)) => {
                println!("{}", "NEEDS BLENDER GENERATOR".yellow().bold());
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

pub fn generate_for_game(game: &GameConfig, blender: &PathBuf) -> Result<GenerateResult> {
    match &game.asset_strategy {
        AssetStrategy::BuildRs => {
            // build.rs generates assets during cargo build - nothing to do here
            Ok(GenerateResult::Skipped(
                "build.rs handles asset generation".to_string(),
            ))
        }

        AssetStrategy::BlenderPipeline => run_blender_pipeline(game, blender),

        AssetStrategy::StandaloneTool { .. } => {
            // Legacy - redirect to Blender pipeline
            run_blender_pipeline(game, blender)
        }

        AssetStrategy::None => {
            // Try Blender pipeline, fall back if not implemented
            match run_blender_pipeline(game, blender) {
                Ok(result) => Ok(result),
                Err(_) => {
                    if game.has_assets() {
                        Ok(GenerateResult::Skipped("assets already exist".to_string()))
                    } else {
                        Ok(GenerateResult::NeedsManual(
                            "Add Blender generator in procgen/games/".to_string(),
                        ))
                    }
                }
            }
        }
    }
}

/// Run the unified Blender + Python asset generation pipeline
fn run_blender_pipeline(game: &GameConfig, blender: &PathBuf) -> Result<GenerateResult> {
    let root = crate::project_root();
    let run_blender_py = root.join("procgen").join("run_blender.py");

    if !run_blender_py.exists() {
        bail!("run_blender.py not found at {}", run_blender_py.display());
    }

    println!();
    println!(
        "      Running: blender --background --python run_blender.py -- --game {} --all",
        game.id
    );

    let output = Command::new(blender)
        .args([
            "--background",
            "--python",
            run_blender_py.to_str().unwrap(),
            "--",
            "--game",
            &game.id,
            "--all",
        ])
        .current_dir(&root)
        .output()
        .context("Failed to run Blender")?;

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
                "Game '{}' Blender generator not yet implemented",
                game.id
            )));
        }

        bail!(
            "Blender asset generation failed:\nstdout: {}\nstderr: {}",
            stdout,
            stderr
        );
    }

    Ok(GenerateResult::Generated)
}
