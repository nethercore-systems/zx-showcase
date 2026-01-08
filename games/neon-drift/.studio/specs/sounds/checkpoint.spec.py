"""Checkpoint passed - positive chime.

Rising C major arpeggio.
"""

SOUND = {
    'sound': {
        'name': 'checkpoint',
        'duration': 0.3,
        'sample_rate': 22050,
        'layers': [
            # C5
            {
                'type': 'sine',
                'freq': 523,
                'amplitude': 0.4,
                'duration': 0.15,
                'delay': 0.0,
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.02,
                    'sustain': 0.5,
                    'release': 0.1,
                },
            },
            # E5
            {
                'type': 'sine',
                'freq': 659,
                'amplitude': 0.4,
                'duration': 0.15,
                'delay': 0.08,
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.02,
                    'sustain': 0.5,
                    'release': 0.1,
                },
            },
            # G5
            {
                'type': 'sine',
                'freq': 784,
                'amplitude': 0.4,
                'duration': 0.15,
                'delay': 0.16,
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.02,
                    'sustain': 0.5,
                    'release': 0.1,
                },
            },
        ],
        'normalize': True,
    }
}
