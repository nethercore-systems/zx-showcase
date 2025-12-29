#!/usr/bin/env python3
"""Generate XM tracker music files for Neon Drift.

Creates synthwave-styled tracker music for each track:
- Sunset Strip (128 BPM, Am) - Nostalgic, warm
- Neon City (132 BPM, Em) - Urban, energetic
- Void Tunnel (138 BPM, Dm) - Mysterious, intense
- Crystal Cavern (130 BPM, Bm) - Ethereal, tense
- Solar Highway (140 BPM, Fm) - Epic, triumphant

XM format is complex, so we generate a simplified structure.
Real XM files would need a proper tracker library or binary writer.
For now, we create placeholder files that indicate the intended music.
"""

import struct
from pathlib import Path


def write_xm_placeholder(path: Path, title: str, bpm: int, key: str, mood: str):
    """Write a minimal XM file placeholder.

    Real XM files require:
    - Header with module info
    - Pattern data (note/instrument/volume/effect commands)
    - Instrument definitions with sample references
    - Sample data

    For the showcase, we create a valid minimal structure.
    """
    # XM file structure (Extended Module)
    # Header: 60 bytes fixed + song name
    # Pattern order table
    # Patterns (variable)
    # Instruments (variable)
    # Samples (embedded in instruments)

    # For now, create a simple binary file with XM header
    # This won't play but is recognized as XM format

    with open(path, 'wb') as f:
        # XM ID text (17 bytes)
        f.write(b'Extended Module: ')

        # Module name (20 bytes, padded)
        name_bytes = title[:20].encode('ascii')
        f.write(name_bytes.ljust(20, b'\x00'))

        # 0x1a (1 byte)
        f.write(b'\x1a')

        # Tracker name (20 bytes)
        tracker = "Neon Drift Procgen"
        f.write(tracker[:20].encode('ascii').ljust(20, b'\x00'))

        # Version (2 bytes) - 0x0104 = version 1.04
        f.write(struct.pack('<H', 0x0104))

        # Header size (4 bytes) - size of header after this point
        header_size = 20 + 256 + 10  # minimal
        f.write(struct.pack('<I', header_size))

        # Song length (2 bytes) - number of patterns in order
        f.write(struct.pack('<H', 4))

        # Restart position (2 bytes)
        f.write(struct.pack('<H', 0))

        # Number of channels (2 bytes)
        f.write(struct.pack('<H', 8))

        # Number of patterns (2 bytes)
        f.write(struct.pack('<H', 4))

        # Number of instruments (2 bytes)
        f.write(struct.pack('<H', 8))

        # Flags (2 bytes)
        f.write(struct.pack('<H', 0x0001))  # Linear frequency table

        # Default tempo (2 bytes) - ticks per row
        f.write(struct.pack('<H', 6))

        # Default BPM (2 bytes)
        f.write(struct.pack('<H', bpm))

        # Pattern order table (256 bytes)
        order = bytes([0, 1, 2, 3] + [0] * 252)
        f.write(order)

        # Write minimal pattern data (4 empty patterns)
        for _ in range(4):
            # Pattern header
            f.write(struct.pack('<I', 9))     # Pattern header length
            f.write(b'\x00')                   # Packing type
            f.write(struct.pack('<H', 64))    # Number of rows
            f.write(struct.pack('<H', 0))     # Packed pattern data size (empty)

        # Note: Real XM would have instrument and sample data here
        # This placeholder is enough to be recognized as XM

    print(f"  Generated: {path.name} ({bpm} BPM, {key}, {mood})")


def create_music_spec(path: Path, title: str, bpm: int, key: str, mood: str, structure: dict):
    """Create a human-readable music specification file."""
    with open(path.with_suffix('.spec.txt'), 'w') as f:
        f.write(f"# {title} - Music Specification\n")
        f.write(f"# Neon Drift Soundtrack\n\n")
        f.write(f"BPM: {bpm}\n")
        f.write(f"Key: {key}\n")
        f.write(f"Mood: {mood}\n\n")

        f.write("## Instruments\n")
        f.write("1. synth_kick.wav - 808-style kick\n")
        f.write("2. synth_snare.wav - Gated reverb snare\n")
        f.write("3. synth_hihat.wav - Closed hi-hat\n")
        f.write("4. synth_openhat.wav - Open hi-hat\n")
        f.write("5. synth_bass.wav - Detuned saw bass\n")
        f.write("6. synth_lead.wav - Bright lead\n")
        f.write("7. synth_pad.wav - Warm pad\n")
        f.write("8. synth_arp.wav - Pluck arp\n\n")

        f.write("## Chord Progression\n")
        for section, chords in structure['chords'].items():
            f.write(f"{section}: {' - '.join(chords)}\n")

        f.write("\n## Pattern Structure\n")
        for i, pattern in enumerate(structure['patterns']):
            f.write(f"Pattern {i}: {pattern}\n")

        f.write("\n## Notes\n")
        f.write(f"{structure.get('notes', 'Standard synthwave arrangement')}\n")


def main():
    base_dir = Path(__file__).parent.parent
    music_dir = base_dir / "assets" / "audio" / "music"
    music_dir.mkdir(parents=True, exist_ok=True)

    print("Generating XM tracker music files...")

    # Sunset Strip - Nostalgic, warm (128 BPM, Am)
    write_xm_placeholder(
        music_dir / "sunset_strip.xm",
        "Sunset Strip",
        128, "Am", "Nostalgic, warm"
    )
    create_music_spec(
        music_dir / "sunset_strip.xm",
        "Sunset Strip",
        128, "Am", "Nostalgic, warm",
        {
            'chords': {
                'Intro': ['Am', 'F', 'C', 'G'],
                'Verse': ['Am', 'F', 'C', 'G'],
                'Chorus': ['F', 'G', 'Am', 'Em'],
            },
            'patterns': [
                'Intro - Pad only, building arp',
                'Verse - Add drums, bass groove',
                'Chorus - Full arrangement, lead melody',
                'Outro - Fade with arp and pad',
            ],
            'notes': 'Warm, sunset vibes. Mellow lead, arpeggiated chords.'
        }
    )

    # Neon City - Urban, energetic (132 BPM, Em)
    write_xm_placeholder(
        music_dir / "neon_city.xm",
        "Neon City",
        132, "Em", "Urban, energetic"
    )
    create_music_spec(
        music_dir / "neon_city.xm",
        "Neon City",
        132, "Em", "Urban, energetic",
        {
            'chords': {
                'Intro': ['Em', 'Am', 'D', 'G'],
                'Verse': ['Em', 'C', 'Am', 'D'],
                'Chorus': ['Em', 'G', 'C', 'D'],
            },
            'patterns': [
                'Intro - Punchy drums, filtered arp',
                'Verse - Driving bass, minimal lead',
                'Chorus - Full energy, layered synths',
                'Bridge - Breakdown, building back',
            ],
            'notes': 'Urban energy. Punchy drums, sidechained bass.'
        }
    )

    # Void Tunnel - Mysterious, intense (138 BPM, Dm)
    write_xm_placeholder(
        music_dir / "void_tunnel.xm",
        "Void Tunnel",
        138, "Dm", "Mysterious, intense"
    )
    create_music_spec(
        music_dir / "void_tunnel.xm",
        "Void Tunnel",
        138, "Dm", "Mysterious, intense",
        {
            'chords': {
                'Intro': ['Dm', 'Bb', 'Gm', 'A'],
                'Verse': ['Dm', 'F', 'C', 'Dm'],
                'Chorus': ['Bb', 'C', 'Dm', 'A'],
            },
            'patterns': [
                'Intro - Dark pads, sparse hits',
                'Verse - Stuttered synths, tension building',
                'Chorus - Intense drums, dark lead',
                'Break - Minimal, eerie atmosphere',
            ],
            'notes': 'Dark and mysterious. Minor key, dissonant moments.'
        }
    )

    # Crystal Cavern - Ethereal, tense (130 BPM, Bm)
    write_xm_placeholder(
        music_dir / "crystal_cavern.xm",
        "Crystal Cavern",
        130, "Bm", "Ethereal, tense"
    )
    create_music_spec(
        music_dir / "crystal_cavern.xm",
        "Crystal Cavern",
        130, "Bm", "Ethereal, tense",
        {
            'chords': {
                'Intro': ['Bm', 'G', 'D', 'A'],
                'Verse': ['Bm', 'Em', 'G', 'D'],
                'Chorus': ['G', 'A', 'Bm', 'F#m'],
            },
            'patterns': [
                'Intro - Crystalline arps, deep sub',
                'Verse - Tight drums, tense progression',
                'Chorus - Ethereal lead, layered pads',
                'Outro - Fading crystals, reverb trails',
            ],
            'notes': 'Ethereal and tense. Crystalline arps, deep bass.'
        }
    )

    # Solar Highway - Epic, triumphant (140 BPM, Fm)
    write_xm_placeholder(
        music_dir / "solar_highway.xm",
        "Solar Highway",
        140, "Fm", "Epic, triumphant"
    )
    create_music_spec(
        music_dir / "solar_highway.xm",
        "Solar Highway",
        140, "Fm", "Epic, triumphant",
        {
            'chords': {
                'Intro': ['Fm', 'Db', 'Ab', 'Eb'],
                'Verse': ['Fm', 'Cm', 'Db', 'Ab'],
                'Chorus': ['Db', 'Eb', 'Fm', 'Cm'],
            },
            'patterns': [
                'Intro - Building energy, epic pads',
                'Verse - Driving rhythm, soaring lead',
                'Chorus - Maximum energy, triumphant melody',
                'Finale - Epic conclusion, layered everything',
            ],
            'notes': 'Epic and triumphant. Highest energy track. Soaring leads.'
        }
    )

    print("\nDone! Generated 5 XM music files + spec files.")


if __name__ == "__main__":
    main()
