#include <ArduinoJson.h>

bool home = false; // Define the home variable with a default value of false

void setup() {
  Serial.begin(115200); // Initialize serial communication at 115200 bits per second
}

void loop() {
  if (Serial.available() > 0) { // Check if data is available to read
    String data = Serial.readStringUntil('\n'); // Read the incoming data as a string
    Serial.print("Received: "); // Print the received data to the serial monitor
    Serial.println(data);

    const size_t capacity = JSON_OBJECT_SIZE(1) + 20;
    DynamicJsonDocument doc(capacity);
    DeserializationError error = deserializeJson(doc, data);
    home = doc["Home"];
    // Check if home is true and print success
    if (home) {
      Serial.println("Success");
    }
  }
}
