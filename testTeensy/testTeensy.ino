void setup() {
  while (!Serial);
  
  int avg = 1;
  // int avg = 4;
  
  for (int res = 8; res <= 16; res += 2) {
    if (res == 12 || res == 14) continue;
    
    Serial.print("res: ");
    Serial.print(res);
    Serial.print(", avg: ");
    Serial.println(avg);
    
    analogReadResolution(res);
    analogReadAveraging(avg);
    
    delay(250);
    for (int i = 0; i < 100; i++) {
      unsigned long beginMicros = micros();
      analogRead(23);
      unsigned long endMicros = micros();
      Serial.println(endMicros - beginMicros);
    }
  }
}

void loop() {}
