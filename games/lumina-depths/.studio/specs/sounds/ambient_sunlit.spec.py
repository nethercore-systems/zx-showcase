"""Zone 1 (Sunlit Waters) ambient audio.

Bright, active underwater ambiance with filtered noise layers.
Duration: 60 seconds.
"""

SOUND = {
    'sound': {
        'name': 'ambient_sunlit',
        'duration': 60.0,
        'sample_rate': 22050,
        'layers': [
            # Base water movement (bright filtered noise)
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.3,
                'duration': 60.0,
                'filter': {
                    'type': 'bandpass',
                    'cutoff_low': 200,
                    'cutoff_high': 6000,
                },
            },
            # High frequency bubble texture
            {
                'type': 'noise_burst',
                'color': 'pink',
                'amplitude': 0.25,
                'duration': 60.0,
                'filter': {
                    'type': 'bandpass',
                    'cutoff_low': 1000,
                    'cutoff_high': 4000,
                },
            },
            # Subtle mid-frequency activity
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.15,
                'duration': 60.0,
                'filter': {
                    'type': 'bandpass',
                    'cutoff_low': 1000,
                    'cutoff_high': 5000,
                },
            },
        ],
        'effects': [
            {'type': 'reverb', 'decay': 0.2, 'delay_ms': 30, 'mix': 0.25},
        ],
        'normalize': True,
    }
}
