"""Snappy snare with body and noise.

Pitched body plus noise for snare wires.
"""

SOUND = {
    'sound': {
        'name': 'synth_snare',
        'duration': 0.25,
        'sample_rate': 22050,
        'layers': [
            # Body
            {
                'type': 'sine',
                'freq': 180,
                'amplitude': 0.4,
                'duration': 0.25,
                'envelope': {
                    'attack': 0.001,
                    'decay': 0.05,
                    'sustain': 0.0,
                    'release': 0.1,
                },
            },
            # Noise (snare wires)
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.5,
                'duration': 0.25,
                'envelope': {
                    'attack': 0.001,
                    'decay': 0.08,
                    'sustain': 0.0,
                    'release': 0.1,
                },
            },
        ],
        'normalize': True,
    }
}
