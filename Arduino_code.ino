// OneWire DS18S20, DS18B20, DS1822 Temperature Example
//
// http://www.pjrc.com/teensy/td_libs_OneWire.html

#include <OneWire.h>

void setup() {
  Serial.begin(9600);
}

const float baselineTemp = 20.0;
char host_Message[10];
int num;

float getTemprature(int pinSensor){
   int sensorVal = analogRead(pinSensor);
   float voltage = (sensorVal / 1024.0) * 5.0; 
   float temprature = (voltage - .5) * 100;
   return temprature;
}

float getCellTemprature(int pinSensor){ 
      OneWire  ds(pinSensor);

      int sensor;
      byte i;                       // for cycles   
      byte present = 0;             // is it present 
      byte type_s;                  // type of sensor 
      byte data[12];                // data read from sensor 
      byte addr[8];                 // address also read from sensor  

      ds.search(addr); 
        
      if (OneWire::crc8(addr, 7) != addr[7]) {   // Check if the address is ok 
          return 0 ;
      }
      // the first ROM byte indicates which chip
      switch (addr[0]) {
          case 0x10:
      // Serial.println("  Chip = DS18S20");  // or old DS1820
               type_s = 1;
               break;
          case 0x28:
               //Serial.println("  Chip = DS18B20");
               type_s = 0;
               break;
          case 0x22:
               // Serial.println("  Chip = DS1822");
               type_s = 0;
               break;
          default:
               // Serial.println("Device is not a DS18x20 family device.");
               return 0;
      } 
      ds.reset();
      ds.select(addr);      //  choose the sensor the arduino  will be talking   
      ds.write(0x44);        // start conversion, use ds.write(0x44,1) with parasite power on at the end
            
      delay(50);     // maybe 750ms is enough, maybe not
              
      // we might do a ds.depower() here, but the reset will take care of it.
            
      present = ds.reset();
      ds.select(addr);    
      ds.write(0xBE);         // Read Scratchpad
            
          
      for ( i = 0; i < 9; i++) {           // we need 9 bytes
          data[i] = ds.read();
      }
            
      // Convert the data to actual temperature
      // because the result is a 16 bit signed integer, it should
      // be stored to an "int16_t" type, which is always 16 bits
      // even when compiled on a 32 bit processor.
      int16_t raw = (data[1] << 8) | data[0];
      if (type_s) {
          raw = raw << 3; // 9 bit resolution default
          if (data[7] == 0x10) {
                  // "count remain" gives full 12 bit resolution
                  raw = (raw & 0xFFF0) + 12 - data[6];
          }
      } else {
          byte cfg = (data[4] & 0x60);    
          // at lower res, the low bits are undefined, so let's zero them
          if (cfg == 0x00) raw = raw & ~7;  // 9 bit resolution, 93.75 ms
          else if (cfg == 0x20) raw = raw & ~3; // 10 bit res, 187.5 ms
          else if (cfg == 0x40) raw = raw & ~1; // 11 bit res, 375 ms
           //// default is 12 bit resolution, 750 ms conversion time
      }
      float celsius = (float)raw / 16.0;
      ds.reset_search();
      return celsius; 
    }

void loop() {
  byte i;
  while(!Serial.available())
    ;
    num = Serial.readBytes(host_Message,1);
    //Serial.println(num)
    if(num!=1) return;
    i = host_Message[0]-'0';
    switch(i){ 
      //Pin A0 predefined as outside temprature other pins correspond to cells 
      case 0 : Serial.println(getTemprature(A0));
               break;
          
      case 1 : Serial.println(getCellTemprature(10));
               break;
               
      case 2 : Serial.println(getCellTemprature(11));
               break;
               
       case 3 : Serial.println(getCellTemprature(6));
               break;
               
       case 4 : Serial.println(getCellTemprature(6));
               break;
               
       case 5 : Serial.println(getCellTemprature(0));
               break;
                
      default : return;
    }
    return;
}
