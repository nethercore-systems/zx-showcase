//! Game configuration and discovery

use anyhow::Result;
use colored::Colorize;
use serde::Deserialize;
use std::path::{Path, PathBuf};

/// Asset generation strategy for a game
#[derive(Debug, Clone)]
pub enum AssetStrategy {
    /// Assets generated in build.rs (Override)
    BuildRs,
    /// Standalone tool must be run first (Prism Survivors)
    StandaloneTool { tool_path: PathBuf },
    /// No asset generation - needs procgen or manual creation
    None,
}

#[derive(Debug, Clone)]
pub struct GameConfig {
    pub id: String,
    pub title: String,
    pub path: PathBuf,
    pub asset_strategy: AssetStrategy,
    pub nether_toml_path: PathBuf,
}

/// nether.toml structure (partial - just what we need)
#[derive(Debug, Deserialize)]
pub struct NetherToml {
    pub game: GameMetadata,
}

#[derive(Debug, Deserialize)]
#[allow(dead_code)]
pub struct GameMetadata {
    pub id: String,
    pub title: String,
    #[serde(default)]
    pub author: String,
    #[serde(default)]
    pub version: String,
    #[serde(default)]
    pub description: String,
}

impl GameConfig {
    /// Check if assets exist for this game
    pub fn has_assets(&self) -> bool {
        let assets_dir = self.path.join("assets");
        if !assets_dir.exists() {
            return false;
        }

        // Check for any files in assets directory (recursively)
        walkdir::WalkDir::new(&assets_dir)
            .into_iter()
            .filter_map(|e| e.ok())
            .any(|e| e.file_type().is_file())
    }

    /// Load metadata from nether.toml
    pub fn load_metadata(&self) -> Result<NetherToml> {
        let content = std::fs::read_to_string(&self.nether_toml_path)?;
        let toml: NetherToml = toml::from_str(&content)?;
        Ok(toml)
    }
}

/// Discover all games in the showcase
pub fn discover_games(root: &Path) -> Result<Vec<GameConfig>> {
    let games_dir = root.join("games");
    let mut games = Vec::new();

    // Override - has build.rs asset generation
    let override_path = games_dir.join("override");
    if override_path.exists() {
        games.push(GameConfig {
            id: "override".to_string(),
            title: "OVERRIDE".to_string(),
            path: override_path.clone(),
            asset_strategy: AssetStrategy::BuildRs,
            nether_toml_path: override_path.join("nether.toml"),
        });
    }

    // Prism Survivors - has tools/asset-gen/
    let prism_path = games_dir.join("prism-survivors");
    if prism_path.exists() {
        games.push(GameConfig {
            id: "prism-survivors".to_string(),
            title: "PRISM SURVIVORS".to_string(),
            path: prism_path.clone(),
            asset_strategy: AssetStrategy::StandaloneTool {
                tool_path: prism_path.join("tools").join("asset-gen"),
            },
            nether_toml_path: prism_path.join("nether.toml"),
        });
    }

    // Lumina Depths - no asset generation yet
    let lumina_path = games_dir.join("lumina-depths");
    if lumina_path.exists() {
        games.push(GameConfig {
            id: "lumina-depths".to_string(),
            title: "LUMINA DEPTHS".to_string(),
            path: lumina_path.clone(),
            asset_strategy: AssetStrategy::None,
            nether_toml_path: lumina_path.join("nether.toml"),
        });
    }

    // Neon Drift - no asset generation yet
    let neon_path = games_dir.join("neon-drift");
    if neon_path.exists() {
        games.push(GameConfig {
            id: "neon-drift".to_string(),
            title: "NEON DRIFT".to_string(),
            path: neon_path.clone(),
            asset_strategy: AssetStrategy::None,
            nether_toml_path: neon_path.join("nether.toml"),
        });
    }

    Ok(games)
}

/// List all games and their status
pub fn list_games() -> Result<()> {
    let root = crate::project_root();
    let games = discover_games(&root)?;

    println!("{}", "ZX-Showcase Games".bold());
    println!("{}", "=================".dimmed());
    println!();

    for game in &games {
        let exists = game.path.exists();
        let has_nether_toml = game.nether_toml_path.exists();
        let has_assets = game.has_assets();

        let status_icon = if exists && has_nether_toml {
            "✓".green()
        } else {
            "✗".red()
        };

        let asset_status = match &game.asset_strategy {
            AssetStrategy::BuildRs => "build.rs (auto)".cyan(),
            AssetStrategy::StandaloneTool { .. } => "standalone tool".yellow(),
            AssetStrategy::None => {
                if has_assets {
                    "manual/procgen".blue()
                } else {
                    "MISSING ASSETS".red().bold()
                }
            }
        };

        let assets_icon = if has_assets {
            "✓".green()
        } else {
            "✗".red()
        };

        println!(
            "  {} {} [Assets: {}] - {}",
            status_icon, game.id.bold(), assets_icon, asset_status
        );

        // Try to load and show metadata
        if let Ok(meta) = game.load_metadata() {
            println!("      {} v{}", meta.game.title.dimmed(), meta.game.version.dimmed());
            if !meta.game.description.is_empty() {
                // Truncate long descriptions
                let desc = if meta.game.description.len() > 60 {
                    format!("{}...", &meta.game.description[..57])
                } else {
                    meta.game.description.clone()
                };
                println!("      {}", desc.dimmed());
            }
        }
        println!();
    }

    // Summary
    let total = games.len();
    let with_assets = games.iter().filter(|g| g.has_assets()).count();
    let missing_assets = total - with_assets;

    println!("{}", "Summary".bold());
    println!("  Total games: {}", total);
    println!("  With assets: {}", with_assets.to_string().green());
    if missing_assets > 0 {
        println!(
            "  Missing assets: {}",
            missing_assets.to_string().red().bold()
        );
        println!();
        println!(
            "{}",
            "Tip: Use nethercore-ai-plugins to generate missing assets:".dimmed()
        );
        println!("  {}", "cargo xtask gen-assets".cyan());
    }

    Ok(())
}
