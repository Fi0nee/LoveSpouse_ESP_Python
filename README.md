# LoveSpouse ESP32 Controller

This project is designed to easily control cheap toys that use Muse/LoveSpouse applications via a web interface.

## Project composition

- LoveSpouseESP32.ino  
  A sketch for ESP32 that allows you to send BLE packets to the device.
- LoveSpouse.py  
  Python script for controlling ESP32 via web server.

---

## Installation and configuration

### Preparing ESP32

1. Open LoveSpouseESP32.ino in Arduino IDE.
2. Install the [`NimBLE-Arduino`](https://github.com/h2zero/NimBLE-Arduino) library version 1.4.2.
3. Upload the sketch to your ESP32.

### Preparing the server

1. Install the required Python libraries:
   ```
    pip install flask pyserial
   ```
2. Open the LoveSpouse.py file and edit the line:
   ```
    SERIAL_PORT = "COM5"
   ```
   Replace "COM5" with the port your ESP32 is connected to.

3. Start the server:
   ```
    python LoveSpouse.py
   ```
4. Open http://localhost:5000 in your browser to manage your device via the web interface.

---

## Requirements

- ESP32 microcontroller
- NimBLE-Arduino library v1.4.2
- Python 3.8+ with installed libraries:
- flask
- pyserial
- A toy compatible with Muse or LoveSpouse apps

---

## Notes

- The project is in early development.
- There may be delays and bugs when transmitting commands via BLE.
- Only basic control functionality is supported.
