# Embedded System Project - Face Tracking with ESP32-CAM

An embedded system project that uses an ESP32-CAM to capture images, detect faces using OpenCV, and control a servo motor based on face position via MQTT communication.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This project implements a face-tracking system where:
1. **ESP32-CAM** captures images at regular intervals and sends them via MQTT
2. **Python Server** receives images, detects faces using OpenCV, and calculates servo position
3. **Servo Motor** is controlled based on the detected face's horizontal position (0-180 degrees)
4. **MQTT Broker** (Mosquitto) handles message communication between components

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│ ESP32-CAM   │────────▶│ MQTT Broker  │────────▶│ Python     │
│             │ publish │ (Mosquitto)  │ publish │ Server     │
│ - Camera    │ images  │              │ position│ - OpenCV   │
│ - Servo     │◀────────│              │◀────────│ - Face     │
│             │ position│              │ subscribe│   Detection│
└─────────────┘         └──────────────┘         └─────────────┘
```

### MQTT Topics

- `camera/image` - ESP32-CAM publishes JPEG images here
- `servo/position` - Python server publishes servo position (0-180) here

## 🔧 Components

### Hardware
- **ESP32-CAM** (AI-Thinker) - Camera module with WiFi
- **Servo Motor** - Connected to GPIO pin 14
- **WiFi Network** - For MQTT communication

### Software
- **Arduino IDE** - For ESP32-CAM firmware
- **Python 3** - For face detection server
- **OpenCV** - Face detection library
- **Mosquitto** - MQTT broker (Docker)

## 📦 Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Arduino IDE with ESP32 board support
- WiFi network access
- MQTT broker (provided via Docker)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone git@github.com:TheMHH/embedded-system-project.git
cd embedded-system-project
```

### 2. Start MQTT Broker

```bash
make broker-up
```

Or manually:
```bash
docker-compose up -d
```

### 3. Install Python Dependencies

```bash
make install
```

Or manually:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r python-server/requirements.txt
```

### 4. Configure ESP32-CAM

1. Open `esp32-cam/esp32_face_tracker.ino` in Arduino IDE
2. Update the following constants:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   const char* mqtt_server = "YOUR_MQTT_BROKER_IP";  // e.g., "192.168.1.100"
   ```
3. Upload to ESP32-CAM

## ⚙️ Configuration

### ESP32-CAM Settings

Edit `esp32-cam/esp32_face_tracker.ino`:

- **WiFi**: Set your network SSID and password
- **MQTT Server**: Set your MQTT broker IP address
- **Picture Interval**: Adjust `PICTURE_INTERVAL_MS` (default: 5000ms = 5 seconds)
- **Servo Pin**: Currently set to GPIO 14

### Python Server Settings

Edit `python-server/face_tracker_server.py`:

- **MQTT Broker**: Default is `localhost` (change if broker is remote)
- **MQTT Port**: Default is `1883`

## 💻 Usage

### Start MQTT Broker

```bash
make broker-up
```

Check status:
```bash
make broker-status
```

View logs:
```bash
make broker-logs
```

### Run Python Server

```bash
make run
```

Or manually:
```bash
source .venv/bin/activate
python python-server/face_tracker_server.py
```

### Stop Services

```bash
make broker-down
```

## 📁 Project Structure

```
embedded-system-project/
├── docker-compose.yml          # Mosquitto MQTT broker configuration
├── Makefile                    # Build and run commands
├── README.md                   # This file
├── LICENSE                     # License file
├── .gitignore                  # Git ignore rules
│
├── esp32-cam/
│   └── esp32_face_tracker.ino  # ESP32-CAM firmware
│
├── python-server/
│   ├── face_tracker_server.py  # Main Python server
│   ├── mqtt_test.py            # MQTT connection test
│   ├── open-cv_test.py         # OpenCV face detection test
│   └── requirements.txt        # Python dependencies
│
└── mosquitto/
    ├── config/
    │   └── mosquitto.conf      # MQTT broker configuration
    ├── data/                   # MQTT broker data (gitignored)
    └── log/                    # MQTT broker logs (gitignored)
```

## 🧪 Testing

### Test MQTT Broker

```bash
make test
```

Or manually:
```bash
source .venv/bin/activate
python python-server/mqtt_test.py
```

### Test Face Detection

1. Place a test image (`test_image.jpg`) in the `python-server/` directory
2. Run:
```bash
source .venv/bin/activate
python python-server/open-cv_test.py
```

Or test with a specific image:
```bash
python python-server/open-cv_test.py path/to/image.jpg
```

### Test ESP32-CAM

1. Upload the firmware to ESP32-CAM
2. Open Serial Monitor (115200 baud)
3. Verify:
   - WiFi connection successful
   - MQTT connection successful
   - Images being captured and sent
   - Servo responding to position commands

## 🔍 Troubleshooting

### MQTT Connection Issues

- **ESP32 can't connect to MQTT broker**
  - Verify broker IP address is correct
  - Check if broker is running: `make broker-status`
  - Ensure ESP32 and broker are on the same network
  - Check firewall settings

- **Python server can't connect**
  - Verify broker is running: `docker ps`
  - Check if using correct host (localhost vs IP address)
  - Verify port 1883 is accessible

### Face Detection Issues

- **No face detected**
  - Ensure good lighting conditions
  - Check image quality/resolution
  - Verify OpenCV is properly installed
  - Test with `open-cv_test.py` using a known good image

- **Position calculation incorrect**
  - Verify image width matches ESP32-CAM resolution (320x240)
  - Check face detection is working correctly
  - Review position mapping logic in `extract_position()`

### ESP32-CAM Issues

- **Camera initialization failed**
  - Check camera module connections
  - Verify pin definitions match your ESP32-CAM model
  - Try restarting the device

- **WiFi connection failed**
  - Verify SSID and password are correct
  - Check WiFi signal strength
  - Ensure 2.4GHz network (ESP32 doesn't support 5GHz)

- **Servo not moving**
  - Verify servo is connected to correct GPIO pin (14)
  - Check servo power supply
  - Test servo with simple Arduino sketch

## 📝 Makefile Commands

```bash
make help           # Show all available commands
make broker-up      # Start MQTT broker
make broker-down    # Stop MQTT broker
make broker-restart # Restart MQTT broker
make broker-logs    # View broker logs
make broker-status  # Check broker status
make install        # Install Python dependencies
make run            # Run Python server
make test           # Test MQTT connection
```

## 📄 License

See [LICENSE](LICENSE) file for details.

## 📧 Contact

For questions or issues, please open an issue on GitHub.
