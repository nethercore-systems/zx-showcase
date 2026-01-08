"""Countdown beep.

Clean beep with harmonics.
"""

SOUND = {
    'sound': {
        'name': 'countdown',
        'duration': 0.15,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 880,
                'amplitude': 0.5,
                'duration': 0.15,
            },
            {
                'type': 'sine',
                'freq': 1760,
                'amplitude': 0.2,
                'duration': 0.15,
            },
        ],
        'envelope': {
            'attack': 0.005,
            'decay': 0.02,
            'sustain': 0.6,
            'release': 0.08,
        },
        'normalize': True,
    }
}
