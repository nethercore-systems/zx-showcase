"""Whale call sound effect.

Main whale call - low fundamental with harmonics and warble.
Uses harmonics synthesis with AM modulation for the characteristic warble.
"""

SOUND = {
    'sound': {
        'name': 'whale',
        'duration': 5.0,
        'sample_rate': 22050,
        'layers': [
            # Fundamental + harmonics (using harmonics synth)
            {
                'type': 'harmonics',
                'freqs': [60, 120, 180, 300],  # fundamental, h2, h3, h5
                'amplitudes': [0.5, 0.25, 0.12, 0.06],
                'duration': 5.0,
            },
        ],
        'envelope': {
            'attack': 0.5,
            'decay': 0.3,
            'sustain': 0.6,
            'release': 1.5,
        },
        'effects': [
            {'type': 'reverb', 'decay': 0.5, 'delay_ms': 100, 'mix': 0.4},
        ],
        'normalize': True,
    }
}
