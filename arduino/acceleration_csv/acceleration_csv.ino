#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <WiFi.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <SPI.h>
#include <SD.h>
#include "FS.h"
#include <Adafruit_GFX.h>      // http://librarymanager/All#Adafruit_GFX_Library
#include <Adafruit_SSD1306.h>  // http://librarymanager/All#Adafruit_SSD1306
#include <ESP32Time.h>
#include "Adafruit_MAX1704X.h"
#include <Adafruit_NeoPixel.h>

Adafruit_NeoPixel rgb_led_1 = Adafruit_NeoPixel(1, 1, NEO_GRB + NEO_KHZ800);

#define BUFFER_SIZE 100  // Define the size of the buffer
struct SensorData {
  float accX;
  float accY;
  float accZ;
  float gyroX;
  float gyroY;
  float gyroZ;
  String timestamp;
};
SensorData buffer[BUFFER_SIZE];  // Create a buffer to store sensor data
int bufferIndex = 0;             // Index to keep track of the current position in the buffer
unsigned long lastSaveTime = 0;  // Variable to store the last time data was saved


#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

String filename;
File Data;
SPIClass sdspi = SPIClass();

const char* ssid = "SSID";
const char* password = "PASSWORD";

Adafruit_MPU6050 mpu;

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP);
ESP32Time rtc;

Adafruit_MAX17048 maxlipo;

void saveDataToSD() {
  rgb_led_1.setPixelColor(0, rgb_led_1.Color(102, 255, 255));
  rgb_led_1.show();
  Data = SD.open(filename, FILE_APPEND);
  if (Data) {
    for (int i = 0; i < bufferIndex; i++) {
      Data.print(buffer[i].accX);
      Data.print(",");
      Data.print(buffer[i].accY);
      Data.print(",");
      Data.print(buffer[i].accZ);
      Data.print(", ");
      Data.print(buffer[i].gyroX);
      Data.print(",");
      Data.print(buffer[i].gyroY);
      Data.print(",");
      Data.print(buffer[i].gyroZ);
      Data.print(",");
      Data.println(buffer[i].timestamp);
    }
    Data.close();
  }
  bufferIndex = 0;  // Reset buffer index after saving data
  rgb_led_1.setPixelColor(0, rgb_led_1.Color(0, 0, 0));
  rgb_led_1.show();
}

void setup(void) {
  Serial.begin(115200);

  delay(100);
  pinMode(IO_ENABLE, OUTPUT);
  digitalWrite(IO_ENABLE, LOW);
  delay(100);
  pinMode(PIN_IO3, OUTPUT);
  digitalWrite(PIN_IO3, LOW);

  rgb_led_1.begin();
  rgb_led_1.setBrightness(100);

  // Display
  display.begin(SSD1306_SWITCHCAPVCC, 0x3D);
  display.display();
  delay(100);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE, BLACK);
  display.setCursor(0, 0);

  // MPU
  display.println("Setup MPU6050");
  display.display();
  if (!mpu.begin(0x68, &Wire1)) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_44_HZ);
  Serial.println("");
  delay(100);


  // WiFi
  display.print("Setup WiFi");
  display.display();
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    display.print(".");
    display.display();
  }
  display.println();
  display.display();

  display.println("Setup NTP");
  display.display();
  timeClient.begin();
  timeClient.update();
  rtc.setTime(timeClient.getEpochTime());
  WiFi.disconnect();

  // SD
  pinMode(SD_ENABLE, OUTPUT);
  digitalWrite(SD_ENABLE, LOW);
  sdspi.begin(VSPI_SCLK, VSPI_MISO, VSPI_MOSI, VSPI_SS);
  display.print("Setup SD: ");
  display.display();
  filename = "/data_" + rtc.getTime("%F_%H-%M-%S") + ".csv";
  display.println(filename);
  display.display();
  SD.begin(VSPI_SS, sdspi);
  Data = SD.open(filename, FILE_WRITE);
  if (!Data) {
    display.println("No SD card found :(");
    display.display();
    while (1) {
      delay(10);
    }
  }
  Data.print("AccX");
  Data.print(",");
  Data.print("AccY");
  Data.print(",");
  Data.print("AccZ");
  Data.print(",");
  Data.print("GyrX");
  Data.print(",");
  Data.print("GyrY");
  Data.print(",");
  Data.print("GyrZ");
  Data.print(",");
  Data.println("Time");
  Data.close();

  display.println("Setup Battery");
  display.display();
  if (!maxlipo.begin()) {
    Serial.println(F("Couldnt find Adafruit MAX17048?\nMake sure a battery is plugged in!"));
    while (1) delay(10);
  }
}

void loop() {

  /* Get new sensor events with the readings */
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  String timestampString = "000" + String(rtc.getMillis());
  String timestamp = String(rtc.getEpoch()) + timestampString.substring(timestampString.length() - 3);

  display.clearDisplay();
  display.setCursor(0, 0);
  display.setTextColor(WHITE, BLACK);

  display.print("Acc. X: ");
  display.println(a.acceleration.x);
  display.print("Acc. Y: ");
  display.println(a.acceleration.y);
  display.print("Acc. Z: ");
  display.println(a.acceleration.z);
  display.print("Gyr. X: ");
  display.println(g.gyro.x);
  display.print("Gyr. Y: ");
  display.println(g.gyro.y);
  display.print("Gyr. Z: ");
  display.println(g.gyro.z);
  display.print("Time  : ");
  display.println(timestamp);
  display.print("Bat.  : ");
  display.print(maxlipo.cellPercent(), 1);
  display.println(" %");

  display.display();

  // Store data in the buffer
  buffer[bufferIndex].accX = a.acceleration.x;
  buffer[bufferIndex].accY = a.acceleration.y;
  buffer[bufferIndex].accZ = a.acceleration.z;
  buffer[bufferIndex].gyroX = g.gyro.x;
  buffer[bufferIndex].gyroY = g.gyro.y;
  buffer[bufferIndex].gyroZ = g.gyro.z;
  buffer[bufferIndex].timestamp = timestamp;
  bufferIndex++;

  // Check if the buffer is full or if one second has elapsed since the last save
  if (bufferIndex >= BUFFER_SIZE || millis() - lastSaveTime >= 1000) {
    saveDataToSD();           // Save data to SD card
    lastSaveTime = millis();  // Update the last save time
  }
}