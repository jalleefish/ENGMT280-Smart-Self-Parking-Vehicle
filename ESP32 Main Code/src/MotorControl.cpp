//Motor.cpp
// This file contains the implementation of motor functionalities for the Self Parking Car project.
#include <Arduino.h>
#include "Settings.h"
#include "DistanceSensors.h"
#include "MotorControl.h"
#include "ServoMotorControl.h"
#include "Communications.h"
#include "SystemLogic.h"

void setupMotor() {
    pinMode(MotorDirection, OUTPUT);
    pinMode(MotorSpeed, OUTPUT);
    digitalWrite(MotorDirection, HIGH);
    digitalWrite(MotorSpeed, HIGH);
    Serial.println("Motor control pins initialized");
}

void motorForward() {
    digitalWrite(MotorDirection, HIGH);
    digitalWrite(MotorSpeed, HIGH);
    Serial.println("Motor moving forward");
}

void motorReverse() {
    digitalWrite(MotorDirection, LOW);
    digitalWrite(MotorSpeed, HIGH);
    Serial.println("Motor reversing");
}

void motorStop() {
    digitalWrite(MotorDirection, LOW);
    digitalWrite(MotorSpeed, LOW);
    Serial.println("Motor stopped");
}