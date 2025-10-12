#include <ArduinoJson.h>

// ================== CONFIG ==================
const long J1stepsPerRevolution = 120000;
const long stepsFor1Degree = J1stepsPerRevolution / 360;   // 1° worth of steps
const int stepPin = 2;
const int dirPin  = 3;
const int homeSwitchPin = 22;

#define STEP_PULSE_HIGH_US 5
int motorSpeed = 120;             // smaller = faster
const float HOME_OFFSET_DEG = -120.0f;
const float maxJ1Angle =  120.0f;
const float minJ1Angle = -120.0f;
const uint16_t TX_INTERVAL_MS = 100;
const float FOLLOW_DEADBAND_DEG = 0.5f;

// ================== STATE ==================
bool moveLeft = false, moveRight = false;
bool homingInProgress = false, homingDone = false;
bool moveToZeroQueued = false;

int Checkpoint = 0;
float Link1Pos = 0.0f;
float lastCommanded = 0.0f;

long currentPosition = 0;
bool motorMoving = false;
bool motorDirection = LOW;
long motorStepsRemaining = 0;
unsigned long motorLastStep = 0;
unsigned long lastTxMs = 0;

// ================== UTILS ==================
inline long degToSteps(float d){return (long)(d*J1stepsPerRevolution/360.0);}
inline float stepsToDeg(long s){return (float)s*360.0/J1stepsPerRevolution;}
void stepPulse(bool dir){digitalWrite(dirPin,dir);digitalWrite(stepPin,HIGH);
delayMicroseconds(STEP_PULSE_HIGH_US);digitalWrite(stepPin,LOW);
currentPosition += dir?1:-1;}

// ================== BASIC MOVE ==================
void moveMotorNonBlocking(long steps,bool dir){
  motorDirection=dir;motorStepsRemaining=steps;motorMoving=true;
  motorLastStep=micros();
}
void moveMotorUpdate(){
  if(motorMoving && motorStepsRemaining>0){
    if(micros()-motorLastStep>=motorSpeed){
      stepPulse(motorDirection);
      motorStepsRemaining--;motorLastStep=micros();
    }
  }else motorMoving=false;
}
void moveToAngle(float deg){
  long stepsToTarget=degToSteps(deg);
  long delta=stepsToTarget-currentPosition;
  if(delta==0)return;
  bool dir=delta>0; long steps=abs(delta);
  moveMotorNonBlocking(steps,dir);
  lastCommanded=deg;
}

// ================== HOMING ==================
void performHoming(){
  const bool HOMING_DIR=LOW;
  const unsigned int STEP_US=600;
  const unsigned long DEB_MS=25;
  const int RELEASE_MARGIN=200;
  const int CLEARANCE=800;
  const long MAX_STEPS=J1stepsPerRevolution*2L;

  auto pressed=[&](){return digitalRead(homeSwitchPin)==LOW;};
  auto pulse=[&](bool d){digitalWrite(dirPin,d);
    digitalWrite(stepPin,HIGH);delayMicroseconds(STEP_US);
    digitalWrite(stepPin,LOW);delayMicroseconds(STEP_US);};

  int k=0;while(pressed()&&k<RELEASE_MARGIN){pulse(!HOMING_DIR);k++;}
  delay(10);

  long walked=0;
  while(!pressed()){
    pulse(HOMING_DIR);
    if(++walked>=MAX_STEPS)return;
  }

  unsigned long t0=millis();
  while(millis()-t0<DEB_MS){
    if(!pressed()){
      do{pulse(HOMING_DIR);if(++walked>=MAX_STEPS)return;}
      while(!pressed());
      t0=millis();
    }
  }

  while(pressed())pulse(!HOMING_DIR);
  for(int i=0;i<RELEASE_MARGIN;i++)pulse(!HOMING_DIR);
  while(!pressed())pulse(HOMING_DIR);
  for(int i=0;i<CLEARANCE;i++)pulse(!HOMING_DIR);

  currentPosition=degToSteps(HOME_OFFSET_DEG);
  homingDone=true;
}

// ================== SERIAL / JSON ==================
void maybeSendAngle(){
  unsigned long now=millis();
  if(now-lastTxMs>TX_INTERVAL_MS){
    Serial.println(stepsToDeg(currentPosition),2);
    lastTxMs=now;
  }
}

// ================== SETUP ==================
void setup(){
  pinMode(stepPin,OUTPUT);pinMode(dirPin,OUTPUT);
  pinMode(homeSwitchPin,INPUT_PULLUP);
  Serial.begin(115200);Serial.setTimeout(50);
}

// ================== LOOP ==================
void loop(){
  // --- read serial JSON ---
  if(Serial.available()>0){
    String data=Serial.readStringUntil('\n');
    DynamicJsonDocument d(160);
    if(!deserializeJson(d,data)){
      if(d.containsKey("MoveJointToLeft")) moveLeft=d["MoveJointToLeft"].as<int>();
      if(d.containsKey("MoveJointToRight")) moveRight=d["MoveJointToRight"].as<int>();
      if(d.containsKey("Checkpoint")) Checkpoint=d["Checkpoint"].as<int>();
      if(d.containsKey("Link1Pos")) Link1Pos=d["Link1Pos"].as<float>();

      // Home button = calibration routine
      if(d.containsKey("Home") && d["Home"].as<int>()==1 && !homingInProgress){
        homingInProgress=true;
        performHoming();
        homingInProgress=false;
      }

      // MoveToAngle button = go to 0 degrees
      if(d.containsKey("MoveToAngle") && d["MoveToAngle"].as<int>()==1){
        if(homingDone && !homingInProgress)
          moveToZeroQueued=true;
      }
    }
  }

  // --- actuation ---
  if(homingDone && !homingInProgress){
    float a=stepsToDeg(currentPosition);

    // ✅ Continuous manual jog (only if Checkpoint==0)
    if(Checkpoint==0){
      if(moveLeft && a<maxJ1Angle){
        digitalWrite(dirPin,HIGH);
        if(micros()-motorLastStep>=motorSpeed){
          stepPulse(HIGH);
          motorLastStep=micros();
        }
      }
      else if(moveRight && a>minJ1Angle){
        digitalWrite(dirPin,LOW);
        if(micros()-motorLastStep>=motorSpeed){
          stepPulse(LOW);
          motorLastStep=micros();
        }
      }
    }

    // Move to 0° when requested
    if(moveToZeroQueued){
      moveToZeroQueued=false;
      moveToAngle(0.0f);
    }

    // Follow Link1 live when checkpoint active
    if(Checkpoint==1){
      float cmd=Link1Pos;
      if(cmd>maxJ1Angle)cmd=maxJ1Angle;
      if(cmd<minJ1Angle)cmd=minJ1Angle;
      if(fabs(cmd-lastCommanded)>=FOLLOW_DEADBAND_DEG)
        moveToAngle(cmd);
    }
  }

  moveMotorUpdate();
  maybeSendAngle();
}
