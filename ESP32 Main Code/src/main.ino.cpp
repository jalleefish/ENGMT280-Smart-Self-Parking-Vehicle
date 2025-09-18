# 1 "C:\\Users\\JOELTO~1\\AppData\\Local\\Temp\\tmp60p8lm95"
#include <Arduino.h>
# 1 "C:/Users/Joel Tolley/Nextcloud/Joel Tolley/Files/University/2025 Semester 2/280 - Mechatronics Design and Manufacturing/ENGMT280-Smart-Self-Parking-Vehicle/ESP32 Main Code/src/main.ino"


#include <Arduino.h>
#include "Settings.h"
#include "DistanceSensors.h"
#include "MotorControl.h"
#include "ServoMotorControl.h"
#include "communications.h"
void setup();
void loop();
#line 10 "C:/Users/Joel Tolley/Nextcloud/Joel Tolley/Files/University/2025 Semester 2/280 - Mechatronics Design and Manufacturing/ENGMT280-Smart-Self-Parking-Vehicle/ESP32 Main Code/src/main.ino"
void setup() {
    Serial.begin(115200);
    setupDist();
    setupMotor();
    setupServo();
    setupComms();
}

void loop() {
    updateDist();
    sendComms();
    receiveComms();
    delay(300);
}