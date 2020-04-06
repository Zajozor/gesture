
// Resources
// ****************************************************************************
// Basic Arduino code
// I2C checking from https://github.com/jainrk/i2c_port_address_scanner/blob/master/i2c_port_address_scanner/i2c_port_address_scanner.ino

// Includes & defines & constants
// ****************************************************************************
#include <Arduino.h>
#include <Wire.h>
#include <MPU6050.h>

#define MPUADDR 0x68 // I2C address of the MPU-6050
#define TCAADDR 0x70 // I2C address of the TCA multiplexer
#define SENSOR_RANGE_START 2 // The IDs of the ports where
#define SENSOR_RANGE_END 6   // the MPU-6050's are wired.

#define BAUDRATE 460800

const uint8_t portArray[] = {16, 5, 4, 0, 2, 14, 12, 13};
const String dPortMap[] = {"D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7"};
const String portMap[] = {"GPIO16", "GPIO5", "GPIO4", "GPIO0", "GPIO2", "GPIO14", "GPIO12", "GPIO13"};

struct sensorData {
  int16_t accX;
  int16_t accY;
  int16_t accZ;
  int16_t gyrX;
  int16_t gyrY;
  int16_t gyrZ;
};

// Functions in module
// ****************************************************************************
bool findConnection();
void multiplexer_select(uint8_t i);
void calibrate_sensor(uint8_t i);

// Globals
// ****************************************************************************
uint8_t sdaPort;
uint8_t sclPort;

MPU6050 sensor(MPUADDR);

sensorData offsets[8];

// Setup and loop
// ****************************************************************************

void setup()
{
  Serial.begin(BAUDRATE);
  Serial.println("\n\nGesture framework glove starting up.");

  while (!findConnection()) {}
  Serial.print("Connection to multiplexer found on SDA:");
  Serial.print(dPortMap[sdaPort]);
  Serial.print(" SCL:");
  Serial.println(dPortMap[sclPort]);

  for (uint8_t i = SENSOR_RANGE_START; i <= SENSOR_RANGE_END; i++) {
    multiplexer_select(i);
    Serial.print("Sensor "); Serial.print(i); Serial.print(": MPU6050 connection ");
    sensor.initialize();
    Serial.println(sensor.testConnection() ? "successful" : "failed");
    calibrate_sensor(i);    
  }
  Serial.println("Setup complete.");
}

void loop()
{
  sensorData data;
  
  ulong t1 = millis();
  for (uint8_t i = SENSOR_RANGE_START; i <= SENSOR_RANGE_END; i++) {
    multiplexer_select(i);
    sensor.getMotion6(&data.accX, &data.accY, &data.accZ, &data.gyrX, &data.gyrY, &data.gyrZ);

    Serial.write(i);

    data.accX -= offsets[i].accX;
    data.accY -= offsets[i].accY;
    data.accZ -= offsets[i].accZ;
    data.gyrX -= offsets[i].gyrX;
    data.gyrY -= offsets[i].gyrY;
    data.gyrZ -= offsets[i].gyrZ;

    Serial.write(data.accX >> 8); Serial.write(data.accX & 0xFF);
    Serial.write(data.accY >> 8); Serial.write(data.accY & 0xFF);
    Serial.write(data.accZ >> 8); Serial.write(data.accZ & 0xFF);
    Serial.write(data.gyrX >> 8); Serial.write(data.gyrX & 0xFF);
    Serial.write(data.gyrY >> 8); Serial.write(data.gyrY & 0xFF);
    Serial.write(data.gyrZ >> 8); Serial.write(data.gyrZ & 0xFF);
    // This serves as a separator to find the edge easier
    Serial.write(255);
    Serial.println();

    // For readable output:
    // Serial.print("Sensor "); Serial.print(i);
    // Serial.print(" a/g:\t");
    // Serial.print(data.accX - offsets[i].accX); Serial.print("\t");
    // Serial.print(data.accY - offsets[i].accY); Serial.print("\t");
    // Serial.print(data.accZ - offsets[i].accZ); Serial.print("\tg:\t");
    // Serial.print(data.gyrX - offsets[i].gyrX); Serial.print("\t");
    // Serial.print(data.gyrY - offsets[i].gyrY); Serial.print("\t");
    // Serial.println(data.gyrZ - offsets[i].gyrZ);
  }
  delay(15 - (millis() - t1));
}

// Function bodies
// ****************************************************************************

bool findConnection()
{
  for (uint8_t i = 0; i < sizeof(portArray); i++) {
    for (uint8_t j = 0; j < sizeof(portArray); j++) {
      if (i != j) {
        Wire.begin(portArray[i], portArray[j]);

        Wire.beginTransmission(TCAADDR);
        byte error = Wire.endTransmission();
        if (!error) {
          sdaPort = i;
          sclPort = j;
          return true;
        }
      }
    }
  }
  return false;
}

void multiplexer_select(uint8_t i) {
  // Select's i'th channel on the multiplexer
  if (i > 7) return;

  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}

void calibrate_sensor(uint8_t sensorId) {
  multiplexer_select(sensorId);
  sensorData calData;
  int32_t accX = 0, accY = 0, accZ = 0,
          gyrX = 0, gyrY = 0, gyrZ = 0;

  for (uint8_t i = 0; i < 100; i++) {    
    sensor.getMotion6(
      &calData.accX, &calData.accY, &calData.accZ,
      &calData.gyrX, &calData.gyrY, &calData.gyrZ
    );
    accX += calData.accX; accY += calData.accY; accZ += calData.accZ;
    gyrX += calData.gyrX; gyrY += calData.gyrY; gyrZ += calData.gyrZ;
  }
  offsets[sensorId].accX = (int16_t)(accX / 100);
  offsets[sensorId].accY = (int16_t)(accY / 100);
  offsets[sensorId].accZ = (int16_t)(accZ / 100);
  offsets[sensorId].gyrX = (int16_t)(gyrX / 100);
  offsets[sensorId].gyrY = (int16_t)(gyrY / 100);
  offsets[sensorId].gyrZ = (int16_t)(gyrZ / 100);
  Serial.print("Sensor "); Serial.print(sensorId); Serial.println(" calibrated.");
}
