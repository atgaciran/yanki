#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

#define DEVICE_ID 1
#define DEVICE_COORD "39.919828, 41.240187"

#define DHTPIN 9       
#define PIRPIN 3       
#define SOUNDPIN 4     
#define RED_LED 5      
#define GREEN_LED 6    


#define DHTTYPE DHT11  


DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2); 


unsigned long currentMillis = 0;


unsigned long sensorReadTimer = 0;
const long sensorInterval = 5000; 


unsigned long lastSoundTime = 0;
const long soundCooldown = 4000; 


unsigned long messageDisplayTime = 0;
bool isMessageShowing = false; 


float lastTemp = 0.0;
float lastHum = 0.0;


bool helpIsComing = false; 

void setup() {
  Serial.begin(9600); 
  
  pinMode(PIRPIN, INPUT);
  pinMode(SOUNDPIN, INPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  

  digitalWrite(RED_LED, HIGH);
  digitalWrite(GREEN_LED, LOW);
  
  dht.begin();
  lcd.init();
  lcd.backlight();
  
  // Açılış Ekranı
  lcd.setCursor(0,0);
  lcd.print("ID: ");
  lcd.print(DEVICE_ID); 
  lcd.setCursor(0,1);
  lcd.print("Konum Ayarlandi");
  delay(2000);
  lcd.clear();
  
  updateDHT();
}

void loop() {
  currentMillis = millis();


  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n'); 
    message.trim(); 
    
    // EKİPLER GELDİ KOMUTU
    if (message == "GREEN_ON") {
      helpIsComing = true;          
      
     
      digitalWrite(RED_LED, LOW);   
      digitalWrite(GREEN_LED, HIGH);
      
      
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("EKIPLER YOLA");  
      lcd.setCursor(0, 1);
      lcd.print("CIKTI...");      
    }
    
    else if (message == "RESET") {
      helpIsComing = false;
      digitalWrite(RED_LED, HIGH);
      digitalWrite(GREEN_LED, LOW);
      lcd.clear(); 
      isMessageShowing = false; 
    }
  }

  
  if (helpIsComing) {
    return; 
  }


  
  int motionVal = digitalRead(PIRPIN);
  int soundVal = digitalRead(SOUNDPIN);
  

  if (motionVal == HIGH) {
    if (!isMessageShowing || (currentMillis - messageDisplayTime > 2000)) { 
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Hareket Verisi");
        lcd.setCursor(0, 1);
        lcd.print("Gonderildi!");
        isMessageShowing = true;
        messageDisplayTime = currentMillis;
    }
    sendJsonData(lastTemp, lastHum, "var", "yok");
    delay(1500); 
  }

 
  else if (soundVal == HIGH && (currentMillis - lastSoundTime > soundCooldown)) {
    lastSoundTime = currentMillis;

    if (!isMessageShowing || (currentMillis - messageDisplayTime > 2000)) {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Ses Verisi");
        lcd.setCursor(0, 1);
        lcd.print("Gonderildi!");
        isMessageShowing = true;
        messageDisplayTime = currentMillis;
    }
    sendJsonData(lastTemp, lastHum, "yok", "var");
  }


  if (currentMillis - sensorReadTimer >= sensorInterval) {
    sensorReadTimer = currentMillis;
    updateDHT(); 
    
    sendJsonData(lastTemp, lastHum, "yok", "yok");
    
    if (!isMessageShowing) {
       printTempToLCD();
    }
  }


  if (isMessageShowing && (currentMillis - messageDisplayTime > 2000)) {
    isMessageShowing = false;
    lcd.clear();
    printTempToLCD(); 
  }
}



void updateDHT() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  if (!isnan(h) && !isnan(t)) {
    lastTemp = t;
    lastHum = h;
  }
}

void printTempToLCD() {
  lcd.setCursor(0, 0);
  lcd.print("Sicaklik: "); 
  lcd.print(lastTemp, 1); 
  lcd.print("C");
  lcd.setCursor(0, 1);
  lcd.print("Nem: %"); 
  lcd.print(lastHum, 1);
}

void sendJsonData(float temp, float hum, String hareket, String ses) {
  Serial.print("{\"id\":");
  Serial.print(DEVICE_ID);
  
  Serial.print(", \"koordinat\":\""); 
  Serial.print(DEVICE_COORD);         
  
  Serial.print("\", \"sicaklik\":");
  Serial.print(temp);
  Serial.print(", \"nem\":");
  Serial.print(hum);
  Serial.print(", \"ses\":\"");
  Serial.print(ses);
  Serial.print("\", \"hareket\":\"");
  Serial.print(hareket);
  Serial.println("\"}");
}