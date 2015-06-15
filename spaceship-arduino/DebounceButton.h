#ifndef __DEBOUNCE_BUTTON_H_
#define __DEBOUNCE_BUTTON_H_

#include <Bounce2.h>

class DebounceButton: public Bounce
{
private:  
  int pin;
  int id;
  int debounceIntervalMs;
  Bounce debounce;
  
public:
  DebounceButton(int pin, int id, int debounceIntervalMs);
  bool update();
  bool rose();
  bool fell();
  int getId();
};

#endif //  __DEBOUNCE_BUTTON_H_
