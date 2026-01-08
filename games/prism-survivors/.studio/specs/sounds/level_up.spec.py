"""Level up - triumphant ascending arpeggio.

C major chord arpeggio with reverb.
"""

SOUND = {
    'sound': {
        'name': 'level_up',
        'duration': 0.6,
        'sample_rate': 22050,
        'layers': [
            # C5
            {
                'type': 'sine',
                'freq': 523,
                'amplitude': 0.35,
                'duration': 0.35,
                'delay': 0.0,
                'envelope': {
                    'attack': 0.02,
                    'decay': 0.05,
                    'sustain': 0.5,
                    'release': 0.15,
                },
            },
            # E5
            {
                'type': 'sine',
                'freq': 659,
                'amplitude': 0.35,
                'duration': 0.35,
                'delay': 0.12,
                'envelope': {
                    'attack': 0.02,
                    'decay': 0.05,
                    'sustain': 0.5,
                    'release': 0.15,
                },
            },
            # G5
            {
                'type': 'sine',
                'freq': 784,
                'amplitude': 0.35,
                'duration': 0.35,
                'delay': 0.24,
                'envelope': {
                    'attack': 0.02,
                    'decay': 0.05,
                    'sustain': 0.5,
                    'release': 0.15,
                },
            },
            # C6
            {
                'type': 'sine',
                'freq': 1047,
                'amplitude': 0.35,
                'duration': 0.35,
                'delay': 0.36,
                'envelope': {
                    'attack': 0.02,
                    'decay': 0.05,
                    'sustain': 0.5,
                    'release': 0.15,
                },
            },
            # Triangle harmonics for brightness
            {
                'type': 'triangle',
                'freq': 1046,
                'amplitude': 0.1,
                'duration': 0.35,
                'delay': 0.0,
            },
        ],
        'effects': [
            {'type': 'reverb', 'decay': 0.2, 'delay_ms': 30, 'mix': 0.3},
        ],
        'normalize': True,
    }
}
