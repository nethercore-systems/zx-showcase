"""Zone 3 (Midnight Abyss) ambient audio.

Sub-bass pressure, isolation, minimal activity.
Duration: 120 seconds.
"""

SOUND = {
    'sound': {
        'name': 'ambient_midnight',
        'duration': 120.0,
        'sample_rate': 22050,
        'layers': [
            # Sub-bass pressure drone
            {
                'type': 'sine',
                'freq': 35,
                'amplitude': 0.4,
                'duration': 120.0,
            },
            # Near-silence base (very quiet)
            {
                'type': 'noise_burst',
                'color': 'brown',
                'amplitude': 0.05,
                'duration': 120.0,
                'filter': {
                    'type': 'lowpass',
                    'cutoff': 500,
                },
            },
            # Rare bioluminescent ping texture
            {
                'type': 'sine',
                'freq': 2000,
                'amplitude': 0.08,
                'duration': 120.0,
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.05,
                    'sustain': 0.1,
                    'release': 1.0,
                },
            },
        ],
        'master_filter': {
            'type': 'lowpass',
            'cutoff': 2000,
        },
        'effects': [
            {'type': 'reverb', 'decay': 0.6, 'delay_ms': 200, 'mix': 0.5},
        ],
        'normalize': True,
    }
}
