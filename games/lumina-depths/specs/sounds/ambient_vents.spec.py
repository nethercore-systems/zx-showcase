"""Zone 4 (Hydrothermal Vents) ambient audio.

Volcanic rumble, hissing, metallic textures.
Duration: 90 seconds.
"""

SOUND = {
    'sound': {
        'name': 'ambient_vents',
        'duration': 90.0,
        'sample_rate': 22050,
        'layers': [
            # Volcanic rumble (low noise)
            {
                'type': 'noise_burst',
                'color': 'brown',
                'amplitude': 0.4,
                'duration': 90.0,
                'filter': {
                    'type': 'lowpass',
                    'cutoff': 150,
                },
            },
            # Hissing vents (mid-high noise)
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.2,
                'duration': 90.0,
                'filter': {
                    'type': 'bandpass',
                    'cutoff_low': 800,
                    'cutoff_high': 4000,
                },
            },
            # Metallic pings (inharmonic partials)
            {
                'type': 'metallic',
                'base_freq': 600,
                'num_partials': 5,
                'inharmonicity': 1.5,
                'amplitude': 0.12,
                'duration': 90.0,
                'envelope': {
                    'attack': 0.005,
                    'decay': 0.02,
                    'sustain': 0.1,
                    'release': 0.15,
                },
            },
            # Bubble texture (distant)
            {
                'type': 'noise_burst',
                'color': 'pink',
                'amplitude': 0.1,
                'duration': 90.0,
                'filter': {
                    'type': 'bandpass',
                    'cutoff_low': 500,
                    'cutoff_high': 1500,
                },
            },
        ],
        'effects': [
            {'type': 'reverb', 'decay': 0.3, 'delay_ms': 40, 'mix': 0.25},
        ],
        'normalize': True,
    }
}
