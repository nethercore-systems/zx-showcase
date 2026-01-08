"""Menu select - confirm click.

Two-tone click.
"""

SOUND = {
    'sound': {
        'name': 'select',
        'duration': 0.08,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 1200,
                'amplitude': 0.35,
                'duration': 0.08,
            },
            {
                'type': 'sine',
                'freq': 1800,
                'amplitude': 0.15,
                'duration': 0.04,
            },
        ],
        'envelope': {
            'attack': 0.002,
            'decay': 0.01,
            'sustain': 0.2,
            'release': 0.04,
        },
        'normalize': True,
    }
}
