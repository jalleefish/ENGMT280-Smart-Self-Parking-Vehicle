// Settings.h
// This file contains the settings and configurations for the Self Parking Car project.
#pragma once
#include <Arduino.h>

// Distance Sensor Pins
extern const uint8_t  DistPin1;  // sensor 1 OUT pin
extern const uint8_t  DistPin2;  // sensor 2 OUT pin
extern const uint8_t  DistPin3;  // sensor 3 OUT pin
extern const uint8_t  DistPin4;  // sensor 4 OUT pin
extern const uint8_t  DistPin5;  // sensor 5 OUT pin

// Motor Pins
extern const int  MotorPin1;  // motor 1 control pin
extern const int  MotorPin2;  // motor 2 control pin

// Servo Motor Pins
extern const int  ServoPin;  // servo motor 1 control pin

// Wi-Fi Credentials
extern const char* ssid;        // Enter SSID here
extern const char* password;    //Enter Password here
extern const char* host;        // your laptop's IP
extern const int port;          // server port