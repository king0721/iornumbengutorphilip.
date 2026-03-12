#include <DHT.h>

#define DHTPIN 4
#define DHTTYPE DHT22
#define MQ4_PIN 34
#define FAN_PIN 26
#define HEATER_PIN 27

DHT dht(DHTPIN, DHTTYPE);

float methaneThreshold = 300;
float tempMin = 25;
float tempMax = 35;

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(FAN_PIN, OUTPUT);
  pinMode(HEATER_PIN, OUTPUT);
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int methane = analogRead(MQ4_PIN);

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("ERROR: Failed to read DHT sensor");
    delay(2000);
    return;
  }

  Serial.print("Temperature: ");
  Serial.println(temperature);
  Serial.print("Humidity: ");
  Serial.println(humidity);
  Serial.print("Methane Level: ");
  Serial.println(methane);

  // Machine-readable log line for the Python logger
  Serial.print("DATA,");
  Serial.print(temperature, 2);
  Serial.print(",");
  Serial.print(humidity, 2);
  Serial.print(",");
  Serial.println(methane);

  if (temperature > tempMax) {
    digitalWrite(FAN_PIN, HIGH);
  } else {
    digitalWrite(FAN_PIN, LOW);
  }

  if (temperature < tempMin) {
    digitalWrite(HEATER_PIN, HIGH);
  } else {
    digitalWrite(HEATER_PIN, LOW);
  }

  if (methane > methaneThreshold) {
    Serial.println("WARNING: Methane levels high");
  }

  delay(5000);
}
