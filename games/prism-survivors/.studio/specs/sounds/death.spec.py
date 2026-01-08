"""Enemy death - shattering crystal.

Noise burst shatter with descending tone.
"""

SOUND = {
    'sound': {
        'name': 'death',
        'duration': 0.35,
        'sample_rate': 22050,
        'layers': [
            # Noise shatter
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.5,
                'duration': 0.35,
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.1,
                    'sustain': 0.2,
                    'release': 0.15,
                },
            },
            # Descending tone
            {
                'type': 'sine',
                'freq': 800,
                'freq_end': 400,
                'amplitude': 0.3,
                'duration': 0.35,
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.05,
                    'sustain': 0.3,
                    'release': 0.2,
                },
            },
        ],
        'master_filter': {
            'type': 'lowpass',
            'cutoff': 3000,
        },
        'normalize': True,
    }
}
