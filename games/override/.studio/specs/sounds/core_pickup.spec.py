"""Core pickup sound effect.

Positive chime for collecting data cores.
"""

SOUND = {
    'sound': {
        'name': 'core_pickup',
        'duration': 0.3,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 800,
                'amplitude': 0.33,
                'duration': 0.3,
            },
            {
                'type': 'sine',
                'freq': 1000,
                'amplitude': 0.33,
                'duration': 0.3,
            },
            {
                'type': 'sine',
                'freq': 1200,
                'amplitude': 0.33,
                'duration': 0.3,
            },
        ],
        'envelope': {
            'attack': 0.01,
            'decay': 0.2,
            'sustain': 0.0,
            'release': 0.0,
        },
        'normalize': True,
    }
}
