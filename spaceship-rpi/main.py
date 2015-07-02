__author__ = 'yaron'

import os
import sys
import atexit

pid_file = "./RUNNING.pid"

def main():
    """
    Exits the application if the PID file exists.
    :return:
    """
    try:
        import RPi.GPIO as GPIO
    except RuntimeError:
        from dummyrpi import DummyRpi as GPIO

    # Check if the PID file exists
    pid = str(os.getpid())
    if os.path.isfile(pid_file):
        print("%s already exists, exiting" % pid_file)
        sys.exit()
    else:
        open(pid_file, 'w').write(pid)

    # Delete the PID file if the application exists
    atexit.register(stop)


def stop():
    os.remove(pid_file)

if __name__=="__main__":
    main()