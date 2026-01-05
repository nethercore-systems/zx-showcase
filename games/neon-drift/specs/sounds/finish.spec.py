"""Race finish - triumphant chord.

Major chord fanfare with saw for brightness.
"""

SOUND = {
    'sound': {
        'name': 'finish',
        'duration': 0.8,
        'sample_rate': 22050,
        'layers': [
            # C5
            {
                'type': 'sine',
                'freq': 523,
                'amplitude': 0.3,
                'duration': 0.8,
                'delay': 0.0,
                'envelope': {
                    'attack': 0.02,
                    'decay': 0.1,
                    'sustain': 0.6,
                    'release': 0.2,
                },
            },
            # E5
            {
                'type': 'sine',
                'freq': 659,
                'amplitude': 0.3,
                'duration': 0.75,
                'delay': 0.05,
                'envelope': {
                    'attack': 0.02,
                    'decay': 0.1,
                    'sustain': 0.6,
                    'release': 0.2,
                },
            },
            # G5
            {
                'type': 'sine',
                'freq': 784,
                'amplitude': 0.3,
                'duration': 0.7,
                'delay': 0.1,
                'envelope': {
                    'attack': 0.02,
                    'decay': 0.1,
                    'sustain': 0.6,
                    'release': 0.2,
                },
            },
            # C6
            {
                'type': 'sine',
                'freq': 1047,
                'amplitude': 0.3,
                'duration': 0.65,
                'delay': 0.15,
                'envelope': {
                    'attack': 0.02,
                    'decay': 0.1,
                    'sustain': 0.6,
                    'release': 0.2,
                },
            },
            # Saw for brassy brightness
            {
                'type': 'saw',
                'freq': 523,
                'amplitude': 0.1,
                'duration': 0.8,
            },
        ],
        'normalize': True,
    }
}
