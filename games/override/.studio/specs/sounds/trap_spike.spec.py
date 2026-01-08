"""Trap spike sound effect.

Sharp metallic stab sound.
"""

SOUND = {
    'sound': {
        'name': 'trap_spike',
        'duration': 0.15,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 800,
                'amplitude': 1.0,
                'duration': 0.15,
            },
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.5,
                'duration': 0.15,
            },
        ],
        'envelope': {
            'attack': 0.001,
            'decay': 0.1,
            'sustain': 0.0,
            'release': 0.0,
        },
        'normalize': True,
    }
}
