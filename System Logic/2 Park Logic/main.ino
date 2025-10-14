// main.ino
// This file is the main entry point for the Self Parking Car project.
#include <Arduino.h>
#include "Settings.h"
#include "DistanceSensors.h"
#include "MotorControl.h"
#include "ServoMotorControl.h"
#include "Communications.h"
#include "SystemLogic.h"
#include "Timer.h"

void setup() {
    Serial.begin(115200);
    setupDist();
    setupMotor();
    setupServo();
    setupComms();
}

void loop() {
    updateDist();
    receiveComms();
    runSystemLogic();
    delay(30);
}
