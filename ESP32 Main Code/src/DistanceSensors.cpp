// DsitanceSensors.cpp
// This file contains the implementation of distance sensor functionalities for the Self Parking Car project.
#include <Arduino.h>
#include "Settings.h"
#include "DistanceSensors.h"
#include "MotorControl.h"
#include "ServoMotorControl.h"
#include "Communications.h"
#include "SystemLogic.h"
#include <Arduino.h>

long distances[5] = {0, 0, 0, 0, 0};  // define the global array

void setupDist() {
  // Initialize distance sensor pins
  pinMode(DistPin1, INPUT);
  pinMode(DistPin2, INPUT);
  pinMode(DistPin3, INPUT);
  pinMode(DistPin4, INPUT);
  pinMode(DistPin5, INPUT);
}

long readDistance(uint8_t pin) {
  uint32_t t = pulseIn(pin, HIGH, 300000); // µs timeout
  if (t == 0 || t > 2000) return -1;     // no reading or out of range
  long d = 4 * (long(t) - 1000);         // convert to mm
  if (d < 0) d = 0;
  return d;
}

void updateDist() {
    distances[0] = readDistance(DistPin1) + 20;
    distances[1] = readDistance(DistPin2) + 35;
    distances[2] = readDistance(DistPin3) + 25;
    distances[3] = readDistance(DistPin4) + 15;
    distances[4] = readDistance(DistPin5) + 30;

    // Debugging output
    Serial.print("Distances: ");
    for (int i = 0; i < 5; i++) {
        Serial.print(distances[i]);
        if (i < 4) Serial.print(", ");

    }
    Serial.println();
}