// ServoMotorControl.cpp
// This file contains the implementation of servo motor functionalities for the Self Parking Car project.
#include "ServoMotorControl.h"
#include "Settings.h"
#include <Arduino.h>
#include <ESP32Servo.h>

Servo myServo;

void setupServo() {
    myServo.attach(ServoPin);
    myServo.write(0);  // Move to 0 degrees
    delay(1000);
    Serial.println("Servo motor initialized");
}

void servoLeft() {
    myServo.write(-90);   // Min angle
    delay(1000);
    Serial.println("Servo moved to left position");
}

void servoRight() {
    myServo.write(90); // Max angle
    delay(1000);
    Serial.println("Servo moved to right position");
}

void servoMiddle() {
    myServo.write(0);  // Middle position
    delay(1000);
    Serial.println("Servo moved to middle position");
}