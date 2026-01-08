"""Coin pickup - metallic ting.

High frequency harmonic stack.
"""

SOUND = {
    'sound': {
        'name': 'coin',
        'duration': 0.1,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 2000,
                'amplitude': 0.4,
                'duration': 0.1,
            },
            {
                'type': 'sine',
                'freq': 3000,
                'amplitude': 0.2,
                'duration': 0.1,
            },
            {
                'type': 'sine',
                'freq': 4000,
                'amplitude': 0.1,
                'duration': 0.1,
            },
        ],
        'envelope': {
            'attack': 0.002,
            'decay': 0.02,
            'sustain': 0.2,
            'release': 0.06,
        },
        'normalize': True,
    }
}
