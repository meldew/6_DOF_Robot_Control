#include <ArduinoJson.h>

const int stepPin = 4;
const int dirPin = 3;
bool moveManuallyMotorToLeft = false; 
bool moveManuallyMotorToRight = false; 
const int homeSwitchPin = 6;
const int moveTOButtonPin = 7; 
const int resetHomingButtonPin = 8;
bool resetHome = false;
bool MoveToAngle = false;

const long stepsPerRevolution = 30620;
const int stepsFor1Degree = (stepsPerRevolution / 360);
const int motorSpeed = 200;
bool homingComplete = false;
long currentPosition = 0;
bool HomingRequest = HIGH;
float targetAngle = 90; 
bool stringComplete = false;

// State variables for non-blocking motor control
bool motorMoving = false;
int motorStepsRemaining = 0;
bool motorDirection = LOW;
unsigned long motorLastStepTime = 0;

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(homeSwitchPin, INPUT_PULLUP);
  pinMode(moveTOButtonPin, INPUT_PULLUP);
  Serial.begin(115200);
}

void loop() {
  // Check for serial input continuously
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');

    const size_t capacity = JSON_OBJECT_SIZE(4) + 40;
    DynamicJsonDocument doc(capacity);
    DeserializationError error = deserializeJson(doc, data);
    resetHome = doc["Home"];
    moveManuallyMotorToLeft = doc["MoveJointToLeft"];
    moveManuallyMotorToRight = doc["MoveJointToRight"];
    MoveToAngle = doc["MoveToAngle"];

    if (resetHome) { 
      homingComplete = false;
      HomingRequest = HIGH;
    }

    if (HomingRequest == HIGH && homingComplete == false) {
      performHoming();
    }

    if (homingComplete) {
      if (moveManuallyMotorToLeft) {
        moveMotorNonBlocking(stepsFor1Degree, LOW);
      } else if (moveManuallyMotorToRight) {
        moveMotorNonBlocking(stepsFor1Degree, HIGH);
      } else if (MoveToAngle) {
        moveToAngle(targetAngle);
      }
    }
    if (homingComplete) {
      float currentAngle = calculateCurrentAngle();
      Serial.print("Current Angle: ");
      Serial.println(currentAngle, 2);
    }
  }  

  moveMotorUpdate();
}

void moveMotorNonBlocking(int steps, bool direction) {
  motorStepsRemaining = steps;
  motorDirection = direction;
  motorMoving = true;
  motorLastStepTime = micros();
}

void moveMotorUpdate() {
  if (motorMoving && motorStepsRemaining > 0) {
    if (micros() - motorLastStepTime >= motorSpeed) {
      digitalWrite(dirPin, motorDirection);
      digitalWrite(stepPin, HIGH);
      delayMicroseconds(10);  // Short pulse to ensure step is registered
      digitalWrite(stepPin, LOW);
      motorStepsRemaining--;
      motorLastStepTime = micros();
      currentPosition += motorDirection ? 1 : -1;
    }
  } else {
    motorMoving = false;
  }
}

void moveToAngle(float angle) {
  long stepsTo_TargetPosition = angle * stepsPerRevolution / 360.0;
  long stepsToMove = stepsTo_TargetPosition - currentPosition;
  if (stepsToMove == 0) return; 
  bool direction = stepsToMove > 0;
  moveMotorNonBlocking(abs(stepsToMove), direction);
}

void performHoming() {
  digitalWrite(dirPin, LOW);
  while (digitalRead(homeSwitchPin) == HIGH) {
    takeStep();
    currentPosition--;
  }
  currentPosition = 0;
  homingComplete = true;
}

void takeStep() {
  digitalWrite(stepPin, HIGH);
  delayMicroseconds(motorSpeed);
  digitalWrite(stepPin, LOW);
  delayMicroseconds(motorSpeed);
}

float calculateCurrentAngle() {
  return static_cast<float>(currentPosition) * 360.0 / stepsPerRevolution;
}
