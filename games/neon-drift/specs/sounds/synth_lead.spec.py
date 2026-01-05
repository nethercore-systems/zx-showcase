"""Bright lead synth.

Square + saw blend with octave harmonic.
"""

SOUND = {
    'sound': {
        'name': 'synth_lead',
        'duration': 0.5,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'square',
                'freq': 440,  # A4
                'amplitude': 0.3,
                'duration': 0.5,
            },
            {
                'type': 'saw',
                'freq': 440,
                'amplitude': 0.2,
                'duration': 0.5,
            },
            {
                'type': 'sine',
                'freq': 880,  # Octave
                'amplitude': 0.1,
                'duration': 0.5,
            },
        ],
        'envelope': {
            'attack': 0.01,
            'decay': 0.1,
            'sustain': 0.6,
            'release': 0.2,
        },
        'normalize': True,
    }
}
