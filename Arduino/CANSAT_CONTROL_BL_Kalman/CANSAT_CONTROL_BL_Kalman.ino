#include <ESP32Servo.h>
#include <analogWrite.h>
#include <ESP32Tone.h>
#include <ESP32PWM.h>
#include <Wire.h> // I2C 통신에 필요한 헤더파일 (ESP32와 MPU6050 사이의 통신)
#include "BluetoothSerial.h" // 블루투스 통신에 필요한 헤더파일 

#define MPU6050_ADDR 0x68
#define ACCEL_XOUT_H 0x3B
#define GYRO_XOUT_H 0x43
#define RAD_TO_DEG 57.2958

Servo motor1;
Servo motor2;
Servo motor3;
Servo motor4;

BluetoothSerial SerialBT;

int16_t AcX, AcY, AcZ;

int16_t GyX, GyY;
double dt, currentTime, previousTime;
double AngleX = 0, AngleY = 0;
double AngleX_ac, AngleY_ac;
double GyXrate, GyYrate;

// Kalman Filter Variables for X
double biasX = 0; 
double P_X[2][2] = {{0,0},{0,0}}; 

// Kalman Filter Variables for Y
double biasY = 0; 
double P_Y[2][2] = {{0,0},{0,0}};

double Q_angle = 0.001; 
double Q_bias = 0.003; 
double R_measure = 0.03;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600); 
  SerialBT.begin("CANSAT");//SerialBT.begin 함수 호출, 블루투스 디바이스 이름 Kocolabs Drone으로 설정
  
  Wire.begin(); // Wire.begin 함수 호출 
  Wire.setClock(400000); // I2C 통신속도 설정 100000(standard) or 400000(fast)으로 설정가능

  Wire.beginTransmission(0x68); // 0x68번지 값을 갖는 MPU6050과 I2C 통신시작
  Wire.write(0x6b);
  Wire.write(0x0); // MPU6050을 깨움
  Wire.endTransmission(true); // 통신 종료

  // motor에 디지털 핀 할당
  motor1.attach(18);
  motor2.attach(19);
  motor3.attach(32);
  motor4.attach(33);
}

int start=0; //초기 start = 0으로 설정

double kalmanFilter(double newAngle, double newRate, double dt, double bias, double P[2][2]) {
  // Discrete Kalman filter time update equations
  double Angle = newAngle + dt * (newRate - bias);
  P[0][0] += dt * (dt*P[1][1] - P[0][1] - P[1][0] + Q_angle);
  P[0][1] -= dt * P[1][1];
  P[1][0] -= dt * P[1][1];
  P[1][1] += Q_bias * dt;

  // Measurement update equations
  double S = P[0][0] + R_measure; // Estimate error
  double K[2]; // Kalman gain
  K[0] = P[0][0] / S;
  K[1] = P[1][0] / S;

  double y = newAngle - Angle; // Angle difference

  // Calculate angle and bias
  Angle += K[0] * y;
  bias += K[1] * y;

  // Calculate estimation error covariance
  double P00_temp = P[0][0];
  double P01_temp = P[0][1];

  P[0][0] -= K[0] * P00_temp;
  P[0][1] -= K[0] * P01_temp;
  P[1][0] -= K[1] * P00_temp;
  P[1][1] -= K[1] * P01_temp;

  return Angle;
}

void loop() {
 unsigned long startMicros = micros();
 //가속도 센서 값 읽기
 Wire.beginTransmission(0x68);
 Wire.write(ACCEL_XOUT_H);
 Wire.endTransmission(false);
 Wire.requestFrom(MPU6050_ADDR, 6, true);
 int16_t AcX = Wire.read() << 8 | Wire.read();
 int16_t AcY = Wire.read() << 8 | Wire.read();
 int16_t AcZ = Wire.read() << 8 | Wire.read();
  

 //자이로 값 받아오기
 Wire.beginTransmission(0x68);
 Wire.write(0x43);
 Wire.endTransmission(false);
 Wire.requestFrom(0x68,6,true);//MPU6050의 0x43번지부터 시작하는 자이로센서 값이 저장됨. (순서대로 XH,XL,YH,YL,ZH,ZL)
 int16_t GyXH = Wire.read();
 int16_t GyXL = Wire.read();
 int16_t GyYH = Wire.read();
 int16_t GyYL = Wire.read(); // 순서대로 회전각속도(자이로 센서가 읽어내는 값)을 저장함.
 int16_t GyX = GyXH <<8 |GyXL;
 int16_t GyY = GyYH <<8 |GyYL; //ZH값을 상위 8비트에, ZL값을 하위 8비트에 넣어 GyZ값에 저장함.

  static int32_t GyXSum=0, GyYSum=0; //32비트 정적변수 선언 GyXSum 은 GyX값을 1000번 더해 저장할 변수
  static double GyXOff=0.0, GyYOff=0.0; // GyY의 평균값을  저장할 정적 실수 변수 GyXOff 선언
  static int cnt_sample=1000;
  if(cnt_sample>0) {
    GyXSum += GyX; GyYSum += GyY; //cnt_sample>0 일동안 자이로 값을 GyXSum에 저장함 (1000번)
    cnt_sample --;
    if(cnt_sample ==0) {
      GyXOff= GyXSum /1000.0;
      GyYOff= GyYSum /1000.0;
    }
    delay(1);
    return;// 루프함수의 처음으로 돌아감
  }
  
  double GyXD =GyX-GyXOff; //GyXD=0에 가까운 자이로 값 (회전하지 않을 때의 자이로값을 0에 가깝도록 보정한것)
  double GyYD =GyY-GyYOff;
 
  double GyXR =GyXD /131; 
  double GyYR =GyYD /131; //회전각속도 GyXR=GyXD/131을 구함
  
  currentTime = micros();
  dt = (double)(currentTime - previousTime) / 1000000; // Convert to seconds
  previousTime = currentTime; //주기 dt 구함

  // 가속도 센서에서 각도 계산
  AngleX_ac = atan2(-AcY, sqrt(AcX * AcX + AcZ * AcZ)) * RAD_TO_DEG;
  AngleY_ac = atan2(-AcX, sqrt(AcY * AcY + AcZ * AcZ)) * RAD_TO_DEG;

  // 자이로스코프에서 각도 계산
  GyXrate = GyX / 131.0; 
  GyYrate = GyY / 131.0; 

  // Apply the Kalman Filter for both axes
  AngleX = -kalmanFilter(AngleX_ac, GyXrate, dt, biasX, P_X);
  AngleY = kalmanFilter(AngleY_ac, GyYrate, dt, biasY, P_Y); //회전각속도*주기를 통해 현재 각도를 구함

  static double tAngleX=0.0,tAngleY=0.0;//목표각도=0.0
  double eAngleX=AngleX-tAngleX;
  double eAngleY=AngleY-tAngleY; //목표회전각도=현재각도-목표각도
  double Kp=20;// P gain (각도제어 증폭)
  double BalX = Kp *eAngleX;
  double BalY = Kp *eAngleY;

  double Kd=10;
  
  static int cnt_stable = 0;
  
  if(abs(AngleX) <= 7 && abs(AngleY) <= 7) {
    cnt_stable++;
  } else {
    cnt_stable = 0;
    Kp = 20;
    Kd = 10;
  }
  
  // stable 모드 돌입
  if(cnt_stable >= 5) {
    Kp = 2;
    Kd = 2;
  }
  
  BalX += Kd*GyXR;
  BalY += Kd*GyYR;
  if(start==0) BalX=BalY=0.0; //약 100~500 오더
  
 if(SerialBT.available()>0) {
  while(SerialBT.available()>0){
  char userInput =SerialBT.read();
  if(userInput >='1'&& userInput <='9') {
    start=1;
    }
  if(userInput =='0') {
    start=0;
    }
  }
 }

double speedA= 1100+BalX; 
double speedB= 1100-BalY; 
double speedC= 1100-BalX;
double speedD= 1100+BalY; // 쓰로틀에 힘 분배

int iSpeedA= constrain((int)speedA, 1100, 1800);
int iSpeedB= constrain((int)speedB, 1100, 1800);
int iSpeedC= constrain((int)speedC, 1100, 1800);
int iSpeedD= constrain((int)speedD, 1100, 1800); //스피드의 범위를 1100에서 1800으로 제한함

motor1.writeMicroseconds(iSpeedA);
motor2.writeMicroseconds(iSpeedB);
motor3.writeMicroseconds(iSpeedC);
motor4.writeMicroseconds(iSpeedD);

// debug
//Serial.print("각도,각속도");
//Serial.print(AngleX);
//Serial.print(',');
//Serial.println(AngleY);
//Serial.print(',');
//Serial.print(GyXR);
//Serial.print(',');
//Serial.print(GyYR);
//Serial.print(" 밸런스값");
//Serial.print(BalX);
//Serial.print(',');
//Serial.print(BalY);
//Serial.print(" 스피드");
//Serial.print(iSpeedA);
//Serial.print(',');
//Serial.print(iSpeedB);
//Serial.print(',');
//Serial.print(iSpeedC);
//Serial.print(',');
//Serial.print(iSpeedD);
//Serial.print(',');
//Serial.print(Kp);
//Serial.print(',');
//Serial.print(Kd);
//Serial.print(',');
//Serial.println(start);
delay(100);

unsigned long endMicros = micros();
Serial.println(endMicros - startMicros);
}
