#!/usr/bin/env python3
"""
Neon Drift XM Music Generator

Generates 5 synthwave tracks for Neon Drift using the xm_writer library.
Each track uses the same synth samples but with different patterns, tempo, and key.

Usage:
    python generate_xm_music.py

Output:
    assets/audio/music/sunset_strip.xm   - 128 BPM, Am, nostalgic/warm
    assets/audio/music/neon_city.xm      - 132 BPM, Em, urban/energetic
    assets/audio/music/void_tunnel.xm    - 138 BPM, Dm, mysterious/intense
    assets/audio/music/crystal_cavern.xm - 130 BPM, Bm, ethereal/tense
    assets/audio/music/solar_highway.xm  - 140 BPM, Fm, epic/triumphant

Sample mapping (must exist in nether.toml):
    synth_kick, synth_snare, synth_hihat, synth_openhat,
    synth_bass, synth_lead, synth_pad, synth_arp
"""

import sys
import wave
from pathlib import Path

# Add xm_writer to path
# From: games/neon-drift/generation/sounds/xm_music.py
# Go up to: zx-showcase/procgen/lib/
ZX_SHOWCASE = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(ZX_SHOWCASE / "procgen" / "lib"))

from xm_types import (
    XmModule, XmPattern, XmNote, XmInstrument, XmEnvelope,
    note_from_name
)
from xm_writer import write_xm, validate_xm

# ============================================================================
# Constants
# ============================================================================

OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated/sounds/music"
SAMPLES_DIR = Path(__file__).parent.parent.parent / "generated/sounds"

# Instrument indices (1-based in XM)
KICK = 1
SNARE = 2
HIHAT = 3
OPENHAT = 4
BASS = 5
LEAD = 6
PAD = 7
ARP = 8

# ============================================================================
# Music Theory Helpers
# ============================================================================

# Note names for scales (starting at octave 3)
SCALES = {
    "Am": ["A-3", "B-3", "C-4", "D-4", "E-4", "F-4", "G-4", "A-4"],  # A minor
    "Em": ["E-3", "F#3", "G-3", "A-3", "B-3", "C-4", "D-4", "E-4"],  # E minor
    "Dm": ["D-3", "E-3", "F-3", "G-3", "A-3", "A#3", "C-4", "D-4"],  # D minor
    "Bm": ["B-2", "C#3", "D-3", "E-3", "F#3", "G-3", "A-3", "B-3"],  # B minor
    "Fm": ["F-3", "G-3", "G#3", "A#3", "C-4", "C#4", "D#4", "F-4"],  # F minor
}

# Chord patterns (scale degrees, 0-indexed)
CHORDS = {
    "i":   [0, 2, 4],      # Minor tonic
    "iv":  [3, 5, 0],      # Minor subdominant
    "v":   [4, 6, 1],      # Minor dominant
    "VI":  [5, 0, 2],      # Major submediant
    "VII": [6, 1, 3],      # Major subtonic
    "III": [2, 4, 6],      # Major mediant
}

# Common synthwave chord progressions
PROGRESSIONS = {
    "nostalgic":  ["i", "VI", "III", "VII"],   # Am - F - C - G
    "energetic":  ["i", "iv", "v", "i"],       # Em - Am - Bm - Em
    "mysterious": ["i", "VII", "VI", "v"],     # Dm - C - Bb - Am
    "ethereal":   ["i", "III", "VI", "VII"],   # Bm - D - G - A
    "epic":       ["i", "VII", "v", "VI"],     # Fm - Eb - Cm - Db
}


def scale_note(scale_name: str, degree: int, octave_offset: int = 0) -> str:
    """Get a note from a scale by degree (0-7) with optional octave shift."""
    scale = SCALES[scale_name]
    note = scale[degree % len(scale)]

    # Parse and adjust octave
    if note[1] == "-":
        base = note[0]
        octave = int(note[2])
    elif note[1] == "#" or note[1].lower() == "b":
        base = note[0:2]
        octave = int(note[2])
    else:
        base = note[0]
        octave = int(note[1])

    new_octave = octave + octave_offset + (degree // len(scale))

    if len(base) == 1:
        return f"{base}-{new_octave}"
    else:
        return f"{base}{new_octave}"


# ============================================================================
# Pattern Generators
# ============================================================================

def create_drum_pattern_verse(num_rows: int = 64) -> tuple:
    """Create a verse drum pattern - lighter, more minimal."""
    pattern_data = []

    for row in range(num_rows):
        notes = [XmNote() for _ in range(8)]

        # Kick: just on 1 and 3
        if row % 16 == 0:
            notes[KICK-1] = XmNote.play("C-4", KICK, 56)

        # Snare: light ghost notes
        if row % 16 == 8:
            notes[SNARE-1] = XmNote.play("C-4", SNARE, 40)

        # Hi-hat: steady 8ths
        if row % 4 == 0:
            vol = 36 if row % 8 == 0 else 28
            notes[HIHAT-1] = XmNote.play("C-4", HIHAT, vol)

        pattern_data.append(notes)

    return pattern_data


def create_drum_pattern_chorus(num_rows: int = 64) -> tuple:
    """Create a chorus drum pattern - full, driving."""
    pattern_data = []

    for row in range(num_rows):
        notes = [XmNote() for _ in range(8)]

        # Kick: 4-on-floor
        if row % 8 == 0:
            notes[KICK-1] = XmNote.play("C-4", KICK, 64)

        # Snare: on 2 and 4, with gated reverb feel (note off after)
        if row % 16 == 8:
            notes[SNARE-1] = XmNote.play("C-4", SNARE, 60)

        # Hi-hat: driving 16ths
        if row % 2 == 0:
            vol = 48 if row % 8 == 0 else 32
            notes[HIHAT-1] = XmNote.play("C-4", HIHAT, vol)

        # Open hat on offbeats for energy
        if row % 8 == 4:
            notes[OPENHAT-1] = XmNote.play("C-4", OPENHAT, 44)

        pattern_data.append(notes)

    return pattern_data


def create_bass_pattern(scale: str, progression: list, num_rows: int = 64, octave: int = -1) -> list:
    """Create an octave bass pattern following the chord progression."""
    pattern_data = []
    rows_per_chord = num_rows // len(progression)

    for row in range(num_rows):
        notes = [XmNote() for _ in range(8)]
        chord_idx = row // rows_per_chord
        chord_idx = min(chord_idx, len(progression) - 1)
        chord_name = progression[chord_idx]
        root_degree = CHORDS[chord_name][0]

        # Bass root on strong beats, octave pattern
        if row % 8 == 0:
            notes[BASS-1] = XmNote.play(scale_note(scale, root_degree, octave), BASS, 60)
        elif row % 8 == 4:
            notes[BASS-1] = XmNote.play(scale_note(scale, root_degree, octave + 1), BASS, 52)

        pattern_data.append(notes)

    return pattern_data


def create_arp_pattern(scale: str, progression: list, num_rows: int = 64) -> list:
    """Create an arpeggiated chord pattern."""
    pattern_data = []
    rows_per_chord = num_rows // len(progression)

    for row in range(num_rows):
        notes = [XmNote() for _ in range(8)]
        chord_idx = row // rows_per_chord
        chord_idx = min(chord_idx, len(progression) - 1)
        chord_name = progression[chord_idx]
        chord_degrees = CHORDS[chord_name]

        # Arp through chord tones every 2 rows
        if row % 2 == 0:
            arp_idx = (row // 2) % 3
            degree = chord_degrees[arp_idx]
            vol = 48 if row % 4 == 0 else 36
            notes[ARP-1] = XmNote.play(scale_note(scale, degree, 1), ARP, vol)

        pattern_data.append(notes)

    return pattern_data


def create_pad_pattern(scale: str, progression: list, num_rows: int = 64) -> list:
    """Create a sustained pad pattern on chord changes."""
    pattern_data = []
    rows_per_chord = num_rows // len(progression)

    for row in range(num_rows):
        notes = [XmNote() for _ in range(8)]
        chord_idx = row // rows_per_chord

        # Pad: play on chord changes
        if row % rows_per_chord == 0:
            chord_idx = min(chord_idx, len(progression) - 1)
            chord_name = progression[chord_idx]
            root_degree = CHORDS[chord_name][0]
            notes[PAD-1] = XmNote.play(scale_note(scale, root_degree, 0), PAD, 40)

        pattern_data.append(notes)

    return pattern_data


def create_lead_pattern(scale: str, melody_contour: list, num_rows: int = 64) -> list:
    """Create a lead melody pattern from a contour."""
    pattern_data = []
    notes_per_phrase = len(melody_contour)
    rows_per_note = num_rows // notes_per_phrase

    for row in range(num_rows):
        notes = [XmNote() for _ in range(8)]

        if row % rows_per_note == 0:
            note_idx = row // rows_per_note
            if note_idx < len(melody_contour):
                degree = melody_contour[note_idx]
                if degree >= 0:  # -1 means rest
                    notes[LEAD-1] = XmNote.play(scale_note(scale, degree, 1), LEAD, 56)

        pattern_data.append(notes)

    return pattern_data


def merge_patterns(*pattern_datas) -> XmPattern:
    """Merge multiple pattern data lists into a single XmPattern."""
    num_rows = len(pattern_datas[0])
    num_channels = 8
    pattern = XmPattern.empty(num_rows, num_channels)

    for row in range(num_rows):
        for ch in range(num_channels):
            for pd in pattern_datas:
                if row < len(pd) and ch < len(pd[row]):
                    note = pd[row][ch]
                    if not note.is_empty():
                        pattern.notes[row][ch] = note
                        break

    return pattern


# ============================================================================
# Track Generators
# ============================================================================

def generate_sunset_strip() -> XmModule:
    """
    Sunset Strip - 128 BPM, Am
    Nostalgic, warm - arpeggiated chords, mellow lead
    """
    scale = "Am"
    progression = PROGRESSIONS["nostalgic"]

    # Verse pattern - gentle intro
    verse_drums = create_drum_pattern_verse()
    verse_bass = create_bass_pattern(scale, progression)
    verse_arp = create_arp_pattern(scale, progression)
    verse_pad = create_pad_pattern(scale, progression)
    verse = merge_patterns(verse_drums, verse_bass, verse_arp, verse_pad)

    # Chorus pattern - full energy
    chorus_drums = create_drum_pattern_chorus()
    chorus_bass = create_bass_pattern(scale, progression)
    chorus_arp = create_arp_pattern(scale, progression)
    chorus_pad = create_pad_pattern(scale, progression)
    lead_melody = [0, 2, 4, 5, 4, 2, 0, -1]  # Simple melodic contour
    chorus_lead = create_lead_pattern(scale, lead_melody)
    chorus = merge_patterns(chorus_drums, chorus_bass, chorus_arp, chorus_pad, chorus_lead)

    return XmModule(
        name="Sunset Strip",
        num_channels=8,
        default_speed=6,
        default_bpm=128,
        restart_position=0,
        order_table=[0, 0, 1, 1, 0, 1, 1, 1],  # Verse-Chorus structure, loop to verse
        patterns=[verse, chorus],
        instruments=create_instruments(),
    )


def generate_neon_city() -> XmModule:
    """
    Neon City - 132 BPM, Em
    Urban, energetic - driving bass, punchy drums
    """
    scale = "Em"
    progression = PROGRESSIONS["energetic"]

    # Verse - driving but controlled
    verse_drums = create_drum_pattern_verse()
    verse_bass = create_bass_pattern(scale, progression)
    verse = merge_patterns(verse_drums, verse_bass)

    # Chorus - full power
    chorus_drums = create_drum_pattern_chorus()
    chorus_bass = create_bass_pattern(scale, progression)
    chorus_arp = create_arp_pattern(scale, progression)
    lead_melody = [0, 4, 3, 2, 4, 5, 4, 2]
    chorus_lead = create_lead_pattern(scale, lead_melody)
    chorus = merge_patterns(chorus_drums, chorus_bass, chorus_arp, chorus_lead)

    return XmModule(
        name="Neon City",
        num_channels=8,
        default_speed=6,
        default_bpm=132,
        restart_position=0,
        order_table=[0, 0, 1, 1, 0, 0, 1, 1],
        patterns=[verse, chorus],
        instruments=create_instruments(),
    )


def generate_void_tunnel() -> XmModule:
    """
    Void Tunnel - 138 BPM, Dm
    Mysterious, intense - dark pads, stuttered synths
    """
    scale = "Dm"
    progression = PROGRESSIONS["mysterious"]

    # Build - tension
    build_drums = create_drum_pattern_verse()
    build_bass = create_bass_pattern(scale, progression)
    build_pad = create_pad_pattern(scale, progression)
    build = merge_patterns(build_drums, build_bass, build_pad)

    # Drop - intense
    drop_drums = create_drum_pattern_chorus()
    drop_bass = create_bass_pattern(scale, progression)
    drop_arp = create_arp_pattern(scale, progression)
    lead_melody = [0, 0, 4, 3, 0, 4, 5, 4]  # Darker contour
    drop_lead = create_lead_pattern(scale, lead_melody)
    drop = merge_patterns(drop_drums, drop_bass, drop_arp, drop_lead)

    return XmModule(
        name="Void Tunnel",
        num_channels=8,
        default_speed=5,  # Faster ticks for intensity
        default_bpm=138,
        restart_position=0,
        order_table=[0, 0, 0, 1, 1, 1, 1, 1],
        patterns=[build, drop],
        instruments=create_instruments(),
    )


def generate_crystal_cavern() -> XmModule:
    """
    Crystal Cavern - 130 BPM, Bm
    Ethereal, tense - crystalline arps, deep sub bass
    """
    scale = "Bm"
    progression = PROGRESSIONS["ethereal"]

    # Ambient intro
    intro_pad = create_pad_pattern(scale, progression)
    intro_arp = create_arp_pattern(scale, progression)
    intro = merge_patterns(intro_pad, intro_arp)

    # Main - full but spacious
    main_drums = create_drum_pattern_chorus()
    main_bass = create_bass_pattern(scale, progression, octave=-2)  # Deeper bass
    main_arp = create_arp_pattern(scale, progression)
    main_pad = create_pad_pattern(scale, progression)
    lead_melody = [4, 5, 7, 5, 4, 2, 4, 2]  # Ethereal climbing
    main_lead = create_lead_pattern(scale, lead_melody)
    main = merge_patterns(main_drums, main_bass, main_arp, main_pad, main_lead)

    return XmModule(
        name="Crystal Cavern",
        num_channels=8,
        default_speed=6,
        default_bpm=130,
        restart_position=0,
        order_table=[0, 0, 1, 1, 1, 0, 1, 1],
        patterns=[intro, main],
        instruments=create_instruments(),
    )


def generate_solar_highway() -> XmModule:
    """
    Solar Highway - 140 BPM, Fm
    Epic, triumphant - soaring lead, layered chords
    """
    scale = "Fm"
    progression = PROGRESSIONS["epic"]

    # Build up
    build_drums = create_drum_pattern_verse()
    build_bass = create_bass_pattern(scale, progression)
    build_pad = create_pad_pattern(scale, progression)
    build = merge_patterns(build_drums, build_bass, build_pad)

    # Epic chorus
    chorus_drums = create_drum_pattern_chorus()
    chorus_bass = create_bass_pattern(scale, progression)
    chorus_arp = create_arp_pattern(scale, progression)
    chorus_pad = create_pad_pattern(scale, progression)
    lead_melody = [0, 2, 4, 7, 5, 4, 2, 4]  # Triumphant, soaring
    chorus_lead = create_lead_pattern(scale, lead_melody)
    chorus = merge_patterns(chorus_drums, chorus_bass, chorus_arp, chorus_pad, chorus_lead)

    return XmModule(
        name="Solar Highway",
        num_channels=8,
        default_speed=5,  # Faster for intensity
        default_bpm=140,
        restart_position=0,
        order_table=[0, 0, 1, 1, 1, 1, 1, 1],
        patterns=[build, chorus],
        instruments=create_instruments(),
    )


def load_wav_sample(name: str) -> bytes:
    """Load a WAV file and return the PCM data as bytes."""
    wav_path = SAMPLES_DIR / f"{name}.wav"
    if not wav_path.exists():
        print(f"Warning: Sample not found: {wav_path}")
        return b""

    with wave.open(str(wav_path), 'rb') as wav:
        # Read all audio data
        pcm_data = wav.readframes(wav.getnframes())
        return pcm_data


def create_instruments() -> list:
    """Create instruments with embedded synth samples."""
    sample_names = [
        "synth_kick",
        "synth_snare",
        "synth_hihat",
        "synth_openhat",
        "synth_bass",
        "synth_lead",
        "synth_pad",
        "synth_arp",
    ]

    instruments = []
    for name in sample_names:
        sample_data = load_wav_sample(name)
        inst = XmInstrument.for_zx(name=name, sample_data=sample_data)
        instruments.append(inst)

    return instruments


# ============================================================================
# Main
# ============================================================================

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tracks = [
        ("sunset_strip", generate_sunset_strip),
        ("neon_city", generate_neon_city),
        ("void_tunnel", generate_void_tunnel),
        ("crystal_cavern", generate_crystal_cavern),
        ("solar_highway", generate_solar_highway),
    ]

    for track_id, generator in tracks:
        module = generator()
        output_path = OUTPUT_DIR / f"{track_id}.xm"

        write_xm(module, str(output_path))

        try:
            validate_xm(str(output_path))
            print(f"Created: {output_path}")
            print(f"  BPM: {module.default_bpm}, Speed: {module.default_speed}")
            print(f"  Patterns: {len(module.patterns)}, Order: {module.order_table}")
        except ValueError as e:
            print(f"FAILED: {track_id} - {e}")
            return 1

    print(f"\nAll 5 tracks generated in {OUTPUT_DIR}")
    print("\nTo add to game, uncomment tracker entries in nether.toml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
