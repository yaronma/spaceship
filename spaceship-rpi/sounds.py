from os import stat_result

__author__ = 'yaron'

import os

# The sound files directory
SOUND_DIR = 'data'

class Sounds:

    def __init__(self):
        pass

    @staticmethod
    def sound_file(filename):
        """ Create the full path for the sound file """
        return os.path.join(SOUND_DIR, filename)

