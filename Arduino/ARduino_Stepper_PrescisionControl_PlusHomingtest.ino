const int stepPin = 4;
const int dirPin = 3;
const int limitSwitchPin = 2;
const int limitSwitchPin2 = 5;
const int homeSwitchPin = 6;
const int moveTOButtonPin = 7; 
const int resetHomingButtonPin = 8;

const long stepsPerRevolution = 30620;
const int stepsFor1Degree = (stepsPerRevolution / 360);
<<<<<<< HEAD
const int motorSpeed = 300;

=======
const int motorSpeed = 400;
>>>>>>> eb8bbe1 (degree feil)
bool homingComplete = false;
long currentPosition = 0;
bool HomingRequest = HIGH;
float targetAngle = false; 
String inputString = "";
bool stringComplete = false;

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(limitSwitchPin, INPUT_PULLUP);
  pinMode(limitSwitchPin2, INPUT_PULLUP);
  pinMode(homeSwitchPin, INPUT_PULLUP);
  pinMode(moveTOButtonPin, INPUT_PULLUP);
  pinMode(resetHomingButtonPin, INPUT_PULLUP);
  Serial.begin(9600);
}

void loop() {

  if (digitalRead(resetHomingButtonPin) == LOW) {
    while(digitalRead(resetHomingButtonPin) == LOW); 
    homingComplete = false;
    HomingRequest = HIGH;
  }

  if (stringComplete) {
    targetAngle = inputString.toFloat(); 
    Serial.print("Target Angle Set To: ");
    Serial.println(targetAngle);
    inputString = ""; 
    stringComplete = false;
  }

  if(HomingRequest == HIGH && homingComplete == false){
    performHoming();
  }

  if (homingComplete) {
    if (digitalRead(limitSwitchPin) == LOW) {
      moveMotor(stepsFor1Degree, HIGH);
    } else if (digitalRead(limitSwitchPin2) == LOW) {
      moveMotor(stepsFor1Degree, LOW);
<<<<<<< HEAD
    } else if (digitalRead(moveTOButtonPin) == LOW){
      moveToAngle(targetAngle);
=======
>>>>>>> eb8bbe1 (degree feil)
    }
    float currentAngle = calculateCurrentAngle();
    Serial.print("Current Angle: ");
    Serial.println(currentAngle, 2);
  }
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

void moveToAngle (float angle){
  long stepsTo_TargetPosition = angle * stepsPerRevolution / 360.0;
  long stepsToMove = stepsTo_TargetPosition - currentPosition;
  Serial.println(stepsTo_TargetPosition);
  if (stepsToMove == 0) return; 
  bool direction = stepsToMove > 0;
  moveMotor(abs(stepsToMove), direction);
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
