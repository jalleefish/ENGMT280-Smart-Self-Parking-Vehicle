#include <Arduino.h>

const uint8_t distPin = 17;  // sensor OUT pin
void setup() {
  Serial.begin(115200);
  pinMode(distPin, INPUT);
}

void loop() {
  uint32_t t = pulseIn(distPin, HIGH, 300000 /*µs timeout*/);
  if (t == 0) {
    Serial.println("No reading or out of range");
  } else {
    long d = 4 * (long(t) - 1000);  // in mm
    if (d < 0) d = 0;
    Serial.print("Distance: ");
    Serial.print(d);
    Serial.println(" mm");
  }
  delay(100);
}