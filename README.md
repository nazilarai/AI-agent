# 🚀 Proximity SE Ultimate Edition

**Advanced Social Engineering & Penetration Testing Platform for ESP32**

A comprehensive ESP32-based device for wireless security research, social engineering, and penetration testing with advanced BLE/WiFi attack capabilities.

## ⚠️ Legal Disclaimer

This project is intended for **educational purposes, authorized security research, and legitimate penetration testing only**. Users are responsible for complying with all applicable laws and regulations. Unauthorized use of this device to attack systems you do not own or have explicit permission to test is illegal and unethical.

## 🎯 Features Overview

### Core Capabilities
- **Advanced BLE Scanning & Analysis** - Detect and classify nearby Bluetooth devices
- **Multi-Platform Beacon Spoofing** - Apple, Samsung, Google, Microsoft beacon emulation
- **WiFi Attack Suite** - Evil Twin, KARMA, WPS attacks, Deauthentication
- **Adaptive Payload Delivery** - Smart targeting based on device type and proximity
- **Real-time Geofencing** - Proximity-based alerts and automated responses
- **Advanced Web Interface** - Professional dashboard with analytics and charts
- **Remote C2 Integration** - Command and control via Telegram/Discord/WebSocket

### Attack Modules

#### 🔵 BLE Attacks
- **Apple AirDrop Spoofing** - Trigger unwanted AirDrop notifications
- **AirPods Pairing Flood** - Spam fake AirPods pairing requests
- **Samsung SmartThings Exploit** - Galaxy device notification flooding
- **Google Fast Pair Abuse** - Android device connection requests
- **Microsoft Swift Pair** - Windows 10/11 notification spam
- **COVID Exposure Notifications** - Fake exposure alert beacons
- **BLE Device Flooding** - Overwhelm target devices with fake devices
- **Device Cloning** - Copy and replay detected BLE advertisements

#### 📶 WiFi Attacks
- **Evil Twin Access Points** - Clone legitimate networks for credential harvesting
- **KARMA Attacks** - Respond to device probe requests with fake APs
- **WPS PIN Attacks** - Attempt WPS vulnerabilities (Pixie Dust)
- **Deauthentication Attacks** - Force disconnections from legitimate APs
- **Handshake Capture** - Collect WPA/WPA2 4-way handshakes
- **Packet Injection** - Custom 802.11 frame injection
- **Captive Portal** - Multi-platform credential harvesting pages

#### 🎭 Social Engineering
- **Adaptive Phishing Pages** - Platform-specific login pages (Apple ID, Google, Facebook)
- **Multi-Factor Authentication Bypass** - Capture 2FA codes and security questions
- **Device-Specific Targeting** - Customized attacks based on detected device types
- **Proximity-Based Triggers** - Automatic payload delivery when targets approach
- **Corporate Device Detection** - Identify high-value business targets

### 🛡️ Stealth & Evasion
- **Stealth Mode** - Reduce attack signatures and RF emissions
- **Power Management** - Battery optimization for extended operations
- **MAC Address Randomization** - Avoid device tracking
- **Attack Scheduling** - Automated, time-based attack execution
- **Emergency Functions** - Quick shutdown and evidence destruction

## 🔧 Hardware Requirements

### ESP32 Development Board
- **Recommended**: ESP32-WROOM-32 or ESP32-S3
- **Minimum**: 4MB Flash, 520KB RAM
- **WiFi**: 802.11 b/g/n support required
- **Bluetooth**: BLE 4.2+ support required

### Additional Components
```
📱 ESP32 Development Board (NodeMCU-32S or similar)
🔋 3.7V Li-Po Battery (2000mAh+ recommended)
💡 Status LEDs (x2)
🔊 Piezo Buzzer
🔘 Push Button
⚡ Relay Module (5V)
📳 Vibration Motor
📡 External Antenna (optional but recommended)
🔌 Voltage Divider Circuit (for battery monitoring)
```

### Pin Configuration
```c
#define LED_PIN GPIO_NUM_2              // Main status LED
#define BUZZER_PIN GPIO_NUM_4           // Audio alerts
#define BUTTON_PIN GPIO_NUM_0           // Manual trigger
#define RELAY_PIN GPIO_NUM_5            // External relay control
#define VIBRATION_PIN GPIO_NUM_12       // Haptic feedback
#define EXTERNAL_ANTENNA_PIN GPIO_NUM_13 // Antenna switching
#define STATUS_LED_PIN GPIO_NUM_14      // Secondary status LED
#define BATTERY_ADC_CHANNEL ADC1_CHANNEL_6 // Battery monitoring
```

## 🚀 Installation & Setup

### 1. Development Environment Setup

#### ESP-IDF Installation
```bash
# Install ESP-IDF v5.0+
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh
source export.sh
```

#### Arduino IDE Alternative
1. Install Arduino IDE 2.0+
2. Add ESP32 board support: `https://dl.espressif.com/dl/package_esp32_index.json`
3. Install required libraries:
   - ESP32 Arduino Core
   - ArduinoJson
   - WebSocketsClient
   - WiFi
   - BluetoothSerial

### 2. Project Compilation

```bash
# Clone repository
git clone https://github.com/yourrepo/proximity-se-ultimate.git
cd proximity-se-ultimate

# Configure project
idf.py menuconfig

# Build and flash
idf.py build
idf.py flash

# Monitor serial output
idf.py monitor
```

### 3. Initial Configuration

#### WiFi Access Point Settings
- **SSID**: `Free WiFi` (configurable)
- **Password**: `free wifi` (configurable)
- **Channel**: 6 (auto-selects optimal)
- **Max Connections**: 15

#### Web Interface Access
1. Connect to the device's WiFi network
2. Navigate to: `http://192.168.4.1/admin`
3. Default credentials: None (open access)

## 🎮 Usage Guide

### Web Interface Overview

#### 🏠 Dashboard
- **Real-time Statistics**: Device counts, battery level, attack success rates
- **System Status**: All subsystem health monitoring
- **Live Device List**: Detected BLE/WiFi devices with vendor classification
- **Analytics Charts**: Visual representation of attack data

#### 🎯 Attack Controls

**BLE Operations**
```
🔍 Start BLE Scan     - Begin device discovery
⏹️ Stop BLE Scan      - Halt scanning operations
💥 BLE Flood          - Execute flooding attack
👥 Clone Strongest    - Copy most active device
```

**WiFi Attacks**
```
👹 Evil Twin          - Launch AP cloning attack
🔥 KARMA Attack       - Respond to probe requests
💀 Deauth All         - Disconnect all clients
🔓 WPS Attack         - Attempt WPS vulnerabilities
```

**Payload Delivery**
```
🍎 Apple Flood        - Target iOS devices
📱 Samsung Flood      - Target Galaxy devices
🪟 Windows Flood      - Target Windows devices
🤖 Android Flood      - Target Android devices
```

### 🔄 Automated Operations

#### Proximity-Based Triggers
The device automatically executes targeted attacks when high-value devices enter the proximity zone (configurable RSSI threshold).

#### Scheduled Attacks
```c
// Default attack schedule (customizable)
"proximity_notifications" - Every 3 minutes
"deauth_attack"          - Every 5 minutes
"ble_flooding"           - Every 10 minutes
"evil_twin"              - Every 15 minutes
"karma_attack"           - Every 20 minutes
```

#### Geofencing Alerts
- **Telegram Integration**: Instant alerts when targets detected
- **Discord Webhooks**: Team notifications
- **Visual/Haptic Alerts**: LED and vibration notifications

### 📱 Remote Control

#### Telegram Bot Integration
1. Create Telegram bot via @BotFather
2. Update `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
3. Receive real-time alerts and device status

#### WebSocket C2
- Real-time command execution
- Status monitoring
- Log streaming
- Attack coordination

## 🛠️ Advanced Configuration

### Custom Beacon Creation
```c
// Example: Custom iBeacon configuration
UUID: e2c56db5-dffb-48d2-b060-d0f5a71096e0
Major: 0001
Minor: 0001
TX Power: -59 dBm
```

### Target Prioritization
```c
// High-value target keywords
"iPhone", "iPad", "MacBook", "AirPods"  // Apple devices
"Galaxy", "Note", "Tab S"              // Samsung devices
"Pixel", "Surface", "ThinkPad"         // Google/Microsoft
"Corporate", "Enterprise", "CEO"        // Business devices
```

### Attack Parameters
```c
#define GEOFENCE_THRESHOLD -55    // RSSI trigger level
#define BLE_SCAN_TIME 5          // Scan duration (seconds)
#define BEACON_ROTATION_TIME 8    // Beacon switching interval
#define MAX_DEVICES 100          // Device tracking limit
```

## 📊 Analytics & Reporting

### Real-time Metrics
- **Device Detection Rate**: Devices discovered per minute
- **Attack Success Rate**: Percentage of successful payload deliveries
- **Battery Efficiency**: Power consumption optimization
- **Target Classification**: Device type distribution

### Exported Data Formats
- **JSON Logs**: Structured logging with timestamps
- **CSV Reports**: Device and attack statistics
- **PCAP Files**: Network traffic captures (if enabled)

## 🔒 Security Features

### Operational Security
- **Stealth Mode**: Reduces RF signatures and attack intervals
- **MAC Randomization**: Prevents device fingerprinting
- **Log Rotation**: Automatic cleanup of sensitive data
- **Emergency Shutdown**: Quick evidence destruction

### Data Protection
- **Encrypted Storage**: Credentials stored with AES encryption
- **Secure Boot**: Prevents unauthorized firmware modifications
- **Remote Wipe**: C2-triggered data destruction

## 🔍 Troubleshooting

### Common Issues

#### Device Not Scanning
```
1. Check antenna connections
2. Verify GPIO pin assignments
3. Monitor power supply voltage
4. Review WiFi interference
```

#### Web Interface Inaccessible
```
1. Confirm WiFi AP is broadcasting
2. Check client connection to correct SSID
3. Verify IP address: 192.168.4.1
4. Clear browser cache and cookies
```

#### BLE Attacks Not Working
```
1. Ensure target devices have Bluetooth enabled
2. Check proximity (optimal range: 1-10 meters)
3. Verify beacon payload formats
4. Monitor for interference from other devices
```

### Debug Output
```bash
# Enable verbose logging
idf.py menuconfig
# Component config → Log output → Verbose

# Monitor serial output
idf.py monitor --port /dev/ttyUSB0
```

## 📈 Performance Optimization

### Battery Life Extension
- **Low Power Mode**: Automatic activation at 3.5V
- **Scan Optimization**: Reduced intervals during idle periods
- **Component Shutdown**: Disable unused peripherals

### Attack Efficiency
- **Target Prioritization**: Focus on high-value devices
- **Adaptive Timing**: Adjust attack intervals based on success rates
- **Resource Management**: Balance between detection and power consumption

## 🤝 Contributing

### Development Guidelines
1. **Code Style**: Follow ESP-IDF coding standards
2. **Documentation**: Update README for new features
3. **Testing**: Validate on multiple ESP32 variants
4. **Security**: Review code for vulnerabilities

### Feature Requests
- Submit issues with detailed use cases
- Include hardware compatibility requirements
- Provide testing results if possible

## 📚 Educational Resources

### Recommended Reading
- **Bluetooth Security**: "Bluetooth Security" by Christian Gehrmann
- **WiFi Hacking**: "WiFi Security" by Stewart Miller
- **Social Engineering**: "The Art of Human Hacking" by Christopher Hadnagy

### Legal Resources
- **Penetration Testing**: Ensure proper authorization
- **Research Ethics**: Follow responsible disclosure practices
- **Local Laws**: Verify compliance with regional regulations

## 🏆 Advanced Features

### Machine Learning Integration
- **Device Fingerprinting**: ML-based device classification
- **Behavioral Analysis**: Pattern recognition for targeted attacks
- **Adaptive Algorithms**: Self-optimizing attack parameters

### Enterprise Integration
- **SIEM Integration**: Log forwarding to security platforms
- **API Endpoints**: RESTful API for automation
- **Multi-Device Coordination**: Distributed attack capabilities

## 📞 Support & Contact

### Issue Reporting
- **GitHub Issues**: Bug reports and feature requests
- **Security Vulnerabilities**: Responsible disclosure via email
- **General Questions**: Community discussion forums

### Acknowledgments
- ESP32 Community for hardware support
- Security researchers for vulnerability discoveries
- Open source contributors for code improvements

---

**⚠️ Remember**: This tool is designed for legitimate security research and authorized penetration testing only. Always obtain proper authorization before testing and comply with all applicable laws and regulations.

**🔐 Stay Ethical**: Use your skills to improve security, not to cause harm.
