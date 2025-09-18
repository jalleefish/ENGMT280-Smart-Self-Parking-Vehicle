// DsitanceSensors.cpp
// This file contains the implementation of distance sensor functionalities for the Self Parking Car project.
#include "Settings.h"
#include "DistanceSensors.h"
#include <Arduino.h>

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
  long d1 = readDistance(DistPin1);
  long d2 = readDistance(DistPin2);
  long d3 = readDistance(DistPin3);
  long d4 = readDistance(DistPin4);
  long d5 = readDistance(DistPin5);

  Serial.println("Distances (mm): ");
  if (d1 < 0) Serial.println("d1: NR"); else Serial.println("d1: " + String(d1));
  if (d2 < 0) Serial.println("d2: NR"); else Serial.println("d2: " + String(d2));
  if (d3 < 0) Serial.println("d3: NR"); else Serial.println("d3: " + String(d3));
  if (d4 < 0) Serial.println("d4: NR"); else Serial.println("d4: " + String(d4));
  if (d5 < 0) Serial.println("d5: NR"); else Serial.println("d5: " + String(d5));
}