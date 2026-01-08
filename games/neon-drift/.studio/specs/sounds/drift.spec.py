"""Tire screech/drift sound.

High-pitched noise for tire screech.
"""

SOUND = {
    'sound': {
        'name': 'drift',
        'duration': 0.5,
        'sample_rate': 22050,
        'layers': [
            # Screech noise
            {
                'type': 'noise_burst',
                'color': 'white',
                'amplitude': 0.5,
                'duration': 0.5,
                'filter': {
                    'type': 'bandpass',
                    'cutoff_low': 1500,
                    'cutoff_high': 4000,
                },
            },
            # Modulated carrier
            {
                'type': 'fm_synth',
                'carrier_freq': 2000,
                'mod_ratio': 0.0075,  # 15 Hz
                'mod_index': 500,
                'index_decay': 0.0,
                'amplitude': 0.3,
                'duration': 0.5,
            },
        ],
        'envelope': {
            'attack': 0.02,
            'decay': 0.1,
            'sustain': 0.6,
            'release': 0.2,
        },
        'master_filter': {
            'type': 'lowpass',
            'cutoff': 4000,
        },
        'normalize': True,
    }
}
