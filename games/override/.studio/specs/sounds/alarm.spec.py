"""Alarm sound effect.

Warning siren with oscillating frequency.
Note: The oscillating frequency pattern is approximated using FM synthesis
since the original uses a custom freq = 400 + 200 * sin(2*pi*2*t) pattern.
"""

SOUND = {
    'sound': {
        'name': 'alarm',
        'duration': 1.0,
        'sample_rate': 22050,
        'layers': [
            {
                'type': 'fm_synth',
                'carrier_freq': 400,
                'mod_ratio': 0.005,  # 2 Hz modulation relative to 400 Hz
                'mod_index': 200,    # 200 Hz frequency deviation
                'index_decay': 0.0,  # No decay - constant modulation
                'amplitude': 1.0,
                'duration': 1.0,
            },
        ],
        'envelope': {
            'attack': 0.05,
            'decay': 0.05,
            'sustain': 0.9,
            'release': 0.05,
        },
        'normalize': True,
    }
}
