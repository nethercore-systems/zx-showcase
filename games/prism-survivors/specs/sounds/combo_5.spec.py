"""Combo 5 milestone - single chime.

Base combo sound.
"""

SOUND = {
    'sound': {
        'name': 'combo_5',
        'duration': 0.1,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 650,
                'amplitude': 0.35,
                'duration': 0.1,
            },
        ],
        'envelope': {
            'attack': 0.005,
            'decay': 0.02,
            'sustain': 0.4,
            'release': 0.08,
        },
        'normalize': True,
    }
}
