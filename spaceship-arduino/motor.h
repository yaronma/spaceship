#ifndef _MOTOR_H_
#define _MOTOR_H_

#define UP 0
#define DOWN 1

class Motor 
{
private:  
  int standby;
  int pwmB;
  int bIn1;
  int bIn2;
  int pwmA;
  int aIn1;
  int aIn2;
  
public:
  Motor(int standby, int pwmA, int aIn1, int aIn2, int pwmB, int bIn1, int bIn2); 
  
  /**
    Move specific motor at speed and direction
    motor: 0 for B 1 for A
    speed: 0 is off, and 255 is full speed
    direction: 0 clockwise, 1 counter-clockwise
   */
  void move(int motor, int direction);
  void stop(int motor);
  void stop();
//  void standby();
};

#endif // _MOTOR_H_
