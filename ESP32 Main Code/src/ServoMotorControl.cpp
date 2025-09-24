// ServoMotorControl.cpp
// This file contains the implementation of servo motor functionalities for the Self Parking Car project.
#include <Arduino.h>
#include "Settings.h"
#include "DistanceSensors.h"
#include "MotorControl.h"
#include "ServoMotorControl.h"
#include "Communications.h"
#include "SystemLogic.h"
#include <ESP32Servo.h>

Servo myServo;

void setupServo() {
	// Allow allocation of all timers
	ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
	myServo.setPeriodHertz(50);    // standard 50 hz servo
	myServo.attach(ServoPin, 500, 2400); // attaches the servo on pin 18 to the servo object
	// using default min/max of 1000us and 2000us
	// different servos may require different min/max settings
	// for an accurate 0 to 180 sweep
    myServo.write(90);  // Move to 0 degrees
    Serial.println("Servo motor initialized");
    delay(15);        // wait for a second
}

void servoLeft() {
    myServo.write(70);   // Min angle
    Serial.println("Servo moved to left position");
    delay(15);
}

void servoRight() {
    myServo.write(110); // Max angle
    Serial.println("Servo moved to right position");
    delay(15);
}

void servoMiddle() {
    myServo.write(90);  // Middle position
    Serial.println("Servo moved to middle position");
    delay(15);
}