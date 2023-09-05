#include <SoftwareSerial.h>
#include "Wire.h"
#include "I2Cdev.h"
#include "MPU9250.h"
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>

// Gyro- SCL A5 SDA A4 INT D2
// GPS- TX D3 RX D4
#define SCL 5
#define SDA 6
#define CSB 7
#define SDO 8
#define RAD_TO_DEG 57.2958

Adafruit_BMP280 bmp(CSB,SDA,SDO,SCL);


// class default I2C address is 0x68
// specific I2C addresses may be passed as a parameter here
// AD0 low = 0x68 (default for InvenSense evaluation board)
// AD0 high = 0x69
MPU9250 accelgyro;
I2Cdev   I2C_M;

uint8_t buffer_m[6];

int16_t ax, ay, az;
int16_t gx, gy, gz;
int16_t   mx, my, mz;

float heading;
float tiltheading;
float heading_offset;
float Axyz[3];
float Gxyz[3];
float Mxyz[3];
#define sample_num_mdate  5000
volatile float mx_sample[3];
volatile float my_sample[3];
volatile float mz_sample[3];

static float mx_centre = 0;
static float my_centre = 0;
static float mz_centre = 0;

volatile int mx_max = 0;
volatile int my_max = 0;
volatile int mz_max = 0;

volatile int mx_min = 0;
volatile int my_min = 0;
volatile int mz_min = 0;

// 기압계 변수 설정
float temperature;
float pressure;
float atm;
float altitude;
bool first=false;

// GPS 변수 설정

float gpstime;
float gpsdate;
float latitude;
float longitude;
float gpsaltitude; //원래 altitude인데 gps altitude로 바꿈
float gpsknots;
float gpstrack;

char latNS, lonEW;
char gpsstatus;
int fixquality;
int numsatelites;
                
volatile int ptr = 0;
volatile bool flag = true;
volatile char redbuffer[120];
volatile char blubuffer[120];

// gpsSerial(receive from GPS,transmit to the GPS module)
SoftwareSerial gpsSerial(3,4);

// 칼만 필터 변수
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
  Serial.begin(9600);
  Wire.begin();
  accelgyro.initialize();

  Mxyz_init_calibrated();

//  North_init_calibrated();

  //bmp
  bmp.begin();
  
  //GPS 설정
  pinMode(3, INPUT);   
  pinMode(4, OUTPUT);
  gpsSerial.begin(9600);
  SelectSentences();
}

//칼만 필터 함수
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
    float init_press;
    if (!first) {
      init_press=bmp.readPressure()/100;
      first=true;
    }
    
    getAccel_Data();
    getGyro_Data();
    getCompassDate_calibrated(); 
    getTiltHeading();
    listen(); // 지우지마라 GPS listen이다          

    int readValue = analogRead(A0); //조도센서 반복 변수 할당

    // 가속도 센서에서 각도 계산
    AngleX_ac = atan2(-Axyz[1], sqrt(Axyz[0] * Axyz[0] + Axyz[2] * Axyz[2])) * RAD_TO_DEG;
    AngleY_ac = atan2(-Axyz[0], sqrt(Axyz[1] * Axyz[1] + Axyz[2] * Axyz[2])) * RAD_TO_DEG;

    AngleX = -kalmanFilter(AngleX_ac, Gxyz[0], dt, biasX, P_X);
    AngleY = kalmanFilter(AngleY_ac, Gxyz[1], dt, biasY, P_Y);

    Serial.print(Axyz[0]); //Acceleration(g) of X,Y,Z
    Serial.print(",");
    Serial.print(Axyz[1]);
    Serial.print(",");
    Serial.print(Axyz[2]);
    Serial.print(",");
    Serial.print(Gxyz[0]); //Gyro(degress/s) of X,Y,Z
    Serial.print(",");
    Serial.print(Gxyz[1]);
    Serial.print(",");
    Serial.print(Gxyz[2]);
    Serial.print(",");
    Serial.print(AngleX); //각도
    Serial.print(",");
    Serial.print(AngleY);
    Serial.print(",");
    Serial.print(tiltheading); //The clockwise angle between the magnetic north and X-Axis
    Serial.print(",");
    Serial.print(bmp.readTemperature()); // 온도
    Serial.print(",");
    Serial.print(bmp.readPressure()); // 압력
    Serial.print(",");
    Serial.print(bmp.readAltitude(init_press)); // 고도
    Serial.print(",");
    Serial.print(latitude, 8); //위도
    Serial.print(",");
    Serial.print(longitude, 8); //경도
    Serial.print(",");
    Serial.print(gpsaltitude); //gps 고도
    Serial.print(",");
    Serial.print(readValue); //조도
    Serial.println();
    delay(200);
}

void getHeading(void)
{
    heading = (180 * atan2(Mxyz[0], Mxyz[1]) / PI);
    if (heading < 0) heading += 360;
}

void getTiltHeading(void)
{
    float pitch = asin(-Axyz[0]);
    float roll = asin(Axyz[1] / cos(pitch));

    float xh = Mxyz[0] * cos(pitch) + Mxyz[2] * sin(pitch);
    float yh = Mxyz[0] * sin(roll) * sin(pitch) + Mxyz[1] * cos(roll) - Mxyz[2] * sin(roll) * cos(pitch);
    float zh = -Mxyz[0] * cos(roll) * sin(pitch) + Mxyz[1] * sin(roll) + Mxyz[2] * cos(roll) * cos(pitch);
    tiltheading = 180 * atan2(xh, yh) / PI;
    if (xh < 0)    tiltheading += 360;
}

void Mxyz_init_calibrated ()
{
    Serial.println("Calibration ready...");
    delay(5000);
    Serial.println("Magnetometer Calibrating... Move cansat for 2 minutes");

    get_calibration_Data ();

    Serial.println("Calibration Complete");
}

//void North_init_calibrated ()
//{
//  delay(3000);
//  Serial.println("Direction Calibration Ready... Face Cansat X Axis to North");
//  delay(3000);
//  for(int i = 10; i > 0; --i) {
//    Serial.println(i); // Print the count down value
//    delay(1000); // Delay for one second
//  }
//  Serial.println("Direction Calibrating...");
//
//  float sum = 0; // heading 값을 더할 변수
//  for(int i = 0; i < 100; i++) {
//    getCompassDate_calibrated(); //지자기값 받아오기
//    getHeading(); // heading 계산
//    Serial.print("heading: ");
//    Serial.println(heading);
//    sum += heading; // heading 값 더하기
//    delay(10); // 데이터를 받아올 시간을 주기 위해 간단한 delay
//  }

//  heading_offset = sum / 100.0; // 평균 계산 및 할당
//
//  Serial.println("Direction Calibration Complete");
//  Serial.print("Heading offset: ");
//  Serial.println(heading_offset);
//  delay(3000);
//  
//}


void get_calibration_Data ()
{
    for (int i = 0; i < sample_num_mdate; i++)
    {
        get_one_sample_date_mxyz();

        if (mx_sample[2] >= mx_sample[1])mx_sample[1] = mx_sample[2];
        if (my_sample[2] >= my_sample[1])my_sample[1] = my_sample[2]; //find max value
        if (mz_sample[2] >= mz_sample[1])mz_sample[1] = mz_sample[2];

        if (mx_sample[2] <= mx_sample[0])mx_sample[0] = mx_sample[2];
        if (my_sample[2] <= my_sample[0])my_sample[0] = my_sample[2]; //find min value
        if (mz_sample[2] <= mz_sample[0])mz_sample[0] = mz_sample[2];

    }

    mx_max = mx_sample[1];
    my_max = my_sample[1];
    mz_max = mz_sample[1];

    mx_min = mx_sample[0];
    my_min = my_sample[0];
    mz_min = mz_sample[0];

    mx_centre = (mx_max + mx_min) / 2;
    my_centre = (my_max + my_min) / 2;
    mz_centre = (mz_max + mz_min) / 2;
}

void get_one_sample_date_mxyz()
{
    getCompass_Data();
    mx_sample[2] = Mxyz[0];
    my_sample[2] = Mxyz[1];
    mz_sample[2] = Mxyz[2];
}

void getAccel_Data(void)
{
    accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);
    Axyz[0] = (double) ax / 16384;
    Axyz[1] = (double) ay / 16384;
    Axyz[2] = (double) az / 16384;
}

void getGyro_Data(void)
{
    accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);

    Gxyz[0] = (double) gx * 250 / 32768;
    Gxyz[1] = (double) gy * 250 / 32768;
    Gxyz[2] = (double) gz * 250 / 32768;
}

void getCompass_Data(void)
{
    I2C_M.writeByte(MPU9150_RA_MAG_ADDRESS, 0x0A, 0x01); //enable the magnetometer
    delay(10);
    I2C_M.readBytes(MPU9150_RA_MAG_ADDRESS, MPU9150_RA_MAG_XOUT_L, 6, buffer_m);

    mx = ((int16_t)(buffer_m[1]) << 8) | buffer_m[0] ;
    my = ((int16_t)(buffer_m[3]) << 8) | buffer_m[2] ;
    mz = ((int16_t)(buffer_m[5]) << 8) | buffer_m[4] ;

    Mxyz[0] = (double) mx * 1200 / 4096;
    Mxyz[1] = (double) my * 1200 / 4096;
    Mxyz[2] = (double) mz * 1200 / 4096;
}

void getCompassDate_calibrated ()
{
    getCompass_Data();
    Mxyz[0] = Mxyz[0] - mx_centre;
    Mxyz[1] = Mxyz[1] - my_centre;
    Mxyz[2] = Mxyz[2] - mz_centre;
}

//GPS 함수

void listen(){

  while (gpsSerial.available())
  {
     read(gpsSerial.read());
  }
}

void read(char nextChar){

  // Start of a GPS message
  if (nextChar == '$') {
    
    flag ? redbuffer[ptr] = '\0' : blubuffer[ptr] = '\0';

    ptr = 0;
  }

  // End of a GPS message
  if (nextChar == '\n') {

    if (flag) {
      flag = false;
      
      // Set termination character of the current buffer
      redbuffer[ptr] = '\0';

      // Process the message if the checksum is correct
      if (CheckSum((char*) redbuffer )) {parseString((char*) redbuffer );}
    }
    else
    {
      flag = true;
      
      // Set termination character of the current buffer
      blubuffer[ptr] = '\0';

      // Process the message if the checksum is correct
      if (CheckSum((char*) blubuffer )) {parseString((char*) blubuffer );}
    }   
    ptr = 0; 
  }

  // Add a new character
  flag ? redbuffer[ptr] = nextChar : blubuffer[ptr] = nextChar;

  // Check we stay within allocated memory
  if (ptr < 119) ptr++;

}

bool CheckSum(char* msg) {

  // Check the checksum
  //$GPGGA,.........................0000*6A
  
  // Length of the GPS message
  int len = strlen(msg);

  // Does it contain the checksum, to check
  if (msg[len-4] == '*') {

  // Read the checksum from the message
  int cksum = 16 * Hex2Dec(msg[len-3]) + Hex2Dec(msg[len-2]);

  // Loop over message characters
  for (int i=1; i < len-4; i++) {
          cksum ^= msg[i];
      }

  // The final result should be zero
  if (cksum == 0){
    return true;
  }
  }

  return false;
}


float DegreeToDecimal(float num, byte sign)
{
   // Want to convert DDMM.MMMM to a decimal number DD.DDDDD

   int intpart= (int) num;
   float decpart = num - intpart;

   int degree = (int)(intpart / 100);
   int mins = (int)(intpart % 100);

   if (sign == 'N' || sign == 'E')
   {
     // Return positive degree
     return (degree + (mins + decpart)/60);
   }   
   // Return negative degree
   return -(degree + (mins + decpart)/60);
}

void parseString(char* msg) {

  messageGGA(msg);
  messageRMC(msg);
}


void messageGGA(char* msg) 
{
  // Ensure the checksum is correct before doing this
  // Replace all the commas by end-of-string character '\0'
  // Read the first string
  // Knowing the length of the first string, can jump over to the next string
  // Repeat the process for all the known fields.
  
  // Do we have a GGA message?
  if (!strstr(msg, "GGA")) return;

  // Length of the GPS message
  int len = strlen(msg);

  // Replace all the commas with end character '\0'
  for (int j=0; j<len; j++){
    if (msg[j] == ',' || msg[j] == '*'){
      msg[j] = '\0';
    }
  }

  // Allocate working variables
  int i = 0;

  //$GPGGA

  // GMT time  094728.000
  i += strlen(&msg[i])+1;
  gpstime = atof(&msg[i]);
  
  // Latitude
  i += strlen(&msg[i])+1;
  latitude = atof(&msg[i]);
  
  // North or South (single char)
  i += strlen(&msg[i])+1;
  latNS = msg[i];
  if (latNS == '\0') latNS = '.';
  
  // Longitude
  i += strlen(&msg[i])+1;
  longitude = atof(&msg[i]);
  
  // East or West (single char)
  i += strlen(&msg[i])+1;
  lonEW = msg[i];
  if (lonEW == '\0') lonEW = '.';  
  
  // Fix quality (1=GPS)(2=DGPS)
  i += strlen(&msg[i])+1;
  fixquality = atof(&msg[i]);   
      
  // Number of satellites being tracked
  i += strlen(&msg[i])+1;
  numsatelites = atoi(&msg[i]); 
  
  // Horizontal dilution of position
  i += strlen(&msg[i])+1;
  
  // Altitude
  i += strlen(&msg[i])+1;
  altitude = atof(&msg[i]);     
  
  // Height of geoid (mean sea level)
  i += strlen(&msg[i])+1;
  
  // Time in seconds since last DGPS update
  i += strlen(&msg[i])+1;
  
  // DGPS station ID number
  i += strlen(&msg[i])+1;
  
  // Convert from degrees and minutes to degrees in decimals
  latitude = DegreeToDecimal(latitude, latNS);
  longitude = DegreeToDecimal(longitude, lonEW);   
}


void messageRMC(char* msg) 
{
  // Ensure the checksum is correct before doing this
  // Replace all the commas by end-of-string character '\0'
  // Read the first string
  // Knowing the length of the first string, can jump over to the next string
  // Repeat the process for all the known fields.
  
  // Do we have a RMC message?
  if (!strstr(msg, "RMC")) return;

  // Length of the GPS message
  int len = strlen(msg);

  // Replace all the commas with end character '\0'
  for (int j=0; j<len; j++){
    if (msg[j] == ',' || msg[j] == '*'){
      msg[j] = '\0';
    }
  }

  // Allocate working variables
  int i = 0;

  //$GPRMC

  // GMT time  094728.000
  i += strlen(&msg[i])+1;
  gpstime = atof(&msg[i]);

  // Status A=active or V=Void.
  i += strlen(&msg[i])+1;
  gpsstatus = msg[i];

  // Latitude
  i += strlen(&msg[i])+1;
  latitude = atof(&msg[i]);

  // North or South (single char)
  i += strlen(&msg[i])+1;
  latNS = msg[i];
  if (latNS == '\0') latNS = '.';

  // Longitude
  i += strlen(&msg[i])+1;
  longitude = atof(&msg[i]);

  // East or West (single char)
  i += strlen(&msg[i])+1;
  lonEW = msg[i];
  if (lonEW == '\0') lonEW = '.';               

  // // Speed over the ground in knots
  i += strlen(&msg[i])+1;
  gpsknots = atof(&msg[i]);

  // Track angle in degrees True North
  i += strlen(&msg[i])+1;
  gpstrack = atof(&msg[i]); 
  
  // Date - 31st of March 2018
  i += strlen(&msg[i])+1;
  gpsdate = atof(&msg[i]); 
                     
  // Magnetic Variation
  
  // Convert from degrees and minutes to degrees in decimals
  latitude = DegreeToDecimal(latitude, latNS);
  longitude = DegreeToDecimal(longitude, lonEW);
}

// Convert HEX to DEC
int Hex2Dec(char c) {

  if (c >= '0' && c <= '9') {
    return c - '0';
  }
  else if (c >= 'A' && c <= 'F') {
    return (c - 'A') + 10;
  }
  else {
    return 0;
  }
}


void AllSentences()
{
  // NMEA_GLL output interval - Geographic Position - Latitude longitude
  // NMEA_RMC output interval - Recommended Minimum Specific GNSS Sentence
  // NMEA_VTG output interval - Course Over Ground and Ground Speed
  // NMEA_GGA output interval - GPS Fix Data
  // NMEA_GSA output interval - GNSS DOPS and Active Satellites
  // NMEA_GSV output interval - GNSS Satellites in View

  // Enable $PUBX,40,GLL,0,1,0,0*5D
  gpsSerial.println("$PUBX,40,GLL,0,1,0,0*5D");
  delay(100);

  // Enable $PUBX,40,RMC,0,1,0,0*46
  gpsSerial.println("$PUBX,40,RMC,0,1,0,0*46");
  delay(100);
  
  // Enable $PUBX,40,VTG,0,1,0,0*5F
  gpsSerial.println("$PUBX,40,VTG,0,1,0,0*5F");
  delay(100);

  // Enable $PUBX,40,GGA,0,1,0,0*5B
  gpsSerial.println("$PUBX,40,GGA,0,1,0,0*5B");
  delay(100);
  
  // Enable $PUBX,40,GSA,0,1,0,0*4F
  gpsSerial.println("$PUBX,40,GSA,0,1,0,0*4F");
  delay(100);  

  // Enable $PUBX,40,GSV,0,5,0,0*5C
  gpsSerial.println("$PUBX,40,GSV,0,5,0,0*5C");
  delay(100);
}


void SelectSentences()
{
  // NMEA_GLL output interval - Geographic Position - Latitude longitude
  // NMEA_RMC output interval - Recommended Minimum Specific GNSS Sentence
  // NMEA_VTG output interval - Course Over Ground and Ground Speed
  // NMEA_GGA output interval - GPS Fix Data
  // NMEA_GSA output interval - GNSS DOPS and Active Satellites
  // NMEA_GSV output interval - GNSS Satellites in View

  // Enable $PUBX,40,RMC,0,1,0,0*46
  gpsSerial.println("$PUBX,40,RMC,0,1,0,0*46");
  delay(100);

  // Enable $PUBX,40,GGA,0,1,0,0*5B
  gpsSerial.println("$PUBX,40,GGA,0,1,0,0*5B");
  delay(100);

  // disable $PUBX,40,GLL,0,0,0,0*5C
  gpsSerial.println("$PUBX,40,GLL,0,0,0,0*5C");
  delay(100);
  
  // disable $PUBX,40,VTG,0,0,0,0*5E
  gpsSerial.println("$PUBX,40,VTG,0,0,0,0*5E");
  delay(100);
  
  // disable $PUBX,40,GSA,0,0,0,0*4E
  gpsSerial.println("$PUBX,40,GSA,0,0,0,0*4E");
  delay(100);  

  // disable $PUBX,40,GSV,0,0,0,0*59
  gpsSerial.println("$PUBX,40,GSV,0,0,0,0*59");
  delay(100);
  
}


void SelectGGAonly()
{
  // NMEA_GLL output interval - Geographic Position - Latitude longitude
  // NMEA_RMC output interval - Recommended Minimum Specific GNSS Sentence
  // NMEA_VTG output interval - Course Over Ground and Ground Speed
  // NMEA_GGA output interval - GPS Fix Data
  // NMEA_GSA output interval - GNSS DOPS and Active Satellites
  // NMEA_GSV output interval - GNSS Satellites in View

  // Enable $PUBX,40,GGA,0,1,0,0*5B
  gpsSerial.println("$PUBX,40,GGA,0,1,0,0*5B");
  delay(100);

  // disable $PUBX,40,RMC,0,0,0,0*47
  gpsSerial.println("$PUBX,40,RMC,0,0,0,0*47");
  delay(100);

  // disable $PUBX,40,GLL,0,0,0,0*5C
  gpsSerial.println("$PUBX,40,GLL,0,0,0,0*5C");
  delay(100);

  // disable $PUBX,40,VTG,0,0,0,0*5E
  gpsSerial.println("$PUBX,40,VTG,0,0,0,0*5E");
  delay(100);
  
  // disable $PUBX,40,GSA,0,0,0,0*4E
  gpsSerial.println("$PUBX,40,GSA,0,0,0,0*4E");
  delay(100);  

  // disable $PUBX,40,GSV,0,0,0,0*59
  gpsSerial.println("$PUBX,40,GSV,0,0,0,0*59");
  delay(100);

}
