"""Longer open hi-hat.

Extended noise with slower decay.
"""

SOUND = {
    'sound': {
        'name': 'synth_openhat',
        'duration': 0.4,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.4,
                'duration': 0.4,
            },
        ],
        'envelope': {
            'attack': 0.001,
            'decay': 0.05,
            'sustain': 0.4,
            'release': 0.3,
        },
        'normalize': True,
    }
}
