"""
XM Writer - Generate valid FastTracker 2 XM files programmatically.

This module provides complete XM file generation with:
- Effect command constants and helpers
- Envelope generators
- Composition helpers (PatternBuilder)
- Full XM file writing

Based on FastTracker 2 XM format v0x0104.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
import struct
import math


# ============================================================================
# Constants
# ============================================================================

XM_MAGIC = b"Extended Module: "
XM_VERSION = 0x0104
XM_HEADER_SIZE = 276

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


# ============================================================================
# Effect Command Constants
# ============================================================================

class Effect:
    """XM effect command constants (main effects 0-F and extended)."""
    # Main effects (effect column)
    ARPEGGIO = 0x00           # 0xy - Arpeggio
    PORTAMENTO_UP = 0x01      # 1xx - Portamento up
    PORTAMENTO_DOWN = 0x02    # 2xx - Portamento down
    TONE_PORTAMENTO = 0x03    # 3xx - Tone portamento (glide to note)
    VIBRATO = 0x04            # 4xy - Vibrato (x=speed, y=depth)
    TONE_PORTA_VOL_SLIDE = 0x05  # 5xy - Tone porta + volume slide
    VIBRATO_VOL_SLIDE = 0x06  # 6xy - Vibrato + volume slide
    TREMOLO = 0x07            # 7xy - Tremolo
    SET_PANNING = 0x08        # 8xx - Set panning (0=left, 128=center, 255=right)
    SAMPLE_OFFSET = 0x09      # 9xx - Sample offset (xx * 256 samples)
    VOLUME_SLIDE = 0x0A       # Axy - Volume slide (x=up, y=down)
    POSITION_JUMP = 0x0B      # Bxx - Position jump
    SET_VOLUME = 0x0C         # Cxx - Set volume (0-64)
    PATTERN_BREAK = 0x0D      # Dxx - Pattern break (go to row xx of next pattern)
    EXTENDED = 0x0E           # Exy - Extended effects
    SET_SPEED_TEMPO = 0x0F    # Fxx - Set speed (<32) or tempo (>=32)

    # Extended effects (effect column, Gxx-Xxx in some trackers)
    SET_GLOBAL_VOLUME = 0x10  # Gxx - Global volume
    GLOBAL_VOL_SLIDE = 0x11   # Hxy - Global volume slide
    KEY_OFF = 0x14            # Kxx - Key off at tick xx
    SET_ENVELOPE_POS = 0x15   # Lxx - Set envelope position
    PANNING_SLIDE = 0x19      # Pxy - Panning slide
    RETRIGGER = 0x1B          # Rxy - Retrigger note


class ExtendedEffect:
    """Extended effect sub-commands (Exy)."""
    FINE_PORTA_UP = 0x10      # E1x - Fine portamento up
    FINE_PORTA_DOWN = 0x20    # E2x - Fine portamento down
    GLISSANDO = 0x30          # E3x - Glissando control
    VIBRATO_WAVEFORM = 0x40   # E4x - Vibrato waveform
    SET_FINETUNE = 0x50       # E5x - Set finetune
    PATTERN_LOOP = 0x60       # E6x - Pattern loop
    TREMOLO_WAVEFORM = 0x70   # E7x - Tremolo waveform
    SET_PANNING_COARSE = 0x80 # E8x - Set panning (coarse)
    RETRIGGER_NOTE = 0x90     # E9x - Retrigger note every x ticks
    FINE_VOL_UP = 0xA0        # EAx - Fine volume up
    FINE_VOL_DOWN = 0xB0      # EBx - Fine volume down
    NOTE_CUT = 0xC0           # ECx - Note cut at tick x
    NOTE_DELAY = 0xD0         # EDx - Note delay until tick x
    PATTERN_DELAY = 0xE0      # EEx - Pattern delay x rows


class VolumeEffect:
    """Volume column effect ranges."""
    VOLUME_BASE = 0x10        # 0x10-0x50 = set volume 0-64
    VOLUME_MAX = 0x50
    SLIDE_DOWN = 0x60         # 0x60-0x6F = volume slide down
    SLIDE_UP = 0x70           # 0x70-0x7F = volume slide up
    FINE_DOWN = 0x80          # 0x80-0x8F = fine volume down
    FINE_UP = 0x90            # 0x90-0x9F = fine volume up
    VIBRATO_SPEED = 0xA0      # 0xA0-0xAF = vibrato speed
    VIBRATO_DEPTH = 0xB0      # 0xB0-0xBF = vibrato depth
    SET_PANNING = 0xC0        # 0xC0-0xCF = set panning
    PAN_SLIDE_LEFT = 0xD0     # 0xD0-0xDF = panning slide left
    PAN_SLIDE_RIGHT = 0xE0    # 0xE0-0xEF = panning slide right
    TONE_PORTAMENTO = 0xF0    # 0xF0-0xFF = tone portamento


# ============================================================================
# Effect Helper Functions
# ============================================================================

def arpeggio(semi1: int, semi2: int) -> Tuple[int, int]:
    """Create arpeggio effect (0xy). Returns (effect, param)."""
    return (Effect.ARPEGGIO, ((semi1 & 0x0F) << 4) | (semi2 & 0x0F))


def vibrato(speed: int, depth: int) -> Tuple[int, int]:
    """Create vibrato effect (4xy). Speed 0-15, depth 0-15."""
    return (Effect.VIBRATO, ((speed & 0x0F) << 4) | (depth & 0x0F))


def volume_slide(up: int = 0, down: int = 0) -> Tuple[int, int]:
    """Create volume slide (Axy). Either up or down, not both."""
    return (Effect.VOLUME_SLIDE, ((up & 0x0F) << 4) | (down & 0x0F))


def portamento_up(speed: int) -> Tuple[int, int]:
    """Create portamento up effect (1xx)."""
    return (Effect.PORTAMENTO_UP, speed & 0xFF)


def portamento_down(speed: int) -> Tuple[int, int]:
    """Create portamento down effect (2xx)."""
    return (Effect.PORTAMENTO_DOWN, speed & 0xFF)


def tone_portamento(speed: int) -> Tuple[int, int]:
    """Create tone portamento (3xx) - glide to target note."""
    return (Effect.TONE_PORTAMENTO, speed & 0xFF)


def set_tempo(bpm: int) -> Tuple[int, int]:
    """Set tempo (Fxx where xx >= 32)."""
    return (Effect.SET_SPEED_TEMPO, max(32, min(255, bpm)))


def set_speed(ticks_per_row: int) -> Tuple[int, int]:
    """Set speed (Fxx where xx < 32)."""
    return (Effect.SET_SPEED_TEMPO, min(31, max(1, ticks_per_row)))


def set_volume(vol: int) -> Tuple[int, int]:
    """Set volume (Cxx)."""
    return (Effect.SET_VOLUME, min(64, max(0, vol)))


def set_panning(position: int) -> Tuple[int, int]:
    """Set panning (8xx). 0=left, 128=center, 255=right."""
    return (Effect.SET_PANNING, position & 0xFF)


def note_cut(tick: int) -> Tuple[int, int]:
    """Cut note at tick (ECx)."""
    return (Effect.EXTENDED, ExtendedEffect.NOTE_CUT | (tick & 0x0F))


def note_delay(tick: int) -> Tuple[int, int]:
    """Delay note until tick (EDx)."""
    return (Effect.EXTENDED, ExtendedEffect.NOTE_DELAY | (tick & 0x0F))


def retrigger(ticks: int, vol_change: int = 0) -> Tuple[int, int]:
    """Retrigger note every N ticks (Rxy or E9x)."""
    if vol_change == 0:
        return (Effect.EXTENDED, ExtendedEffect.RETRIGGER_NOTE | (ticks & 0x0F))
    return (Effect.RETRIGGER, ((vol_change & 0x0F) << 4) | (ticks & 0x0F))


def pattern_break(row: int = 0) -> Tuple[int, int]:
    """Break to next pattern at row (Dxx)."""
    return (Effect.PATTERN_BREAK, row & 0xFF)


def position_jump(position: int) -> Tuple[int, int]:
    """Jump to order position (Bxx)."""
    return (Effect.POSITION_JUMP, position & 0xFF)


def sample_offset(offset_256: int) -> Tuple[int, int]:
    """Start sample at offset*256 samples (9xx)."""
    return (Effect.SAMPLE_OFFSET, offset_256 & 0xFF)


def pattern_loop(count: int = 0) -> Tuple[int, int]:
    """Pattern loop (E6x). count=0 sets start, count>0 loops."""
    return (Effect.EXTENDED, ExtendedEffect.PATTERN_LOOP | (count & 0x0F))


def tremolo(speed: int, depth: int) -> Tuple[int, int]:
    """Create tremolo effect (7xy)."""
    return (Effect.TREMOLO, ((speed & 0x0F) << 4) | (depth & 0x0F))


# ============================================================================
# Pitch Correction
# ============================================================================

def calculate_pitch_correction(sample_rate: int) -> Tuple[int, int]:
    """
    Calculate finetune and relative_note for a sample at given sample rate.

    XM expects samples tuned for 8363 Hz at C-4. This function calculates
    the pitch correction needed to play a sample at the correct pitch.

    Returns:
        Tuple of (finetune, relative_note)
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


def note_to_name(note: int) -> str:
    """Convert XM note value to name."""
    if note == 0:
        return "---"
    if note == 97:
        return "==="

    note -= 1
    octave = note // 12
    semitone = note % 12
    names = ["C-", "C#", "D-", "D#", "E-", "F-", "F#", "G-", "G#", "A-", "A#", "B-"]
    return f"{names[semitone]}{octave}"


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

    @staticmethod
    def with_effect(
        note_name: str,
        instrument: int,
        effect: Tuple[int, int],
        volume: int = 64
    ) -> "XmNote":
        """Create a note with effect."""
        return XmNote(
            note=note_from_name(note_name),
            instrument=instrument,
            volume=0x10 + min(64, max(0, volume)),
            effect=effect[0],
            effect_param=effect[1]
        )


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
class XmInstrument:
    """Instrument with optional embedded sample data."""
    name: str = ""
    volume_envelope: Optional[XmEnvelope] = None
    panning_envelope: Optional[XmEnvelope] = None
    vibrato_type: int = 0
    vibrato_sweep: int = 0
    vibrato_depth: int = 0
    vibrato_rate: int = 0
    volume_fadeout: int = 0
    sample_finetune: int = 0
    sample_relative_note: int = 0
    sample_loop_start: int = 0
    sample_loop_length: int = 0
    sample_loop_type: int = 0  # 0=none, 1=forward, 2=ping-pong
    sample_data: Optional[bytes] = None
    sample_bits: int = 16
    sample_rate: int = 0

    def get_pitch_correction(self) -> Tuple[int, int]:
        """Get effective finetune and relative_note."""
        if self.sample_rate > 0:
            return calculate_pitch_correction(self.sample_rate)
        return (self.sample_finetune, self.sample_relative_note)

    @staticmethod
    def for_zx(name: str, sample_data: Optional[bytes] = None, **kwargs) -> "XmInstrument":
        """Create instrument configured for ZX 22050 Hz samples."""
        return XmInstrument(
            name=name,
            sample_data=sample_data,
            sample_rate=ZX_SAMPLE_RATE,
            sample_bits=16,
            **kwargs
        )


@dataclass
class XmModule:
    """Complete XM module."""
    name: str = "Untitled"
    num_channels: int = 4
    default_speed: int = 6
    default_bpm: int = 125
    restart_position: int = 0
    linear_frequency_table: bool = True
    order_table: List[int] = field(default_factory=list)
    patterns: List[XmPattern] = field(default_factory=list)
    instruments: List[XmInstrument] = field(default_factory=list)


# ============================================================================
# Envelope Generators
# ============================================================================

def create_adsr_envelope(
    attack_ticks: int = 0,
    decay_ticks: int = 0,
    sustain_level: int = 48,
    release_ticks: int = 0,
    peak_level: int = 64
) -> XmEnvelope:
    """Create a standard ADSR volume envelope."""
    points = []
    current_tick = 0

    points.append((0, 0))
    if attack_ticks > 0:
        current_tick = attack_ticks
        points.append((current_tick, peak_level))
    else:
        points.append((0, peak_level))

    if decay_ticks > 0:
        current_tick += decay_ticks
        points.append((current_tick, sustain_level))

    sustain_point = len(points) - 1

    if release_ticks > 0:
        current_tick += release_ticks
        points.append((current_tick, 0))

    return XmEnvelope(
        points=points,
        sustain_point=sustain_point,
        enabled=True,
        sustain_enabled=True,
    )


def create_pad_envelope(attack_ms: int = 200, release_ms: int = 500) -> XmEnvelope:
    """Create slow attack/release envelope for pads."""
    attack_ticks = int(attack_ms / 20)
    release_ticks = int(release_ms / 20)
    return create_adsr_envelope(
        attack_ticks=attack_ticks,
        decay_ticks=0,
        sustain_level=50,
        release_ticks=release_ticks
    )


def create_pluck_envelope(decay_ms: int = 150) -> XmEnvelope:
    """Create quick attack, medium decay for plucked sounds."""
    decay_ticks = int(decay_ms / 20)
    return create_adsr_envelope(
        attack_ticks=0,
        decay_ticks=decay_ticks,
        sustain_level=0,
        release_ticks=0,
        peak_level=64
    )


def create_organ_envelope() -> XmEnvelope:
    """Create instant attack/release (organ style)."""
    return create_adsr_envelope(
        attack_ticks=0,
        decay_ticks=0,
        sustain_level=64,
        release_ticks=0
    )


def create_tremolo_envelope(
    speed_ticks: int = 4,
    depth_low: int = 32,
    depth_high: int = 64,
    cycles: int = 4
) -> XmEnvelope:
    """Create tremolo effect via envelope looping."""
    points = []
    tick = 0
    for _ in range(cycles):
        points.append((tick, depth_high))
        tick += speed_ticks
        points.append((tick, depth_low))
        tick += speed_ticks

    return XmEnvelope(
        points=points[:12],  # XM max 12 points
        loop_start=0,
        loop_end=min(len(points) - 1, 11),
        enabled=True,
        loop_enabled=True,
    )


# ============================================================================
# Pattern Builder
# ============================================================================

class PatternBuilder:
    """Helper for building patterns programmatically."""

    def __init__(self, num_rows: int = 64, num_channels: int = 8):
        self.num_rows = num_rows
        self.num_channels = num_channels
        self.notes = [[XmNote() for _ in range(num_channels)] for _ in range(num_rows)]

    def note_on(
        self,
        row: int,
        channel: int,
        note: str,
        instrument: int,
        volume: int = 64,
        effect: Tuple[int, int] = None
    ) -> "PatternBuilder":
        """Add a note at position."""
        if 0 <= row < self.num_rows and 0 <= channel < self.num_channels:
            xm_note = XmNote(
                note=note_from_name(note),
                instrument=instrument,
                volume=0x10 + min(64, max(0, volume)),
            )
            if effect:
                xm_note.effect, xm_note.effect_param = effect
            self.notes[row][channel] = xm_note
        return self

    def note_off(self, row: int, channel: int) -> "PatternBuilder":
        """Add note off at position."""
        if 0 <= row < self.num_rows and 0 <= channel < self.num_channels:
            self.notes[row][channel] = XmNote.off()
        return self

    def effect_only(
        self,
        row: int,
        channel: int,
        effect: Tuple[int, int]
    ) -> "PatternBuilder":
        """Add effect without note."""
        if 0 <= row < self.num_rows and 0 <= channel < self.num_channels:
            self.notes[row][channel].effect = effect[0]
            self.notes[row][channel].effect_param = effect[1]
        return self

    def drum_pattern(
        self,
        channel: int,
        instrument: int,
        pattern: str,
        volume: int = 64,
        note: str = "C-4"
    ) -> "PatternBuilder":
        """
        Add drum pattern using string notation.

        pattern: "x---x---x---x---" where x=hit, -=rest
        """
        step = self.num_rows // len(pattern)
        for i, char in enumerate(pattern):
            if char.lower() == 'x':
                row = i * step
                self.note_on(row, channel, note, instrument, volume)
        return self

    def arpeggio_line(
        self,
        channel: int,
        instrument: int,
        root: str,
        chord_type: str,
        step: int = 2,
        octave: int = 4,
        volume: int = 48
    ) -> "PatternBuilder":
        """Add arpeggiated chord throughout pattern."""
        from .music_theory import get_chord_midi, midi_to_note
        notes = get_chord_midi(root, chord_type, octave)
        for row in range(0, self.num_rows, step):
            note_idx = (row // step) % len(notes)
            note_name = midi_to_note(notes[note_idx])
            xm_note = note_from_name(note_name)
            self.notes[row][channel] = XmNote(
                note=xm_note,
                instrument=instrument,
                volume=0x10 + volume
            )
        return self

    def bass_line(
        self,
        channel: int,
        instrument: int,
        root: str,
        octave: int = 2,
        pattern: str = "x---x---",
        volume: int = 60
    ) -> "PatternBuilder":
        """Add simple bass line on root note."""
        note_name = f"{root}-{octave}"
        step = self.num_rows // len(pattern)
        for i, char in enumerate(pattern):
            if char.lower() == 'x':
                row = i * step
                self.note_on(row, channel, note_name, instrument, volume)
        return self

    def chord(
        self,
        row: int,
        start_channel: int,
        root: str,
        chord_type: str,
        instrument: int,
        octave: int = 4,
        volume: int = 48
    ) -> "PatternBuilder":
        """Play a chord across multiple channels."""
        from .music_theory import get_chord_midi, midi_to_note
        notes = get_chord_midi(root, chord_type, octave)
        for i, midi in enumerate(notes):
            ch = start_channel + i
            if ch < self.num_channels:
                self.note_on(row, ch, midi_to_note(midi), instrument, volume)
        return self

    def build(self) -> XmPattern:
        """Build the XmPattern."""
        return XmPattern(num_rows=self.num_rows, notes=self.notes)


# ============================================================================
# Pattern Packing
# ============================================================================

def pack_pattern_data(pattern: XmPattern, num_channels: int) -> bytes:
    """Pack pattern data using XM compressed format."""
    output = bytearray()

    for row in pattern.notes:
        for ch_idx in range(min(len(row), num_channels)):
            note = row[ch_idx]

            if note.is_empty():
                output.append(0x80)
                continue

            flags = 0x80
            if note.note != 0:
                flags |= 0x01
            if note.instrument != 0:
                flags |= 0x02
            if note.volume != 0:
                flags |= 0x04
            if note.effect != 0:
                flags |= 0x08
            if note.effect_param != 0:
                flags |= 0x10

            output.append(flags)

            if note.note != 0:
                output.append(note.note)
            if note.instrument != 0:
                output.append(note.instrument)
            if note.volume != 0:
                output.append(note.volume)
            if note.effect != 0:
                output.append(note.effect)
            if note.effect_param != 0:
                output.append(note.effect_param)

    return bytes(output)


# ============================================================================
# XM File Writer
# ============================================================================

def write_xm(module: XmModule, output_path: str) -> None:
    """Write XM module to file."""
    output = bytearray()

    num_patterns = len(module.patterns)
    num_instruments = len(module.instruments)
    song_length = len(module.order_table) if module.order_table else 1

    if num_patterns > MAX_PATTERNS:
        raise ValueError(f"Too many patterns: {num_patterns}")
    if num_instruments > MAX_INSTRUMENTS:
        raise ValueError(f"Too many instruments: {num_instruments}")
    if module.num_channels > MAX_CHANNELS:
        raise ValueError(f"Too many channels: {module.num_channels}")

    # XM Header
    output.extend(XM_MAGIC)
    name_bytes = module.name.encode("ascii", errors="replace")[:20]
    output.extend(name_bytes.ljust(20, b"\x00"))
    output.append(0x1A)
    tracker_name = b"ZX Showcase procgen "
    output.extend(tracker_name.ljust(20, b"\x00"))
    output.extend(struct.pack("<H", XM_VERSION))
    output.extend(struct.pack("<I", 276))
    output.extend(struct.pack("<H", song_length))
    output.extend(struct.pack("<H", module.restart_position))
    output.extend(struct.pack("<H", module.num_channels))
    output.extend(struct.pack("<H", num_patterns))
    output.extend(struct.pack("<H", num_instruments))
    flags = 1 if module.linear_frequency_table else 0
    output.extend(struct.pack("<H", flags))
    output.extend(struct.pack("<H", module.default_speed))
    output.extend(struct.pack("<H", module.default_bpm))

    for i in range(256):
        if i < len(module.order_table):
            output.append(module.order_table[i])
        else:
            output.append(0)

    # Patterns
    for pattern in module.patterns:
        packed_data = pack_pattern_data(pattern, module.num_channels)
        output.extend(struct.pack("<I", 9))
        output.append(0)
        output.extend(struct.pack("<H", pattern.num_rows))
        output.extend(struct.pack("<H", len(packed_data)))
        output.extend(packed_data)

    # Instruments
    for instrument in module.instruments:
        _write_instrument(output, instrument)

    with open(output_path, "wb") as f:
        f.write(output)


def _delta_encode_16bit(sample_data: bytes) -> bytes:
    """Delta-encode 16-bit signed PCM samples."""
    num_samples = len(sample_data) // 2
    samples = struct.unpack(f"<{num_samples}h", sample_data)

    encoded = []
    prev = 0
    for sample in samples:
        delta = (sample - prev) & 0xFFFF
        encoded.append(delta)
        prev = sample

    return struct.pack(f"<{len(encoded)}H", *encoded)


def _write_instrument(output: bytearray, instrument: XmInstrument) -> None:
    """Write a single instrument to the output buffer."""
    num_samples = 1
    header_size = 263

    output.extend(struct.pack("<I", header_size))

    name_bytes = instrument.name.encode("ascii", errors="replace")[:22]
    output.extend(name_bytes.ljust(22, b"\x00"))

    output.append(0)
    output.extend(struct.pack("<H", num_samples))
    output.extend(struct.pack("<I", 40))
    output.extend(bytes(96))

    vol_env = instrument.volume_envelope
    for i in range(12):
        if vol_env and i < len(vol_env.points):
            output.extend(struct.pack("<HH", vol_env.points[i][0], vol_env.points[i][1]))
        else:
            output.extend(struct.pack("<HH", 0, 0))

    pan_env = instrument.panning_envelope
    for i in range(12):
        if pan_env and i < len(pan_env.points):
            output.extend(struct.pack("<HH", pan_env.points[i][0], pan_env.points[i][1]))
        else:
            output.extend(struct.pack("<HH", 0, 0))

    output.append(len(vol_env.points) if vol_env else 0)
    output.append(len(pan_env.points) if pan_env else 0)

    output.append(vol_env.sustain_point if vol_env else 0)
    output.append(vol_env.loop_start if vol_env else 0)
    output.append(vol_env.loop_end if vol_env else 0)

    output.append(pan_env.sustain_point if pan_env else 0)
    output.append(pan_env.loop_start if pan_env else 0)
    output.append(pan_env.loop_end if pan_env else 0)

    vol_flags = 0
    if vol_env:
        if vol_env.enabled:
            vol_flags |= 1
        if vol_env.sustain_enabled:
            vol_flags |= 2
        if vol_env.loop_enabled:
            vol_flags |= 4
    output.append(vol_flags)

    pan_flags = 0
    if pan_env:
        if pan_env.enabled:
            pan_flags |= 1
        if pan_env.sustain_enabled:
            pan_flags |= 2
        if pan_env.loop_enabled:
            pan_flags |= 4
    output.append(pan_flags)

    output.append(instrument.vibrato_type)
    output.append(instrument.vibrato_sweep)
    output.append(instrument.vibrato_depth)
    output.append(instrument.vibrato_rate)

    output.extend(struct.pack("<H", instrument.volume_fadeout))
    output.extend(bytes(22))

    # Sample header
    finetune, relative_note = instrument.get_pitch_correction()
    sample_len = len(instrument.sample_data) if instrument.sample_data else 0

    output.extend(struct.pack("<I", sample_len))
    output.extend(struct.pack("<I", instrument.sample_loop_start))
    output.extend(struct.pack("<I", instrument.sample_loop_length))
    output.append(64)
    output.append(finetune & 0xFF)

    type_byte = instrument.sample_loop_type & 0x03
    if instrument.sample_bits == 16:
        type_byte |= 0x10
    output.append(type_byte)

    output.append(128)
    output.append(relative_note & 0xFF)
    output.append(0)

    output.extend(name_bytes.ljust(22, b"\x00"))

    if instrument.sample_data:
        if instrument.sample_bits == 16:
            output.extend(_delta_encode_16bit(instrument.sample_data))
        else:
            output.extend(instrument.sample_data)


# ============================================================================
# Validation
# ============================================================================

def validate_xm(path: str) -> bool:
    """Validate that an XM file has correct magic and version."""
    with open(path, "rb") as f:
        data = f.read(64)

    if len(data) < 60:
        raise ValueError(f"File too small: {len(data)} bytes")

    if data[:17] != XM_MAGIC:
        raise ValueError(f"Invalid magic: {data[:17]!r}")

    version = struct.unpack("<H", data[58:60])[0]
    if version != XM_VERSION:
        raise ValueError(f"Unsupported version: 0x{version:04X}")

    return True
