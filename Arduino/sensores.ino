//This script contains sensor stuff to the Arduino UNO controller

#include <Servo.h>

bool isAble = false;
int trig = 11, echo = 12, time, distance = 0, var = 0;

Servo myServo;

void treintaA180() {
  for (int pos = 30 ; pos <= 130 ; pos += 20) {
    myServo.write(pos);
    delay(500);
  }
}

void rotate() {
  myServo.write(90);
  delay(1000);
  treintaA180();
  delay(1000);
  myServo.write(90);
  isAble = true;
}

void setup(){
  myServo.attach(9);
  //Input Definition
  pinMode(1, INPUT);
  pinMode(7, INPUT);
  pinMode(10, INPUT);
  pinMode(12, INPUT);
  pinMode(13, INPUT);

  //Output Definition
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(A5, OUTPUT);

  isAble = true;

  //init serial communication

  Serial.begin(9600);
  myServo.write(90);

}

void loop(){
  //Infrared
  if(!digitalRead(10)) analogWrite(A5, 255);
  else analogWrite(A5, 0);

  if(digitalRead(13)) digitalWrite(8, true);
  else digitalWrite(8, false);

  //Servo
  if(digitalRead(7) && isAble){
    isAble = false;
    rotate();
  }

  Serial.println(digitalRead(7));

  //Distance
  digitalWrite(trig, HIGH);
  digitalWrite(trig, LOW);
  time = pulseIn(echo, HIGH);
  distance = time / 58.2;
  delay(100);

  if (distance <= 20 && distance > 0) digitalWrite(2, true);
  else digitalWrite(2, false);

  if (distance <= 40 && distance > 20) digitalWrite(3, true); else digitalWrite(3, false);

  if (distance <= 100 && distance > 40) digitalWrite(4, true);
  else digitalWrite(4, false);


  if (distance <= 160 && distance > 100) digitalWrite(5, true);
   else digitalWrite(5, false);

  if (distance > 160) digitalWrite(6, true);
  else digitalWrite(6, false);
}