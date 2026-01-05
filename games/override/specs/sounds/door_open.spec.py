"""Door open sound effect.

Mechanical sliding door opening. Sweep from low to mid frequency.
"""

SOUND = {
    'sound': {
        'name': 'door_open',
        'duration': 0.4,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 200,
                'freq_end': 400,
                'amplitude': 1.0,
                'duration': 0.4,
            },
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.2,
                'duration': 0.4,
            },
        ],
        'envelope': {
            'attack': 0.01,
            'decay': 0.1,
            'sustain': 0.8,
            'release': 0.1,
        },
        'normalize': True,
    }
}
