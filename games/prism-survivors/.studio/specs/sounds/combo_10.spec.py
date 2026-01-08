"""Combo 10 milestone - double chime.

Escalating combo sound.
"""

SOUND = {
    'sound': {
        'name': 'combo_10',
        'duration': 0.2,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 700,
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
                'freq': 875,
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
        ],
        'normalize': True,
    }
}
