//Motor.cpp
// This file contains the implementation of motor functionalities for the Self Parking Car project.
#include "MotorControl.h"
#include "Settings.h"
#include <Arduino.h>

void setupMotor() {
    pinMode(MotorPin1, OUTPUT);
    pinMode(MotorPin2, OUTPUT);
    digitalWrite(MotorPin1, LOW);
    digitalWrite(MotorPin2, LOW);
    Serial.println("Motor control pins initialized");
}

void motorForward() {
    digitalWrite(MotorPin1, HIGH);
    digitalWrite(MotorPin2, LOW);
    Serial.println("Motor moving forward");
}

void motorReverse() {
    digitalWrite(MotorPin1, LOW);
    digitalWrite(MotorPin2, HIGH);
    Serial.println("Motor reversing");
}

void motorStop() {
    digitalWrite(MotorPin1, LOW);
    digitalWrite(MotorPin2, LOW);
    Serial.println("Motor stopped");
}