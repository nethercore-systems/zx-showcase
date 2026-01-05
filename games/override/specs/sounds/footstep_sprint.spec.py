"""Sprint footstep sound effect.

Faster, sharper footstep for sprinting.
"""

SOUND = {
    'sound': {
        'name': 'footstep_sprint',
        'duration': 0.04,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 100,
                'amplitude': 1.0,
                'duration': 0.08,
            },
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.4,
                'duration': 0.04,
            },
        ],
        'envelope': {
            'attack': 0.001,
            'decay': 0.05,
            'sustain': 0.0,
            'release': 0.0,
        },
        'normalize': True,
    }
}
