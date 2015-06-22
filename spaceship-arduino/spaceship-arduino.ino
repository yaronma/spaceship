#include <Bounce2.h>
#include <DualLedDisplay.h>
#include <LedControl.h>
#include "DebounceButton.h"
#include "motor.h"

//////////////////////////////////////////////////////////////
// Input Buttons - Definitions
//////////////////////////////////////////////////////////////
#define DEBOUNCE_INTERVAL_MS 5

//////////////////////////////////////////////////////////////
// Input Buttons - Pin Numbers
//////////////////////////////////////////////////////////////
#define OXYGEN_BUTTON       51
#define FUEL_BUTTON         52
#define LIGHTS_BUTTON       50
#define SPACESHIP_UP_BUTTON   49
#define SPACESHIP_DOWN_BUTTON 48
#define LEFT_ENGINE_BUTTON  47
#define RIGHT_ENGINE_BUTTON 46
#define SOUND_BUTTON        45
#define SPACESHIP_ON_BUTTON 53

//////////////////////////////////////////////////////////////
// Outputs - Pin Numbers
//////////////////////////////////////////////////////////////
#define OXYGEN_BUTTON_LED_ID 41
#define FUEL_BUTTON_LED_ID   43
#define LIGHTS_BUTTON_LED_ID 40
#define SPACESHIP_UP_BUTTON_LED_ID   39
#define SPACESHIP_DOWN_BUTTON_LED_ID 38
#define SPACESHIP_ON_BUTTON_LED_ID   42
#define SOUND_BUTTON_LED_ID  37
#define LEFT_ENGINE_ID       36
#define RIGHT_ENGINE_ID      35

//////////////////////////////////////////////////////////////
// We intentionally seperate the led id and the led pin in 
// order to be more indifferent to new/deletion of leds
//////////////////////////////////////////////////////////////
#define OXYGEN_BUTTON_LED 41
#define FUEL_BUTTON_LED   43
#define LIGHTS_BUTTON_LED 40
#define SPACESHIP_UP_BUTTON_LED   39
#define SPACESHIP_DOWN_BUTTON_LED 38
#define SPACESHIP_ON_BUTTON_LED   42
#define SOUND_BUTTON_LED  37
#define LEFT_ENGINE       36
#define RIGHT_ENGINE      35

// Protocol
#define FLAG 85 // Byte that marks the start of protocol packet (HEX 0x55)

boolean incoming = false;

// The input command data
byte buffer[3];

// The number of bytes we actually received
byte bufferDataSize = 0;

#define NUM_LEDS 7
byte ledIds[NUM_LEDS] = {OXYGEN_BUTTON_LED_ID, FUEL_BUTTON_LED_ID, LIGHTS_BUTTON_LED_ID, SPACESHIP_UP_BUTTON_LED_ID, 
  SPACESHIP_DOWN_BUTTON_LED_ID, SOUND_BUTTON_LED_ID, SPACESHIP_ON_BUTTON_LED_ID};

// Holds the corresponding led for the specific button; -1 for no corresponding led
byte ledPins[NUM_LEDS] = {OXYGEN_BUTTON_LED, FUEL_BUTTON_LED, LIGHTS_BUTTON_LED, SPACESHIP_UP_BUTTON_LED, 
  SPACESHIP_DOWN_BUTTON_LED, SOUND_BUTTON_LED, SPACESHIP_ON_BUTTON_LED};

//////////////////////////////////////////////////////////////
// Event IDs for buttons events
//////////////////////////////////////////////////////////////
#define EVT_SC_ON_PRESSED  49  // == '1'. To convert from ASCII, use EVT_yyy = int.from_bytes(b'1', 'big')
#define EVT_SC_ON_RELEASED  50  // '2'
#define EVT_SC_SOUND_PRESSED 51  // '3'
#define EVT_SC_SOUND_RELEASED  52
#define EVT_SC_FUEL_PRESSED  53
#define EVT_SC_FUEL_RELEASED  54
#define EVT_SC_OXYGEN_PRESSED  55
#define EVT_SC_OXYGEN_RELEASED  56
#define EVT_SC_LEFT_ENGINE_PRESSED  57
#define EVT_SC_LEFT_ENGINE_RELEASED  58
#define EVT_SC_RIGHT_ENGINE_PRESSED  59
#define EVT_SC_RIGHT_ENGINE_RELEASED  60
#define EVT_SC_LIGHTS_PRESSED  61
#define EVT_SC_LIGHTS_RELEASED  62
#define EVT_SC_UP_PRESSED  63
#define EVT_SC_UP_RELEASED  64
#define EVT_SC_DOWN_PRESSED  65
#define EVT_SC_DOWN_RELEASED  66

//////////////////////////////////////////////////////////////
// Input Buttons - Definitions 
// [For simplicity, we only handle push-buttons presses events,  
// we ignore push-buttons releases]
//////////////////////////////////////////////////////////////
DebounceButton oxygen(
, EVT_SC_OXYGEN_PRESSED, DEBOUNCE_INTERVAL_MS);
DebounceButton fuel(FUEL_BUTTON, EVT_SC_FUEL_PRESSED, DEBOUNCE_INTERVAL_MS);
DebounceButton lights(LIGHTS_BUTTON, EVT_SC_LIGHTS_PRESSED ,DEBOUNCE_INTERVAL_MS);
DebounceButton sound(SOUND_BUTTON, EVT_SC_SOUND_PRESSED, DEBOUNCE_INTERVAL_MS);
DebounceButton up(SPACESHIP_UP_BUTTON, EVT_SC_UP_PRESSED, DEBOUNCE_INTERVAL_MS);
DebounceButton down(SPACESHIP_DOWN_BUTTON, EVT_SC_DOWN_PRESSED, DEBOUNCE_INTERVAL_MS);
DebounceButton leftEngine(LEFT_ENGINE_BUTTON, EVT_SC_LEFT_ENGINE_PRESSED, DEBOUNCE_INTERVAL_MS);
DebounceButton rightEngine(RIGHT_ENGINE_BUTTON, EVT_SC_RIGHT_ENGINE_PRESSED, DEBOUNCE_INTERVAL_MS);
DebounceButton on(SPACESHIP_ON_BUTTON, EVT_SC_ON_PRESSED, DEBOUNCE_INTERVAL_MS);

#define NUM_BUTTONS 9
DebounceButton* buttons[NUM_BUTTONS] = {&on, &fuel, &oxygen, &lights, &sound, &up, &down, &leftEngine, &rightEngine};

DualLedDisplay ledDisplay(12,11,10);
Motor motors = Motor(2,3,4,5,6,7,8);

void setup() {

  // Setup the serial port for debugging
  Serial.begin(9600);
  Serial.println("Spaceship: Arduino controller srated!");

  Serial2.begin(57600);
  
  // Initialize the output leds
  for (int i = 0; i < NUM_LEDS; i++) {
    pinMode(ledPins[i], OUTPUT);
  }

  Serial.write("Self test started!\r\n");
  Serial.write("Testing bar graphs\n");
  testBarGraphs();
  Serial.write("Testing LEDs\n");
  testLeds();
  Serial.write("Self test completed\n\n");
}

// Update all the inputs
boolean updateAll() {
  boolean changed = false;  
  for (int i = 0; i < NUM_BUTTONS; i++) {
    changed |= buttons[i] -> update();
  }
  return changed;
}

void sendCommand(unsigned char code, unsigned char key, unsigned char value) {

  // For now just send the button id
  Serial2.write(key);
  Serial2.write(0);
  Serial2.write(0);
  
  Serial.write("Button ");
  Serial.write(key);
  Serial.write(" pressed\n");
}

// Called after each loop()
void serialEvent2() {
    while (Serial2.available()) {

      Serial.write("Reading new character\r\n");
      
      char ch = (char)Serial2.read();
      
      // If we received the flag, reset the input buffer
      if (ch == FLAG) {
        Serial.write("Received Frame Start\r\n");
        bufferDataSize = 0;
        incoming = false;
        continue;
      }
      
      // get the new byte:
      buffer[bufferDataSize] = ch; 
      bufferDataSize++;
 
      // Mark that we got a complete command         
      if (bufferDataSize == 3) {
         incoming = true;
         bufferDataSize = 0;
         break;
      } 
    }
  }

/**
  Changes the value of the bar graph
 */
void changeBarGraphValue(byte channel, byte value) {
        Serial.write("Setting Led channel ");
      Serial.write(channel);
      Serial.write(" to value ");
      Serial.write(value);
      Serial.write("\n");

  ledDisplay.setValue(channel, value);
}

/*
  Changes the motor state (up, down, stopped)
  'motor' Values:
  ---------------
     1 - left motor
     2 - right motor
     3 - both motors
     
  'action' Values:
  ----------------
     1 - move up
     2 - move down
     3 - stop
*/

// Motor Definitions
#define MOTOR_UP   1
#define MOTOR_DOWN 2
#define MOTOR_STOP 3

// Motor Selection
#define LEFT_MOTOR  1
#define RIGHT_MOTOR 2
#define BOTH_MOTORS 3

void changeMotoroState(byte motor, byte action) {
  switch(action) {
    case MOTOR_UP:
      if (motor == LEFT_MOTOR || motor == BOTH_MOTORS)
        motors.move(0, UP);
      if (motor == RIGHT_MOTOR || motor == BOTH_MOTORS)
        motors.move(1, UP);
    break;
    case MOTOR_DOWN:
      if (motor == LEFT_MOTOR || motor == BOTH_MOTORS)
        motors.move(0, DOWN);
      if (motor == RIGHT_MOTOR || motor == BOTH_MOTORS)
        motors.move(1, DOWN);
    break;
    case MOTOR_STOP:
      if (motor == LEFT_MOTOR || motor == BOTH_MOTORS)
        motors.stop(0);
      if (motor == RIGHT_MOTOR || motor == BOTH_MOTORS)
        motors.stop(1);
    break;
  }
}

/**
  Change arduino pin value.
  */
void changePinState(byte pin, byte state) {
  
  if (state == 0) {
    digitalWrite(pin, LOW);
  } else {
    digitalWrite(pin, HIGH);
  }
}

// Protocol: 
// ---------
// First byte is the command:
// 1 - CHANGE_PIN_STATE
// 2 - CHANGE_GAUGE_VALUE 
// For commands [1]: Second byte is the PIN number, thirt byte is the value (HIGH/LOW)
// For commands [2]: Second byte is the value

// Protocol Commands
#define CMD_BUTTON 1
#define CMD_CHANGE_PIN_STATE 97
#define CMD_CHANGE_BRG_VALUE 98
#define CMD_CHANGE_MOTOR_STATE 99

// Protocol Button Definitions
#define SPACESHIP_ON_BUTTON_PRESSED  49
#define SPACESHIP_ON_BUTTON_RELEASED 50

#define CMD_ROSE 1
#define CMD_FELL 2

int getPinNumber(int ledId) {
    for (int i = 0; i < NUM_LEDS; i++) {
      if (ledIds[i] == ledId) {
        return ledPins[i];
      }
   }
}

// Run a test on all components
void testBarGraphs() {
  ledDisplay.clear();
  delay(500);
  ledDisplay.allOn(0);
  delay(500);
  ledDisplay.allOn(1);
  delay(500);
  
  for (int i = 0; i <= 20; i++) {
    ledDisplay.setValue(0, i);
    ledDisplay.setValue(1, 20-i);
    delay(100);
  }
  
  delay(250);
  ledDisplay.setValue(1, 12);
  ledDisplay.setValue(0, 8);
  delay(1000);
  ledDisplay.clear();
}

// Ensure that all leds are working
void testLeds() {

  bool state = HIGH;
  for (int j =0; j < 4; j++) {
    for (int i = 0; i < NUM_LEDS; i++) {
      digitalWrite(ledPins[i], state);
    }
  
    state = ~state;

    delay(500);
  }
}

void loop() {
 
    //serialEvent();
  
    // First check if we have a pending command
    if (incoming == true) {
      
      // Prepare for the next command
      incoming = false;
      
      Serial.write("Parsing packet ");
      Serial.print(buffer[0], DEC);
      Serial.write(", ");
      Serial.print(buffer[1], DEC);
      Serial.write(", ");
      Serial.print(buffer[2], DEC);
      Serial.write("\n");
      
      // The command type is the first byte
      switch (buffer[0]) {
        case CMD_CHANGE_PIN_STATE:
          changePinState(getPinNumber(buffer[1]), buffer[2]);
          break;
        case CMD_CHANGE_BRG_VALUE:
          changeBarGraphValue(buffer[1], buffer[2]);
          break;
        case CMD_CHANGE_MOTOR_STATE:
          changeMotoroState(buffer[1], buffer[2]);
          break;
        default: 
          Serial.write("Unknown packet received ");
          break;
      }
    }
    
    // Check if any button was pressed 
    for (int i = 0; i < NUM_BUTTONS; i++) {
      // Check for button changes
      if (buttons[i] -> update() == false) {
        // There was no change, continue to the next button
        continue;
      }

      // Send the button change to the master
      if (buttons[i] -> rose()) {
        Serial.write("Button press detected\n");
        sendCommand(CMD_BUTTON, buttons[i]->getId(), CMD_ROSE);
      }      

      // For now we ignore key releases
      if (buttons[i] -> fell()) {
        Serial.write("Button release detected\n");
        // Do nothing...
        //sendCommand(CMD_BUTTON, buttons[i].getId(), CMD_FELL);
      }      
   }  
}

