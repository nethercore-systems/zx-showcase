"""Engine revving up sound.

Frequency sweep with harmonics and noise texture.
"""

SOUND = {
    'sound': {
        'name': 'engine_rev',
        'duration': 0.6,
        'sample_rate': 22050,
        'layers': [
            # Main sweep
            {
                'type': 'sine',
                'freq': 80,
                'freq_end': 280,
                'amplitude': 0.4,
                'duration': 0.6,
            },
            # Second harmonic
            {
                'type': 'sine',
                'freq': 160,
                'freq_end': 560,
                'amplitude': 0.2,
                'duration': 0.6,
            },
            # Third harmonic
            {
                'type': 'sine',
                'freq': 240,
                'freq_end': 840,
                'amplitude': 0.1,
                'duration': 0.6,
            },
            # Texture
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.08,
                'duration': 0.6,
            },
        ],
        'envelope': {
            'attack': 0.05,
            'decay': 0.1,
            'sustain': 0.8,
            'release': 0.2,
        },
        'master_filter': {
            'type': 'lowpass',
            'cutoff': 800,
        },
        'normalize': True,
    }
}
