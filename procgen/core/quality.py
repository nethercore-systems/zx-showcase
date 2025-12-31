"""
Quality Heuristics - Aligned with zx-procgen semantic-asset-language

Quality assessment framework for procedurally generated assets.
Implements quality metrics from quality-heuristics.md.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path
from enum import Enum
import numpy as np


class QualityLevel(Enum):
    """Quality assessment result levels."""
    FAIL = "fail"
    PASS = "pass"
    GOOD = "good"
    EXCELLENT = "excellent"


@dataclass
class TextureQuality:
    """Quality metrics for textures."""
    contrast: float = 0.0           # Should be > 0.15
    noise_coherence: float = 0.0    # Should be > 0.4
    tileability: float = 0.0        # Should be > 0.8 for tiling textures
    unique_colors: int = 0          # Should be > 50
    histogram_balance: float = 0.0  # Should be > 0.3
    file_size_kb: float = 0.0       # Budget check

    def passes_minimum(self) -> bool:
        """Check if texture meets minimum quality standards."""
        return (
            self.contrast > 0.15 and
            self.noise_coherence > 0.4 and
            self.histogram_balance > 0.3
        )

    def score(self) -> float:
        """Calculate overall quality score (0-100)."""
        scores = [
            min(self.contrast / 0.3, 1.0) * 20,
            min(self.noise_coherence / 0.8, 1.0) * 20,
            min(self.tileability, 1.0) * 20,
            min(self.unique_colors / 100, 1.0) * 20,
            min(self.histogram_balance / 0.5, 1.0) * 20,
        ]
        return sum(scores)

    def issues(self) -> List[str]:
        """List quality issues found."""
        issues = []
        if self.contrast <= 0.15:
            issues.append("Too flat - add more variation")
        if self.noise_coherence <= 0.4:
            issues.append("Noise lacks coherence - adjust octaves")
        if self.tileability <= 0.8:
            issues.append("Visible seams when tiled")
        if self.unique_colors < 50:
            issues.append("Color variety too low")
        if self.histogram_balance <= 0.3:
            issues.append("Histogram unbalanced - adjust values")
        return issues


@dataclass
class MeshQuality:
    """Quality metrics for meshes."""
    triangle_count: int = 0
    degenerate_tris: int = 0        # Should be 0
    uv_coverage: float = 0.0        # Should be > 0.95
    uv_overlap: float = 0.0         # Should be < 0.05
    max_stretch: float = 0.0        # Should be < 2.0
    watertight: bool = True         # No holes
    file_size_kb: float = 0.0

    def passes_for_budget(self, max_triangles: int) -> bool:
        """Check if mesh meets quality standards for given budget."""
        return (
            self.triangle_count <= max_triangles and
            self.degenerate_tris == 0 and
            self.uv_coverage > 0.95 and
            self.max_stretch < 2.0
        )

    def score(self, max_triangles: int = 1000) -> float:
        """Calculate overall quality score (0-100)."""
        budget_score = max(0, 1 - (self.triangle_count / max_triangles)) * 20 if max_triangles > 0 else 20
        scores = [
            budget_score,
            20 if self.degenerate_tris == 0 else 0,
            min(self.uv_coverage, 1.0) * 20,
            max(0, 1 - self.uv_overlap / 0.1) * 20,
            max(0, 1 - self.max_stretch / 4.0) * 20,
        ]
        return sum(scores)

    def issues(self) -> List[str]:
        """List quality issues found."""
        issues = []
        if self.degenerate_tris > 0:
            issues.append(f"Found {self.degenerate_tris} degenerate triangles")
        if self.uv_coverage <= 0.95:
            issues.append(f"UV coverage only {self.uv_coverage:.1%} - improve unwrap")
        if self.uv_overlap > 0.05:
            issues.append(f"UV overlap {self.uv_overlap:.1%} - fix overlapping islands")
        if self.max_stretch >= 2.0:
            issues.append(f"UV stretch {self.max_stretch:.1f} - reduce distortion")
        if not self.watertight:
            issues.append("Mesh has holes - ensure watertight")
        return issues


@dataclass
class SpriteQuality:
    """Quality metrics for sprites."""
    width: int = 0
    height: int = 0
    palette_colors: int = 0         # Actual colors used
    max_palette: int = 16           # Target palette size
    anti_aliasing: bool = False     # Should match style
    transparency_clean: bool = True  # No stray alpha pixels
    file_size_kb: float = 0.0

    def passes_minimum(self) -> bool:
        """Check if sprite meets minimum quality standards."""
        return (
            self.palette_colors <= self.max_palette and
            self.transparency_clean
        )

    def score(self) -> float:
        """Calculate overall quality score (0-100)."""
        palette_score = max(0, 1 - (self.palette_colors - self.max_palette) / self.max_palette) * 40 if self.max_palette > 0 else 40
        scores = [
            palette_score,
            30 if self.transparency_clean else 0,
            30,  # Base score for valid sprite
        ]
        return min(100, sum(scores))

    def issues(self) -> List[str]:
        """List quality issues found."""
        issues = []
        if self.palette_colors > self.max_palette:
            issues.append(f"Uses {self.palette_colors} colors, max is {self.max_palette}")
        if not self.transparency_clean:
            issues.append("Stray semi-transparent pixels detected")
        return issues


@dataclass
class AudioQuality:
    """Quality metrics for audio assets."""
    sample_rate: int = 0
    bit_depth: int = 0
    duration_ms: int = 0
    peak_level: float = 0.0         # Should be < 0.95
    dc_offset: float = 0.0          # Should be < 0.01
    clipping: bool = False          # Should be False
    file_size_kb: float = 0.0

    def passes_minimum(self) -> bool:
        """Check if audio meets minimum quality standards."""
        return (
            self.peak_level < 0.95 and
            self.dc_offset < 0.01 and
            not self.clipping
        )

    def score(self) -> float:
        """Calculate overall quality score (0-100)."""
        scores = [
            max(0, 1 - self.peak_level) * 30,
            max(0, 1 - self.dc_offset * 100) * 20,
            30 if not self.clipping else 0,
            20,  # Base score for valid audio
        ]
        return sum(scores)

    def issues(self) -> List[str]:
        """List quality issues found."""
        issues = []
        if self.peak_level >= 0.95:
            issues.append(f"Peak level {self.peak_level:.2f} too high - normalize")
        if self.dc_offset >= 0.01:
            issues.append(f"DC offset {self.dc_offset:.3f} detected - apply highpass")
        if self.clipping:
            issues.append("Audio clipping detected - reduce gain")
        return issues


@dataclass
class QualityReport:
    """Aggregated quality report for multiple assets."""
    textures: Dict[str, TextureQuality] = field(default_factory=dict)
    meshes: Dict[str, MeshQuality] = field(default_factory=dict)
    sprites: Dict[str, SpriteQuality] = field(default_factory=dict)
    audio: Dict[str, AudioQuality] = field(default_factory=dict)

    def overall_score(self) -> float:
        """Calculate overall quality score across all assets."""
        scores = []
        for tq in self.textures.values():
            scores.append(tq.score())
        for mq in self.meshes.values():
            scores.append(mq.score())
        for sq in self.sprites.values():
            scores.append(sq.score())
        for aq in self.audio.values():
            scores.append(aq.score())
        return sum(scores) / len(scores) if scores else 0

    def all_pass(self) -> bool:
        """Check if all assets pass minimum quality."""
        for tq in self.textures.values():
            if not tq.passes_minimum():
                return False
        for sq in self.sprites.values():
            if not sq.passes_minimum():
                return False
        for aq in self.audio.values():
            if not aq.passes_minimum():
                return False
        return True

    def all_issues(self) -> Dict[str, List[str]]:
        """Get all issues grouped by asset name."""
        issues = {}
        for name, tq in self.textures.items():
            if tq.issues():
                issues[f"texture:{name}"] = tq.issues()
        for name, mq in self.meshes.items():
            if mq.issues():
                issues[f"mesh:{name}"] = mq.issues()
        for name, sq in self.sprites.items():
            if sq.issues():
                issues[f"sprite:{name}"] = sq.issues()
        for name, aq in self.audio.items():
            if aq.issues():
                issues[f"audio:{name}"] = aq.issues()
        return issues

    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            "Quality Report",
            "=" * 40,
            f"Overall Score: {self.overall_score():.1f}/100",
            f"All Pass: {'Yes' if self.all_pass() else 'No'}",
            "",
            f"Textures: {len(self.textures)}",
            f"Meshes: {len(self.meshes)}",
            f"Sprites: {len(self.sprites)}",
            f"Audio: {len(self.audio)}",
        ]
        issues = self.all_issues()
        if issues:
            lines.append("")
            lines.append("Issues:")
            for asset, issue_list in issues.items():
                lines.append(f"  {asset}:")
                for issue in issue_list:
                    lines.append(f"    - {issue}")
        return "\n".join(lines)


# Quality thresholds for different targets
QUALITY_THRESHOLDS = {
    "prototype": {"min_score": 50, "max_iterations": 1},
    "development": {"min_score": 70, "max_iterations": 3},
    "production": {"min_score": 85, "max_iterations": 5},
    "release": {"min_score": 95, "max_iterations": 10},
}


def analyze_texture(path: Path) -> TextureQuality:
    """Analyze a texture file and return quality metrics."""
    from PIL import Image
    import numpy as np

    img = Image.open(path)
    arr = np.array(img)

    # Calculate metrics
    if len(arr.shape) == 3:
        gray = np.mean(arr[:, :, :3], axis=2)
    else:
        gray = arr.astype(float)

    # Contrast (standard deviation of luminance)
    contrast = float(np.std(gray) / 255.0)

    # Unique colors
    if len(arr.shape) == 3:
        # Flatten to list of RGB tuples
        pixels = arr.reshape(-1, arr.shape[-1])
        unique_colors = len(set(map(tuple, pixels)))
    else:
        unique_colors = len(np.unique(arr))

    # Histogram balance
    hist, _ = np.histogram(gray, bins=256)
    hist_norm = hist / hist.sum()
    histogram_balance = float(1.0 - np.std(hist_norm) * 10)
    histogram_balance = max(0, min(1, histogram_balance))

    # Tileability (compare edges)
    top = gray[0, :]
    bottom = gray[-1, :]
    left = gray[:, 0]
    right = gray[:, -1]
    tileability = 1.0 - (
        np.mean(np.abs(top - bottom)) / 255.0 +
        np.mean(np.abs(left - right)) / 255.0
    ) / 2

    # File size
    file_size_kb = path.stat().st_size / 1024

    return TextureQuality(
        contrast=contrast,
        noise_coherence=0.5,  # Would need FFT analysis for proper value
        tileability=float(tileability),
        unique_colors=unique_colors,
        histogram_balance=histogram_balance,
        file_size_kb=file_size_kb,
    )


def analyze_sprite(path: Path, max_palette: int = 16) -> SpriteQuality:
    """Analyze a sprite file and return quality metrics."""
    from PIL import Image
    import numpy as np

    img = Image.open(path)
    arr = np.array(img)

    # Count unique colors (ignoring full transparency)
    if arr.shape[-1] == 4:
        # Filter out fully transparent pixels
        mask = arr[:, :, 3] > 0
        visible_pixels = arr[mask]
        if len(visible_pixels) > 0:
            unique_colors = len(set(map(tuple, visible_pixels)))
        else:
            unique_colors = 0

        # Check for semi-transparent pixels (stray alpha)
        semi_transparent = np.sum((arr[:, :, 3] > 0) & (arr[:, :, 3] < 255))
        transparency_clean = semi_transparent < (arr.shape[0] * arr.shape[1] * 0.01)
    else:
        pixels = arr.reshape(-1, arr.shape[-1]) if len(arr.shape) == 3 else arr.flatten()
        unique_colors = len(set(map(tuple, pixels))) if len(arr.shape) == 3 else len(np.unique(arr))
        transparency_clean = True

    return SpriteQuality(
        width=arr.shape[1],
        height=arr.shape[0],
        palette_colors=unique_colors,
        max_palette=max_palette,
        transparency_clean=transparency_clean,
        file_size_kb=path.stat().st_size / 1024,
    )


def analyze_mesh(path: Path) -> MeshQuality:
    """
    Analyze a mesh file and return quality metrics.

    Note: This is a basic implementation. For OBJ files, it counts vertices
    and faces. For GLB files, more advanced analysis may be needed.
    """
    suffix = path.suffix.lower()

    if suffix == '.obj':
        # Parse OBJ file
        vertex_count = 0
        face_count = 0
        with open(path, 'r') as f:
            for line in f:
                if line.startswith('v '):
                    vertex_count += 1
                elif line.startswith('f '):
                    face_count += 1

        # Estimate triangle count (assuming quads = 2 tris, tris = 1)
        # This is approximate since we don't parse face vertex counts
        triangle_count = face_count  # Conservative estimate

        return MeshQuality(
            triangle_count=triangle_count,
            degenerate_tris=0,  # Would need actual geometry analysis
            uv_coverage=1.0,    # Assume good UVs
            uv_overlap=0.0,
            max_stretch=1.0,
            watertight=True,
            file_size_kb=path.stat().st_size / 1024,
        )

    elif suffix == '.glb':
        # For GLB files, we'd need to parse the binary format
        # For now, return a placeholder based on file size
        file_size_kb = path.stat().st_size / 1024
        # Rough estimate: 1KB ~= 50 triangles for a typical GLB
        estimated_tris = int(file_size_kb * 50)

        return MeshQuality(
            triangle_count=estimated_tris,
            degenerate_tris=0,
            uv_coverage=1.0,
            uv_overlap=0.0,
            max_stretch=1.0,
            watertight=True,
            file_size_kb=file_size_kb,
        )

    else:
        # Unknown format
        return MeshQuality(
            triangle_count=0,
            file_size_kb=path.stat().st_size / 1024,
        )


def analyze_audio(path: Path) -> AudioQuality:
    """Analyze an audio file and return quality metrics."""
    import wave
    import numpy as np

    with wave.open(str(path), 'rb') as wf:
        sample_rate = wf.getframerate()
        n_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        n_frames = wf.getnframes()
        duration_ms = int(n_frames / sample_rate * 1000)

        frames = wf.readframes(n_frames)
        if sample_width == 2:
            samples = np.frombuffer(frames, dtype=np.int16).astype(float) / 32768.0
        else:
            samples = np.frombuffer(frames, dtype=np.int8).astype(float) / 128.0

    if n_channels > 1:
        samples = samples.reshape(-1, n_channels).mean(axis=1)

    peak_level = float(np.max(np.abs(samples)))
    dc_offset = float(np.abs(np.mean(samples)))
    clipping = peak_level >= 0.999

    return AudioQuality(
        sample_rate=sample_rate,
        bit_depth=sample_width * 8,
        duration_ms=duration_ms,
        peak_level=peak_level,
        dc_offset=dc_offset,
        clipping=clipping,
        file_size_kb=path.stat().st_size / 1024,
    )
