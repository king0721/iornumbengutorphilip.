#define SOLAR_SENSOR 35
#define BIOGAS_VALVE 14
#define POWER_RELAY 12

int solarThreshold = 600;

void setup() {
  Serial.begin(115200);
  pinMode(BIOGAS_VALVE, OUTPUT);
  pinMode(POWER_RELAY, OUTPUT);
}

void loop() {
  int solarLevel = analogRead(SOLAR_SENSOR);

  if (solarLevel > solarThreshold) {
    digitalWrite(POWER_RELAY, HIGH);
    digitalWrite(BIOGAS_VALVE, LOW);
    Serial.println("Running on Solar Power");
  } else {
    digitalWrite(POWER_RELAY, LOW);
    digitalWrite(BIOGAS_VALVE, HIGH);
    Serial.println("Switching to Biogas Power");
  }

  delay(3000);
}
