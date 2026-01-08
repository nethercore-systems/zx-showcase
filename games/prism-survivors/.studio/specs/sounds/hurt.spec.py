"""Player hurt - low impact.

Low sine with noise impact, heavily filtered.
"""

SOUND = {
    'sound': {
        'name': 'hurt',
        'duration': 0.15,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 100,
                'amplitude': 0.5,
                'duration': 0.15,
                'envelope': {
                    'attack': 0.005,
                    'decay': 0.03,
                    'sustain': 0.2,
                    'release': 0.1,
                },
            },
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.3,
                'duration': 0.05,
            },
        ],
        'master_filter': {
            'type': 'lowpass',
            'cutoff': 400,
        },
        'normalize': True,
    }
}
