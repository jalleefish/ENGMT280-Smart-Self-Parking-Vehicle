// main.ino
// This file is the main entry point for the Self Parking Car project.
#include <Arduino.h>
#include "Settings.h"
#include "DistanceSensors.h"
#include "MotorControl.h"
#include "ServoMotorControl.h"
#include "Communications.h"
#include "SystemLogic.h"

void setup() {
    Serial.begin(115200);
    setupDist();
    setupMotor();
    setupServo();
    setupComms();
}

void loop() {
    updateDist();
    sendComms();
    receiveComms();
    // servoMiddle();
    // motorForward();
    // delay(1000);
    // // servoLeft();
    // motorReverse();
    // delay(1000);
    // // servoRight();
    // motorStop();
    delay(200);
}
