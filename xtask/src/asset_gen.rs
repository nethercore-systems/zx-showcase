//! Asset generation for different game types

use crate::config::{discover_games, AssetStrategy, GameConfig};
use anyhow::{bail, Context, Result};
use colored::Colorize;
use std::path::Path;
use std::process::Command;

/// Generate assets for a specific game or all games
pub fn generate_assets(game_filter: Option<&str>) -> Result<()> {
    let root = crate::project_root();
    let games = discover_games(&root)?;

    println!("{}", "Asset Generation".bold());
    println!("{}", "================".dimmed());
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

        match generate_for_game(game) {
            Ok(GenerateResult::Generated) => {
                println!("{}", "OK".green());
                success_count += 1;
            }
            Ok(GenerateResult::Skipped(reason)) => {
                println!("{} ({})", "SKIPPED".yellow(), reason);
                skip_count += 1;
            }
            Ok(GenerateResult::NeedsManual(msg)) => {
                println!("{}", "NEEDS MANUAL".yellow().bold());
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

pub fn generate_for_game(game: &GameConfig) -> Result<GenerateResult> {
    match &game.asset_strategy {
        AssetStrategy::BuildRs => {
            // build.rs generates assets during cargo build - nothing to do here
            Ok(GenerateResult::Skipped(
                "build.rs handles asset generation".to_string(),
            ))
        }

        AssetStrategy::StandaloneTool { tool_path } => {
            run_standalone_asset_gen(tool_path, game)
        }

        AssetStrategy::None => {
            // Check if assets already exist
            if game.has_assets() {
                Ok(GenerateResult::Skipped("assets already exist".to_string()))
            } else {
                Ok(GenerateResult::NeedsManual(
                    "Use nethercore-ai-plugins /generate-asset to create assets".to_string(),
                ))
            }
        }
    }
}

/// Run the standalone asset generator tool (e.g., prism-survivors/tools/asset-gen)
fn run_standalone_asset_gen(tool_path: &Path, _game: &GameConfig) -> Result<GenerateResult> {
    if !tool_path.join("Cargo.toml").exists() {
        bail!(
            "Asset generator not found at {}",
            tool_path.display()
        );
    }

    println!();
    println!("      Running: cargo run --release in {}", tool_path.display());

    let output = Command::new("cargo")
        .args(["run", "--release"])
        .current_dir(tool_path)
        .output()
        .context("Failed to run asset generator")?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        let stdout = String::from_utf8_lossy(&output.stdout);
        bail!(
            "Asset generator failed:\nstdout: {}\nstderr: {}",
            stdout,
            stderr
        );
    }

    Ok(GenerateResult::Generated)
}
