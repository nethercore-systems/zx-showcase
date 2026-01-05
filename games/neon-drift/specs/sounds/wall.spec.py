"""Wall collision - heavy impact.

Low impact thud with crunch noise.
"""

SOUND = {
    'sound': {
        'name': 'wall',
        'duration': 0.3,
        'sample_rate': 22050,
        'layers': [
            # Low thud
            {
                'type': 'sine',
                'freq': 80,
                'amplitude': 0.6,
                'duration': 0.3,
                'envelope': {
                    'attack': 0.005,
                    'decay': 0.05,
                    'sustain': 0.2,
                    'release': 0.2,
                },
            },
            # Thud harmonic
            {
                'type': 'sine',
                'freq': 160,
                'amplitude': 0.3,
                'duration': 0.3,
                'envelope': {
                    'attack': 0.005,
                    'decay': 0.05,
                    'sustain': 0.2,
                    'release': 0.2,
                },
            },
            # Crunch noise
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.5,
                'duration': 0.15,
                'envelope': {
                    'attack': 0.002,
                    'decay': 0.03,
                    'sustain': 0.3,
                    'release': 0.1,
                },
            },
        ],
        'master_filter': {
            'type': 'lowpass',
            'cutoff': 600,
        },
        'normalize': True,
    }
}
