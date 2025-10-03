#include <Arduino.h>
#include "Settings.h"
#include "DistanceSensors.h"
#include "DistanceCalibration.h" // Calibration functions

long distances[5] = {0, 0, 0, 0, 0};  // filtered distances

// Rolling buffer for filtering (5 sensors, last 5 samples each)
long rawReadings[5][5] = {0};
uint8_t rawIndex = 0; // circular buffer index

// Array of sensor pins
const uint8_t distPins[5] = {DistPin1, DistPin2, DistPin3, DistPin4, DistPin5};

// -------------------- Read raw distance --------------------
long readDistance(uint8_t pin) {
  uint32_t t = pulseIn(pin, HIGH, 300000); // µs timeout (0.3s)
  if (t == 0 || t > 20000) return -1;      // invalid reading
  long d = 4 * (long(t) - 1000);           // convert to mm
  if (d < 0) d = 0;
  return d;
}

// -------------------- Setup --------------------
void setupDist() {  
  for (int i = 0; i < 5; i++) {
    pinMode(distPins[i], INPUT);
    // Initialize buffer with first reading
    long raw = readDistance(distPins[i]);
    long corrected = correctDistance(i, raw);
    for (int j = 0; j < 5; j++) {
      rawReadings[i][j] = corrected;
    }
  }

  loadCalibration(); // Load coefficients from EEPROM
}

// -------------------- Trimmed mean filter --------------------
long trimmedMean(long *values, int n) {
  if (n <= 2) return values[0];

  long temp[n];
  for (int i = 0; i < n; i++) temp[i] = values[i];

  // Bubble sort
  for (int i = 0; i < n-1; i++) {
    for (int j = 0; j < n-i-1; j++) {
      if (temp[j] > temp[j+1]) {
        long swap = temp[j];
        temp[j] = temp[j+1];
        temp[j+1] = swap;
      }
    }
  }

  long sum = 0;
  for (int i = 1; i < n-1; i++) sum += temp[i]; // drop min & max
  return sum / (n-2);
}

// -------------------- Update distances --------------------
void updateDist() {
  for (int i = 0; i < 5; i++) {
    long raw = readDistance(distPins[i]);     // Read raw sensor
    long corrected = correctDistance(i, raw); // Apply calibration
    rawReadings[i][rawIndex] = corrected;     // Store in buffer
  }

  rawIndex = (rawIndex + 1) % 5; // advance circular buffer

  // Compute filtered distances
  for (int i = 0; i < 5; i++) {
    distances[i] = trimmedMean(rawReadings[i], 5);
  }

  // Debug output
  Serial.print("Distances: ");
  for (int i = 0; i < 5; i++) {
    Serial.print(distances[i]);
    if (i < 4) Serial.print(", ");
  }
  Serial.println();
}
