
#include "Arduino.h"
#include "motor.h"

Motor::Motor(int standby, int pwmA, int aIn1, int aIn2, int pwmB, int bIn1, int bIn2) 
  {
    this->standbyPin = standbyPin;
    this->pwmA = pwmA;
    this->aIn1 = aIn1;
    this->aIn2 = aIn2;
    this->pwmB = pwmB;
    this->bIn1 = bIn1;
    this->bIn2 = bIn2;
    
    pinMode(standbyPin, OUTPUT);
    pinMode(pwmA, OUTPUT);
    pinMode(aIn1, OUTPUT);
    pinMode(aIn2, OUTPUT);
    pinMode(pwmB, OUTPUT);
    pinMode(bIn1, OUTPUT);
    pinMode(bIn2, OUTPUT);
  }
  
  /*
    Move specific motor at speed and direction
    motor: 0 for B 1 for A
    speed: 0 is off, and 255 is full speed
    direction: 0 clockwise, 1 counter-clockwise
   */
void Motor::move(int motor, int direction){

    digitalWrite(standbyPin, HIGH); //disable standby

    boolean inPin1 = LOW;
    boolean inPin2 = HIGH;

    if(direction == 1){
      inPin1 = HIGH;
      inPin2 = LOW;
    }

    if(motor == 1){
      digitalWrite(aIn1, inPin1);
      digitalWrite(aIn2, inPin2);
      analogWrite(pwmA, HIGH);
    } else {
      digitalWrite(bIn1, inPin1);
      digitalWrite(bIn2, inPin2);
      digitalWrite(pwmB, HIGH);
    }
}

void Motor::stop(int motor){
  if (motor == 1) {
    digitalWrite(pwmB, LOW);
  } else {
    digitalWrite(pwmA, LOW);
  }
}


void Motor::stop(){
  //enable standby  
  digitalWrite(standbyPin, LOW); 
}

