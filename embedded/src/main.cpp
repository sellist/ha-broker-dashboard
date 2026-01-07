#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include "secrets.h"

const char* TOPIC_TEMPERATURE = "home/living_room/temperature";
const char* TOPIC_HUMIDITY = "home/living_room/humidity";
const char* TOPIC_STATUS = "home/living_room/status";

#define DHT_PIN 4
#define DHT_TYPE DHT11

const unsigned long SENSOR_READ_INTERVAL = 60000;
const unsigned long WIFI_RETRY_DELAY = 5000;
const unsigned long MQTT_RETRY_DELAY = 5000;

#define LED_BUILTIN 2

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
DHT dht(DHT_PIN, DHT_TYPE);

unsigned long lastSensorRead = 0;

void setupWiFi();
void setupMQTT();
void reconnectMQTT();
void readAndPublishSensorData();
void blinkLED(int times, int delayMs);

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  dht.begin();
  Serial.println("Sensor initialized on GPIO " + String(DHT_PIN));

  setupWiFi();
  setupMQTT();
  blinkLED(3, 200);
  
  Serial.println("\n[SYSTEM] Setup complete. Starting main loop...\n");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    setupWiFi();
  }

  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop();

  unsigned long currentMillis = millis();
  if (currentMillis - lastSensorRead >= SENSOR_READ_INTERVAL) {
    lastSensorRead = currentMillis;
    readAndPublishSensorData();
  }
}

void setupWiFi() {
  Serial.print("Connecting to ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to connect. Will retry...");
  }
}

void setupMQTT() {
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  Serial.print("[MQTT] Broker configured: ");
  Serial.print(MQTT_BROKER);
  Serial.print(":");
  Serial.println(MQTT_PORT);
}

void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("[MQTT] Attempting connection...");
    
    if (mqttClient.connect(MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD)) {
      Serial.println(" connected");
      mqttClient.publish(TOPIC_STATUS, "online", true);
      Serial.println("[MQTT] Published online status");
    } else {
      Serial.print(" failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(". Retrying in 5 seconds...");
      delay(MQTT_RETRY_DELAY);
    }
  }
}

void readAndPublishSensorData() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("[DHT] Error: Failed to read from sensor!");
    return;
  }

  Serial.print("[Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");

  char tempStr[8];
  char humStr[8];
  dtostrf(temperature, 4, 1, tempStr);
  dtostrf(humidity, 4, 1, humStr);

  if (mqttClient.connected()) {
    bool tempPublished = mqttClient.publish(TOPIC_TEMPERATURE, tempStr);
    bool humPublished = mqttClient.publish(TOPIC_HUMIDITY, humStr);

    if (tempPublished && humPublished) {
      Serial.println("Data published successfully");
      blinkLED(1, 100);
    } else {
      Serial.println("Error: Failed to publish data");
    }
  } else {
    Serial.println("Error: Not connected to broker");
  }
}

void blinkLED(int times, int delayMs) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(delayMs);
    digitalWrite(LED_BUILTIN, LOW);
    delay(delayMs);
  }
}