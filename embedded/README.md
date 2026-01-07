## Setup

1. Install [PlatformIO](https://platformio.org/install)

2. Copy the secrets template and add your credentials:
   ```
   cp include/secrets.h.example include/secrets.h
   ```

3. Edit `include/secrets.h` with your WiFi and MQTT broker details

## Deploy

Build and upload to the ESP32:
```
pio run -t upload
```

Monitor serial output:
```
pio device monitor
```