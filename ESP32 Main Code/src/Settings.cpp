// Settings.cpp
// This file contains the settings and configurations for the Self Parking Car project.
#include "Settings.h"
#include "DistanceSensors.h"
#include "MotorControl.h"
#include "ServoMotorControl.h"

// Distance Sensor Pins
const uint8_t  DistPin1 = 4;  // sensor 1 OUT pin
const uint8_t  DistPin2 = 16;  // sensor 2 OUT pin
const uint8_t  DistPin3 = 17;  // sensor 3 OUT pin
const uint8_t  DistPin4 = 32;  // sensor 4 OUT pin
const uint8_t  DistPin5 = 33;  // sensor 5 OUT pin

// Motor Pins
const int  MotorPin1 = 18;  // motor 1 control pin
const int  MotorPin2 = 19;  // motor 2 control pin

// Servo Motor Pins
const int  ServoPin = 2;  // servo motor 1 control pin

// Replace with your network credentials
const char* ssid = "JOELS-LAPTOP";  // Enter SSID here
const char* password = "28075851";  //Enter Password here
const char* host = "192.168.137.1";  // your laptop's IP
const int port = 5000;