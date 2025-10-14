// Communications.h
// This file contains the declarations for communications functionalities for the Self Parking Car project.
#pragma once
#include <Arduino.h>

//Outputs
extern String sender;
extern int firstTarget;
extern int secondTarget;

//Functions
void setupComms();          // Setup communications
void sendComms();           // Send communications data
void receiveComms();        // Receive communications data