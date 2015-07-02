from os import stat_result

__author__ = 'yaron'

import os

# The sound files directory
SOUND_DIR = 'data'

class Sounds:

    # No Oxygen Sounds
    SND_NO_OXYGEN1 = 'no_oxygen.wav'

    # Engine Starting Sounds
    SND_ENGINE_STARTING1 = 'engine_stopping.wav'

    # Engine Running Sounds
    SND_ENGINE_RUNNING = 'engine_running.wav'

    # Engine Stopping Sounds
    SND_ENGINE_STOPPING1 = 'engine_stopping.wav'

    # Spaceship ON Sounds
    SND_SPACESHIP_ON = 'start_spaceship.wav'

    # No Fule Sounds
    SND_NO_FUEL1 = 'no_fuel.wav'
    SND_NO_FUEL2 = 'no_fuel.wav'

    # Spaceship is Off Sounds
    SND_SC_TURNED_OFF = 'spaceship_is_turned_off.wav'

    # Fuel is Low Sounds
    SND_LOW_FUEL_WARNING = 'low_fuel.wav'

    def __init__(self):
        pass

    @staticmethod
    def sound_file(filename):
        """ Create the full path for the sound file """
        return os.path.join(SOUND_DIR, filename)

