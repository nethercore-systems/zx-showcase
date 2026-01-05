"""Footstep sound effect.

Low thud for normal footstep.
"""

SOUND = {
    'sound': {
        'name': 'footstep',
        'duration': 0.05,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 80,
                'amplitude': 1.0,
                'duration': 0.1,
            },
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.3,
                'duration': 0.05,
            },
        ],
        'envelope': {
            'attack': 0.001,
            'decay': 0.08,
            'sustain': 0.0,
            'release': 0.0,
        },
        'normalize': True,
    }
}
