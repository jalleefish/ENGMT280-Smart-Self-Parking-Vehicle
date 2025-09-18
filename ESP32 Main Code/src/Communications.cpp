// Communications.cpp
// This file contains the implementation of communications functionalities for the Self Parking Car project.
#include <Arduino.h>
#include "Settings.h"
#include "DistanceSensors.h"
#include "MotorControl.h"
#include "ServoMotorControl.h"
#include "Communications.h"
#include <WiFi.h>

WiFiClient client;

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

    String msg = "[";
    for (int i = 0; i < 5; i++) {
        msg += String(distances[i]);
        if (i < 4) msg += ",";
    }
    msg += "]\n";   // newline important for Python parsing
    client.print(msg);
    Serial.println("Sent: " + msg);
}

void receiveComms() {
  Serial.println("Receiving communications data...");

}