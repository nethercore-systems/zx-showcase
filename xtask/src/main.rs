//! ZX-Showcase Build System
//!
//! Commands:
//! - `cargo xtask build-all` - Build and install all games
//! - `cargo xtask build <game>` - Build specific game
//! - `cargo xtask install` - Install pre-built games
//! - `cargo xtask clean` - Clean all build artifacts
//! - `cargo xtask list` - Show games and their status
//! - `cargo xtask gen-assets` - Generate assets only

mod config;
mod asset_gen;
mod build;
mod install;

use anyhow::Result;
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "xtask")]
#[command(about = "ZX-Showcase build and installation tasks")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Build and install all games
    BuildAll {
        /// Skip asset generation (use existing assets)
        #[arg(long)]
        skip_assets: bool,

        /// Build sequentially instead of in parallel
        #[arg(long)]
        sequential: bool,
    },

    /// Build a specific game
    Build {
        /// Game name (lumina-depths, neon-drift, prism-survivors, override)
        game: String,

        /// Skip asset generation
        #[arg(long)]
        skip_assets: bool,
    },

    /// Install built games to ~/.nethercore/games/
    Install {
        /// Game to install (or all if not specified)
        game: Option<String>,
    },

    /// Clean all build artifacts
    Clean {
        /// Also clean generated assets
        #[arg(long)]
        assets: bool,
    },

    /// List available games and their status
    List,

    /// Generate assets for games that need them
    GenAssets {
        /// Game to generate assets for (or all if not specified)
        game: Option<String>,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::BuildAll {
            skip_assets,
            sequential,
        } => build::build_all(skip_assets, !sequential),
        Commands::Build { game, skip_assets } => build::build_game(&game, skip_assets),
        Commands::Install { game } => install::install_games(game.as_deref()),
        Commands::Clean { assets } => build::clean_all(assets),
        Commands::List => config::list_games(),
        Commands::GenAssets { game } => asset_gen::generate_assets(game.as_deref()),
    }
}

/// Get the project root (parent of xtask directory)
pub fn project_root() -> std::path::PathBuf {
    std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .expect("xtask should be in a subdirectory")
        .to_path_buf()
}
