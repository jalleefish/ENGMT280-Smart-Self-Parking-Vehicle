// DistanceCalibration.cpp
// Handles calibration for rear sensors only

#include <Arduino.h>
#include <EEPROM.h>
#include "DistanceCalibration.h"
#include "DistanceSensors.h"
#include "Settings.h"

// -------------------- Configuration --------------------
struct PolyCoeffs {
  float a0 = 0;
  float a1 = 1;
  float a2 = 0;
};

PolyCoeffs coeffs[5];       // one set per sensor
const int EEPROM_ADDR = 0;  // EEPROM starting address

// -------------------- Save/Load --------------------
void saveCalibration() {
  EEPROM.put(EEPROM_ADDR, coeffs);
  Serial.println("Calibration saved to EEPROM");
}

void loadCalibration() {
  EEPROM.get(EEPROM_ADDR, coeffs);
  Serial.println("Calibration loaded from EEPROM");
}

// -------------------- Apply polynomial correction --------------------
long correctDistance(int sensorIndex, long raw) {
  if (raw < 0) return -1;
  float r = (float)raw;
  float d = coeffs[sensorIndex].a0 +
            coeffs[sensorIndex].a1 * r +
            coeffs[sensorIndex].a2 * r * r;
  if (d < 0) d = 0;
  return (long)d;
}

// -------------------- Calibration routine --------------------
// Rear sensors 3 & 4: dynamic over 1000mm at 20mm/s
void calibrateRearSensors() {
  Serial.println("Starting dynamic rear sensor calibration...");

  int rearSensors[2] = {3, 4};
  const float carSpeed = 20.0;      // mm/s
  const long distance = 1000;       // mm
  const unsigned long duration = (unsigned long)(distance / carSpeed * 1000); // ms

  unsigned long startTime = millis();
  unsigned long endTime = startTime + duration;

  // Record raw readings during movement
  long sumRaw[2] = {0, 0};
  int samples = 0;

  while (millis() < endTime) {
    for (int i = 0; i < 2; i++) {
      long raw = distances[rearSensors[i]]; // use the filtered distances array
      if (raw > 0) sumRaw[i] += raw;
    }
    samples++;
    delay(50); // sample every 50ms
  }

  // Compute average and set calibration coefficients
  for (int i = 0; i < 2; i++) {
    long avgRaw = (samples > 0) ? sumRaw[i] / samples : 1;
    coeffs[rearSensors[i]].a0 = 0;
    coeffs[rearSensors[i]].a1 = (float)distance / (float)avgRaw; // scale to 1000mm
    coeffs[rearSensors[i]].a2 = 0;
    Serial.print("Rear sensor ");
    Serial.print(rearSensors[i]);
    Serial.print(" a1: ");
    Serial.println(coeffs[rearSensors[i]].a1);
  }

  saveCalibration();
  Serial.println("Rear sensor calibration complete!");
}
