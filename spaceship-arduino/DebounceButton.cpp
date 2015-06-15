#include "DebounceButton.h"
#include "Arduino.h"

/**
  Initialize the DebounceButton instance, including attachuing to the correct pin 
  and setting the debounce interval
*/

DebounceButton::DebounceButton(int pin, int id, int debounceIntervalMs) 
{
  this->pin = pin;
  this->id = id;
  this->debounceIntervalMs = debounceIntervalMs;
  this->debounce = debounce;
  pinMode(pin, INPUT_PULLUP);
  debounce.attach(pin);
  debounce.interval(debounceIntervalMs);   
}

/**
  Updates the debounce state.
  Retuns true if the button state has changed; flase otherwise.
  */
bool DebounceButton::update()
{
  return debounce.update();
}

/**
  Retuns true if the button was pressed; flase otherwise.
 */
bool DebounceButton::rose()
{
  return debounce.rose();
}

/**
  Retuns true if the button was released; flase otherwise.
 */
bool DebounceButton::fell()
{
  return debounce.fell();
}

/**
  Retuns the ID of this button
 */
int DebounceButton::getId()
{
  return id;
}


