"""Barrier scrape - lighter impact.

Scrape noise with metallic ring.
"""

SOUND = {
    'sound': {
        'name': 'barrier',
        'duration': 0.25,
        'sample_rate': 22050,
        'layers': [
            # Scrape noise
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.4,
                'duration': 0.25,
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.05,
                    'sustain': 0.5,
                    'release': 0.15,
                },
            },
            # Metallic ring
            {
                'type': 'sine',
                'freq': 600,
                'amplitude': 0.3,
                'duration': 0.25,
                'envelope': {
                    'attack': 0.005,
                    'decay': 0.08,
                    'sustain': 0.2,
                    'release': 0.1,
                },
            },
            {
                'type': 'sine',
                'freq': 900,
                'amplitude': 0.15,
                'duration': 0.25,
                'envelope': {
                    'attack': 0.005,
                    'decay': 0.08,
                    'sustain': 0.2,
                    'release': 0.1,
                },
            },
        ],
        'normalize': True,
    }
}
