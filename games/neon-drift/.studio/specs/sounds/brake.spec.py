"""Brake sound - lower screech.

Descending frequency with noise.
"""

SOUND = {
    'sound': {
        'name': 'brake',
        'duration': 0.3,
        'sample_rate': 22050,
        'layers': [
            # Descending screech
            {
                'type': 'sine',
                'freq': 800,
                'freq_end': 500,
                'amplitude': 0.4,
                'duration': 0.3,
            },
            # Noise texture
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.2,
                'duration': 0.3,
            },
        ],
        'envelope': {
            'attack': 0.01,
            'decay': 0.1,
            'sustain': 0.4,
            'release': 0.15,
        },
        'normalize': True,
    }
}
