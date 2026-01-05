"""XP pickup - sparkle.

High frequency sine harmonics.
"""

SOUND = {
    'sound': {
        'name': 'xp',
        'duration': 0.12,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 1500,
                'amplitude': 0.4,
                'duration': 0.12,
            },
            {
                'type': 'sine',
                'freq': 2250,
                'amplitude': 0.2,
                'duration': 0.12,
            },
        ],
        'envelope': {
            'attack': 0.005,
            'decay': 0.02,
            'sustain': 0.3,
            'release': 0.08,
        },
        'normalize': True,
    }
}
