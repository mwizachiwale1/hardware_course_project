# hardware_course_project
 This project contains code for my hardware project which comprises of utilizing microcontrolers, sensors and actuators

#include <WiFi.h>
#include <WiFiMulti.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <MFRC522.h>  // RFID library
#include <SPI.h>
#include <WebSocketsClient_Generic.h>
#include <ArduinoJson.h>

WiFiMulti WiFiMulti;
WebSocketsClient webSocket;

#define RELAY_PIN 13
#define BUZZER_PIN 12
#define DHTPIN 14
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// RFID configuration
#define SS_PIN 5
#define RST_PIN 4
MFRC522 rfid(SS_PIN, RST_PIN);  // Create instance of the RFID reader

// Predefined RFID UID (replace with your tag UID)
byte predefinedRFID[] = {0x5C, 0x0F, 0x7B, 0x75};  // Example UID

// Server address and endpoint for relay state
const char* serverName = "http://192.168.43.52:8002/weather/api/get-bulb-state/";

// WebSocket configuration
const char* wsServer = "192.168.43.52";  // WebSocket server IP
const int wsPort = 8002;                 // WebSocket server port

// Function to print hex dump for binary messages (for WebSocket callback)
void hexdump(const void *mem, const uint32_t& len, const uint8_t& cols = 16) {
  const uint8_t* src = (const uint8_t*) mem;
  Serial.printf("\n[HEXDUMP] Address: 0x%08X len: 0x%X (%d)", (ptrdiff_t)src, len, len);
  for (uint32_t i = 0; i < len; i++) {
    if (i % cols == 0) {
      Serial.printf("\n[0x%08X] 0x%08X: ", (ptrdiff_t)src, i);
    }
    Serial.printf("%02X ", *src);
    src++;
  }
  Serial.printf("\n");
}

// WebSocket event handler
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.println("[WSc] Disconnected!");
      break;
    case WStype_CONNECTED:
      Serial.println("[WSc] Connected to server.");
      break;
    case WStype_TEXT:
      Serial.printf("[WSc] Received text: %s\n", payload);
      break;
    default:
      break;
  }
}

void setup() {
  Serial.begin(115200);
  while (!Serial);

  // Initialize DHT sensor
  dht.begin();
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);  // Start with relay OFF
  digitalWrite(BUZZER_PIN, LOW); // Start with buzzer OFF

  // Initialize SPI and RFID module
  SPI.begin();
  rfid.PCD_Init();
  Serial.println("RFID reader initialized.");

  // Connect to WiFi
  WiFiMulti.addAP("Galaxy S9+49f2", "uvxl3993");
  while (WiFiMulti.run() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("\nConnected to WiFi!");

  // Initialize WebSocket client
  webSocket.begin(wsServer, wsPort, "/ws/sensor/");
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);  // Reconnect every 5 seconds
  webSocket.enableHeartbeat(15000, 3000, 2);  // Optional heartbeat
}

void loop() {
  // WebSocket loop to keep connection alive
  webSocket.loop();

  // Check relay state from server every 5 seconds
  static unsigned long lastRequestTime = 0;
  static unsigned long lastDHTReadTime = 0;
  unsigned long currentMillis = millis();

  if (currentMillis - lastRequestTime >= 5000) {
    lastRequestTime = currentMillis;
    checkBulbState();  // Fetch relay state from Django API
  }

  // Send temperature and humidity data every 5 seconds
  if (currentMillis - lastDHTReadTime >= 5000) {
    lastDHTReadTime = currentMillis;
    sendTemperatureHumidity();  // Read and send temperature and humidity
  }

  // Check for RFID scan and trigger buzzer if match
  checkRFID();
}

// Function to check relay state from server
void checkBulbState() {
  if (WiFiMulti.run() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);

    int httpResponseCode = http.GET();  // Send the request

    if (httpResponseCode > 0) {
      String payload = http.getString();
      Serial.println("Response payload: " + payload);

      // Parse the state from the response (ON or OFF)
      if (payload.indexOf("ON") != -1) {
        digitalWrite(RELAY_PIN, HIGH);  // Turn relay ON
        Serial.println("Relay turned ON");
      } else if (payload.indexOf("OFF") != -1) {
        digitalWrite(RELAY_PIN, LOW);  // Turn relay OFF
        Serial.println("Relay turned OFF");
      }
    } else {
      Serial.printf("Failed to retrieve relay state. Error: %s\n", http.errorToString(httpResponseCode).c_str());
    }

    http.end();
  }
}

// Function to check RFID and trigger buzzer if match is found
void checkRFID() {
  if (!rfid.PICC_IsNewCardPresent()) {
    return; // No card is present
  }

  if (!rfid.PICC_ReadCardSerial()) {
    return; // Unable to read card
  }

  Serial.print("RFID tag scanned. UID: ");
  for (byte i = 0; i < rfid.uid.size; i++) {
    Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(rfid.uid.uidByte[i], HEX);
  }
  Serial.println();

  // Check if the scanned RFID matches the predefined RFID
  if (checkRFIDMatch(predefinedRFID, rfid.uid.uidByte, rfid.uid.size)) {
    Serial.println("RFID match found! Activating buzzer.");
    digitalWrite(BUZZER_PIN, HIGH);  // Turn the buzzer ON
    delay(1000);  // Buzzer ON for 1 second
    digitalWrite(BUZZER_PIN, LOW);   // Turn the buzzer OFF
  } else {
    Serial.println("RFID does not match.");
  }

  rfid.PICC_HaltA();  // Halt the RFID card
  rfid.PCD_StopCrypto1();  // Stop the encryption on RFID card
}

// Function to check if RFID matches the predefined UID
bool checkRFIDMatch(byte *predefined, byte *scanned, byte length) {
  for (byte i = 0; i < length; i++) {
    if (predefined[i] != scanned[i]) {
      return false;  // RFID does not match
    }
  }
  return true;  // RFID match
}

// Function to send temperature and humidity data via WebSocket
void sendTemperatureHumidity() {
  // Read temperature and humidity
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Check if readings are valid
  if (!isnan(temperature) && !isnan(humidity)) {
    // Create JSON payload
    StaticJsonDocument<200> doc;
    doc["temperature"] = temperature;
    doc["humidity"] = humidity;

    // Convert JSON to string
    String jsonString;
    serializeJson(doc, jsonString);

    // Send the payload via WebSocket
    webSocket.sendTXT(jsonString);
    Serial.println("Data sent: " + jsonString);
  } else {
    Serial.println("Failed to read from DHT sensor!");
  }
}
