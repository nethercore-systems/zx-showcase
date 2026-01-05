#!/usr/bin/env python3
"""
IT Types - API surface for IT (Impulse Tracker) file generation.

READ THIS FILE to understand the IT API. The implementation details
are in it_writer.py (which you don't need to read).

IT format advantages over XM:
- Up to 64 channels (vs XM's 32)
- NNA (New Note Actions) for polyphonic instruments
- Pitch envelopes (in addition to volume/panning)
- Resonant filters
- Multi-sample instruments

Usage:
    from it_types import ItModule, ItPattern, ItNote, ItInstrument, ItSample
    from it_types import NOTE_OFF, NNA_FADE, NNA_CUT
    from it_writer import write_it

    module = ItModule(
        name="My Song",
        num_channels=8,
        patterns=[...],
        instruments=[...],
        samples=[...],
        sample_data=[...],
    )
    write_it(module, "output.it")
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# =============================================================================
# Constants
# =============================================================================

# Note values
NOTE_MIN = 0
NOTE_MAX = 119
NOTE_FADE = 253
NOTE_CUT = 254
NOTE_OFF = 255

# Order table markers
ORDER_END = 255
ORDER_SKIP = 254

# IT Flags (for ItModule.flags)
FLAG_STEREO = 0x01
FLAG_VOL_0_MIX = 0x02
FLAG_INSTRUMENTS = 0x04
FLAG_LINEAR_SLIDES = 0x08
FLAG_OLD_EFFECTS = 0x10
FLAG_LINK_G_MEMORY = 0x20

# Sample Flags (for ItSample.flags)
SAMPLE_LOOP = 0x10
SAMPLE_SUSTAIN_LOOP = 0x20
SAMPLE_LOOP_PINGPONG = 0x40
SAMPLE_SUSTAIN_PINGPONG = 0x80

# Envelope Flags (for ItEnvelope.flags)
ENV_ENABLED = 0x01
ENV_LOOP = 0x02
ENV_SUSTAIN_LOOP = 0x04
ENV_CARRY = 0x08
ENV_FILTER = 0x80

# NNA (New Note Action) - what happens when a new note plays
NNA_CUT = 0       # Cut previous note immediately
NNA_CONTINUE = 1  # Continue previous note
NNA_OFF = 2       # Note-off previous note
NNA_FADE = 3      # Fade out previous note

# DCT (Duplicate Check Type)
DCT_OFF = 0
DCT_NOTE = 1
DCT_SAMPLE = 2
DCT_INSTRUMENT = 3

# DCA (Duplicate Check Action)
DCA_CUT = 0
DCA_OFF = 1
DCA_FADE = 2

# Effects (letter-based, A=1, B=2, etc.)
EFFECT_SET_SPEED = 1          # A - Set speed
EFFECT_POSITION_JUMP = 2      # B - Position jump
EFFECT_PATTERN_BREAK = 3      # C - Pattern break
EFFECT_VOLUME_SLIDE = 4       # D - Volume slide
EFFECT_PORTA_DOWN = 5         # E - Portamento down
EFFECT_PORTA_UP = 6           # F - Portamento up
EFFECT_TONE_PORTA = 7         # G - Tone portamento
EFFECT_VIBRATO = 8            # H - Vibrato
EFFECT_TREMOR = 9             # I - Tremor
EFFECT_ARPEGGIO = 10          # J - Arpeggio
EFFECT_VIBRATO_VOL_SLIDE = 11 # K - Vibrato + volume slide
EFFECT_TONE_PORTA_VOL_SLIDE = 12  # L - Tone porta + volume slide
EFFECT_SET_CHANNEL_VOL = 13   # M - Set channel volume
EFFECT_CHANNEL_VOL_SLIDE = 14 # N - Channel volume slide
EFFECT_SAMPLE_OFFSET = 15     # O - Sample offset
EFFECT_PANNING_SLIDE = 16     # P - Panning slide
EFFECT_RETRIGGER = 17         # Q - Retrigger
EFFECT_TREMOLO = 18           # R - Tremolo
EFFECT_EXTENDED = 19          # S - Extended effects
EFFECT_TEMPO = 20             # T - Set tempo
EFFECT_FINE_VIBRATO = 21      # U - Fine vibrato


# =============================================================================
# Note Helpers
# =============================================================================

def note_from_name(name: str) -> int:
    """
    Convert note name to IT note number.

    Examples:
        note_from_name("C-4") -> 48
        note_from_name("A#5") -> 70
        note_from_name("---") -> 0
    """
    name = name.strip().replace('-', '')

    if not name or name == "":
        return 0

    semitone_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

    if name[0] not in semitone_map:
        return 0

    semitone = semitone_map[name[0]]
    offset = 1

    if len(name) > offset:
        if name[offset] == '#':
            semitone += 1
            offset += 1
        elif name[offset] == 'b':
            semitone -= 1
            offset += 1

    try:
        octave = int(name[offset:])
    except ValueError:
        return 0

    if not (0 <= octave <= 9):
        return 0

    note = octave * 12 + semitone
    return max(0, min(119, note))


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ItNote:
    """Single note/command in a pattern cell."""
    note: int = 0              # 0=none, 1-119=C-0..B-9, 254=cut, 255=off
    instrument: int = 0        # 0=none, 1-99=instrument
    volume: int = 0            # Volume column (0-64)
    effect: int = 0            # Effect letter (A=1, B=2, etc.)
    effect_param: int = 0      # Effect parameter (0-255)

    @staticmethod
    def play(note_name: str, instrument: int, volume: int) -> 'ItNote':
        """Create a note with pitch, instrument, and volume."""
        return ItNote(
            note=note_from_name(note_name),
            instrument=instrument,
            volume=min(64, volume),
        )

    @staticmethod
    def play_note(note: int, instrument: int, volume: int) -> 'ItNote':
        """Create a note with MIDI note number."""
        return ItNote(
            note=min(119, note),
            instrument=instrument,
            volume=min(64, volume),
        )

    @staticmethod
    def off() -> 'ItNote':
        """Create a note-off (^^^)."""
        return ItNote(note=NOTE_OFF)

    @staticmethod
    def cut() -> 'ItNote':
        """Create a note-cut (===)."""
        return ItNote(note=NOTE_CUT)

    @staticmethod
    def fade() -> 'ItNote':
        """Create a note-fade."""
        return ItNote(note=NOTE_FADE)

    def with_effect(self, effect: int, param: int) -> 'ItNote':
        """Add effect to note (chainable)."""
        self.effect = effect
        self.effect_param = param
        return self


@dataclass
class ItEnvelope:
    """Envelope for volume, panning, or pitch."""
    points: List[Tuple[int, int]] = field(default_factory=list)  # [(tick, value)]
    loop_begin: int = 0
    loop_end: int = 0
    sustain_begin: int = 0
    sustain_end: int = 0
    flags: int = 0  # Use ENV_ENABLED, ENV_LOOP, ENV_SUSTAIN_LOOP


@dataclass
class ItInstrument:
    """
    IT instrument definition.

    ## NNA (New Note Action)

    IT's killer feature for polyphony. When a new note plays on a channel
    that already has a note playing:
    - NNA_CUT: Cut previous note immediately (default, like XM)
    - NNA_CONTINUE: Both notes play (uses virtual channels)
    - NNA_OFF: Previous note gets note-off
    - NNA_FADE: Previous note fades out

    Example (polyphonic piano):
        piano = ItInstrument(
            name="Piano",
            nna=NNA_FADE,      # Fade previous notes
            dct=DCT_NOTE,      # Check for duplicate notes
            dca=DCA_FADE,      # Fade duplicates
            fadeout=512,
        )
    """
    name: str = ""
    filename: str = ""
    nna: int = NNA_CUT
    dct: int = DCT_OFF
    dca: int = DCA_CUT
    fadeout: int = 256
    pitch_pan_separation: int = 0
    pitch_pan_center: int = 60
    global_volume: int = 128
    default_pan: Optional[int] = 32  # 0-64, None = disabled
    random_volume: int = 0
    random_pan: int = 0
    note_sample_table: List[Tuple[int, int]] = field(default_factory=lambda: [(i, 1) for i in range(120)])
    volume_envelope: Optional[ItEnvelope] = None
    panning_envelope: Optional[ItEnvelope] = None
    pitch_envelope: Optional[ItEnvelope] = None  # IT-only feature!
    filter_cutoff: Optional[int] = None  # 0-127
    filter_resonance: Optional[int] = None  # 0-127
    midi_channel: int = 0
    midi_program: int = 0
    midi_bank: int = 0


@dataclass
class ItSample:
    """IT sample definition."""
    name: str = ""
    filename: str = ""
    global_volume: int = 64
    flags: int = 0  # Use SAMPLE_LOOP, SAMPLE_LOOP_PINGPONG, etc.
    default_volume: int = 64
    default_pan: Optional[int] = None
    length: int = 0
    loop_begin: int = 0
    loop_end: int = 0
    c5_speed: int = 22050  # Sample rate for C-5 playback
    sustain_loop_begin: int = 0
    sustain_loop_end: int = 0
    vibrato_speed: int = 0
    vibrato_depth: int = 0
    vibrato_rate: int = 0
    vibrato_type: int = 0


@dataclass
class ItPattern:
    """IT pattern containing rows of note data."""
    num_rows: int
    notes: List[List[ItNote]]  # [row][channel]

    @staticmethod
    def empty(num_rows: int, num_channels: int) -> 'ItPattern':
        """Create an empty pattern."""
        notes = [[ItNote() for _ in range(num_channels)] for _ in range(num_rows)]
        return ItPattern(num_rows=num_rows, notes=notes)

    def set_note(self, row: int, channel: int, note: ItNote) -> None:
        """Set a note at the given row and channel."""
        if 0 <= row < len(self.notes) and 0 <= channel < len(self.notes[0]):
            self.notes[row][channel] = note


@dataclass
class ItModule:
    """
    Complete IT module.

    Example:
        module = ItModule(
            name="Boss Theme",
            num_channels=8,
            default_speed=6,
            default_bpm=140,
            order_table=[0, 1, 1, 2, 1, 1, 2, 3],
            patterns=[intro, verse, chorus, bridge],
            instruments=[piano, strings, bass],
            samples=[piano_sample, strings_sample, bass_sample],
            sample_data=[piano_bytes, strings_bytes, bass_bytes],
        )
    """
    name: str = "Untitled"
    num_channels: int = 4
    default_speed: int = 6
    default_bpm: int = 125
    global_volume: int = 128
    mix_volume: int = 48
    panning_separation: int = 128
    pitch_wheel_depth: int = 0
    flags: int = FLAG_STEREO | FLAG_INSTRUMENTS | FLAG_LINEAR_SLIDES
    order_table: List[int] = field(default_factory=list)
    patterns: List[ItPattern] = field(default_factory=list)
    instruments: List[ItInstrument] = field(default_factory=list)
    samples: List[ItSample] = field(default_factory=list)
    sample_data: List[bytes] = field(default_factory=list)  # Raw PCM for each sample
    message: Optional[str] = None
