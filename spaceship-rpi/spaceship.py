#!/usr/bin/python3
# spaceship1.py

# TODO:
# - Turn the oxygen and fuel into gauge class


# TODO - Delete the spaceship.event_count variable and make all relevant methods static
import os
import logging
import pygame
import time

from arduino import Arduino
from sounds import Sounds
from webinterface import WebInterface

try:
    from dummyrpi import DummyRpi as GPIO 
    # import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!")


# pygame.USEREVENT is reserved for the Arduino originated events
# Accroding to the docs, the events must be between USEREVENT and NUMEVENTS
EVT_MUSIC_END = pygame.USEREVENT + 1
EVT_TIMER_FUEL = pygame.USEREVENT + 2  # Triggered when the fuel usage timer has elapsed
EVT_TIMER_OXYGEN = pygame.USEREVENT + 3  # Triggered when the oxygen usage timer has elapsed
EVT_TIMER_FILL_FUEL = pygame.USEREVENT + 4  # Triggered when the fuel button is pressed and the timer has passed
EVT_TIMER_FILL_OXYGEN = pygame.USEREVENT + 5  # Triggered when the oxygen button is pressed and the timer has passed

# The maximum level of the oxygen and fuel bargraph
MAX_BARGRAPH_LEVEL = 20
FILL_TIMER = 1000
FUEL_USAGE_TIMER = 5000
OXYGEN_USAGE_TIMER = 18000

# Sounds
SND_NO_OXYGEN = Sounds.sound_file('no_oxygen.wav')
SND_ENGINE_STARTING = Sounds.sound_file('engine_stopping.wav')
SND_ENGINE_RUNNING = Sounds.sound_file('engine_running.wav')
SND_ENGINE_STOPPING = Sounds.sound_file('engine_stopping.wav')
SND_LIFTOFF = Sounds.sound_file('engine_running.wav')
SND_NO_FUEL = Sounds.sound_file('no_fuel.wav')
SND_SC_TURNED_OFF = Sounds.sound_file('spaceship_is_turned_off.wav')
SND_LOW_FUEL_WARNING = Sounds.sound_file('low_fuel.wav')

# Spaceship Movement
UP = 1
DOWN = 2

class Buttons:
    def __init__(self):
        self.FUEL = 1

# Build dummy video so we can use the event loop
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Initialize PyGame
#pygame.mixer.pre_init(44100, 16, 2, 4096)  # frequency, size, channels, buffersize
pygame.init()
pygame.display.set_mode((1, 1))

# When we receive data on the serial line,
# post an event to the loop for handling
# pygame.event.post(pygame.event.Event(USEREVENT+1))
clock = pygame.time.Clock()


# Initialize the logging module
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logger = logging.getLogger('Spaceship')
logger.addHandler(console)
logger.setLevel(logging.DEBUG)
logger.debug("Spaceship application starting")


class Spaceship:

    # Get current volume settings
    

    def __init__(self):
        """ Initialize our spaceship object """

        self.volume = pygame.mixer.music.get_volume()
        # Turn the volume off, since on startup, there is white noise
        #pygame.mixer.music.set_volume(0.0)

        # The RPi Indicators
        # The LED indicating that the spaceship app is running
        self.spaceship_running_rpi_led = 24
        # The LED indicating that the spaceship is turned on
        self.spaceship_on_rpi_led = 25

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.spaceship_running_rpi_led, GPIO.OUT)
        GPIO.setup(self.spaceship_on_rpi_led, GPIO.OUT)
        GPIO.output(self.spaceship_running_rpi_led, GPIO.HIGH)
        GPIO.output(self.spaceship_on_rpi_led, GPIO.HIGH)

        # The fuel gauge is in the value of 0-20. Start the spaceship fully fueld
        self.fuel_level = MAX_BARGRAPH_LEVEL

        # The oxygen gauge is in the value of 0-20. Start the spaceship fully filled
        self.oxygen_level = MAX_BARGRAPH_LEVEL

        # Corresponding variables for the buttons
        self.spaceship_turned_on = False
        self.fuel_pressed = False
        self.oxygen_pressed = False
        self.sound_on = True
        self.left_engine_on = False
        self.right_engine_on = False
        self.lights_on = False
        self.move_up = False
        self.move_down = False
        self.spaceship_flying = False

        # The arduino interface
        self.arduino = Arduino(self)
        self.arduino.reset()
        time.sleep(5)

        # The web interface
        self.web_interface = WebInterface()

        # The sounds
        self.sounds = Sounds()

        # User events count
        self.event_count = 0

        self.handlers = {
            Arduino.EVT_SC_ON_PRESSED: self.handle_sc_on_pressed,
            Arduino.EVT_SC_ON_RELEASED: self.handle_sc_on_released,
            Arduino.EVT_SC_DOWN_PRESSED: self.handle_down_pressed,
            Arduino.EVT_SC_DOWN_RELEASED: self.handle_down_released,
            Arduino.EVT_SC_UP_PRESSED: self.handle_up_pressed,
            Arduino.EVT_SC_UP_RELEASED: self.handle_up_released,
            Arduino.EVT_SC_KEY_FUEL_PRESSED: self.handle_fuel_pressed,
            Arduino.EVT_SC_KEY_FUEL_RELEASED: self.handle_fuel_released,
            Arduino.EVT_SC_KEY_OXYGEN_PRESSED: self.handle_oxygen_pressed,
            Arduino.EVT_SC_KEY_OXYGEN_RELEASED: self.handle_oxygen_released,
            Arduino.EVT_SC_LEFT_ENGINE_PRESSED: self.handle_left_engine_on,
            Arduino.EVT_SC_LEFT_ENGINE_RELEASED: self.handle_left_engine_off,
            Arduino.EVT_SC_RIGHT_ENGINE_PRESSED: self.handle_right_engine_on,
            Arduino.EVT_SC_RIGHT_ENGINE_RELEASED: self.handle_right_engine_off,
            Arduino.EVT_SC_SOUND_PRESSED: self.handle_sound_pressed,
            Arduino.EVT_SC_SOUND_RELEASED: self.handle_sound_released,
            Arduino.EVT_SC_LIGHTS_PRESSED: self.handle_lights_pressed,
            Arduino.EVT_SC_LIGHTS_RELEASED: self.handle_lights_released,
        }

        # Initialize the spaceship controls
        self.init()
        #pygame.mixer.music.set_volume(self.volume)
        self.play_sound(self.sounds.spaceship_ready())

    def init(self):

        # Stop and shutdown all modules
        self.arduino.set_oxygen(self.oxygen_level)
        self.arduino.set_fuel(self.fuel_level)
        self.arduino.stop_right_engine()
        self.arduino.stop_left_engine()
        self.arduino.lights_off()

        # LEDs
        self.arduino.lights_led_off()
        self.arduino.sounds_led_on()
        self.arduino.spaceship_led_off()
        self.arduino.oxygen_led_off()
        self.arduino.fuel_led_off()
        self.arduino.move_up_led_off()
        self.arduino.move_down_led_off()

        # Set the volume
        

    @staticmethod
    def stop_music():
        try:
            pygame.mixer.music.stop()
        except RuntimeError as e:
            logger.error("Failed in stop_music, error is " + str(e))

    def play_music(self, soundfile):
        """
        Stream music with mixer.music module using the event module to wait
        until the playback has finished.

        This method doesn't use a busy/poll loop, but has the disadvantage that
        you neet to initialize the video module to use the event module.
        """
        logger.debug("Spaceship starting to play music")
        if self.sound_on:
            pygame.mixer.music.load(soundfile)
            pygame.mixer.music.play(-1)

    def play_sound(self, sound_file):
        """
        Plays a sound file if the sound button is turned on
        :param sound_file: The sound file to play
        :return: None
        """
        logger.debug("Spaceship playing sound %s", sound_file)
        if self.sound_on:
            sound = pygame.mixer.Sound(sound_file)
            sound.play()

    def handle_fuel_timer(self):
        """ Called when the fuel timer has expired. """
        logger.debug("Fuel timer fired, fuel value %d", self.fuel_level)

        # In case the engines are turned off don't waste fuel
        if not self.left_engine_on and not self.right_engine_on:
            logger.debug("Engines are off, not using fuel")
            return

        # If the fuel level is 0, we are out of fuel...
        if self.fuel_level == 1:
            self.play_sound(SND_LOW_FUEL_WARNING)

        if self.fuel_level == 0:
            self.play_sound(SND_NO_FUEL)
            self.shutdown()
        else:
            self.fuel_level -= 1
            self.arduino.set_fuel(self.fuel_level)

    def handle_oxygen_timer(self):
        """ Called when the oxygen timer has expired. """
        logger.debug("Oxygen timer fired, oxygen value %d", self.oxygen_level)

        # In case the engines are turned off don't waste oxygen
        if not self.left_engine_on and not self.right_engine_on:
            logger.debug("Engines are off, not using oxygen")
            return

        # If the oxygen level is 0, we are dead...
        if self.oxygen_level == 0:
            self.play_sound(SND_NO_OXYGEN)
            self.shutdown()
        else:
            self.oxygen_level -= 1
            self.arduino.set_oxygen(self.oxygen_level)

    def handle_sc_on_pressed(self):
        logger.debug("Spaceship ON button pressed")
        # If the spaceship is turned on, this is shutdown command
        if self.spaceship_turned_on:
            self.shutdown()
            self.spaceship_turned_on = False
            self.arduino.spaceship_led_off()
            return

        # The spaceship is turned off, start it
        self.arduino.spaceship_led_on()
        self.spaceship_turned_on = True

    def handle_sc_on_released(self):
        logger.debug("Spaceship ON button released")
        self.event_count += 1
        pass

    def handle_sound_pressed(self):
        """
        Turn on and off the sound system
        """

        logger.debug("Spaceship Sound button pressed")
        self.event_count += 1

        # If the sound is on, turn it off
        if self.sound_on:
            self.sound_on = False
            self.arduino.sounds_led_off()
            self.stop_music()

        else:
            # The sound is off, turn it on
            self.sound_on = True
            self.arduino.sounds_led_on()

            # If one of the engines is running, play the engine music
            if self.spaceship_turned_on and (self.right_engine_on or self.left_engine_on):
                self.play_music(SND_ENGINE_RUNNING)

    def handle_sound_released(self):
        logger.debug("Spaceship Sound button released")
        self.event_count += 1
        pass

    def handle_fuel_filling_timer(self):
        logger.debug("Spaceship fuel filling timer elapsed")
        self.event_count += 1

        # Check that the fuel is not already full
        if self.fuel_level == MAX_BARGRAPH_LEVEL:
            self.handle_fuel_pressed()  # Simulate another press that will turn off fueling
            logger.debug("Fuel filling timer: Fuel is full")
            return

        self.fuel_level += 1
        self.arduino.set_fuel(self.fuel_level)
        logger.debug("Fuel filling timer: New fuel value: %d", self.fuel_level)

    def handle_fuel_pressed(self):
        """
        The fuel button is pressed. Instantly add 1 bar and start the fuel timer
        """

        logger.debug("Spaceship Fuel button pressed")

        if self.fuel_pressed:
            self.fuel_pressed = False
            self.arduino.fuel_led_off()
            pygame.time.set_timer(EVT_TIMER_FILL_FUEL, 0)
        else:
            self.fuel_pressed = True
            self.arduino.fuel_led_on()
#            self.handle_fuel_filling_timer()
            # Start the fueling timer #
            pygame.time.set_timer(EVT_TIMER_FILL_FUEL, FILL_TIMER)

    def handle_fuel_released(self):
        logger.debug("Spaceship Fuel button released")
        self.event_count += 1
        # We don't do nothing on key release
        pass

    def handle_oxygen_filling_timer(self):

        # Check that the oxygen is not already full
        if self.oxygen_level == MAX_BARGRAPH_LEVEL:
            self.handle_oxygen_pressed()  # Simulate another press that will turn off oxygen
            logger.debug("Fuel filling timer: Fuel is full")
            return

        self.oxygen_level += 1
        self.arduino.set_oxygen(self.oxygen_level)

    def handle_oxygen_pressed(self):
        logger.debug("Spaceship Oxygen button pressed")

        if self.oxygen_pressed:
            self.oxygen_pressed = False
            self.arduino.oxygen_led_off()
            pygame.time.set_timer(EVT_TIMER_FILL_OXYGEN, 0)
        else:
            self.oxygen_pressed = True
            self.arduino.oxygen_led_on()
            pygame.time.set_timer(EVT_TIMER_FILL_OXYGEN, FILL_TIMER)

    def handle_oxygen_released(self):
        logger.debug("Spaceship Oxygen button released")
        self.event_count += 1
        # We don't do nothing on key release
        pass

    def handle_left_engine_on(self):
        logger.debug("Spaceship left engine turned on")

        # If the spaceship is not turned on, play sound
        if not self.spaceship_turned_on:
            self.play_sound(self.sounds.spaceship_turned_off())
            return

        # If the fuel level is 0, we are out of fuel...
        if self.fuel_level == 0:
            self.play_sound(SND_NO_FUEL)
            return

        # If the engine is running, turn it off
        if self.left_engine_on:
            self.handle_left_engine_off()
            return

        self.play_sound(SND_ENGINE_STARTING)
        self.left_engine_on = True
      


        # If this is the first engine, the spaceship is starting to use fuel and oxygen
        if not self.right_engine_on:
            pygame.time.set_timer(EVT_TIMER_OXYGEN, OXYGEN_USAGE_TIMER)
            pygame.time.set_timer(EVT_TIMER_FUEL, FUEL_USAGE_TIMER)
            self.play_music(SND_ENGINE_RUNNING)

    def handle_left_engine_off(self):
        logger.debug("Spaceship left engine turned off")

        # If the engine is not turned on (there was no fuel in activation)
        if not self.left_engine_on:
            return

        # Turn on the engine
        self.left_engine_on = False
        self.play_sound(SND_ENGINE_STOPPING)

        # If the right engine is not running, shutdown the spaceship
        if not self.right_engine_on:
            self.shutdown()

    def handle_right_engine_on(self):
        logger.debug("Spaceship right engine turned on")

        # If the spaceship is not turned on, play sound
        if not self.spaceship_turned_on:
            self.play_sound(self.sounds.spaceship_turned_off())
            return

        # If the fuel level is 0, we are out of fuel...
        if self.fuel_level == 0:
            self.play_sound(SND_NO_FUEL)
            return

        # If the engine is running, turn it off
        if self.right_engine_on:
            self.handle_right_engine_off()
            return

        # In any case play the 'Engine Starting' sound
        self.play_sound(SND_ENGINE_STARTING)
        self.right_engine_on = True
        

        # If this is the first engine, the spaceship is starting to use fuel and oxygen
        if not self.left_engine_on:
            pygame.time.set_timer(EVT_TIMER_OXYGEN, OXYGEN_USAGE_TIMER)
            pygame.time.set_timer(EVT_TIMER_FUEL, FUEL_USAGE_TIMER)
            self.play_music(SND_ENGINE_RUNNING)

    def handle_right_engine_off(self):
        logger.debug("Spaceship right engine turned off")

        # If the engine is not turned on (there was no fuel in activation)
        if not self.right_engine_on:
            return

        # Turn on the engine
        self.right_engine_on = False
        self.play_sound(SND_ENGINE_STOPPING)

        # If the right engine is not running, shutdown the spaceship
        if not self.left_engine_on:
            self.shutdown()

    def handle_lights_pressed(self):
        logger.debug("Spaceship Lights button pressed")

        if self.lights_on:
            self.lights_on = False
            self.play_sound(self.sounds.lights_off())
            self.arduino.lights_led_off()  # Turn off the lights led in the control panel
            self.arduino.lights_off()     # Turn off all the lights of the spaceship
        else:
            self.lights_on = True
            self.play_sound(self.sounds.lights_on())
            self.arduino.lights_led_on()  # Turn on the lights led in the control panel
            self.arduino.lights_on()      # Turn on all the lights of the spaceship

    def handle_lights_released(self):
        logger.debug("Spaceship Lights button released")
        self.event_count += 1
        # We don't do nothing on key release
        pass

    # Stops any movement (up and down)
    def stop_movement(self):
        self.move_up = False
        self.arduino.motor_stop()
        self.arduino.move_up_led_off()
        self.arduino.move_down_led_off()
        self.move_down = False

    def handle_up_pressed(self):
        logger.debug("Spaceship Up button pressed")

        if not self.spaceship_turned_on:
            self.play_sound(self.sounds.spaceship_turned_off())
            return

        # Store the current spaceship movement
        spaceship_moving = self.move_up

        # Stop the movement (if the spaceship is moving)
        self.stop_movement()

        # If the spaceship is not moving, start moving upward
        if not spaceship_moving:
            self.move_up = True
            self.play_sound(self.sounds.spaceship_up())
            self.arduino.move_up_led_on()
            self.arduino.motor_up()

    def handle_up_released(self):
        logger.debug("Spaceship Up button released")
        # We don't do nothing on key release
        self.event_count += 1
        pass

    def handle_down_pressed(self):
        logger.debug("Spaceship Down button pressed")

        if not self.spaceship_turned_on:
            self.play_sound(self.sounds.spaceship_turned_off())
            return

        # Store the current spaceship movement
        spaceship_moving = self.move_down

        # Stop the movement (if the spaceship is moving)
        self.stop_movement()

        # If the spaceship is not moving, start moving down
        if not spaceship_moving:
            self.move_down = True
            self.play_sound(self.sounds.spaceship_down())
            self.arduino.move_down_led_on()
            self.arduino.motor_down()

    def handle_down_released(self):
        logger.debug("Spaceship Down button released")
        # We don't do nothing on key release
        self.event_count += 1
        pass

    def shutdown(self):
        """
        Stops the spaceship: Turns off engines and 'On' status led
        """
        # If the engines are running stop them
        if self.left_engine_on or self.right_engine_on:
            self.play_sound(SND_ENGINE_STOPPING)
        self.stop_music()
        self.spaceship_flying = False
        self.left_engine_on = False
        self.arduino.stop_left_engine()
        self.right_engine_on = False
        self.arduino.stop_right_engine()
        pygame.time.set_timer(EVT_TIMER_OXYGEN, 0)
        pygame.time.set_timer(EVT_TIMER_FUEL, 0)


    def handle_user_event(self, event_type, data=0):
        logger.debug("Handling user event of type %d", event_type)
        self.event_count += 1
        user_event = pygame.event.Event(pygame.USEREVENT, user_event_type=event_type, data=data)
        pygame.event.post(user_event)

    @staticmethod
    def state(var):
        if not var:
            return "OFF"
        else:
            return "ON"

    def __str__(self):
        sep = os.linesep
        sep = "<br>"
        text = "Spaceship:"
        text += sep
        text += "Fuel: "
        text += str(self.fuel_level)
        text += sep
        text += "Oxygen: "
        text += str(self.oxygen_level)
        text += sep
        text += "LEDs:"
        text += sep
        text += "ON: "
        text += Spaceship.state(self.spaceship_turned_on)
        text += sep
        text += "LIGHTS: "
        text += Spaceship.state(self.lights_on)
        text += sep
        text += "SOUND: "
        text += Spaceship.state(self.sound_on)
        text += sep
        text += "UP: "
        text += Spaceship.state(self.move_up)
        text += sep
        text += "DOWN: "
        text += Spaceship.state(self.move_down)
        text += sep
        text += sep

        return text

# Create our glorious spaceship object
logger.debug("Creating spaceship")
spaceship = Spaceship()
logger.debug("Spaceship created")
logger.debug(spaceship)

# Assign our spaceship to the web interface
spaceship.web_interface.set(spaceship)

start = False
if start:
    spaceship.handle_user_event(Arduino.EVT_SC_ON_PRESSED)
    spaceship.handle_user_event(Arduino.EVT_SC_ON_RELEASED)
    spaceship.handle_user_event(Arduino.EVT_SC_LIGHTS_PRESSED)
    spaceship.handle_user_event(Arduino.EVT_SC_RIGHT_ENGINE_PRESSED)
    spaceship.handle_user_event(Arduino.EVT_SC_LIGHTS_RELEASED)
    spaceship.handle_user_event(Arduino.EVT_SC_LIGHTS_PRESSED)
    spaceship.handle_user_event(Arduino.EVT_SC_LIGHTS_RELEASED)

while 1:
    # check if there is a pending command
    for event in pygame.event.get():
        logger.debug("Received event %d, ", event.type)
        if event.type == EVT_MUSIC_END:
            print("Music playing completed")
        elif event.type == EVT_TIMER_FUEL:
            spaceship.handle_fuel_timer()
        elif event.type == EVT_TIMER_OXYGEN:
            spaceship.handle_oxygen_timer()
        elif event.type == EVT_TIMER_FILL_FUEL:
            spaceship.handle_fuel_filling_timer()
        elif event.type == EVT_TIMER_FILL_OXYGEN:
            spaceship.handle_oxygen_filling_timer()
        elif event.type == pygame.USEREVENT:
            logger.debug("Received USEREVENT, type %d, data = %d", event.user_event_type, event.data)
            if event.user_event_type in Arduino.events:
                handler = spaceship.handlers[event.user_event_type]
                handler()
            else:
                logger.debug("Ignoring unknown USEREVENT, type %d, data = %d", event.user_event_type, event.data)
        else:
            logger.debug("Ignoring unknown event %d, ", event.type)