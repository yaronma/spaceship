__author__ = 'yaron'

class DummyRpi:

        OUT = "output"

        HIGH = "high"

        BCM = "bcm"

        @staticmethod
        def setmode(mode):
            print("Setting mode to" + mode)

        @staticmethod
        def setup(pin, mode):
            print("Setting pin " + str(pin) + " to" + mode)

        @staticmethod
        def output(pin, mode):
            print("Changing pin " + str(pin) + " to" + mode)
