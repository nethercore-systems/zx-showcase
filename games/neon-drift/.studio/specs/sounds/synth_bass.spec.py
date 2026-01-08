"""Synth bass - detuned saws.

Low A1 with slight detune for thickness.
"""

SOUND = {
    'sound': {
        'name': 'synth_bass',
        'duration': 0.5,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'saw',
                'freq': 55,  # A1
                'amplitude': 0.4,
                'duration': 0.5,
            },
            {
                'type': 'saw',
                'freq': 55.165,  # Slight detune
                'amplitude': 0.3,
                'duration': 0.5,
            },
        ],
        'envelope': {
            'attack': 0.01,
            'decay': 0.1,
            'sustain': 0.7,
            'release': 0.15,
        },
        'master_filter': {
            'type': 'lowpass',
            'cutoff': 300,
        },
        'normalize': True,
    }
}
