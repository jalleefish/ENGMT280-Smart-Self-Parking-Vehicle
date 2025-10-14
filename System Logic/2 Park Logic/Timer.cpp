// Timer.cpp
#include <Arduino.h>
#include "Settings.h"
#include "DistanceSensors.h"
#include "MotorControl.h"
#include "ServoMotorControl.h"
#include "Communications.h"
#include "SystemLogic.h"
#include "Timer.h"

static bool timerRunning = false;
static unsigned long timerStartTime = 0;
unsigned long timerElapsed = 0;

void timerStart() {
    if (!timerRunning) {
        timerStartTime = millis();
        timerRunning = true;
    }
}

void timerStop() {
    if (timerRunning) {
        timerElapsed += millis() - timerStartTime;
        timerRunning = false;
    }
}

void timerReset() {
    timerRunning = false;
    timerStartTime = 0;
    timerElapsed = 0;
}

unsigned long timerGetElapsed() {
    if (timerRunning) {
        return timerElapsed + (millis() - timerStartTime);
    }
    return timerElapsed;
}

bool timerIsRunning() {
    return timerRunning;
}
