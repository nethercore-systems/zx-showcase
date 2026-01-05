"""Wave complete - victory fanfare.

Ascending C major arpeggio with reverb.
"""

SOUND = {
    'sound': {
        'name': 'wave_complete',
        'duration': 0.5,
        'sample_rate': 22050,
        'layers': [
            # C5
            {
                'type': 'sine',
                'freq': 523,
                'amplitude': 0.3,
                'duration': 0.25,
                'delay': 0.0,
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.05,
                    'sustain': 0.5,
                    'release': 0.15,
                },
            },
            # E5
            {
                'type': 'sine',
                'freq': 659,
                'amplitude': 0.3,
                'duration': 0.25,
                'delay': 0.08,
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.05,
                    'sustain': 0.5,
                    'release': 0.15,
                },
            },
            # G5
            {
                'type': 'sine',
                'freq': 784,
                'amplitude': 0.3,
                'duration': 0.25,
                'delay': 0.16,
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.05,
                    'sustain': 0.5,
                    'release': 0.15,
                },
            },
            # A5
            {
                'type': 'sine',
                'freq': 880,
                'amplitude': 0.3,
                'duration': 0.25,
                'delay': 0.24,
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.05,
                    'sustain': 0.5,
                    'release': 0.15,
                },
            },
            # C6
            {
                'type': 'sine',
                'freq': 1047,
                'amplitude': 0.3,
                'duration': 0.25,
                'delay': 0.32,
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.05,
                    'sustain': 0.5,
                    'release': 0.15,
                },
            },
            # Saw brightness overlay
            {
                'type': 'saw',
                'freq': 523,
                'amplitude': 0.1,
                'duration': 0.25,
            },
        ],
        'effects': [
            {'type': 'reverb', 'decay': 0.2, 'delay_ms': 35, 'mix': 0.3},
        ],
        'normalize': True,
    }
}
