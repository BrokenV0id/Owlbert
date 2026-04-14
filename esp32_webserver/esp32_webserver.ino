// =========== LIBRARIES ===========
#include <WiFi.h>
#include <WebServer.h>

// =========== VARIABLES ===========
WebServer server(80);

// =========== FUNCTIONS ===========
void handle_root() {
  server.send(200);
}

void handle_int(int value) {
  Serial.println(value);
  server.send(200, "text/plain", "OK");
}

void handle_string(String value) {
  Serial.println(value);
  server.send(200, "text/plain", "OK");
}

void setup() {
  Serial.begin(115200);

  WiFi.begin("", ""); // SSID, PASSWORD
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("IP");
  Serial.println(WiFi.localIP());

  server.on("/", handle_root);

  server.on("/int", []() {
    if (server.hasArg("value")) {
      handle_int(server.arg("value").toInt());
    }
  });

  server.on("/string", []() {
    if (server.hasArg("value")) {
      handle_string(server.arg("value"));
    }
  });

  server.begin();
}

void loop() {
  server.handleClient();
}
