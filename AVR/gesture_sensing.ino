#include<Wire.h>
#include<SparkFun_APDS9960.h>
#define AINT 2

//refered: http://makezine.jp/blog/2015/10/apds-9960.html
//you must use modified c++ library
//Wiring "atmega328(can use arduinoUNO or nano) -  APDS9960(gesture sensor)"
//A5-SCL,A4-SDA,D2-INT,GND-GND,3.3V-LED&VDD
//

SparkFun_APDS9960 apds=SparkFun_APDS9960();
int isr_flag=0;
uint8_t proximity_data=0;

void interruptRoutine(){
isr_flag=1;
}
void handleGesture(){
if(apds.isGestureAvailable()){
	//this part is different to original (use readGesture2)
	Serial.print(apds.readGesture2());

}
}

void setup(){
	pinMode(AINT,INPUT_PULLUP);
	Serial.begin(9600);
	attachInterrupt(0,interruptRoutine,FALLING);
	if(apds.init()){
		Serial.println(F("APDS-9960 initialization complete"));
	}else{
		Serial.println(F("Something went wrong during APDS9960 init!"));
	}
	if(apds.enableGestureSensor(true)){
		Serial.println(F("Gesture sensor is now running"));
	}else{
		Serial.println(F("Something went wrong during gesture sensor init!"));
}
}

void loop(){
if(isr_flag==1){
detachInterrupt(AINT);
handleGesture();
isr_flag=0;
attachInterrupt(AINT,interruptRoutine,FALLING);
}
}

