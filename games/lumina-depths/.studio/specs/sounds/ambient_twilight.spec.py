"""Zone 2 (Twilight Realm) ambient audio.

Mysterious, darker underwater ambiance with pressure drone.
Duration: 90 seconds.
"""

SOUND = {
    'sound': {
        'name': 'ambient_twilight',
        'duration': 90.0,
        'sample_rate': 22050,
        'layers': [
            # Darker base (more lowpass)
            {
                'type': 'noise_burst',
                'color': 'brown',
                'amplitude': 0.25,
                'duration': 90.0,
                'filter': {
                    'type': 'bandpass',
                    'cutoff_low': 50,
                    'cutoff_high': 2000,
                },
            },
            # Pressure drone (low sine)
            {
                'type': 'sine',
                'freq': 55,
                'amplitude': 0.3,
                'duration': 90.0,
            },
            # Marine snow tinkle (high frequency texture)
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.08,
                'duration': 90.0,
                'filter': {
                    'type': 'bandpass',
                    'cutoff_low': 3000,
                    'cutoff_high': 8000,
                },
            },
            # Subtle distant whale presence
            {
                'type': 'harmonics',
                'freqs': [100, 200, 300],
                'amplitudes': [0.08, 0.04, 0.02],
                'duration': 90.0,
                'filter': {
                    'type': 'lowpass',
                    'cutoff': 800,
                },
            },
        ],
        'effects': [
            {'type': 'reverb', 'decay': 0.4, 'delay_ms': 80, 'mix': 0.35},
        ],
        'normalize': True,
    }
}
