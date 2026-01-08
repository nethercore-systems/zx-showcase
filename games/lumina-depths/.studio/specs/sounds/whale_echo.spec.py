"""Distant whale echo sound effect.

Distant whale call with heavy reverb and filtering.
Higher fundamental, fewer harmonics, heavy lowpass for distance.
"""

SOUND = {
    'sound': {
        'name': 'whale_echo',
        'duration': 8.0,
        'sample_rate': 22050,
        'layers': [
            # Distant whale harmonics
            {
                'type': 'harmonics',
                'freqs': [80, 160, 240],  # fundamental, h2, h3
                'amplitudes': [0.3, 0.15, 0.05],
                'duration': 4.8,  # 60% of total
                'envelope': {
                    'attack': 0.8,
                    'decay': 0.5,
                    'sustain': 0.4,
                    'release': 1.0,
                },
                'filter': {
                    'type': 'lowpass',
                    'cutoff': 600,  # Heavy lowpass for distance
                },
            },
        ],
        'effects': [
            # Multiple reverb passes for cathedral effect
            {'type': 'reverb', 'decay': 0.6, 'delay_ms': 150, 'mix': 0.5},
            {'type': 'reverb', 'decay': 0.4, 'delay_ms': 300, 'mix': 0.4},
            {'type': 'reverb', 'decay': 0.3, 'delay_ms': 500, 'mix': 0.3},
        ],
        'normalize': True,
    }
}
