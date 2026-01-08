"""Combo 50 milestone - quad chime.

Maximum escalating combo sound.
"""

SOUND = {
    'sound': {
        'name': 'combo_50',
        'duration': 0.4,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 1100,
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
                'freq': 1375,
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
                'freq': 1650,
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
        'effects': [
            {'type': 'reverb', 'decay': 0.15, 'delay_ms': 20, 'mix': 0.2},
        ],
        'normalize': True,
    }
}
