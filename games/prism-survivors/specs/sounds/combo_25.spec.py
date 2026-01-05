"""Combo 25 milestone - triple chime.

Higher escalating combo sound.
"""

SOUND = {
    'sound': {
        'name': 'combo_25',
        'duration': 0.25,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 850,
                'amplitude': 0.35,
                'duration': 0.12,
                'delay': 0.0,
                'envelope': {
                    'attack': 0.005,
                    'decay': 0.02,
                    'sustain': 0.4,
                    'release': 0.08,
                },
            },
            {
                'type': 'sine',
                'freq': 1062,
                'amplitude': 0.35,
                'duration': 0.12,
                'delay': 0.05,
                'envelope': {
                    'attack': 0.005,
                    'decay': 0.02,
                    'sustain': 0.4,
                    'release': 0.08,
                },
            },
            {
                'type': 'sine',
                'freq': 1275,
                'amplitude': 0.35,
                'duration': 0.12,
                'delay': 0.1,
                'envelope': {
                    'attack': 0.005,
                    'decay': 0.02,
                    'sustain': 0.4,
                    'release': 0.08,
                },
            },
        ],
        'normalize': True,
    }
}
