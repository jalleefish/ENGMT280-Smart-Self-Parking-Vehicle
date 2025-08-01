// main.ino
// This file is the main entry point for the Self Parking Car project.
#include <Arduino.h>
#include "Settings.h"
#include "DistanceSensors.h"
#include "MotorControl.h"

void setup() {
    Serial.begin(115200);
    setupDist();
    setupMotor();
}

void loop() {
    updateDist();
    motorForward();  // test run
    delay(1000);
    motorStop();
    delay(100);  // Adjust delay as needed
}
