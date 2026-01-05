#!/usr/bin/env python3
"""
Song Parser - Converts .spec.py files (with SONG dict) to XM/IT tracker modules.

Deterministic tracker module generation from declarative specs. Follows the same
pattern as animation.py for animations and sound.py for audio.

Usage:
    python song_parser.py input.spec.py output.xm
    python song_parser.py input.spec.py output.it

Arguments:
    input.spec.py   - Path to song spec file (contains SONG dict)
    output.xm/it    - Output path for generated module

Example:
    python song_parser.py .studio/music/boss_theme.spec.py generated/tracks/boss_theme.xm

Requires xm_types.py, xm_writer.py, it_types.py, it_writer.py in the same directory
or accessible via PYTHONPATH.
"""

import sys
import os
import struct
import copy
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union


# =============================================================================
# CONSTANTS
# =============================================================================

SAMPLE_RATE = 22050  # ZX standard sample rate

# Effect name to XM effect code mapping
XM_EFFECT_MAP = {
    'arpeggio': 0x0,
    'porta_up': 0x1,
    'porta_down': 0x2,
    'tone_porta': 0x3,
    'vibrato': 0x4,
    'tone_porta_vol_slide': 0x5,
    'vibrato_vol_slide': 0x6,
    'tremolo': 0x7,
    'panning': 0x8,
    'sample_offset': 0x9,
    'vol_slide': 0xA,
    'position_jump': 0xB,
    'set_volume': 0xC,
    'pattern_break': 0xD,
    'extended': 0xE,
    'speed_tempo': 0xF,
}

# Effect name to IT effect code mapping (letter-based, A=1)
IT_EFFECT_MAP = {
    'set_speed': 1,          # A
    'position_jump': 2,      # B
    'pattern_break': 3,      # C
    'vol_slide': 4,          # D
    'porta_down': 5,         # E
    'porta_up': 6,           # F
    'tone_porta': 7,         # G
    'vibrato': 8,            # H
    'tremor': 9,             # I
    'arpeggio': 10,          # J
    'vibrato_vol_slide': 11, # K
    'tone_porta_vol_slide': 12,  # L
    'set_channel_vol': 13,   # M
    'channel_vol_slide': 14, # N
    'sample_offset': 15,     # O
    'panning_slide': 16,     # P
    'retrigger': 17,         # Q
    'tremolo': 18,           # R
    'extended': 19,          # S
    'tempo': 20,             # T
    'fine_vibrato': 21,      # U
}


# =============================================================================
# SPEC LOADING
# =============================================================================

def load_song_spec(spec_path: str) -> Dict[str, Any]:
    """Load SONG spec from .spec.py file via exec()."""
    with open(spec_path, 'r') as f:
        code = f.read()

    namespace = {}
    exec(code, namespace)

    if 'SONG' not in namespace:
        raise ValueError(f"No SONG dict found in {spec_path}")

    return namespace['SONG']


def resolve_paths(spec: Dict[str, Any], spec_dir: str) -> Dict[str, Any]:
    """Resolve relative paths in spec to absolute paths."""
    spec = copy.deepcopy(spec)
    song = spec.get('song', spec)

    # Resolve instrument paths
    for inst in song.get('instruments', []):
        if isinstance(inst, dict):
            if 'ref' in inst and not os.path.isabs(inst['ref']):
                inst['ref'] = os.path.join(spec_dir, inst['ref'])
            if 'wav' in inst and not os.path.isabs(inst['wav']):
                inst['wav'] = os.path.join(spec_dir, inst['wav'])

    return spec


# =============================================================================
# INSTRUMENT LOADING
# =============================================================================

def load_wav(wav_path: str) -> Tuple[bytes, int]:
    """Load sample data from WAV file. Returns (pcm_bytes, sample_rate)."""
    with open(wav_path, 'rb') as f:
        # Parse RIFF header
        riff = f.read(12)
        if riff[:4] != b'RIFF' or riff[8:12] != b'WAVE':
            raise ValueError(f"Invalid WAV file: {wav_path}")

        sample_rate = 22050
        bits_per_sample = 16
        data = b''

        # Parse chunks
        while True:
            chunk_header = f.read(8)
            if len(chunk_header) < 8:
                break

            chunk_id = chunk_header[:4]
            chunk_size = struct.unpack('<I', chunk_header[4:8])[0]

            if chunk_id == b'fmt ':
                fmt_data = f.read(chunk_size)
                sample_rate = struct.unpack('<I', fmt_data[4:8])[0]
                bits_per_sample = struct.unpack('<H', fmt_data[14:16])[0]
            elif chunk_id == b'data':
                data = f.read(chunk_size)
            else:
                f.seek(chunk_size, 1)

        return data, sample_rate


def generate_instrument_from_inline(inst_spec: Dict[str, Any]) -> np.ndarray:
    """Generate instrument from inline synthesis spec."""
    # Import sound_parser functions (assumes it's available)
    try:
        from sound_parser import generate_instrument
        wrapped = {'instrument': inst_spec}
        return generate_instrument(wrapped)
    except ImportError:
        # Fallback: generate a simple sine wave
        freq = 440.0
        base_note = inst_spec.get('base_note', 'C4')

        # Parse note to frequency
        note_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
        if isinstance(base_note, str) and len(base_note) >= 2:
            semitone = note_map.get(base_note[0].upper(), 0)
            octave = int(base_note[-1])
            midi = 12 + octave * 12 + semitone
            freq = 440.0 * (2 ** ((midi - 69) / 12))

        duration = inst_spec.get('output', {}).get('duration', 1.0)
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
        return np.sin(2 * np.pi * freq * t).astype(np.float32)


def load_instruments(
    spec: Dict[str, Any],
    spec_dir: str
) -> Tuple[List[bytes], List[str], List[int]]:
    """
    Load all instruments from spec.

    Returns:
        Tuple of (sample_data_list, instrument_names, sample_rates)
    """
    song = spec.get('song', spec)
    instruments = song.get('instruments', [])

    sample_data = []
    names = []
    rates = []

    for inst_spec in instruments:
        if isinstance(inst_spec, dict):
            if 'ref' in inst_spec:
                # External reference
                ref_path = inst_spec['ref']
                try:
                    from sound_parser import load_spec, generate_instrument
                    external_spec = load_spec(ref_path)
                    signal = generate_instrument(external_spec)
                    samples = np.clip(signal * 32767, -32768, 32767).astype(np.int16)
                    data = samples.tobytes()
                    name = external_spec.get('instrument', {}).get('name', 'instrument')
                    rate = external_spec.get('instrument', {}).get('sample_rate', SAMPLE_RATE)
                except ImportError:
                    print(f"Warning: sound_parser not available, using fallback for {ref_path}")
                    signal = generate_instrument_from_inline({'base_note': 'C4'})
                    samples = np.clip(signal * 32767, -32768, 32767).astype(np.int16)
                    data = samples.tobytes()
                    name = Path(ref_path).stem
                    rate = SAMPLE_RATE

            elif 'wav' in inst_spec:
                # Pre-recorded WAV
                wav_path = inst_spec['wav']
                data, rate = load_wav(wav_path)
                name = inst_spec.get('name', Path(wav_path).stem)

            else:
                # Inline synthesis
                signal = generate_instrument_from_inline(inst_spec)
                samples = np.clip(signal * 32767, -32768, 32767).astype(np.int16)
                data = samples.tobytes()
                name = inst_spec.get('name', 'inline')
                rate = inst_spec.get('sample_rate', SAMPLE_RATE)
        else:
            raise ValueError(f"Invalid instrument spec: {inst_spec}")

        sample_data.append(data)
        names.append(name)
        rates.append(rate)

    return sample_data, names, rates


# =============================================================================
# NOTE PARSING
# =============================================================================

def parse_note_name_xm(name: str) -> int:
    """Convert note name to XM note value."""
    if name in ('---', '...', '', None):
        return 0  # No note
    if name in ('===', 'OFF'):
        return 97  # Note off

    name = str(name).upper().replace('-', '')
    note_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

    if name[0] not in note_map:
        return 0

    semitone = note_map[name[0]]
    idx = 1

    if len(name) > 1 and name[1] == '#':
        semitone += 1
        idx = 2
    elif len(name) > 1 and name[1] == 'B':
        semitone -= 1
        idx = 2

    octave = int(name[idx:])
    return octave * 12 + semitone + 1


def parse_note_name_it(name: str) -> int:
    """Convert note name to IT note value."""
    if name in ('---', '...', '', None):
        return 0
    if name in ('===', 'OFF'):
        return 255  # Note off
    if name in ('^^^', 'CUT'):
        return 254  # Note cut
    if name in ('~~~', 'FADE'):
        return 253  # Note fade

    name = str(name).upper().replace('-', '')
    note_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

    if not name or name[0] not in note_map:
        return 0

    semitone = note_map[name[0]]
    idx = 1

    if len(name) > idx and name[idx] == '#':
        semitone += 1
        idx += 1
    elif len(name) > idx and name[idx] == 'B':
        semitone -= 1
        idx += 1

    try:
        octave = int(name[idx:])
    except ValueError:
        return 0

    note = octave * 12 + semitone
    return max(0, min(119, note))


# =============================================================================
# XM PATTERN BUILDING
# =============================================================================

def build_xm_patterns(
    spec: Dict[str, Any],
    num_channels: int
) -> Tuple[List[Any], Dict[str, int]]:
    """Build XM patterns from spec. Returns (patterns, name_to_index_map)."""
    from xm_types import XmPattern, XmNote

    song = spec.get('song', spec)
    pattern_specs = song.get('patterns', {})

    patterns = []
    pattern_map = {}

    for name, pattern_spec in pattern_specs.items():
        pattern_map[name] = len(patterns)

        num_rows = pattern_spec.get('rows', 64)
        notes_spec = pattern_spec.get('notes', {})

        pattern = XmPattern.empty(num_rows, num_channels)

        for channel_str, note_list in notes_spec.items():
            channel = int(channel_str)
            if channel >= num_channels:
                continue

            for note_spec in note_list:
                row = note_spec.get('row', 0)
                if row >= num_rows:
                    continue

                # Parse note
                note_val = note_spec.get('note')
                if isinstance(note_val, int):
                    note_num = note_val
                else:
                    note_num = parse_note_name_xm(note_val)

                # Instrument is 1-indexed in XM
                inst = note_spec.get('inst')
                if inst is not None:
                    inst += 1
                else:
                    inst = 0

                # Volume (XM uses 0x10-0x50 for set volume)
                vol = note_spec.get('vol', 0)
                if vol > 0:
                    vol = 0x10 + min(64, vol)

                # Effects
                effect = note_spec.get('effect', 0)
                param = note_spec.get('param', 0)

                # Handle named effects
                if 'effect_name' in note_spec:
                    effect = XM_EFFECT_MAP.get(note_spec['effect_name'], 0)
                    if 'effect_xy' in note_spec:
                        x, y = note_spec['effect_xy']
                        param = (x << 4) | y
                    else:
                        param = note_spec.get('param', 0)

                xm_note = XmNote(
                    note=note_num,
                    instrument=inst,
                    volume=vol,
                    effect=effect,
                    effect_param=param
                )
                pattern.set_note(row, channel, xm_note)

        patterns.append(pattern)

    return patterns, pattern_map


# =============================================================================
# IT PATTERN BUILDING
# =============================================================================

def build_it_patterns(
    spec: Dict[str, Any],
    num_channels: int
) -> Tuple[List[Any], Dict[str, int]]:
    """Build IT patterns from spec. Returns (patterns, name_to_index_map)."""
    from it_types import ItPattern, ItNote

    song = spec.get('song', spec)
    pattern_specs = song.get('patterns', {})

    patterns = []
    pattern_map = {}

    for name, pattern_spec in pattern_specs.items():
        pattern_map[name] = len(patterns)

        num_rows = pattern_spec.get('rows', 64)
        notes_spec = pattern_spec.get('notes', {})

        pattern = ItPattern.empty(num_rows, num_channels)

        for channel_str, note_list in notes_spec.items():
            channel = int(channel_str)
            if channel >= num_channels:
                continue

            for note_spec in note_list:
                row = note_spec.get('row', 0)
                if row >= num_rows:
                    continue

                # Parse note
                note_val = note_spec.get('note')
                if isinstance(note_val, int):
                    note_num = note_val
                else:
                    note_num = parse_note_name_it(note_val)

                # Instrument is 1-indexed in IT
                inst = note_spec.get('inst')
                if inst is not None:
                    inst += 1
                else:
                    inst = 0

                # Volume (IT uses 0-64 directly)
                vol = note_spec.get('vol', 0)

                # Effects
                effect = note_spec.get('effect', 0)
                param = note_spec.get('param', 0)

                # Handle named effects
                if 'effect_name' in note_spec:
                    effect = IT_EFFECT_MAP.get(note_spec['effect_name'], 0)
                    if 'effect_xy' in note_spec:
                        x, y = note_spec['effect_xy']
                        param = (x << 4) | y
                    else:
                        param = note_spec.get('param', 0)

                it_note = ItNote(
                    note=note_num,
                    instrument=inst,
                    volume=vol,
                    effect=effect,
                    effect_param=param
                )
                pattern.set_note(row, channel, it_note)

        patterns.append(pattern)

    return patterns, pattern_map


# =============================================================================
# ARRANGEMENT
# =============================================================================

def build_order_table(
    arrangement: List[Dict[str, Any]],
    pattern_map: Dict[str, int]
) -> List[int]:
    """Build order table from arrangement spec."""
    order = []

    for entry in arrangement:
        pattern_name = entry.get('pattern')
        if pattern_name not in pattern_map:
            raise ValueError(f"Unknown pattern in arrangement: {pattern_name}")

        pattern_idx = pattern_map[pattern_name]
        repeat = entry.get('repeat', 1)

        for _ in range(repeat):
            order.append(pattern_idx)

    return order


# =============================================================================
# AUTOMATION
# =============================================================================

def apply_automation_xm(
    patterns: List[Any],
    automation: List[Dict[str, Any]],
    pattern_map: Dict[str, int]
) -> None:
    """Apply automation to XM patterns (modifies in place)."""
    for auto in automation:
        auto_type = auto.get('type')

        if auto_type == 'volume_fade':
            pattern_name = auto.get('pattern')
            if pattern_name not in pattern_map:
                continue

            pattern_idx = pattern_map[pattern_name]
            pattern = patterns[pattern_idx]
            channel = auto.get('channel', 0)
            start_row = auto.get('start_row', 0)
            end_row = auto.get('end_row', 63)
            start_vol = auto.get('start_vol', 0)
            end_vol = auto.get('end_vol', 64)

            for row in range(start_row, min(end_row + 1, pattern.num_rows)):
                progress = (row - start_row) / max(1, end_row - start_row)
                vol = int(start_vol + (end_vol - start_vol) * progress)
                # XM volume column: 0x10 + volume
                pattern.notes[row][channel].volume = 0x10 + min(64, vol)

        elif auto_type == 'tempo_change':
            pattern_name = auto.get('pattern')
            if pattern_name not in pattern_map:
                continue

            pattern_idx = pattern_map[pattern_name]
            pattern = patterns[pattern_idx]
            row = auto.get('row', 0)
            bpm = auto.get('bpm', 125)

            # Find empty effect slot
            for ch in range(len(pattern.notes[row])):
                note = pattern.notes[row][ch]
                if note.effect == 0 and note.effect_param == 0:
                    note.effect = 0xF  # Speed/tempo
                    note.effect_param = bpm
                    break


def apply_automation_it(
    patterns: List[Any],
    automation: List[Dict[str, Any]],
    pattern_map: Dict[str, int]
) -> None:
    """Apply automation to IT patterns (modifies in place)."""
    for auto in automation:
        auto_type = auto.get('type')

        if auto_type == 'volume_fade':
            pattern_name = auto.get('pattern')
            if pattern_name not in pattern_map:
                continue

            pattern_idx = pattern_map[pattern_name]
            pattern = patterns[pattern_idx]
            channel = auto.get('channel', 0)
            start_row = auto.get('start_row', 0)
            end_row = auto.get('end_row', 63)
            start_vol = auto.get('start_vol', 0)
            end_vol = auto.get('end_vol', 64)

            for row in range(start_row, min(end_row + 1, pattern.num_rows)):
                progress = (row - start_row) / max(1, end_row - start_row)
                vol = int(start_vol + (end_vol - start_vol) * progress)
                pattern.notes[row][channel].volume = min(64, vol)

        elif auto_type == 'tempo_change':
            pattern_name = auto.get('pattern')
            if pattern_name not in pattern_map:
                continue

            pattern_idx = pattern_map[pattern_name]
            pattern = patterns[pattern_idx]
            row = auto.get('row', 0)
            bpm = auto.get('bpm', 125)

            for ch in range(len(pattern.notes[row])):
                note = pattern.notes[row][ch]
                if note.effect == 0 and note.effect_param == 0:
                    note.effect = 20  # IT tempo command (T)
                    note.effect_param = bpm
                    break


# =============================================================================
# MODULE BUILDING
# =============================================================================

def build_xm_module(
    spec: Dict[str, Any],
    patterns: List[Any],
    sample_data: List[bytes],
    instrument_names: List[str],
    sample_rates: List[int],
    order_table: List[int]
) -> Any:
    """Build complete XmModule from components."""
    from xm_types import XmModule, XmInstrument

    song = spec.get('song', spec)

    # Create instruments
    instruments = []
    for data, name, rate in zip(sample_data, instrument_names, sample_rates):
        inst = XmInstrument.for_zx(name, data)
        # Override sample rate if different
        if rate != 22050:
            inst.sample_rate = rate
        instruments.append(inst)

    return XmModule(
        name=song.get('title', song.get('name', 'Untitled')),
        num_channels=song.get('channels', 8),
        default_speed=song.get('speed', 6),
        default_bpm=song.get('bpm', 125),
        restart_position=song.get('restart_position', 0),
        linear_frequency_table=True,
        order_table=order_table,
        patterns=patterns,
        instruments=instruments
    )


def build_it_module(
    spec: Dict[str, Any],
    patterns: List[Any],
    sample_data: List[bytes],
    instrument_names: List[str],
    sample_rates: List[int],
    order_table: List[int]
) -> Any:
    """Build complete ItModule from components."""
    from it_types import (
        ItModule, ItInstrument, ItSample,
        NNA_CUT, FLAG_STEREO, FLAG_INSTRUMENTS, FLAG_LINEAR_SLIDES
    )

    song = spec.get('song', spec)
    it_opts = song.get('it_options', {})

    instruments = []
    samples = []

    for i, (data, name, rate) in enumerate(zip(sample_data, instrument_names, sample_rates)):
        # Create instrument
        inst = ItInstrument(
            name=name,
            nna=NNA_CUT,
            fadeout=256,
            note_sample_table=[(n, i + 1) for n in range(120)]
        )
        instruments.append(inst)

        # Create sample
        sample = ItSample(
            name=name,
            global_volume=64,
            default_volume=64,
            c5_speed=rate,
            length=len(data) // 2  # 16-bit samples
        )
        samples.append(sample)

    # Build flags
    flags = FLAG_INSTRUMENTS | FLAG_LINEAR_SLIDES
    if it_opts.get('stereo', True):
        flags |= FLAG_STEREO

    return ItModule(
        name=song.get('title', song.get('name', 'Untitled')),
        num_channels=song.get('channels', 8),
        default_speed=song.get('speed', 6),
        default_bpm=song.get('bpm', 125),
        global_volume=it_opts.get('global_volume', 128),
        mix_volume=it_opts.get('mix_volume', 48),
        flags=flags,
        order_table=order_table,
        patterns=patterns,
        instruments=instruments,
        samples=samples,
        sample_data=sample_data
    )


# =============================================================================
# MAIN
# =============================================================================

def parse_song(spec_path: str, output_path: str) -> None:
    """Parse song spec and generate XM/IT module."""
    print(f"Loading song spec: {spec_path}")

    spec = load_song_spec(spec_path)
    spec_dir = os.path.dirname(os.path.abspath(spec_path))
    spec = resolve_paths(spec, spec_dir)

    song = spec.get('song', spec)

    # Determine format from output extension or spec
    if output_path.lower().endswith('.it'):
        fmt = 'it'
    elif output_path.lower().endswith('.xm'):
        fmt = 'xm'
    else:
        fmt = song.get('format', 'xm')
        if not output_path.endswith(f'.{fmt}'):
            output_path += f'.{fmt}'

    num_channels = song.get('channels', 8)

    # Load instruments
    print("Loading instruments...")
    sample_data, instrument_names, sample_rates = load_instruments(spec, spec_dir)
    print(f"  Loaded {len(sample_data)} instruments")

    # Build patterns
    print("Building patterns...")
    if fmt == 'xm':
        patterns, pattern_map = build_xm_patterns(spec, num_channels)
    else:
        patterns, pattern_map = build_it_patterns(spec, num_channels)
    print(f"  Built {len(patterns)} patterns")

    # Build order table
    arrangement = song.get('arrangement', [])
    if not arrangement:
        # Default: play patterns in defined order
        arrangement = [{'pattern': name} for name in pattern_map.keys()]

    order_table = build_order_table(arrangement, pattern_map)
    print(f"  Order table: {len(order_table)} entries")

    # Apply automation
    automation = song.get('automation', [])
    if automation:
        print(f"Applying {len(automation)} automation entries...")
        if fmt == 'xm':
            apply_automation_xm(patterns, automation, pattern_map)
        else:
            apply_automation_it(patterns, automation, pattern_map)

    # Build and write module
    print(f"Building {fmt.upper()} module...")

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if fmt == 'xm':
        from xm_writer import write_xm
        module = build_xm_module(
            spec, patterns, sample_data, instrument_names, sample_rates, order_table
        )
        write_xm(module, output_path)
    else:
        from it_writer import write_it
        module = build_it_module(
            spec, patterns, sample_data, instrument_names, sample_rates, order_table
        )
        write_it(module, output_path)

    print(f"Wrote: {output_path}")
    print("Done!")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    spec_path = sys.argv[1]
    output_path = sys.argv[2]

    # Add current directory to path for imports
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    parse_song(spec_path, output_path)


if __name__ == "__main__":
    main()
