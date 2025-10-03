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

// DistanceSensors.cpp
// This file contains the implementation of distance sensor functionalities for the Self Parking Car project.
// #include <Arduino.h>
// #include "Settings.h"
// #include "DistanceSensors.h"
// #include "MotorControl.h"
// #include "ServoMotorControl.h"
// #include "Communications.h"
// #include "SystemLogic.h"

// long distances[5] = {0, 0, 0, 0, 0};  // global filtered distances

// // Raw readings for each sensor (for filtering)
// long rawReadings[5][5];  // 5 sensors, store last 5 samples
// uint8_t rawIndex = 0;    // circular buffer index

// void setupDist() {
//   // Initialize distance sensor pins
//   pinMode(DistPin1, INPUT);
//   pinMode(DistPin2, INPUT);
//   pinMode(DistPin3, INPUT);
//   pinMode(DistPin4, INPUT);
//   pinMode(DistPin5, INPUT);
// }

// long readDistance(uint8_t pin) {
//   uint32_t t = pulseIn(pin, HIGH, 300000); // µs timeout (0.3s)
//   if (t == 0 || t > 20000) return -1;      // invalid or too far (> ~3m)
//   long d = 4 * (long(t) - 1000);           // convert to mm
//   if (d < 0) d = 0;
//   return d;
// }

// // Helper: trimmed mean filter (drop min & max, average rest)
// long trimmedMean(long *values, int n) {
//   if (n <= 2) return values[0];  // fallback if not enough values

//   // Copy to temp for sorting
//   long temp[n];
//   for (int i = 0; i < n; i++) temp[i] = values[i];

//   // Simple bubble sort (small n, so fine)
//   for (int i = 0; i < n-1; i++) {
//     for (int j = 0; j < n-i-1; j++) {
//       if (temp[j] > temp[j+1]) {
//         long swap = temp[j];
//         temp[j] = temp[j+1];
//         temp[j+1] = swap;
//       }
//     }
//   }

//   // Drop extremes and average middle values
//   long sum = 0;
//   for (int i = 1; i < n-1; i++) {
//     sum += temp[i];
//   }
//   return sum / (n-2);
// }

// void updateDist() {
//   // Read and store new values in rolling buffer
//   rawReadings[0][rawIndex] = readDistance(DistPin1) + 20;
//   rawReadings[1][rawIndex] = readDistance(DistPin2) + 35;
//   rawReadings[2][rawIndex] = readDistance(DistPin3) + 25;
//   rawReadings[3][rawIndex] = readDistance(DistPin4) + 15;
//   rawReadings[4][rawIndex] = readDistance(DistPin5) + 30;

//   // Move buffer index
//   rawIndex = (rawIndex + 1) % 5;

//   // Compute filtered value for each sensor
//   for (int i = 0; i < 5; i++) {
//     distances[i] = trimmedMean(rawReadings[i], 5);
//   }

//   // Debugging output
//   Serial.print("Filtered Distances: ");
//   for (int i = 0; i < 5; i++) {
//     Serial.print(distances[i]);
//     if (i < 4) Serial.print(", ");
//   }
//   Serial.println();
// }
