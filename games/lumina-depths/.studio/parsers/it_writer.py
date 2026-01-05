#!/usr/bin/env python3
"""
IT Writer - Implementation for writing IT (Impulse Tracker) files.

DO NOT READ THIS FILE for API understanding - read it_types.py instead.
This file contains only binary packing implementation details.

Usage:
    from it_types import ItModule, ItPattern, ItNote, ItInstrument, ItSample
    from it_writer import write_it, validate_it

    module = ItModule(...)
    write_it(module, "output.it")
"""

from it_types import (
    ItModule, ItPattern, ItNote, ItInstrument, ItSample, ItEnvelope,
)
import struct

# Internal constants
IT_MAGIC = b"IMPM"
INSTRUMENT_MAGIC = b"IMPI"
SAMPLE_MAGIC = b"IMPS"

SAMPLE_HAS_DATA = 0x01
SAMPLE_16BIT = 0x02


# =============================================================================
# Internal Helpers
# =============================================================================

def _write_string(data: bytearray, s: str, length: int):
    """Write a fixed-length string, padded with zeros."""
    b = s.encode('latin-1')[:length]
    data.extend(b)
    data.extend(bytes(length - len(b)))


def _write_envelope(env: ItEnvelope | None) -> bytes:
    """Write envelope data (82 bytes)."""
    data = bytearray()

    if env is None:
        env = ItEnvelope()

    data.append(env.flags)

    num_points = min(len(env.points), 25)
    data.append(num_points)

    data.append(env.loop_begin)
    data.append(env.loop_end)
    data.append(env.sustain_begin)
    data.append(env.sustain_end)

    for i in range(25):
        if i < len(env.points):
            tick, value = env.points[i]
            data.append(value & 0xFF)
            data.extend(struct.pack('<H', tick))
        else:
            data.extend(bytes(3))

    data.append(0)  # Reserved

    return bytes(data)


def _pack_pattern(pattern: ItPattern, num_channels: int) -> bytes:
    """Pack pattern data using IT compression."""
    data = bytearray()

    prev_note = [0] * 64
    prev_instrument = [0] * 64
    prev_volume = [0] * 64
    prev_effect = [0] * 64
    prev_effect_param = [0] * 64

    for row in pattern.notes:
        for channel, note in enumerate(row[:num_channels]):
            if (note.note == 0 and note.instrument == 0 and
                note.volume == 0 and note.effect == 0 and note.effect_param == 0):
                continue

            mask = 0

            if note.note != 0 and note.note != prev_note[channel]:
                mask |= 0x01
                prev_note[channel] = note.note
            elif note.note != 0:
                mask |= 0x10

            if note.instrument != 0 and note.instrument != prev_instrument[channel]:
                mask |= 0x02
                prev_instrument[channel] = note.instrument
            elif note.instrument != 0:
                mask |= 0x20

            if note.volume != 0 and note.volume != prev_volume[channel]:
                mask |= 0x04
                prev_volume[channel] = note.volume
            elif note.volume != 0:
                mask |= 0x40

            if ((note.effect != 0 or note.effect_param != 0) and
                (note.effect != prev_effect[channel] or note.effect_param != prev_effect_param[channel])):
                mask |= 0x08
                prev_effect[channel] = note.effect
                prev_effect_param[channel] = note.effect_param
            elif note.effect != 0 or note.effect_param != 0:
                mask |= 0x80

            if mask == 0:
                continue

            data.append(channel | 0x80)
            data.append(mask)

            if mask & 0x01:
                data.append(note.note)
            if mask & 0x02:
                data.append(note.instrument)
            if mask & 0x04:
                data.append(note.volume)
            if mask & 0x08:
                data.append(note.effect)
                data.append(note.effect_param)

        data.append(0)  # End of row

    return bytes(data)


# =============================================================================
# Public API
# =============================================================================

def write_it(module: ItModule, filename: str) -> None:
    """
    Write IT module to file.

    Args:
        module: ItModule containing song data
        filename: Path to write the .it file
    """
    data = bytearray()

    # Calculate offsets
    header_size = 192
    orders_size = len(module.order_table)
    num_instruments = len(module.instruments)
    num_samples = len(module.samples)
    num_patterns = len(module.patterns)

    offset_table_start = header_size + orders_size
    offset_table_size = (num_instruments + num_samples + num_patterns) * 4

    # Message
    message_offset = 0
    message_size = 0
    special = 0
    if module.message:
        message_offset = offset_table_start + offset_table_size
        message_size = len(module.message) + 1
        special = 1

    # Instruments
    instruments_start = offset_table_start + offset_table_size + message_size
    instrument_size = 550
    instrument_offsets = [instruments_start + i * instrument_size for i in range(num_instruments)]

    # Samples
    samples_start = instruments_start + num_instruments * instrument_size
    sample_header_size = 80
    sample_offsets = [samples_start + i * sample_header_size for i in range(num_samples)]

    # Patterns
    patterns_start = samples_start + num_samples * sample_header_size
    packed_patterns = [_pack_pattern(p, module.num_channels) for p in module.patterns]
    pattern_offsets = []
    current_offset = patterns_start
    for packed in packed_patterns:
        pattern_offsets.append(current_offset)
        current_offset += 8 + len(packed)

    # Sample data
    sample_data_start = current_offset
    sample_data_offsets = []
    current_offset = sample_data_start
    for sample_bytes in module.sample_data:
        sample_data_offsets.append(current_offset)
        current_offset += len(sample_bytes)

    # ========== Write Header ==========

    data.extend(IT_MAGIC)
    _write_string(data, module.name, 26)
    data.extend(bytes([0x04, 0x10]))  # PHilight
    data.extend(struct.pack('<H', len(module.order_table)))
    data.extend(struct.pack('<H', num_instruments))
    data.extend(struct.pack('<H', num_samples))
    data.extend(struct.pack('<H', num_patterns))
    data.extend(struct.pack('<H', 0x0214))  # Cwt
    data.extend(struct.pack('<H', 0x0200))  # Cmwt
    data.extend(struct.pack('<H', module.flags))
    data.extend(struct.pack('<H', special))
    data.append(module.global_volume)
    data.append(module.mix_volume)
    data.append(module.default_speed)
    data.append(module.default_bpm)
    data.append(module.panning_separation)
    data.append(module.pitch_wheel_depth)
    data.extend(struct.pack('<H', len(module.message) if module.message else 0))
    data.extend(struct.pack('<I', message_offset))
    data.extend(bytes(4))  # Reserved

    # Channel pan/vol
    channel_pan = [32] * module.num_channels + [128] * (64 - module.num_channels)
    channel_vol = [64] * module.num_channels + [0] * (64 - module.num_channels)
    data.extend(bytes(channel_pan))
    data.extend(bytes(channel_vol))

    # ========== Write Order Table ==========
    data.extend(bytes(module.order_table))

    # ========== Write Offset Tables ==========
    for offset in instrument_offsets:
        data.extend(struct.pack('<I', offset))
    for offset in sample_offsets:
        data.extend(struct.pack('<I', offset))
    for offset in pattern_offsets:
        data.extend(struct.pack('<I', offset))

    # ========== Write Message ==========
    if module.message:
        data.extend(module.message.encode('latin-1'))
        data.append(0)

    # ========== Write Instruments ==========
    for instr in module.instruments:
        idata = bytearray()
        idata.extend(INSTRUMENT_MAGIC)
        _write_string(idata, instr.filename, 12)
        idata.append(0)  # Reserved
        idata.append(instr.nna)
        idata.append(instr.dct)
        idata.append(instr.dca)
        idata.extend(struct.pack('<H', instr.fadeout))
        idata.append(instr.pitch_pan_separation & 0xFF)
        idata.append(instr.pitch_pan_center)
        idata.append(instr.global_volume)
        dfp = (instr.default_pan | 0x80) if instr.default_pan is not None else 32
        idata.append(dfp)
        idata.append(instr.random_volume)
        idata.append(instr.random_pan)
        idata.extend(bytes(4))  # TrkVers/NoS
        _write_string(idata, instr.name, 26)
        ifc = (instr.filter_cutoff | 0x80) if instr.filter_cutoff is not None else 0
        ifr = (instr.filter_resonance | 0x80) if instr.filter_resonance is not None else 0
        idata.append(ifc)
        idata.append(ifr)
        idata.append(instr.midi_channel)
        idata.append(instr.midi_program)
        idata.extend(struct.pack('<H', instr.midi_bank))

        # Note-sample table
        for note, sample in instr.note_sample_table:
            idata.append(note)
            idata.append(sample)

        # Envelopes
        idata.extend(_write_envelope(instr.volume_envelope))
        idata.extend(_write_envelope(instr.panning_envelope))
        idata.extend(_write_envelope(instr.pitch_envelope))

        data.extend(idata)

    # ========== Write Sample Headers ==========
    for i, sample in enumerate(module.samples):
        sdata = bytearray()
        sdata.extend(SAMPLE_MAGIC)
        _write_string(sdata, sample.filename, 12)
        sdata.append(0)  # Reserved
        sdata.append(sample.global_volume)

        flags = sample.flags | SAMPLE_16BIT | SAMPLE_HAS_DATA
        sdata.append(flags)
        sdata.append(sample.default_volume)
        _write_string(sdata, sample.name, 26)
        sdata.append(0x01)  # Cvt - signed samples
        dfp = (sample.default_pan | 0x80) if sample.default_pan is not None else 0
        sdata.append(dfp)
        sdata.extend(struct.pack('<I', len(module.sample_data[i]) // 2))
        sdata.extend(struct.pack('<I', sample.loop_begin))
        sdata.extend(struct.pack('<I', sample.loop_end))
        sdata.extend(struct.pack('<I', sample.c5_speed))
        sdata.extend(struct.pack('<I', sample.sustain_loop_begin))
        sdata.extend(struct.pack('<I', sample.sustain_loop_end))
        sdata.extend(struct.pack('<I', sample_data_offsets[i]))
        sdata.append(sample.vibrato_speed)
        sdata.append(sample.vibrato_depth)
        sdata.append(sample.vibrato_rate)
        sdata.append(sample.vibrato_type)
        data.extend(sdata)

    # ========== Write Patterns ==========
    for i, packed in enumerate(packed_patterns):
        data.extend(struct.pack('<H', len(packed)))
        data.extend(struct.pack('<H', module.patterns[i].num_rows))
        data.extend(bytes(4))  # Reserved
        data.extend(packed)

    # ========== Write Sample Data ==========
    for sample_bytes in module.sample_data:
        data.extend(sample_bytes)

    with open(filename, 'wb') as f:
        f.write(data)


def validate_it(filename: str) -> bool:
    """
    Validate IT file has correct magic.

    Returns True if valid, raises ValueError if not.
    """
    with open(filename, 'rb') as f:
        magic = f.read(4)
        if magic != IT_MAGIC:
            raise ValueError(f"Invalid IT magic: {magic}")
    return True
