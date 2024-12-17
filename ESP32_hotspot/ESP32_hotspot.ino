#include <WiFi.h>

// Wi-Fi credentials
const char *ssid = "Pk";
const char *password = "12345678";

// Static IP configuration for the ESP32
IPAddress local_IP(192, 168, 4, 1); // ESP32's static IP
IPAddress gateway(192, 168, 4, 1);  // Gateway IP
IPAddress subnet(255, 255, 255, 0); // Subnet mask

void setup() {
  Serial.begin(115200);

  // Configure ESP32 as a Wi-Fi Access Point
  if (!WiFi.softAPConfig(local_IP, gateway, subnet)) {
    Serial.println("Failed to configure the access point with static IP.");
    return;
  }

  // Start the access point on channel 6, allowing up to 4 connections
  if (!WiFi.softAP(ssid, password, 6)) {
    Serial.println("Failed to start the access point.");
    return;
  }

  Serial.println("Access Point started.");
  Serial.print("SSID: ");
  Serial.println(ssid);
  Serial.print("IP Address: ");
  Serial.println(WiFi.softAPIP());
}

void loop() {
  // Monitor client connections
  Serial.print("Connected devices: ");
  Serial.println(WiFi.softAPgetStationNum());
  delay(5000);
}
