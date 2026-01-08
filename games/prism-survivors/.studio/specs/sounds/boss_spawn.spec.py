"""Boss spawn - ominous rumble with impact.

Low rumble with FM modulation and impact at end.
"""

SOUND = {
    'sound': {
        'name': 'boss_spawn',
        'duration': 1.0,
        'sample_rate': 22050,
        'layers': [
            # Low rumble with modulation
            {
                'type': 'fm_synth',
                'carrier_freq': 40,
                'mod_ratio': 0.05,  # 2 Hz modulation
                'mod_index': 20,    # Frequency deviation
                'index_decay': 0.0,
                'amplitude': 0.4,
                'duration': 1.0,
                'envelope': {
                    'attack': 0.1,
                    'decay': 0.3,
                    'sustain': 0.5,
                    'release': 0.4,
                },
            },
            # Impact at end
            {
                'type': 'sine',
                'freq': 60,
                'amplitude': 0.6,
                'duration': 0.3,
                'delay': 0.6,
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.1,
                    'sustain': 0.2,
                    'release': 0.15,
                },
            },
            # Impact noise
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.4,
                'duration': 0.1,
                'delay': 0.6,
                'envelope': {
                    'attack': 0.005,
                    'decay': 0.03,
                    'sustain': 0.1,
                    'release': 0.05,
                },
            },
        ],
        'master_filter': {
            'type': 'lowpass',
            'cutoff': 500,
        },
        'normalize': True,
    }
}
