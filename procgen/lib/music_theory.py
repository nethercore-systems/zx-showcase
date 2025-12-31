"""
Music theory utilities for procedural music generation.

Provides scales, chords, progressions, and composition helpers.
"""

from typing import List, Tuple, Dict
from enum import Enum


# ============================================================================
# Note Constants
# ============================================================================

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
ENHARMONIC_MAP = {"Db": "C#", "Eb": "D#", "Fb": "E", "Gb": "F#", "Ab": "G#", "Bb": "A#", "Cb": "B"}


# ============================================================================
# Scales
# ============================================================================

SCALES = {
    # Major modes
    "major": [0, 2, 4, 5, 7, 9, 11],
    "ionian": [0, 2, 4, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],

    # Minor variants
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],

    # Pentatonic
    "pentatonic_major": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],

    # Blues
    "blues": [0, 3, 5, 6, 7, 10],
    "blues_major": [0, 2, 3, 4, 7, 9],

    # Exotic
    "whole_tone": [0, 2, 4, 6, 8, 10],
    "diminished": [0, 2, 3, 5, 6, 8, 9, 11],
    "chromatic": list(range(12)),
}


# ============================================================================
# Chords
# ============================================================================

CHORD_TYPES = {
    # Triads
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],

    # Seventh chords
    "7": [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dim7": [0, 3, 6, 9],
    "m7b5": [0, 3, 6, 10],  # Half-diminished

    # Extended
    "add9": [0, 4, 7, 14],
    "9": [0, 4, 7, 10, 14],
    "maj9": [0, 4, 7, 11, 14],
    "min9": [0, 3, 7, 10, 14],

    # Power chord
    "power": [0, 7],
    "power5": [0, 7, 12],
}


# ============================================================================
# Progressions
# ============================================================================

PROGRESSIONS = {
    # By mood
    "triumphant": ["I", "IV", "V", "I"],
    "epic": ["I", "V", "vi", "IV"],
    "tense": ["i", "VI", "III", "VII"],
    "mysterious": ["i", "VII", "VI", "VII"],
    "melancholic": ["i", "iv", "i", "V"],
    "peaceful": ["I", "iii", "IV", "I"],
    "hopeful": ["I", "V", "vi", "IV"],
    "dark": ["i", "bII", "i", "V"],
    "uplifting": ["vi", "IV", "I", "V"],

    # By genre
    "synthwave": ["i", "VI", "III", "VII"],
    "rock": ["I", "IV", "V", "I"],
    "pop": ["I", "V", "vi", "IV"],
    "jazz_ii_v_i": ["ii7", "V7", "Imaj7"],
    "blues": ["I7", "IV7", "I7", "V7"],
    "ambient": ["Imaj7", "IVmaj7"],

    # Classic
    "pachelbel": ["I", "V", "vi", "iii", "IV", "I", "IV", "V"],
    "andalusian": ["i", "VII", "VI", "V"],
}


# ============================================================================
# Tempo Ranges
# ============================================================================

TEMPO_RANGES = {
    "ambient": (60, 90),
    "ballad": (70, 90),
    "menu": (80, 110),
    "exploration": (70, 100),
    "puzzle": (80, 110),
    "action": (120, 150),
    "combat": (140, 180),
    "boss": (150, 190),
    "stealth": (60, 90),
    "chase": (160, 200),
    "victory": (100, 140),
    "defeat": (60, 80),
}


# ============================================================================
# Note Conversion Functions
# ============================================================================

def note_to_midi(note_name: str) -> int:
    """
    Convert note name to MIDI number.

    Examples:
        note_to_midi("C4") -> 60
        note_to_midi("A4") -> 69
        note_to_midi("F#3") -> 54
    """
    note = note_name[:-1].upper()
    octave = int(note_name[-1])

    # Handle flats
    if note in ENHARMONIC_MAP:
        note = ENHARMONIC_MAP[note]

    if note not in NOTE_NAMES:
        raise ValueError(f"Invalid note: {note_name}")

    semitone = NOTE_NAMES.index(note)
    return 12 * (octave + 1) + semitone


def midi_to_note(midi: int) -> str:
    """
    Convert MIDI number to note name.

    Examples:
        midi_to_note(60) -> "C4"
        midi_to_note(69) -> "A4"
    """
    octave = midi // 12 - 1
    semitone = midi % 12
    return f"{NOTE_NAMES[semitone]}{octave}"


def note_to_xm(note_name: str) -> int:
    """
    Convert note name to XM note number.

    XM notes: 1=C-0, 13=C-1, 49=C-4, 97=note-off
    """
    if note_name in ("---", "...", ""):
        return 0  # No note
    if note_name in ("===", "OFF"):
        return 97  # Note off

    note = note_name.upper().replace("-", "")

    note_map = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

    note_char = note[0]
    if note_char not in note_map:
        raise ValueError(f"Invalid note: {note_name}")

    semitone = note_map[note_char]

    # Check for sharp/flat
    idx = 1
    if len(note) > 1 and note[1] == "#":
        semitone += 1
        idx = 2
    elif len(note) > 1 and note[1] == "B":
        semitone -= 1
        idx = 2

    # Parse octave
    octave = int(note[idx:])

    # XM note value: 1 = C-0, 13 = C-1, 49 = C-4, etc.
    return octave * 12 + semitone + 1


def xm_to_note(xm_note: int) -> str:
    """Convert XM note number to note name."""
    if xm_note == 0:
        return "---"
    if xm_note == 97:
        return "OFF"

    xm_note -= 1
    octave = xm_note // 12
    semitone = xm_note % 12
    return f"{NOTE_NAMES[semitone]}-{octave}"


# ============================================================================
# Scale Functions
# ============================================================================

def get_scale_notes(root: str, scale_name: str, octaves: int = 1) -> List[str]:
    """
    Get all notes in a scale.

    Args:
        root: Root note (e.g., "C", "F#")
        scale_name: Scale name from SCALES
        octaves: Number of octaves to generate

    Returns:
        List of note names (e.g., ["C4", "D4", "E4", ...])
    """
    root_midi = note_to_midi(f"{root}4")
    intervals = SCALES.get(scale_name, SCALES["major"])

    notes = []
    for octave in range(octaves):
        for interval in intervals:
            midi = root_midi + interval + (octave * 12)
            notes.append(midi_to_note(midi))

    return notes


def scale_degree_to_note(
    root: str,
    scale_name: str,
    degree: int,
    octave_offset: int = 0
) -> str:
    """
    Get note name for a scale degree.

    Args:
        root: Root note
        scale_name: Scale name
        degree: Scale degree (0-indexed, can exceed scale length)
        octave_offset: Additional octave offset
    """
    root_midi = note_to_midi(f"{root}4")
    scale = SCALES.get(scale_name, SCALES["major"])

    octaves, scale_degree = divmod(degree, len(scale))
    semitones = scale[scale_degree] + (octaves + octave_offset) * 12

    return midi_to_note(root_midi + semitones)


# ============================================================================
# Chord Functions
# ============================================================================

def get_chord_notes(
    root: str,
    chord_type: str,
    octave: int = 4
) -> List[str]:
    """
    Get notes in a chord.

    Args:
        root: Root note
        chord_type: Chord type from CHORD_TYPES
        octave: Base octave
    """
    root_midi = note_to_midi(f"{root}{octave}")
    intervals = CHORD_TYPES.get(chord_type, CHORD_TYPES["major"])
    return [midi_to_note(root_midi + i) for i in intervals]


def get_chord_midi(
    root: str,
    chord_type: str,
    octave: int = 4
) -> List[int]:
    """Get MIDI numbers for chord notes."""
    root_midi = note_to_midi(f"{root}{octave}")
    intervals = CHORD_TYPES.get(chord_type, CHORD_TYPES["major"])
    return [root_midi + i for i in intervals]


# ============================================================================
# Progression Functions
# ============================================================================

def parse_roman_numeral(numeral: str) -> Tuple[int, str, bool]:
    """
    Parse a Roman numeral chord notation.

    Returns:
        Tuple of (degree, quality_suffix, is_minor)
    """
    numeral_map = {
        "I": 0, "II": 1, "III": 2, "IV": 3, "V": 4, "VI": 5, "VII": 6,
        "i": 0, "ii": 1, "iii": 2, "iv": 3, "v": 4, "vi": 5, "vii": 6,
    }

    # Extract base numeral and suffix
    base = ""
    suffix = ""
    for char in numeral:
        if char.upper() in "IViv" or (char == "b" and not base):
            base += char
        else:
            suffix += char

    # Check for flat prefix
    flat = base.startswith("b")
    if flat:
        base = base[1:]

    is_minor = base.islower()
    degree = numeral_map.get(base.upper(), 0)

    if flat:
        degree -= 1  # Will be adjusted by scale interval

    return (degree, suffix, is_minor)


def progression_to_chords(
    root: str,
    scale_name: str,
    progression_name: str
) -> List[Tuple[str, str]]:
    """
    Convert progression name to list of (root, chord_type) tuples.

    Example:
        progression_to_chords("C", "major", "epic")
        -> [("C", "major"), ("G", "major"), ("A", "minor"), ("F", "major")]
    """
    progression = PROGRESSIONS.get(progression_name, ["I"])
    intervals = SCALES.get(scale_name, SCALES["major"])

    root_semitone = NOTE_NAMES.index(root.replace("#", "")) + (1 if "#" in root else 0)

    chords = []
    for numeral in progression:
        degree, suffix, is_minor = parse_roman_numeral(numeral)

        # Get scale degree semitone
        if degree < len(intervals):
            semitone = intervals[degree % len(intervals)]
        else:
            semitone = 0

        # Calculate chord root
        chord_root_semitone = (root_semitone + semitone) % 12
        chord_root = NOTE_NAMES[chord_root_semitone]

        # Determine chord quality
        if "7" in suffix:
            if "maj" in suffix:
                chord_type = "maj7"
            elif is_minor:
                chord_type = "min7"
            else:
                chord_type = "7"
        elif "dim" in suffix:
            chord_type = "dim"
        else:
            chord_type = "minor" if is_minor else "major"

        chords.append((chord_root, chord_type))

    return chords


# ============================================================================
# Utility Functions
# ============================================================================

def suggest_tempo(context: str) -> int:
    """Suggest a tempo for a game context."""
    import random
    low, high = TEMPO_RANGES.get(context, (100, 120))
    return random.randint(low, high)


def suggest_key(genre: str) -> str:
    """Suggest a key for a genre."""
    import random
    key_suggestions = {
        "fantasy": ["D", "G", "C", "Am", "Em"],
        "horror": ["Cm", "F#m", "Dm"],
        "scifi": ["Dm", "Bm", "Am"],
        "action": ["Em", "Am", "Cm"],
        "puzzle": ["C", "G", "F"],
        "retro": ["C", "G", "Am"],
        "synthwave": ["Am", "Em", "Dm", "Fm"],
        "ambient": ["Am", "Dm", "Em"],
    }
    keys = key_suggestions.get(genre.lower(), ["C", "Am"])
    return random.choice(keys)


def interval_name(semitones: int) -> str:
    """Get interval name from semitones."""
    intervals = {
        0: "unison", 1: "m2", 2: "M2", 3: "m3", 4: "M3", 5: "P4",
        6: "tritone", 7: "P5", 8: "m6", 9: "M6", 10: "m7", 11: "M7", 12: "octave"
    }
    return intervals.get(semitones % 12, f"+{semitones}")


def transpose(note: str, semitones: int) -> str:
    """Transpose a note by semitones."""
    midi = note_to_midi(note)
    return midi_to_note(midi + semitones)
