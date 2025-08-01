// Settings.cpp
// This file contains the settings and configurations for the Self Parking Car project.
#include "Settings.h"
#include "DistanceSensors.h"

// Distance Sensor Pins
const uint8_t  DistPin1 = 19;  // sensor 1 OUT pin
const uint8_t  DistPin2 = 18;  // sensor 2 OUT pin
const uint8_t  DistPin3 = 17;  // sensor 3 OUT pin
const uint8_t  DistPin4 = 16;  // sensor 4 OUT pin
const uint8_t  DistPin5 = 4;  // sensor 5 OUT pin

// Motor Pins
const int  MotorPin1 = 32;  // motor 1 control pin
const int  MotorPin2 = 33;  // motor 2 control pin