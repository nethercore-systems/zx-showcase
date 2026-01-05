"""Punchy kick drum.

Pitch drop from 150Hz to 40Hz with sharp attack.
"""

SOUND = {
    'sound': {
        'name': 'synth_kick',
        'duration': 0.3,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'pitched_body',
                'start_freq': 150,
                'end_freq': 40,
                'amplitude': 0.8,
                'duration': 0.3,
            },
        ],
        'envelope': {
            'attack': 0.001,
            'decay': 0.25,
            'sustain': 0.0,
            'release': 0.05,
        },
        'normalize': True,
    }
}
