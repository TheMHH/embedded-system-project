#include <WiFi.h>
#include <PubSubClient.h>
#include "esp_camera.h"
#include <ESP32Servo.h>

#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM     -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define Y1_GPIO_NUM       17
#define Y0_GPIO_NUM       16
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Servo pin
#define SERVO_PIN         14

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

const char* mqtt_server = "YOUR_MQTT_BROKER_IP";  // e.g., "192.168.1.100"
const int mqtt_port = 1883;
const char* mqtt_client_id = "esp32_cam_client";
const char* image_topic = "camera/image";
const char* position_topic = "servo/position";

const unsigned long PICTURE_INTERVAL_MS = 5000;

WiFiClient espClient;
PubSubClient client(espClient);
Servo servo;

camera_fb_t* fb = NULL;

int servoPosition = 90;
unsigned long lastPictureTime = 0;

void reconnectWiFi() {
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    Serial.print("Attempting to connect to WiFi...");
    WiFi.begin(ssid, password);
    delay(2000);
    attempts++;
    Serial.print(".");
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed!");
  }
}

void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect(mqtt_client_id)) {
      Serial.println("connected");
      client.subscribe(position_topic);
      Serial.print("Subscribed to topic: ");
      Serial.println(position_topic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  char payloadStr[length + 1];
  memcpy(payloadStr, payload, length);
  payloadStr[length] = '\0';
  
  int position = atoi(payloadStr);
  position = constrain(position, 0, 180);
  
  servoPosition = position;
  servo.write(servoPosition);
  
  Serial.print("Servo position set to: ");
  Serial.println(servoPosition);
}

bool initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA;  // 320x240
  config.jpeg_quality = 12;
  config.fb_count = 1;
  
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return false;
  }
  
  Serial.println("Camera initialized successfully");
  return true;
}

void sendPicture() {
  fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }
  
  if (client.publish(image_topic, (const uint8_t*)fb->buf, fb->len)) {
    Serial.print("Published image (");
    Serial.print(fb->len);
    Serial.println(" bytes)");
  } else {
    Serial.println("Failed to publish image");
  }
  
  esp_camera_fb_return(fb);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("ESP32-CAM Picture Sender Starting...");
  
  servo.attach(SERVO_PIN);
  servo.write(servoPosition);
  Serial.println("Servo initialized");
  
  if (!initCamera()) {
    Serial.println("Camera initialization failed. Restarting...");
    delay(5000);
    ESP.restart();
  }
  
  WiFi.mode(WIFI_STA);
  reconnectWiFi();
  
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  Serial.println("Setup complete!");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Reconnecting...");
    reconnectWiFi();
  }
  
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();
  
  unsigned long currentTime = millis();
  if (currentTime - lastPictureTime >= PICTURE_INTERVAL_MS) {
    sendPicture();
    lastPictureTime = currentTime;
  }
  
  delay(10);
}

