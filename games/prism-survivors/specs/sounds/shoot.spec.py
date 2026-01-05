"""Projectile fire - crystalline zap.

High frequency burst with quick decay.
"""

SOUND = {
    'sound': {
        'name': 'shoot',
        'duration': 0.15,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'square',
                'freq': 1200,
                'amplitude': 0.4,
                'duration': 0.15,
            },
            {
                'type': 'sine',
                'freq': 2400,
                'amplitude': 0.2,
                'duration': 0.15,
            },
        ],
        'envelope': {
            'attack': 0.005,
            'decay': 0.03,
            'sustain': 0.2,
            'release': 0.1,
        },
        'master_filter': {
            'type': 'highpass',
            'cutoff': 800,
        },
        'normalize': True,
    }
}
