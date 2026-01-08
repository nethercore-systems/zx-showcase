"""Low rumbling engine idle sound.

Base frequency with harmonics and subtle noise texture.
"""

SOUND = {
    'sound': {
        'name': 'engine_idle',
        'duration': 0.5,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 60,
                'amplitude': 0.4,
                'duration': 0.5,
            },
            {
                'type': 'sine',
                'freq': 120,
                'amplitude': 0.2,
                'duration': 0.5,
            },
            {
                'type': 'sine',
                'freq': 180,
                'amplitude': 0.1,
                'duration': 0.5,
            },
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.05,
                'duration': 0.5,
            },
        ],
        'master_filter': {
            'type': 'lowpass',
            'cutoff': 400,
        },
        'normalize': True,
    }
}
