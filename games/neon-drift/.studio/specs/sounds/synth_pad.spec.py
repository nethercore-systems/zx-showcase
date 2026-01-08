"""Soft pad sound.

Multiple detuned sines for warmth.
"""

SOUND = {
    'sound': {
        'name': 'synth_pad',
        'duration': 1.0,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'sine',
                'freq': 220,  # A3
                'amplitude': 0.3,
                'duration': 1.0,
            },
            {
                'type': 'sine',
                'freq': 220.44,  # +2 cents
                'amplitude': 0.25,
                'duration': 1.0,
            },
            {
                'type': 'sine',
                'freq': 219.56,  # -2 cents
                'amplitude': 0.25,
                'duration': 1.0,
            },
            {
                'type': 'sine',
                'freq': 440,  # Octave
                'amplitude': 0.1,
                'duration': 1.0,
            },
        ],
        'envelope': {
            'attack': 0.15,
            'decay': 0.2,
            'sustain': 0.7,
            'release': 0.3,
        },
        'master_filter': {
            'type': 'lowpass',
            'cutoff': 1000,
        },
        'normalize': True,
    }
}
