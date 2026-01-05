"""Menu navigate - soft tick.

Simple sine tick.
"""

SOUND = {
    'sound': {
        'name': 'menu',
        'duration': 0.1,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 800,
                'amplitude': 0.3,
                'duration': 0.1,
            },
        ],
        'envelope': {
            'attack': 0.005,
            'decay': 0.02,
            'sustain': 0.2,
            'release': 0.05,
        },
        'normalize': True,
    }
}
