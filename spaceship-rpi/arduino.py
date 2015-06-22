__author__ = 'yaron'

import serial
import platform
import threading
import logging


class Arduino:
    """
    A class for handling communications with the Arduino.
    This class handles the two-way communication with the Arduino.
    On one side, this class receives events on the serial line regarding
    actions performed on the Arduino (Button pressed).
    On the other side, this class sends commands to the Arduino (Turn on
    Motor, Turn off Led)
    """

    # Engine enumeration
    LEFT_ENGINE = 1
    RIGHT_ENGINE = 2

    # Led status
    LED_OFF = 0
    LED_ON = 1

    # LEDs enumeration
    SPACESHIP_FUEL_LED_ID = 43
    SPACESHIP_OXYGEN_LED_ID = 41
    SPACESHIP_ON_LED_ID = 42
    SPACESHIP_LIGHTS_LED_ID = 40
    SPACESHIP_SOUNDS_LED_ID = 37
    SPACESHIP_UP_LED_ID = 39
    SPACESHIP_DOWN_LED_ID = 38
    SPACESHIP_LIGHTS_ID = 40  # The ID of the actual lights (not the led on the main panel)

    # Command Types
    CMD_CHANGE_PIN = 97
    CMD_BARGRAPH = 98
    CMD_ENGINE = 99
	
    FLAG = 85

    # Bar-Graphs enumeration
    FUEL_BARGRAPH_ID = 0
    OXYGEN_BARGRAPH_ID = 1

    # Event IDs - I intentionally use ASCII values in order to be able
    # to test the web interface using only a browser
    EVT_SC_ON_PRESSED = 49  # == '1'. To convert from ASCII, use EVT_yyy = int.from_bytes(b'1', 'big')
    EVT_SC_ON_RELEASED = 50  # == '2'
    EVT_SC_SOUND_PRESSED = 51  # == '3'
    EVT_SC_SOUND_RELEASED = 52
    EVT_SC_KEY_FUEL_PRESSED = 53
    EVT_SC_KEY_FUEL_RELEASED = 54
    EVT_SC_KEY_OXYGEN_PRESSED = 55
    EVT_SC_KEY_OXYGEN_RELEASED = 56
    EVT_SC_LEFT_ENGINE_PRESSED = 57
    EVT_SC_LEFT_ENGINE_RELEASED = 58
    EVT_SC_RIGHT_ENGINE_PRESSED = 59
    EVT_SC_RIGHT_ENGINE_RELEASED = 60
    EVT_SC_LIGHTS_PRESSED = 61
    EVT_SC_LIGHTS_RELEASED = 62
    EVT_SC_UP_PRESSED = 63
    EVT_SC_UP_RELEASED = 64
    EVT_SC_DOWN_PRESSED = 65
    EVT_SC_DOWN_RELEASED = 66

    # A list of all the events for easy event data validations
    events = [EVT_SC_ON_PRESSED,
              EVT_SC_ON_RELEASED,
              EVT_SC_SOUND_PRESSED,
              EVT_SC_SOUND_RELEASED,
              EVT_SC_KEY_FUEL_PRESSED,
              EVT_SC_KEY_FUEL_RELEASED,
              EVT_SC_KEY_OXYGEN_PRESSED,
              EVT_SC_KEY_OXYGEN_RELEASED,
              EVT_SC_LEFT_ENGINE_PRESSED,
              EVT_SC_LEFT_ENGINE_RELEASED,
              EVT_SC_RIGHT_ENGINE_PRESSED,
              EVT_SC_RIGHT_ENGINE_RELEASED,
              EVT_SC_LIGHTS_PRESSED,
              EVT_SC_LIGHTS_RELEASED,
              EVT_SC_UP_PRESSED,
              EVT_SC_UP_RELEASED,
              EVT_SC_DOWN_PRESSED,
              EVT_SC_DOWN_RELEASED]

    def __init__(self, spaceship):

        self.spaceship = spaceship
        self.port = '/dev/??'

        if platform.system() == 'Windows':
            self.port = '\\.\COM7'
        else:
            self.port = "/dev/ttyUSB0"

        self.alive = True
        self._reader_alive = False
        self.receiver_thread = None

        # Input buffer from the Serial port
        self.buffer = b""

        # Used for debugging where the Serial port is not available
        self.enable_serial = True

        if self.enable_serial:
            # self.serial = serial.Serial(self.port, 9600, timeout=1, bytesize=8, parity='N')
            self.serial = serial.Serial("/dev/ttyUSB0", baudrate=57600, parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, writeTimeout = 0, timeout = 10,rtscts=False,dsrdtr=False, xonxoff=False)
            self.start()
        else:
            from dummyserial import DummySerial
            self.serial = DummySerial()

    def set_oxygen(self, level):
        self.send_command(Arduino.CMD_BARGRAPH, Arduino.OXYGEN_BARGRAPH_ID, level)

    def set_fuel(self, level):
        self.send_command(Arduino.CMD_BARGRAPH, Arduino.FUEL_BARGRAPH_ID, level)

    def set(self, element_id, state):
        new_state = 0
        if state:
            new_state = 1
        self.send_command(Arduino.CMD_CHANGE_PIN, element_id, new_state)

    def start_right_engine(self):
        self.start_engine(Arduino.RIGHT_ENGINE)

    def start_left_engine(self):
        self.start_engine(Arduino.LEFT_ENGINE)

    def start_engine(self, engine_id):
        # Check that engine ID is valid
        if engine_id not in [self.LEFT_ENGINE, self.RIGHT_ENGINE]:
            return

        self.send_command(Arduino.CMD_ENGINE, engine_id, 1)

    def stop_engine(self, engine_id):
        # Check that engine ID is valid
        if engine_id not in [self.LEFT_ENGINE, self.RIGHT_ENGINE]:
            return

        self.send_command(Arduino.CMD_ENGINE, engine_id, 0)

    def stop_right_engine(self):
        self.stop_engine(Arduino.RIGHT_ENGINE)

    def stop_left_engine(self):
        self.stop_engine(Arduino.LEFT_ENGINE)

    def fuel_led_off(self):
        self.led(Arduino.SPACESHIP_FUEL_LED_ID, Arduino.LED_OFF)

    def fuel_led_on(self):
        self.led(Arduino.SPACESHIP_FUEL_LED_ID, Arduino.LED_ON)

    def oxygen_led_off(self):
        self.led(Arduino.SPACESHIP_OXYGEN_LED_ID, Arduino.LED_OFF)

    def oxygen_led_on(self):
        self.led(Arduino.SPACESHIP_OXYGEN_LED_ID, Arduino.LED_ON)

    def spaceship_led_off(self):
        self.led(Arduino.SPACESHIP_ON_LED_ID, Arduino.LED_OFF)

    def spaceship_led_on(self):
        self.led(Arduino.SPACESHIP_ON_LED_ID, Arduino.LED_ON)

    def lights_on(self):
        self.led(Arduino.SPACESHIP_LIGHTS_ID, Arduino.LED_ON)

    def lights_off(self):
        self.led(Arduino.SPACESHIP_LIGHTS_ID, Arduino.LED_OFF)

    def lights_led_on(self):
        self.led(Arduino.SPACESHIP_LIGHTS_LED_ID, Arduino.LED_ON)

    def lights_led_off(self):
        self.led(Arduino.SPACESHIP_LIGHTS_LED_ID, Arduino.LED_OFF)

    def move_up_led_on(self):
        self.led(Arduino.SPACESHIP_UP_LED_ID, Arduino.LED_ON)

    def move_up_led_off(self):
        self.led(Arduino.SPACESHIP_UP_LED_ID, Arduino.LED_OFF)

    def sounds_led_on(self):
        self.led(Arduino.SPACESHIP_SOUNDS_LED_ID, Arduino.LED_ON)

    def sounds_led_off(self):
        self.led(Arduino.SPACESHIP_SOUNDS_LED_ID, Arduino.LED_OFF)

    def move_down_led_on(self):
        self.led(Arduino.SPACESHIP_DOWN_LED_ID, Arduino.LED_ON)

    def move_down_led_off(self):
        self.led(Arduino.SPACESHIP_DOWN_LED_ID, Arduino.LED_OFF)

    def motor_up(self):
        pass

    def motor_down(self):
        pass

    def motor_stop(self):
        pass

    # Send the Arduino a message to change the state of a specific pin
    def led(self, led_id, led_state):
        self.send_command(Arduino.CMD_CHANGE_PIN, led_id, led_state)

    def send_command(self, command_type, command_id, value):
#        data = b'\x61\x2a\x01'
#        data = bytearray([chr(command_type), chr(command_id), chr(value)])
        data = bytearray([chr(Arduino.FLAG), chr(command_type), chr(command_id), chr(value)])
#       data = bytes([command_type, command_id, value])
#        print(type(command_type))
#        print(bytes([command_type, command_id, value]))
        print("Arduino: Sending: " + str(command_type) + ", " + str(command_id) + ", " + str(value))
#        print("Binary data: ")
#        print(data)
        print("\n")
        self.serial.write(data)

    def start(self):
        """ Start reader thread """
        logging.debug("Arduino: Listening thread started!")
        self._reader_alive = True
        # start serial->console thread
        self.receiver_thread = threading.Thread(target=self.reader)
        self.receiver_thread.setDaemon(True)
        self.receiver_thread.start()

    def stop(self):
        self.alive = False

    def handle_packet(self, data):

        print("Received ")
        print(ord(data[0]))
        print(", ")
        print(ord(data[1]))
        print(", ")
        print(ord(data[2]))
        print("\n")

        # Check that we recognize this event type
        if not ord(data[0]) in Arduino.events:
            print("Cannot find handler, aborting...")
            return

        # For now, we just send an event to the spaceship on all events
        # (only with the event id, no data)

        self.spaceship.handle_user_event(ord(data[0]))

    def reader(self):
            """ Read the pending protocol packets sent from the Arduino to the application """
            try:
                while self.alive:
                    reading = self.serial.read(1)

                    if not len(reading) == 1:
                        continue

                    self.buffer += reading

                    # For now the protocol is very simple and relays on constant packet size
                    # of 3 bytes. We didn't implemented mechanisms of Flow-Control/Error Recovery or Encryption
                    if len(self.buffer) == 3:
                        self.handle_packet(self.buffer)
                        self.buffer = b""

            except serial.SerialException as e:
                self.alive = False
                logging.debug("Failure on the serial line. Error {}", e)
                raise
