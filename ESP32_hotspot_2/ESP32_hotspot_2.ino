#include <WiFi.h>

const char *ssid = "Pk";
const char *password = "12345678";

void setup() {
  Serial.begin(115200);

  // Start the ESP32 as a Wi-Fi Access Point
  WiFi.softAP(ssid, password);

  Serial.println("Access Point started.");
  Serial.print("SSID: ");
  Serial.println(ssid);
  Serial.print("IP Address: ");
  Serial.println(WiFi.softAPIP());
}

void printConnectedDevices() {
  // Get the number of connected devices
  int numStations = WiFi.softAPgetStationNum();
  Serial.print("Number of connected devices: ");
  Serial.println(numStations);

  // NOTE: WiFi.softAPgetStationInfo is not available in the Arduino core.
  Serial.println("MAC addresses of connected devices cannot be displayed without esp_wifi functions.");
}

void loop() {
  // Print connected devices every 10 seconds
  printConnectedDevices();
  delay(10000);
}
