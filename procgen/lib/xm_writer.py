#!/usr/bin/env python3
"""
XM Writer - Implementation for writing XM files.

DO NOT READ THIS FILE for API understanding - read xm_types.py instead.
This file contains only binary packing implementation details.

Usage:
    from xm_types import XmModule, XmPattern, XmNote, XmInstrument
    from xm_writer import write_xm, validate_xm

    module = XmModule(...)
    write_xm(module, "output.xm")
"""

from xm_types import (
    XmModule, XmPattern, XmNote, XmInstrument, XmEnvelope,
    MAX_CHANNELS, MAX_PATTERNS, MAX_INSTRUMENTS,
)
import struct

# Internal constants
XM_MAGIC = b"Extended Module: "
XM_VERSION = 0x0104


# ============================================================================
# Pattern Packing (internal)
# ============================================================================

def _pack_pattern_data(pattern: XmPattern, num_channels: int) -> bytes:
    """Pack pattern data using XM compressed format."""
    output = bytearray()

    for row in pattern.notes:
        for ch_idx, note in enumerate(row):
            if ch_idx >= num_channels:
                break

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


def _delta_encode_16bit(sample_data: bytes) -> bytes:
    """Delta-encode 16-bit signed PCM samples for XM format."""
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

    output.append(0)  # type
    output.extend(struct.pack("<H", num_samples))
    output.extend(struct.pack("<I", 40))  # sample header size

    output.extend(bytes(96))  # note-sample mapping

    # Volume envelope
    vol_env = instrument.volume_envelope
    for i in range(12):
        if vol_env and i < len(vol_env.points):
            output.extend(struct.pack("<HH", vol_env.points[i][0], vol_env.points[i][1]))
        else:
            output.extend(struct.pack("<HH", 0, 0))

    # Panning envelope
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
    output.extend(bytes(22))  # reserved

    # Sample header
    finetune, relative_note = instrument.get_pitch_correction()
    sample_len = len(instrument.sample_data) if instrument.sample_data else 0

    output.extend(struct.pack("<I", sample_len))
    output.extend(struct.pack("<I", instrument.sample_loop_start))
    output.extend(struct.pack("<I", instrument.sample_loop_length))
    output.append(64)  # volume
    output.append(finetune & 0xFF)

    type_byte = instrument.sample_loop_type & 0x03
    if instrument.sample_bits == 16:
        type_byte |= 0x10
    output.append(type_byte)

    output.append(128)  # panning
    output.append(relative_note & 0xFF)
    output.append(0)  # reserved
    output.extend(name_bytes.ljust(22, b"\x00"))

    # Sample data
    if instrument.sample_data:
        if instrument.sample_bits == 16:
            output.extend(_delta_encode_16bit(instrument.sample_data))
        else:
            output.extend(instrument.sample_data)


# ============================================================================
# Public API
# ============================================================================

def write_xm(module: XmModule, output_path: str) -> None:
    """
    Write XM module to file.

    Args:
        module: XmModule containing song data
        output_path: Path to write the .xm file
    """
    output = bytearray()

    num_patterns = len(module.patterns)
    num_instruments = len(module.instruments)
    song_length = len(module.order_table) if module.order_table else 1

    # Validation
    if num_patterns > MAX_PATTERNS:
        raise ValueError(f"Too many patterns: {num_patterns} > {MAX_PATTERNS}")
    if num_instruments > MAX_INSTRUMENTS:
        raise ValueError(f"Too many instruments: {num_instruments} > {MAX_INSTRUMENTS}")
    if module.num_channels > MAX_CHANNELS:
        raise ValueError(f"Too many channels: {module.num_channels} > {MAX_CHANNELS}")

    # XM Header
    output.extend(XM_MAGIC)

    name_bytes = module.name.encode("ascii", errors="replace")[:20]
    output.extend(name_bytes.ljust(20, b"\x00"))

    output.append(0x1A)
    output.extend(b"Nethercore XM Writer".ljust(20, b"\x00"))

    output.extend(struct.pack("<H", XM_VERSION))
    output.extend(struct.pack("<I", 276))
    output.extend(struct.pack("<H", song_length))
    output.extend(struct.pack("<H", module.restart_position))
    output.extend(struct.pack("<H", module.num_channels))
    output.extend(struct.pack("<H", num_patterns))
    output.extend(struct.pack("<H", num_instruments))
    output.extend(struct.pack("<H", 1 if module.linear_frequency_table else 0))
    output.extend(struct.pack("<H", module.default_speed))
    output.extend(struct.pack("<H", module.default_bpm))

    for i in range(256):
        output.append(module.order_table[i] if i < len(module.order_table) else 0)

    # Patterns
    for pattern in module.patterns:
        packed_data = _pack_pattern_data(pattern, module.num_channels)
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


def validate_xm(path: str) -> bool:
    """
    Validate that an XM file has correct magic and version.

    Returns True if valid, raises ValueError if not.
    """
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
