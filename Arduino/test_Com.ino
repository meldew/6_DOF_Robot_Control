#include <ArduinoJson.h>

void setup() {
  Serial.begin(115200); // Initialize serial communication at 9600 bits per second
}

void loop() {
  if (Serial.available() > 0) { // Check if data is available to read
    String data = Serial.readStringUntil('\n'); // Read the incoming data as a string
    Serial.print("Received: "); // Print the received data to the serial monitor
    Serial.println(data);
  }
}