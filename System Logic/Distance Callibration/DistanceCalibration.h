// DistanceCalibration.h
// Declarations for distance sensor functionalities
#pragma once
#include <Arduino.h>

// -------------------- Global variables --------------------
extern long distances[5];  // filtered distances array

// -------------------- Functions --------------------
long correctDistance(int sensorIndex, long raw);

// -------------------- Calibration functions --------------------
void loadCalibration();
void saveCalibration();
void calibrateRearSensors();
