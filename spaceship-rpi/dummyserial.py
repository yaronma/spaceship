__author__ = 'yaron'

class DummySerial:

    @staticmethod
    def write(args):
        print("Serial:", args)

