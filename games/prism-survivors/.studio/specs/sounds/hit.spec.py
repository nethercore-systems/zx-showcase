"""Enemy hit - punchy impact.

Low thud with high crack overlay.
"""

SOUND = {
    'sound': {
        'name': 'hit',
        'duration': 0.1,
        'sample_rate': 22050,
        'layers': [
            # Low thud
            {
                'type': 'sine',
                'freq': 150,
                'amplitude': 0.5,
                'duration': 0.1,
                'envelope': {
                    'attack': 0.002,
                    'decay': 0.02,
                    'sustain': 0.1,
                    'release': 0.05,
                },
            },
            # High crack
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.4,
                'duration': 0.03,
                'envelope': {
                    'attack': 0.001,
                    'decay': 0.01,
                    'sustain': 0.1,
                    'release': 0.02,
                },
            },
        ],
        'normalize': True,
    }
}
