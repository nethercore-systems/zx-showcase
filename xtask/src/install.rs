//! Installation to ~/.nethercore/games/

use crate::config::{discover_games, GameConfig};
use anyhow::{Context, Result};
use colored::Colorize;
use serde_json::json;
use std::fs;
use std::path::PathBuf;

/// Get the games installation directory
fn games_dir() -> Result<PathBuf> {
    let dirs = directories::ProjectDirs::from("", "", "Nethercore")
        .context("Failed to determine data directory")?;
    Ok(dirs.data_dir().join("games"))
}

/// Install all or a specific game
pub fn install_games(game_filter: Option<&str>) -> Result<()> {
    let root = crate::project_root();
    let games = discover_games(&root)?;
    let install_dir = games_dir()?;

    fs::create_dir_all(&install_dir).context("Failed to create games directory")?;

    println!("Installing to: {}", install_dir.display());
    println!();

    let mut installed = 0;
    let mut skipped = 0;

    for game in &games {
        if let Some(filter) = game_filter {
            if game.id != filter {
                continue;
            }
        }

        match install_single_game(game) {
            Ok(true) => {
                println!("  {} {}", "OK".green(), game.id);
                installed += 1;
            }
            Ok(false) => {
                println!("  {} {} (not built)", "SKIP".yellow(), game.id);
                skipped += 1;
            }
            Err(e) => {
                println!("  {} {} - {}", "FAILED".red(), game.id, e);
            }
        }
    }

    println!();
    println!("Installed: {}", installed.to_string().green());
    if skipped > 0 {
        println!("Skipped: {}", skipped.to_string().yellow());
    }

    Ok(())
}

/// Install a single game, returns Ok(false) if game wasn't built
pub fn install_single_game(game: &GameConfig) -> Result<bool> {
    let install_dir = games_dir()?;
    let rom_filename = format!("{}.nczx", game.id);
    let rom_path = game.path.join(&rom_filename);

    if !rom_path.exists() {
        return Ok(false);
    }

    let game_install_dir = install_dir.join(&game.id);
    fs::create_dir_all(&game_install_dir)?;

    // Copy ROM (install as rom.nczx to match player expectations)
    let dest_rom = game_install_dir.join("rom.nczx");
    fs::copy(&rom_path, &dest_rom).context(format!("Failed to copy ROM for {}", game.id))?;

    // Load metadata from nether.toml if available
    let (title, author, version, description) = if let Ok(meta) = game.load_metadata() {
        (
            meta.game.title,
            meta.game.author,
            meta.game.version,
            meta.game.description,
        )
    } else {
        (
            game.title.clone(),
            "ZX Showcase".to_string(),
            "1.0.0".to_string(),
            String::new(),
        )
    };

    // Create manifest.json
    let manifest = json!({
        "id": game.id,
        "title": title,
        "author": author,
        "version": version,
        "description": description,
        "downloaded_at": chrono::Utc::now().to_rfc3339()
    });

    let manifest_path = game_install_dir.join("manifest.json");
    fs::write(&manifest_path, serde_json::to_string_pretty(&manifest)?)
        .context("Failed to write manifest")?;

    Ok(true)
}
