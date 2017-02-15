/*
 edited by Zajozor, 2017
 based on:
 
 created back in the mists of time
 modified 25 May 2012
 by Tom Igoe
 based on Mikal Hart's example

 This example code is in the public domain.

 */
#include <SoftwareSerial.h>
//SoftwareSerial mySerial(5, 6); // RX, TX (the blutooth chip RX is connected to 6, and TX to 5)
SoftwareSerial mySerial(11, 10); // RX, TX (the blutooth chip RX is connected to 6, and TX to 5)

void setup() {
  //HM-10 is connected straight to arduino on pins 2 to 7
/*
  // 3 is VCC (HIGH)
  pinMode(3,OUTPUT);  
  digitalWrite(3,HIGH);
  // 4 is GND (LOW)
  pinMode(4,OUTPUT);
  digitalWrite(4,LOW);  
  */
  //Serial.begin(115200);
  Serial.begin(57600);
  while (!Serial) ;

  //mySerial.begin(115200);
  mySerial.begin(57600);
  mySerial.println("greetings");
  Serial.println("Initialized receiver, tried to greet");
}

void loop() {
  if (mySerial.available()) { Serial.write(mySerial.read()); }
  if (Serial.available()) { mySerial.write(Serial.read()); }
}

