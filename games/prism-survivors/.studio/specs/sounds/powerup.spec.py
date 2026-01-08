"""Powerup pickup - magical ascending.

Rising frequency sweep with harmonic.
"""

SOUND = {
    'sound': {
        'name': 'powerup',
        'duration': 0.4,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 400,
                'freq_end': 1200,
                'amplitude': 0.4,
                'duration': 0.4,
            },
            {
                'type': 'sine',
                'freq': 600,
                'freq_end': 1800,
                'amplitude': 0.15,
                'duration': 0.4,
            },
        ],
        'envelope': {
            'attack': 0.02,
            'decay': 0.1,
            'sustain': 0.5,
            'release': 0.2,
        },
        'effects': [
            {'type': 'reverb', 'decay': 0.15, 'delay_ms': 25, 'mix': 0.25},
        ],
        'normalize': True,
    }
}
