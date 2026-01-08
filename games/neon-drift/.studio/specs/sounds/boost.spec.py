"""Boost activation - whoosh with synth accent.

Noise whoosh plus rising pitch synth.
"""

SOUND = {
    'sound': {
        'name': 'boost',
        'duration': 0.4,
        'sample_rate': 22050,
        'layers': [
            # Whoosh noise
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.5,
                'duration': 0.4,
                'envelope': {
                    'attack': 0.02,
                    'decay': 0.1,
                    'sustain': 0.3,
                    'release': 0.2,
                },
            },
            # Rising synth accent
            {
                'type': 'sine',
                'freq': 400,
                'freq_end': 1200,
                'amplitude': 0.3,
                'duration': 0.4,
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.15,
                    'sustain': 0.3,
                    'release': 0.15,
                },
            },
        ],
        'normalize': True,
    }
}
