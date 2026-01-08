"""Menu back - descending.

Descending frequency sweep.
"""

SOUND = {
    'sound': {
        'name': 'back',
        'duration': 0.12,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 1000,
                'freq_end': 600,
                'amplitude': 0.3,
                'duration': 0.12,
            },
        ],
        'envelope': {
            'attack': 0.005,
            'decay': 0.02,
            'sustain': 0.2,
            'release': 0.06,
        },
        'normalize': True,
    }
}
