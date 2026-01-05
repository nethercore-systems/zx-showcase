"""Door locked sound effect.

Denied - harsh buzz sound.
"""

SOUND = {
    'sound': {
        'name': 'door_locked',
        'duration': 0.2,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 100,
                'amplitude': 0.5,
                'duration': 0.2,
            },
            {
                'type': 'sine',
                'freq': 150,
                'amplitude': 0.5,
                'duration': 0.2,
            },
        ],
        'envelope': {
            'attack': 0.01,
            'decay': 0.05,
            'sustain': 0.8,
            'release': 0.05,
        },
        'normalize': True,
    }
}
