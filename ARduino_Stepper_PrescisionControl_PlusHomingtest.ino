const int stepPin = 4;
const int dirPin = 3;
const int limitSwitchPin = 2;
const int limitSwitchPin2 = 5;
const int homeSwitchPin = 6;
const long stepsPerRevolution = 30620;
const int stepsFor10Degrees = (stepsPerRevolution / 360);
const int motorSpeed = 400;
bool homingComplete = false;
long currentPosition = 0;
bool HomingRequest = HIGH;

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(limitSwitchPin, INPUT_PULLUP);
  pinMode(limitSwitchPin2, INPUT_PULLUP);
  pinMode(homeSwitchPin, INPUT_PULLUP);
  Serial.begin(9600);
}

void loop() {
  if(HomingRequest == HIGH && homingComplete == false){
    performHoming();
  }

  if (homingComplete) {
    if (digitalRead(limitSwitchPin) == LOW) {
      moveMotor(stepsFor10Degrees, HIGH);
    } else if (digitalRead(limitSwitchPin2) == LOW) {
      moveMotor(stepsFor10Degrees, LOW);
    }
    float currentAngle = calculateCurrentAngle();
    Serial.print("Current Angle: ");
    Serial.println(currentAngle, 2);
  }
}

void performHoming() {
  digitalWrite(dirPin, LOW);
  while (digitalRead(homeSwitchPin) == HIGH) {
    takeStep();
    currentPosition--;
  }
  currentPosition = 0;
  homingComplete = true;
  Serial.println("Homing Complete. Current Position Reset.");
}

void moveMotor(int steps, bool direction) {
  digitalWrite(dirPin, direction);
  for (int i = 0; i < steps; i++) {
    takeStep();
    currentPosition += direction ? 1 : -1;
  }
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
