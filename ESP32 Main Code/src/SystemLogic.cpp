// SystemLogic.cpp
// This file contains the implementation of system logic functionalities for the Self Parking Car project.
#include <Arduino.h>
#include "Settings.h"
#include "DistanceSensors.h"
#include "MotorControl.h"
#include "ServoMotorControl.h"
#include "Communications.h"
#include "SystemLogic.h"
#include "Timer.h"

// ---------- GLOBAL CONSTANTS ----------
const int MAX_ANGLE        = 23;     // max steering angle (deg)
const int PARK_DIST        = 30;     // stop distance inside bay (mm)
const int DIST_FROM_TARGET = 50;    // distance past bay before reversing (mm)
const int REVERSE_ANGLE      = 98 - MAX_ANGLE;
const int FORWARD_ANGLE      = 98 + MAX_ANGLE;
const int STRAIGHT_ANGLE     = 98;
const int REVERSE_TARGET_POS = 50;
const int FORWARD_TARGET_POS = 5;
const int  parkSpacing   = 120;
const int  dist2start    = 410;

// ---------- STATE FLAGS ----------
bool runLoop      = true;
bool firstPark    = true;
bool secondPark   = false;
bool reversing    = false;
bool parking      = false;
bool leavePark    = false;
bool colourScan   = true;
bool reversingTurn  = false;
bool pullingForward = false;
bool finalReverse   = false;

// ---------- OUTPUTS ----------
int  motorCmd     = 0;
int  turnAngle    = 0;
int  carPos       = 0;
int  targetCount  = 0;

// ---------- HELPER: keep straight ----------
void straightCorrection() {
    if (parking || leavePark) return;
    long dS = distances[2];

    if (dS < 0) return;                   // ignore if no side wall
    if (dS > (115))      turnAngle += 1;  // steer toward wall if too far
    else if (dS < (105)) turnAngle -= 1;  // steer away if too close
    else                 turnAngle  = 0;

    if (abs(turnAngle) > MAX_ANGLE)
        turnAngle = (turnAngle > 0) ? MAX_ANGLE : -MAX_ANGLE;
    steering(98 + turnAngle);
}

// void rearStraightCorrection(){
//     long dR = distances[3];
//     long dL = distances[4];

//     if(dR<0 || dL<0) return; // ignore if invalid reading
//         int diff = dR - dL;
//     if(diff > 5){
//         turnAngle += 1; // steer toward closer wall
//     } else if (diff < -5){
//         turnAngle -= 1; // steer toward closer wall
//     } else {
//         turnAngle = 0; // keep straight
//     }
//     if (abs(turnAngle) > MAX_ANGLE) {
//         turnAngle = (turnAngle > 0) ? MAX_ANGLE : -MAX_ANGLE;
//     }
//     steering(98 + turnAngle);
// }

bool carParallel() {
    long dR = distances[3];
    long dL = distances[4];
    if (dR < 0 || dL < 0) return false; // invalid reading → not parallel
    int diff = dR - dL;
    return (abs(diff) < 3); // true if within 5mm
    // return (distances[3] == distances[4]);
}

// ---------- FIRST PARK ----------
void firstParkLogic() {
    if (firstTarget == -1) return;
    colourScan = false;
    parking = true;
    int targetPos = dist2start + firstTarget * parkSpacing;
    int backAverage = (distances[3] + distances[4]) / 2;
    carPos = backAverage + 105;

    // Turn forward for 2s
    if (!pullingForward && (carPos > targetPos)) {
        steering(FORWARD_ANGLE);
        delay(6500);
        pullingForward = true;
    }

    // --- 2. switch to forward pull after arc ---
    if (pullingForward && !reversingTurn && !carParallel()) {
        motorReverse();
        steering(REVERSE_ANGLE);
        delay(10000);
        reversingTurn  = true;
    }

    // --- 3. pull forward then final straight reverse ---
    if (pullingForward && reversingTurn && !finalReverse && carParallel()) {
        finalReverse   = true;
        steering(STRAIGHT_ANGLE);
        // rearStraightCorrection();
    }

    if (finalReverse && backAverage < 30) {
        motorStop();
        reversing     = false;
        parking       = false;
        leavePark     = true;
        firstPark     = false;
        secondPark    = true;   // move to second stage
        delay(500);
        motorForward();
    }
}

// ---------- MAIN LOOP ----------
void runSystemLogic() {
    straightCorrection();
    // if (finalReverse) rearStraightCorrection();

    if (firstPark)       
        firstParkLogic();
    // else if (secondPark) 
        // secondParkLogic();
    
    sender = "distances:" + 
             String(distances[0]) + "," +
             String(distances[1]) + "," +
             String(distances[2]) + "," +
             String(distances[3]) + "," +
             String(distances[4]);
    sendComms();

    if (colourScan) {
        sender = "colourScan:0";
        sendComms();
    } else {
        sender = "noScan:0";
        sendComms();
    }
}

