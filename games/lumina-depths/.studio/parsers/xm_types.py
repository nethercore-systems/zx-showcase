#!/usr/bin/env python3
"""
XM Types - API surface for XM file generation.

READ THIS FILE to understand the XM API. The implementation details
are in xm_writer.py (which you don't need to read).

Usage:
    from xm_types import XmModule, XmPattern, XmNote, XmInstrument, NOTE_OFF
    from xm_writer import write_xm

    module = XmModule(
        name="My Song",
        num_channels=4,
        patterns=[...],
        instruments=[...],
    )
    write_xm(module, "output.xm")
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import math


# ============================================================================
# Constants
# ============================================================================

# XM reference frequency (C-4 in XM)
XM_BASE_FREQ = 8363  # Hz

# Nethercore ZX standard sample rate
ZX_SAMPLE_RATE = 22050  # Hz

# Note values
NOTE_NONE = 0
NOTE_OFF = 97
NOTE_MIN = 1   # C-0
NOTE_MAX = 96  # B-7

# Limits
MAX_CHANNELS = 32
MAX_PATTERNS = 256
MAX_PATTERN_ROWS = 256
MAX_INSTRUMENTS = 128

# Effects (hex values for effect column)
EFFECT_ARPEGGIO = 0x0
EFFECT_PORTA_UP = 0x1
EFFECT_PORTA_DOWN = 0x2
EFFECT_TONE_PORTA = 0x3
EFFECT_VIBRATO = 0x4
EFFECT_TONE_PORTA_VOL_SLIDE = 0x5
EFFECT_VIBRATO_VOL_SLIDE = 0x6
EFFECT_TREMOLO = 0x7
EFFECT_SET_PANNING = 0x8
EFFECT_SAMPLE_OFFSET = 0x9
EFFECT_VOL_SLIDE = 0xA
EFFECT_POSITION_JUMP = 0xB
EFFECT_SET_VOLUME = 0xC
EFFECT_PATTERN_BREAK = 0xD
EFFECT_EXTENDED = 0xE
EFFECT_SET_SPEED_TEMPO = 0xF


# ============================================================================
# Pitch Correction Helpers
# ============================================================================

def calculate_pitch_correction(sample_rate: int) -> Tuple[int, int]:
    """
    Calculate finetune and relative_note for a sample at given sample rate.

    XM expects samples tuned for 8363 Hz at C-4. This function calculates
    the pitch correction needed to play a sample at the correct pitch.

    Args:
        sample_rate: The sample rate of the audio (e.g., 22050)

    Returns:
        Tuple of (finetune, relative_note)

    Examples:
        >>> calculate_pitch_correction(22050)  # ZX standard
        (101, 16)
        >>> calculate_pitch_correction(8363)   # XM native
        (0, 0)
    """
    semitones = 12.0 * math.log2(sample_rate / XM_BASE_FREQ)
    relative_note = int(math.floor(semitones))
    finetune = int(round((semitones - relative_note) * 128))

    if finetune >= 128:
        finetune -= 128
        relative_note += 1

    return (finetune, relative_note)


# ============================================================================
# Note Helpers
# ============================================================================

def note_from_name(name: str) -> int:
    """
    Convert note name to XM note value.

    Examples:
        note_from_name("C-4") -> 49
        note_from_name("A#3") -> 46
        note_from_name("---") -> 0 (no note)
        note_from_name("===") -> 97 (note off)
    """
    if name in ("---", "...", ""):
        return NOTE_NONE
    if name in ("===", "OFF"):
        return NOTE_OFF

    name = name.upper().replace("-", "")
    note_map = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

    note_char = name[0]
    if note_char not in note_map:
        raise ValueError(f"Invalid note: {name}")

    semitone = note_map[note_char]

    idx = 1
    if len(name) > 1 and name[1] == "#":
        semitone += 1
        idx = 2
    elif len(name) > 1 and name[1] == "B":
        semitone -= 1
        idx = 2

    octave = int(name[idx:])
    return octave * 12 + semitone + 1


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class XmNote:
    """Single note/command in a pattern cell."""
    note: int = 0           # 0=none, 1-96=C-0..B-7, 97=note-off
    instrument: int = 0     # 0=none, 1-128=instrument
    volume: int = 0         # 0=none, 0x10-0x50=set volume (0-64)
    effect: int = 0         # Effect command (0-35)
    effect_param: int = 0   # Effect parameter (0-255)

    def is_empty(self) -> bool:
        """Check if note cell is completely empty."""
        return (self.note == 0 and self.instrument == 0 and
                self.volume == 0 and self.effect == 0 and self.effect_param == 0)

    @staticmethod
    def off() -> "XmNote":
        """Create a note-off."""
        return XmNote(note=NOTE_OFF)

    @staticmethod
    def play(note_name: str, instrument: int, volume: int = 64) -> "XmNote":
        """Create a note with instrument and volume."""
        return XmNote(
            note=note_from_name(note_name),
            instrument=instrument,
            volume=0x10 + min(64, max(0, volume))
        )

    def with_effect(self, effect: int, param: int) -> "XmNote":
        """Add effect to this note (chainable)."""
        self.effect = effect
        self.effect_param = param
        return self


@dataclass
class XmPattern:
    """Pattern containing rows of note data."""
    num_rows: int = 64
    notes: List[List[XmNote]] = field(default_factory=list)  # [row][channel]

    @staticmethod
    def empty(num_rows: int, num_channels: int) -> "XmPattern":
        """Create an empty pattern with given dimensions."""
        notes = [[XmNote() for _ in range(num_channels)] for _ in range(num_rows)]
        return XmPattern(num_rows=num_rows, notes=notes)

    def set_note(self, row: int, channel: int, note: XmNote) -> None:
        """Set a note at the given position."""
        if row < len(self.notes) and channel < len(self.notes[row]):
            self.notes[row][channel] = note


@dataclass
class XmEnvelope:
    """Volume or panning envelope."""
    points: List[Tuple[int, int]] = field(default_factory=list)  # [(tick, value)]
    sustain_point: int = 0
    loop_start: int = 0
    loop_end: int = 0
    enabled: bool = False
    sustain_enabled: bool = False
    loop_enabled: bool = False


@dataclass
class XmInstrument:
    """
    Instrument with optional embedded sample data.

    ## Quick Start

    For ZX (22050 Hz) samples, use the convenience constructor:
    ```python
    kick = XmInstrument.for_zx("kick", kick_pcm_bytes)
    ```

    ## Pitch Correction

    XM expects 8363 Hz samples at C-4. Set `sample_rate` for auto-correction:
    ```python
    XmInstrument(name="kick", sample_rate=22050, sample_data=data)
    ```

    ## Sample Data

    - For embedded samples: provide sample_data as bytes (16-bit signed PCM)
    - For ROM-only: set sample_data=None
    """
    name: str = ""
    volume_envelope: Optional[XmEnvelope] = None
    panning_envelope: Optional[XmEnvelope] = None
    vibrato_type: int = 0      # 0=sine, 1=square, 2=ramp down, 3=ramp up
    vibrato_sweep: int = 0
    vibrato_depth: int = 0
    vibrato_rate: int = 0
    volume_fadeout: int = 0    # 0-4095
    sample_finetune: int = 0   # -128 to 127
    sample_relative_note: int = 0  # Semitones from C-4
    sample_loop_start: int = 0
    sample_loop_length: int = 0
    sample_loop_type: int = 0  # 0=none, 1=forward, 2=ping-pong
    sample_data: Optional[bytes] = None
    sample_bits: int = 16      # 8 or 16
    sample_rate: int = 0       # Hz (0 = use manual finetune/relative_note)

    def get_pitch_correction(self) -> Tuple[int, int]:
        """Get effective (finetune, relative_note) for this instrument."""
        if self.sample_rate > 0:
            return calculate_pitch_correction(self.sample_rate)
        return (self.sample_finetune, self.sample_relative_note)

    @staticmethod
    def for_zx(name: str, sample_data: Optional[bytes] = None, **kwargs) -> "XmInstrument":
        """
        Create an instrument configured for ZX 22050 Hz samples.

        Args:
            name: Instrument name (becomes ROM sample ID)
            sample_data: Optional PCM data (16-bit signed little-endian)
            **kwargs: Additional XmInstrument fields

        Example:
            kick = XmInstrument.for_zx("kick", kick_pcm_bytes)
        """
        return XmInstrument(
            name=name,
            sample_data=sample_data,
            sample_rate=ZX_SAMPLE_RATE,
            sample_bits=16,
            **kwargs
        )


@dataclass
class XmModule:
    """
    Complete XM module.

    Example:
        module = XmModule(
            name="Boss Theme",
            num_channels=8,
            default_speed=6,
            default_bpm=140,
            order_table=[0, 1, 1, 2, 1, 1, 2, 3],
            restart_position=1,
            patterns=[intro, verse, chorus, bridge],
            instruments=[kick, snare, hat, bass, lead],
        )
    """
    name: str = "Untitled"
    num_channels: int = 4
    default_speed: int = 6     # Ticks per row
    default_bpm: int = 125     # Beats per minute
    restart_position: int = 0  # Order position for looping
    linear_frequency_table: bool = True
    order_table: List[int] = field(default_factory=list)  # Pattern order
    patterns: List[XmPattern] = field(default_factory=list)
    instruments: List[XmInstrument] = field(default_factory=list)
