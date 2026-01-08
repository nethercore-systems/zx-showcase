"""Short closed hi-hat.

Quick noise burst.
"""

SOUND = {
    'sound': {
        'name': 'synth_hihat',
        'duration': 0.08,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.6,
                'duration': 0.08,
            },
        ],
        'envelope': {
            'attack': 0.001,
            'decay': 0.02,
            'sustain': 0.3,
            'release': 0.05,
        },
        'normalize': True,
    }
}
