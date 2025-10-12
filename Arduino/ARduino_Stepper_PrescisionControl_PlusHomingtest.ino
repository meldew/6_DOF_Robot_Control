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

inline bool homePressed() {                 // INPUT_PULLUP: pressed = LOW
  return digitalRead(homeSwitchPin) == LOW;
}

// one step with your timing; keeps your sign convention (HIGH = +1, LOW = -1)
inline void stepOnce(bool dir, unsigned int us) {
  digitalWrite(dirPin, dir);
  digitalWrite(stepPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(stepPin, LOW);
  delayMicroseconds(us);
  currentPosition += dir ? 1 : -1;
}

void moveMotorNonBlocking(long steps, bool direction) {
  motorStepsRemaining = steps;
  motorDirection = direction;
  motorMoving = true;
  motorLastStepTime = micros();
}


bool readHomeStableLow(unsigned long hold_us = 25000) {  // ~3 ms
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
  const bool HOMING_DIR = LOW;        // flip to HIGH if this moves away from the switch
  const unsigned int STEP_US = 900;  // homing speed (bigger = slower)
  const unsigned long DEBOUNCE_MS = 25;
  const int RELEASE_MARGIN_STEPS = 200;  // extra after release
  const int CLEARANCE_STEPS = 800;        // final back-off so we don't sit on switch
  const long MAX_STEPS = stepsPerRevolution * 2L;

  auto pressed = [&](){ return digitalRead(homeSwitchPin) == LOW; }; // INPUT_PULLUP
  auto pulse = [&](bool dir){
    digitalWrite(dirPin, dir);
    digitalWrite(stepPin, HIGH); delayMicroseconds(10);
    digitalWrite(stepPin, LOW);  delayMicroseconds(STEP_US);
  };

  motorMoving = false; motorStepsRemaining = 0;

  // If starting pressed, back off to get a clean HIGH
  int k=0;
  while (pressed() && k < RELEASE_MARGIN_STEPS) { pulse(!HOMING_DIR); k++; }
  delay(10);

  // 1) Approach until first press (or timeout)
  long walked = 0;
  while (!pressed()) {
    pulse(HOMING_DIR);
    if (++walked >= MAX_STEPS) { homingComplete = false; return; }
  }

  // 2) Debounce: require LOW to hold for DEBOUNCE_MS
  unsigned long t0 = millis();
  while (millis() - t0 < DEBOUNCE_MS) {
    if (!pressed()) {                 // bounced open -> keep approaching and restart timer
      do { pulse(HOMING_DIR); if (++walked >= MAX_STEPS) { homingComplete=false; return; } }
      while (!pressed());
      t0 = millis();
    }
  }

  // 3) Back off until released, then add margin
  while (pressed()) { pulse(!HOMING_DIR); }
  for (int i=0; i<RELEASE_MARGIN_STEPS; ++i) pulse(!HOMING_DIR);

  // 4) Re-approach slowly to press again (clean edge)
  while (!pressed()) { pulse(HOMING_DIR); }

  // 5) Final tiny clearance and set reference
  for (int i=0; i<CLEARANCE_STEPS; ++i) pulse(!HOMING_DIR);

  // Your logical reference (example: home end = -120°)
  currentPosition = (long)(-120.0 * stepsPerRevolution / 360.0);
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

