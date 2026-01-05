"""Gear shift click.

Sharp click with mechanical thunk.
"""

SOUND = {
    'sound': {
        'name': 'shift',
        'duration': 0.1,
        'sample_rate': 22050,
        'layers': [
            # Sharp click
            {
                'type': 'sine',
                'freq': 1200,
                'amplitude': 0.8,
                'duration': 0.02,
                'envelope': {
                    'attack': 0.001,
                    'decay': 0.01,
                    'sustain': 0.2,
                    'release': 0.02,
                },
            },
            {
                'type': 'sine',
                'freq': 2400,
                'amplitude': 0.4,
                'duration': 0.02,
                'envelope': {
                    'attack': 0.001,
                    'decay': 0.01,
                    'sustain': 0.2,
                    'release': 0.02,
                },
            },
            # Mechanical thunk
            {
                'type': 'sine',
                'freq': 200,
                'amplitude': 0.5,
                'duration': 0.08,
                'envelope': {
                    'attack': 0.005,
                    'decay': 0.03,
                    'sustain': 0.3,
                    'release': 0.04,
                },
            },
            # Thunk noise
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.2,
                'duration': 0.08,
                'envelope': {
                    'attack': 0.002,
                    'decay': 0.02,
                    'sustain': 0.2,
                    'release': 0.04,
                },
            },
        ],
        'normalize': True,
    }
}
