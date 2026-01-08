"""Dash ability - whoosh.

White noise with rising pitch accent.
"""

SOUND = {
    'sound': {
        'name': 'dash',
        'duration': 0.25,
        'sample_rate': 22050,
        'layers': [
            # Whoosh noise
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.4,
                'duration': 0.25,
                'envelope': {
                    'attack': 0.02,
                    'decay': 0.08,
                    'sustain': 0.3,
                    'release': 0.12,
                },
            },
            # Rising pitch accent
            {
                'type': 'sine',
                'freq': 300,
                'freq_end': 900,
                'amplitude': 0.2,
                'duration': 0.25,
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.1,
                    'sustain': 0.3,
                    'release': 0.1,
                },
            },
        ],
        'normalize': True,
    }
}
