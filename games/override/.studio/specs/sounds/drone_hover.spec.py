"""Drone hover sound effect.

Constant mechanical hum.
"""

SOUND = {
    'sound': {
        'name': 'drone_hover',
        'duration': 0.5,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 120,
                'amplitude': 0.5,
                'duration': 0.5,
            },
            {
                'type': 'sine',
                'freq': 180,
                'amplitude': 0.5,
                'duration': 0.5,
            },
        ],
        'envelope': {
            'attack': 0.05,
            'decay': 0.05,
            'sustain': 0.9,
            'release': 0.05,
        },
        'normalize': True,
    }
}
