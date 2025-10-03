// SystemLogic.cpp
// This file contains the implementation of system logic functionalities for the Self Parking Car project.
#include <Arduino.h>
#include "Settings.h"
#include "DistanceSensors.h"
#include "MotorControl.h"
#include "ServoMotorControl.h"
#include "Communications.h"
#include "SystemLogic.h"

// ---------- GLOBAL CONSTANTS ----------
const int MAX_ANGLE        = 25;     // max steering angle (deg)
const int PARK_DIST        = 30;     // stop distance inside bay (mm)
const int DIST_FROM_TARGET = 50;    // distance past bay before reversing (mm)

int  parkSpacing   = 150;
int  dist2start    = 425;

// ---------- STATE FLAGS ----------
bool runLoop      = true;
bool firstPark    = true;
bool secondPark   = false;
bool reversing    = false;
bool parking      = false;
bool steeringBool = false;
bool leavePark    = false;
bool colourScan   = true;

int  targetCount  = 0;
int  timer        = 0;

// ---------- OUTPUTS ----------
int  motorCmd     = 0;
int  turnAngle    = 0;

// ---------- HELPER: keep straight ----------
void straightCorrection() {
    if (steeringBool || parking) return;

    long dS = distances[2];
    long dR = distances[3];
    long dL = distances[4];

    if (((dL + dR) / 2) < 50) return;
    leavePark = false;

    if (dS < 0) return;                    // ignore if no side wall
    if (dS > (115))      turnAngle += 1;  // steer toward wall if too far
    else if (dS < (105)) turnAngle -= 1;  // steer away if too close
    else                     turnAngle  = 0;

    if (abs(turnAngle) > MAX_ANGLE)
        turnAngle = (turnAngle > 0) ? MAX_ANGLE : -MAX_ANGLE;

    steering(98 + turnAngle);
}

// ---------- PARKING CONSTANTS ----------
const int REVERSE_ANGLE      = 98 - MAX_ANGLE;
const int FORWARD_ANGLE      = 98 + MAX_ANGLE;
const int STRAIGHT_ANGLE     = 98;
const int REVERSE_TARGET_POS = 50;
const int FORWARD_TARGET_POS = 5;

// ---------- FIRST PARK ----------
void firstParkLogic() {
    if (firstTarget == -1) return;
    parking = true;

    static bool reversingTurn  = false;
    static bool pullingForward = false;
    static bool finalReverse   = false;

    int targetPos = dist2start + firstTarget * parkSpacing;
    int carPos    = (distances[3] + distances[4]) / 2;
    straightCorrection();

    // --- 1. trigger first reverse turn ---
    if (!reversingTurn && abs(carPos - targetPos - DIST_FROM_TARGET) < 15) {
        reversingTurn = false;
        pullingForward = true;
        motorForward();
        steering(FORWARD_ANGLE);
        return;
    }

    // --- 2. switch to forward pull after arc ---
    if (reversingTurn && carPos <= targetPos - REVERSE_TARGET_POS) {
        reversingTurn  = true;
        pullingForward = false;
        motorReverse();
        steering(REVERSE_ANGLE);
        return;
    }

    // --- 3. pull forward then final straight reverse ---
    if (pullingForward && carPos >= targetPos - FORWARD_TARGET_POS) {
        pullingForward = false;
        finalReverse   = true;
        motorReverse();
        steering(STRAIGHT_ANGLE);
        return;
    }

    // // --- 4. final straight reverse ---
    // if (finalReverse) {
    //     if (carPos <= targetPos - PARK_DIST) {
    //         motorStop();
    //         parking      = false;
    //         finalReverse = false;
    //     }

    //     // extra logic for keeping straight during reverse
    //     if (parking && reversing && steeringBool) {
    //         int dR = distances[3];
    //         int dL = distances[4];

    //         if (dR < 0 || dL < 0) return; // invalid reading

    //         timer++;
    //         if (timer > 150) {
    //             if (abs(distances[4] - distances[3]) < 10) {
    //                 steeringBool = false;
    //                 timer        = 0;
    //                 steering(98);
    //             }
    //         }
    //     }

    //     colourScan = false;
    //     long rearAvg = (distances[3] + distances[4]) / 2;
    //     if (rearAvg != -1 && rearAvg <= PARK_DIST) {
    //         motorStop();
    //         reversing     = false;
    //         parking       = false;
    //         steeringBool  = false;
    //         leavePark     = true;
    //         firstPark     = false;
    //         secondPark    = true;   // move to second stage
    //         delay(500);
    //         motorForward();
    //     }
    // }

    // if (!reversing && !steeringBool)
    //     colourScan = true;
}   // <<< fixed: properly closes firstParkLogic() >>>


// ---------- SECOND PARK ----------
const int PULL_OUT_DIST = 150;  // distance to pull out of first park

void secondParkLogic() {
    if (!reversing && !steeringBool)
        colourScan = true;                 // keep scanning until move

    if (secondTarget == -1) return;        // nothing yet

    colourScan = false;
    parking    = true;

    int targetPos = dist2start + secondTarget * parkSpacing;
    int carPos    = (distances[3] + distances[4]) / 2;

    static bool pullingOut      = false;
    static bool reversingTurn   = false;
    static bool pullingForward  = false;
    static bool finalReverse    = false;
    static bool finished        = false;

    // 1. drive straight out of first bay
    if (!pullingOut && !reversingTurn && !pullingForward && !finalReverse && !finished) {
        pullingOut = true;
        motorForward();
        steering(STRAIGHT_ANGLE);
        return;
    }

    if (pullingOut && carPos >= PULL_OUT_DIST) {
        pullingOut    = false;
        reversingTurn = true;
        motorReverse();
        steering(REVERSE_ANGLE);
        return;
    }

    // 2. reverse turning arc into 2nd bay
    if (reversingTurn && carPos <= targetPos - REVERSE_TARGET_POS) {
        reversingTurn  = false;
        pullingForward = true;
        motorForward();
        steering(FORWARD_ANGLE);
        return;
    }

    // 3. forward turning arc
    if (pullingForward && carPos >= targetPos - FORWARD_TARGET_POS) {
        pullingForward = false;
        finalReverse   = true;
        motorReverse();
        steering(STRAIGHT_ANGLE);
        return;
    }

    // 4. final straight reverse
    if (finalReverse) {
        if (carPos <= targetPos - PARK_DIST) {
            motorStop();
            finalReverse = false;
            finished     = true;
            runLoop      = false;      // all done
        }
    }
}


// ---------- MAIN LOOP ----------
void runSystemLogic() {
    if (steeringBool)
        steering(98 - MAX_ANGLE);

    if (firstPark)       
        firstParkLogic();
    else if (secondPark) 
        secondParkLogic();
    else                 
        motorStop();
    if (!parking && !steeringBool){
    straightCorrection();
    }
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

