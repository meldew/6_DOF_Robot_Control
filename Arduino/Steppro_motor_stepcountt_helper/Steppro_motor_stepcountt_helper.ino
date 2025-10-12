#include <ArduinoJson.h>

const long J1stepsPerRevolution = 120000;
const int TestingStepperPerRevolution = 30620;

const int stepPin = 2;
const int dirPin = 3;
const int homeSwitchPin = 22;

bool moveManuallyMotorToLeft = false; 
bool moveManuallyMotorToRight = false; 
bool resetHome = false;
bool MoveToAngle = false;

const long stepsPerRevolution = J1stepsPerRevolution;
const long stepsFor1Degree = (stepsPerRevolution / 360);
const int motorSpeed = 200;
bool homingComplete = false;
long currentPosition = 0;
bool HomingRequest = HIGH;

float targetAngle = 0; 
bool stringComplete = false;
float maxJ1Angle = 120.0;
float minJ1Angle = -120.0;

// State variables for non-blocking motor control
bool motorMoving = false;
long motorStepsRemaining = 0;
bool motorDirection = LOW;
unsigned long motorLastStepTime = 0;

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(homeSwitchPin, INPUT_PULLUP);
  Serial.begin(115200);
}

void loop() {
  J1_NormalOperation();
}

void moveMotorNonBlocking(long steps, bool direction) {
  motorStepsRemaining = steps;
  motorDirection = direction;
  motorMoving = true;
  motorLastStepTime = micros();
}


bool readHomeStableLow(unsigned long hold_us = 7000) {  // ~3 ms
  unsigned long t0 = micros();
  while (micros() - t0 < hold_us) {
    if (digitalRead(homeSwitchPin) != LOW) return false;
  }
  return true;
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
  long steps = (stepsToMove >= 0) ? stepsToMove : -stepsToMove;
  moveMotorNonBlocking(steps, direction);
}

void performHoming() {
  digitalWrite(dirPin, LOW);

  // Step until switch goes LOW (normal homing)
  while (digitalRead(homeSwitchPin) == HIGH) {
    takeStep();
    currentPosition--;
  }

  if (!readHomeStableLow()) {
    // False trigger (noise or bounce) — keep stepping until truly LOW
    while (digitalRead(homeSwitchPin) == HIGH) {
      takeStep();
      currentPosition--;
    }
  }

  // Then finalize
  currentPosition = -120L * stepsPerRevolution / 360L;
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

void J1_NormalOperation() {
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
        float currentAngle = calculateCurrentAngle();
        Serial.print("J1 Angle:");
        Serial.println(currentAngle, 2);

        if (moveManuallyMotorToLeft && currentAngle < maxJ1Angle) {
          moveMotorNonBlocking(stepsFor1Degree, HIGH);
        } else if (moveManuallyMotorToRight && currentAngle > minJ1Angle) {
          moveMotorNonBlocking(stepsFor1Degree, LOW);
        } else if (MoveToAngle) {
          moveToAngle(targetAngle);
        }
      }
    } else {
      
    }
    moveMotorUpdate();
}

bool checkForError(bool error){
  if (!Serial.available() > 0 || error == true) {
    return true;
  }
}

