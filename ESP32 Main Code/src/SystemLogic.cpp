// SystemLogic.cpp
// This file contains the implementation of system logic functionalities for the Self Parking Car project.
#include <Arduino.h>
#include "Settings.h"
#include "DistanceSensors.h"
#include "MotorControl.h"
#include "ServoMotorControl.h"
#include "Communications.h"
#include "SystemLogic.h"

// Limits for parking and steering
const int MAX_ANGLE = 25;            // max steering angle (deg)
const int PARK_DIST = 30;            // stop distance inside bay (mm)
const int DIST_FROM_TARGET = 200;  // distance past bay before reversing (mm)

/******** STATE ********/
// Core state flags and counters
bool runLoop   = true;    // master run flag
bool firstPark = true;    // true until first parking complete
bool secondPark= false;   // true if second park required
bool reversing = false;   // true while reversing
bool parking   = false;   // true during a parking manoeuvre
int  targetCount = 0;     // number of detected target bays
int  targetPos[2] = {0,0}; // recorded odometer positions of targets
bool colourScan = true;   // true to perform colour scan

// Outputs
int motorCmd = 0;         // motor command: -1 reverse, 0 stop, 1 forward
int turnAngle = 0;        // steering angle (deg)

/******** LOGIC ********/
// Adjust steering to keep straight using left/right wall sensors
void straightCorrection(){
  long dR = distances[3];
  long dL = distances[4];
  if(dR<0 || dL<0) return; // ignore if invalid reading
  int diff = dR - dL;
  if(abs(diff)>10){
    turnAngle = (diff>0) ? 10 : -10; // steer toward closer wall
  } else {
    turnAngle = 0; // keep straight
  }
  steering(98+turnAngle);
}

// Emergency stop if any sensor detects obstacle too close
// void checkEmergency(){
//   for(int i=0;i<5;i++){
//     if(distances[i] != -1 && distances[i] < 10){
//       motorStop();
//       runLoop = false;
//     }
//   }
// }

// First parking manoeuvre
void firstParkLogic(){
    if(targetCount<1) return; // no bay recorded yet

    // Trigger reverse when past target bay
    if(!reversing && ((distances[3]+distances[4])/2 - targetPos[0]) > DIST_FROM_TARGET){
        reversing = true; parking=true;
        motorReverse(); steering(98+MAX_ANGLE);
    }

    // While reversing, stop once inside bay
    if(parking && reversing){
        colourScan = false;
        long rearAvg = (distances[3]+distances[4])/2;
        if(rearAvg != -1 && rearAvg <= PARK_DIST){
        motorStop();
        reversing=false; parking=false;
        firstPark=false; secondPark=true; // move to second stage
        }
    if (!reversing && !steering){
        colourScan = true;
    }
  }
}

// Second parking manoeuvre (if required)
void secondParkLogic(){
    colourScan = true;
    if(targetCount<2) return; // no second bay recorded yet
    if(!reversing && ((distances[3]+distances[4])/2 - targetPos[1]) > DIST_FROM_TARGET){
        reversing=true; parking=true;
        motorReverse(); steering(98+MAX_ANGLE);
    }
    if(parking && reversing){
        long rearAvg = (distances[3]+distances[4])/2;
        if(rearAvg != -1 && rearAvg <= PARK_DIST){
        motorStop();
        runLoop=false; // finished after second park
        }
    }
}

void saveDistance() {
    long pos = (distances[3] + distances[4]) / 2;
    if (targetPos[0] == 0) {
        targetPos[0] = pos;
        Serial.println("First target saved at position: " + String(pos));
    } else if ((targetPos[1] == 0) && (pos > targetPos[0] + 50)) {
        targetPos[1] = pos;
        Serial.println("Second target saved at position: " + String(pos));
    } else if (targetPos[1] != 0) {
        Serial.println("Two targets already saved");
    }
}
// Arduino loop function: main control flow
void runSystemLogic(){
//   checkEmergency();
  if(firstPark) firstParkLogic();
  else if(secondPark) secondParkLogic();
  else motorStop(); // finished all tasks
  straightCorrection();
  if (colourScan == true) {
      sender = "colourScan";
      sendComms();
  }
  if (colourScan == false) {
      sender = "noScan";
      sendComms();
  }
}