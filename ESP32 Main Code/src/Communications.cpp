// Communications.cpp
// This file contains the implementation of communications functionalities for the Self Parking Car project.
#include <Arduino.h>
#include "Settings.h"
#include "DistanceSensors.h"
#include "MotorControl.h"
#include "ServoMotorControl.h"
#include "Communications.h"
#include "SystemLogic.h"
#include <WiFi.h>

WiFiClient client;

String sender = "";

void setupComms() {
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }
    Serial.println("\nConnected! IP: " + WiFi.localIP().toString());
}

void sendComms() {
    if (!client.connected()) {
      Serial.println("Connecting to server...");
      if (!client.connect(host, port)) {
        delay(1000);
        return;
      }
      Serial.println("Connected!");
  }

    client.print(sender + "\n");
    Serial.println("Sent: " + sender);
    sender = "";
}

void receiveComms() {
    if (client.connected() && client.available()) {
        String line = client.readStringUntil('\n');
        line.trim();
        int separatorIndex = line.indexOf(':');
        if (separatorIndex != -1) {
            String cmd = line.substring(0, separatorIndex);
            String valueStr = line.substring(separatorIndex + 1);
            int value = valueStr.toInt();  // convert to int
            Serial.println("Received command: " + cmd);
            
            if (cmd == "setFirstTarget") {
                firstTarget = value;
                Serial.println("Found First Target: " + String(firstTarget));
            } else if (cmd == "setSecondTarget") {
                secondTarget = value;
                Serial.println("Found Second Target: " + String(secondTarget));
            } else if (cmd == "motorForward") {
                motorForward();
            } else if (cmd == "motorReverse") {
                motorReverse();
            } else if (cmd == "motorStop") {
                motorStop();
            } else if (cmd == "steering") {
                steering(value);
            } else {
                Serial.println("Unknown command: " + cmd);
            }
        }
    }
}