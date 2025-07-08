# 🔒 ESP32 Advanced WiFi Captive Portal Toolkit

**Professional Expert-Level Implementation for Authorized Security Testing**

[![ESP-IDF](https://img.shields.io/badge/ESP--IDF-v5.0+-blue.svg)](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)
[![License](https://img.shields.io/badge/License-Educational%20Use-orange.svg)](#license)
[![Platform](https://img.shields.io/badge/Platform-ESP32-green.svg)](https://www.espressif.com/en/products/socs/esp32)

## ⚠️ IMPORTANT LEGAL DISCLAIMER

**FOR AUTHORIZED TESTING AND EDUCATIONAL PURPOSES ONLY**

This toolkit is designed exclusively for:
- Authorized penetration testing
- Security research in controlled environments
- Educational cybersecurity training
- Red team exercises with proper authorization

**DO NOT use this tool for:**
- Unauthorized network infiltration
- Credential harvesting
- Malicious activities
- Any illegal purposes

Users are solely responsible for ensuring compliance with all applicable laws and regulations.

## 📋 Table of Contents

- [Features](#-features)
- [Hardware Requirements](#-hardware-requirements)
- [Software Requirements](#-software-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Admin Interface](#-admin-interface)
- [Log Analysis](#-log-analysis)
- [Security Features](#-security-features)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Features

### Core Capabilities
- **WiFi Access Point**: Custom SSID broadcast (default: "Free_Public_WiFi")
- **DNS Redirection**: All DNS queries redirected to captive portal
- **HTTP Server**: Modern, responsive captive portal interface
- **Client Logging**: MAC address, RSSI, hostname, timestamp tracking
- **SPIFFS Storage**: Local log storage with configurable limits

### Advanced Features
- **Admin Interface**: Real-time monitoring at `http://192.168.4.1:8080/admin`
- **Site Survey**: WiFi network scanning and analysis
- **Remote Control**: Toggle AP/server via button or web interface
- **Alert System**: Telegram Bot and webhook notifications
- **CLI Integration**: Compatible with standard Linux/Windows tools

### Professional Capabilities
- **Memory Management**: Efficient FreeRTOS task management
- **Error Handling**: Comprehensive error recovery and logging
- **Configuration**: JSON-based persistent configuration
- **Security**: Ethical design with clear testing disclaimers
- **Modularity**: Clean, maintainable C++ codebase

## 🔧 Hardware Requirements

### Primary Hardware
- **ESP32 DevKit** (38-pin recommended)
- **USB Cable** (for programming and power)
- **MicroSD Card** (optional, for extended logging)

### GPIO Configuration
| Pin | Function | Description |
|-----|----------|-------------|
| GPIO 0 | Boot Button | Toggle AP on/off |
| GPIO 2 | Status LED | Connection status indicator |

### Recommended Setup
- **Power Supply**: 5V via USB or external 3.3V
- **Antenna**: Use ESP32 with external antenna for better range
- **Enclosure**: Professional enclosure for field deployment

## 💻 Software Requirements

### Development Environment
- **ESP-IDF v5.0+**: [Installation Guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/)
- **Python 3.7+**: For log analysis tools
- **Git**: For version control

### Dependencies
```bash
# Python dependencies (for log analysis)
pip3 install pyserial argparse
```

### Supported Platforms
- **Linux**: Ubuntu 20.04+, Debian 10+, Arch Linux
- **macOS**: 10.15+
- **Windows**: Windows 10+ (WSL recommended)

## 📦 Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd esp32_captive_portal
```

### 2. Set up ESP-IDF Environment
```bash
# Install ESP-IDF (if not already installed)
mkdir -p ~/esp
cd ~/esp
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh

# Source environment (add to ~/.bashrc for persistence)
. ~/esp/esp-idf/export.sh
```

### 3. Build and Flash
```bash
# Make build script executable
chmod +x build.sh

# Build project
./build.sh build

# Flash to ESP32 (adjust port as needed)
./build.sh flash /dev/ttyUSB0

# Monitor serial output
./build.sh monitor /dev/ttyUSB0
```

## ⚙️ Configuration

### Basic Configuration

The device uses the following default settings:

| Setting | Default Value | Description |
|---------|---------------|-------------|
| SSID | Free_Public_WiFi | WiFi network name |
| Password | (none) | Open network |
| Channel | 6 | WiFi channel |
| IP Address | 192.168.4.1 | Gateway and DNS server |
| HTTP Port | 80 | Captive portal |
| Admin Port | 8080 | Admin interface |

### Advanced Configuration

Edit `main/main.cpp` for advanced settings:

```cpp
// WiFi Configuration
#define WIFI_SSID           "Your_Custom_SSID"
#define WIFI_CHANNEL        11
#define MAX_STA_CONN        20

// Alert Configuration
// Configure in admin interface or config.json
```

### Alert Configuration

Create `/spiffs/config.json` on the device:

```json
{
  "telegram_token": "YOUR_BOT_TOKEN",
  "telegram_chat_id": "YOUR_CHAT_ID",
  "webhook_url": "https://your-webhook-url.com/alert",
  "ap_enabled": true,
  "server_enabled": true
}
```

## 🖥️ Usage

### Quick Start
1. **Power on** the ESP32
2. **Connect** to "Free_Public_WiFi" network
3. **Navigate** to any website (automatic redirect)
4. **Access admin** at `http://192.168.4.1:8080/admin`

### Physical Controls
- **Boot Button**: Press to toggle AP on/off
- **Status LED**: 
  - Solid: AP active, no clients
  - Blinking: Clients connected
  - Off: AP disabled

### Serial Monitor
```bash
# Monitor real-time logs
./build.sh monitor /dev/ttyUSB0

# Parse logs with Python tool
python3 log_parser.py -s /dev/ttyUSB0
```

## 🎛️ Admin Interface

Access the professional admin interface at `http://192.168.4.1:8080/admin`

### Features
- **Real-time Statistics**: Active clients, total connections
- **Client List**: MAC addresses, RSSI, connection times
- **System Controls**: Toggle AP/server, clear logs
- **Site Survey**: Scan and display nearby WiFi networks
- **Auto-refresh**: Updates every 10 seconds

### Controls
| Button | Function |
|--------|----------|
| Toggle AP | Enable/disable access point |
| Toggle Server | Enable/disable web server |
| Start/Stop Survey | WiFi network scanning |
| Clear Logs | Remove all stored logs |
| Refresh | Manual page refresh |

## 📊 Log Analysis

### Real-time Monitoring
```bash
# Monitor with built-in parser
python3 log_parser.py -s /dev/ttyUSB0 -b 115200

# Basic statistics only
python3 log_parser.py -s /dev/ttyUSB0 --stats
```

### File Analysis
```bash
# Capture logs to file
./build.sh monitor /dev/ttyUSB0 > capture.log

# Analyze log file
python3 log_parser.py -f capture.log -r text

# Generate JSON report
python3 log_parser.py -f capture.log -r json -o report.json

# Export to CSV
python3 log_parser.py -f capture.log -c analysis
```

### CLI Integration
```bash
# Extract client data with grep
grep "CLIENT_LOG:" capture.log | cut -d',' -f2-4

# Count unique MACs with awk
grep "CLIENT_LOG:" capture.log | awk -F',' '{print $2}' | sort -u | wc -l

# Real-time monitoring with netcat (if using webhook)
nc -l 8080

# Use curl for webhook testing
curl -X POST http://192.168.4.1:8080/admin/toggle_ap
```

## 🛡️ Security Features

### Ethical Design
- **Clear Disclaimers**: All pages clearly state testing purpose
- **No Credential Capture**: Only usernames logged, no passwords
- **Transparent Logging**: All activity clearly logged and accessible
- **Educational Focus**: Designed for learning and authorized testing

### Security Considerations
- **Default Passwords**: No default passwords (open network)
- **Encryption**: No WEP/WPA (intentionally open for testing)
- **Data Storage**: Local storage only (no external transmission)
- **Access Control**: Admin interface on separate port

### Best Practices
1. **Authorization**: Always obtain written permission
2. **Scope**: Define clear testing boundaries
3. **Documentation**: Maintain detailed test logs
4. **Cleanup**: Remove device after testing
5. **Reporting**: Provide comprehensive test reports

## 🔍 Troubleshooting

### Common Issues

#### Build Errors
```bash
# Clean and rebuild
./build.sh clean
./build.sh build

# Check ESP-IDF version
idf.py --version

# Reconfigure if needed
./build.sh menuconfig
```

#### Flash Errors
```bash
# Check port permissions
sudo usermod -a -G dialout $USER
# Log out and back in

# Try different baud rate
esptool.py -p /dev/ttyUSB0 -b 460800 flash_id

# Erase flash completely
./build.sh erase /dev/ttyUSB0
```

#### WiFi Issues
```bash
# Check WiFi configuration
grep "WIFI_" main/main.cpp

# Monitor WiFi events
./build.sh monitor | grep "wifi"

# Scan for interference
python3 log_parser.py -s /dev/ttyUSB0 | grep "Site Survey"
```

#### Memory Issues
```bash
# Check memory usage
./build.sh size

# Monitor heap usage
./build.sh monitor | grep "heap"

# Optimize SPIFFS
./build.sh menuconfig  # → Component config → SPIFFS
```

### Debug Commands
```bash
# Full verbose build
idf.py -v build

# Partition table info
esptool.py -p /dev/ttyUSB0 read_flash 0x8000 0x1000 partition_table.bin
python3 $IDF_PATH/components/partition_table/gen_esp32part.py partition_table.bin

# Core dump analysis (if enabled)
idf.py coredump-info
```

## 📈 Performance Optimization

### Memory Management
- **Heap Monitoring**: Track memory usage during operation
- **Task Optimization**: Adjust stack sizes based on usage
- **SPIFFS Tuning**: Configure for optimal log storage

### WiFi Performance
- **Channel Selection**: Use WiFi analyzer to find clear channel
- **TX Power**: Adjust transmission power for range vs. battery
- **Buffer Tuning**: Optimize WiFi buffers for client capacity

### Code Optimization
```cpp
// Enable compiler optimizations in sdkconfig
CONFIG_COMPILER_OPTIMIZATION_SIZE=y

// Monitor task stack usage
vTaskList(pcWriteBuffer);
```

## 🤝 Contributing

### Development Guidelines
1. **Code Style**: Follow ESP-IDF coding standards
2. **Testing**: Test on multiple ESP32 variants
3. **Documentation**: Update README for new features
4. **Security**: Maintain ethical design principles

### Pull Request Process
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Bug Reports
Please include:
- ESP32 model and revision
- ESP-IDF version
- Complete error logs
- Steps to reproduce

## 📄 License

This project is licensed under the **Educational Use License** - see the [LICENSE](LICENSE) file for details.

### Terms Summary
- ✅ Educational use and research
- ✅ Authorized penetration testing
- ✅ Security training and demonstrations
- ❌ Unauthorized network attacks
- ❌ Commercial exploitation
- ❌ Malicious activities

## 🙋 Support

### Documentation
- [ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)
- [ESP32 Technical Reference](https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf)

### Community
- [ESP32 Forum](https://esp32.com/)
- [ESP-IDF GitHub](https://github.com/espressif/esp-idf)

### Professional Support
For professional security testing support or custom implementations, please contact through official channels.

---

## 🎯 Project Roadmap

### Version 2.0 (Planned)
- [ ] WPA2 Enterprise support
- [ ] Advanced packet analysis
- [ ] Machine learning client classification
- [ ] Mobile app for remote control
- [ ] Extended hardware sensor support

### Version 1.5 (In Progress)
- [ ] Enhanced webhook retry mechanism
- [ ] SD card logging implementation
- [ ] Real-time client device fingerprinting
- [ ] Advanced admin authentication
- [ ] Multi-language captive portal

---

**Remember: This tool is designed for legitimate security testing only. Always ensure you have proper authorization before use.**

*Built with ❤️ for the cybersecurity community*