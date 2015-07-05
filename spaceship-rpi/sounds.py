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

    # No Fuel Sounds
    SND_NO_FUEL1 = 'no_fuel.wav'
    SND_NO_FUEL2 = 'no_fuel.wav'

    # Spaceship is Off Sounds
    SND_SC_TURNED_OFF = 'spaceship_is_turned_off.wav'
    SND_SC_TURNED_OFF2 = 'spaceship_is_turned_off2.wav'
    SND_SC_TURNED_OFF_X2 = 'spaceship_is_turned_x2_off'
    SND_SC_TURNED_OFF_X4 = 'spaceship_is_turned_x4_off'
    SND_SC_TURNED_OFF_X6 = 'spaceship_is_turned_x6_off'
    SND_SC_TURNED_OFF_X8 = 'spaceship_is_turned_x8_off'
    SND_SC_TURNED_OFF_X12 = 'spaceship_is_turned_x12_off'

    # Fuel is Low Sounds
    SND_LOW_FUEL_WARNING = 'low_fuel.wav'

    def __init__(self):
        """
        Convert the sounds files to full path
        """
        sc_turned_off = [Sounds.sound_file(Sounds.SND_SC_TURNED_OFF),
                         Sounds.sound_file(Sounds.SND_SC_TURNED_OFF2),
                         Sounds.sound_file(Sounds.SND_SC_TURNED_OFF_X2),
                         Sounds.sound_file(Sounds.SND_SC_TURNED_OFF_X4),
                         Sounds.sound_file(Sounds.SND_SC_TURNED_OFF_X6),
                         Sounds.sound_file(Sounds.SND_SC_TURNED_OFF_X8),
                         Sounds.sound_file(Sounds.SND_SC_TURNED_OFF_X12)]

        self.last_turned_off = -1

    @staticmethod
    def sound_file(filename):
        """ Create the full path for the sound file """
        return os.path.join(SOUND_DIR, filename)

    def spaceship_turned_off(self):
        """
        Returns the next sound when the spaceship is turned off.
        Here the sounds are played in sequence
        """
        self.last_turned_off += 1;

        if self.last_turned_off == len(self.sc_turned_off):
            self.last_turned_off = 0

        return self.sc_turned_off[self.last_turned_off]

    def no_oxygen(self):
        pass

    def engine_statring(self):
        pass

    def engine_running(self):
        return













