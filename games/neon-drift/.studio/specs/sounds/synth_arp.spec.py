"""Arpeggio pluck sound.

Short saw with quick decay.
"""

SOUND = {
    'sound': {
        'name': 'synth_arp',
        'duration': 0.15,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'saw',
                'freq': 330,  # E4
                'amplitude': 0.5,
                'duration': 0.15,
            },
        ],
        'envelope': {
            'attack': 0.002,
            'decay': 0.03,
            'sustain': 0.3,
            'release': 0.1,
        },
        'master_filter': {
            'type': 'lowpass',
            'cutoff': 2000,
        },
        'normalize': True,
    }
}
