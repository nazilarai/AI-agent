#!/bin/bash

# ESP32 Captive Portal Build Script
# Professional Red Team Testing Tool

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔒 ESP32 Advanced Captive Portal Toolkit"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

function print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

function print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

function print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if ESP-IDF is set up
if [ -z "$IDF_PATH" ]; then
    print_error "ESP-IDF environment not found!"
    echo "Please set up ESP-IDF first:"
    echo "1. Install ESP-IDF: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/"
    echo "2. Source the environment: . \$HOME/esp/esp-idf/export.sh"
    exit 1
fi

print_success "ESP-IDF found at: $IDF_PATH"

# Parse command line arguments
ACTION=${1:-build}
PORT=${2:-/dev/ttyUSB0}

case $ACTION in
    "clean")
        print_step "Cleaning project..."
        idf.py fullclean
        print_success "Project cleaned"
        ;;
    
    "build")
        print_step "Building ESP32 Captive Portal..."
        idf.py build
        print_success "Build completed successfully"
        
        # Show build info
        echo ""
        echo "Build Information:"
        echo "=================="
        if [ -f "build/project_description.json" ]; then
            cat build/project_description.json | grep -E '"app_name"|"idf_ver"|"target"' | sed 's/^/  /'
        fi
        
        echo ""
        print_warning "⚠️  IMPORTANT SECURITY NOTICE:"
        echo "   This tool is for AUTHORIZED TESTING ONLY"
        echo "   Do not use for illegal activities"
        echo "   Ensure proper authorization before deployment"
        ;;
    
    "flash")
        print_step "Flashing to ESP32 on port $PORT..."
        idf.py -p $PORT flash
        print_success "Flashing completed"
        ;;
    
    "monitor")
        print_step "Starting serial monitor on port $PORT..."
        echo "Press Ctrl+] to exit monitor"
        echo ""
        idf.py -p $PORT monitor
        ;;
    
    "flash-monitor")
        print_step "Flashing and monitoring ESP32 on port $PORT..."
        idf.py -p $PORT flash monitor
        ;;
    
    "erase")
        print_step "Erasing flash on ESP32 at port $PORT..."
        esptool.py -p $PORT erase_flash
        print_success "Flash erased"
        ;;
    
    "menuconfig")
        print_step "Opening configuration menu..."
        idf.py menuconfig
        ;;
    
    "size")
        print_step "Analyzing binary size..."
        idf.py size
        ;;
    
    "partition-table")
        print_step "Building and flashing partition table..."
        idf.py partition-table-flash
        ;;
    
    *)
        echo "Usage: $0 [action] [port]"
        echo ""
        echo "Actions:"
        echo "  build          - Build the project (default)"
        echo "  clean          - Clean build files"
        echo "  flash          - Flash firmware to ESP32"
        echo "  monitor        - Start serial monitor"
        echo "  flash-monitor  - Flash and start monitor"
        echo "  erase          - Erase ESP32 flash completely"
        echo "  menuconfig     - Configure project settings"
        echo "  size           - Show binary size analysis"
        echo "  partition-table - Flash partition table"
        echo ""
        echo "Port (default: /dev/ttyUSB0):"
        echo "  Common ports: /dev/ttyUSB0, /dev/ttyACM0, COM3, COM4"
        echo ""
        echo "Examples:"
        echo "  $0 build"
        echo "  $0 flash /dev/ttyUSB0"
        echo "  $0 flash-monitor COM3"
        echo "  $0 monitor"
        exit 1
        ;;
esac

print_success "Operation completed successfully!"
echo ""
echo "🌐 Access Points:"
echo "   Captive Portal: http://192.168.4.1"
echo "   Admin Panel:    http://192.168.4.1:8080/admin"
echo ""
echo "📱 WiFi Network:"
echo "   SSID: Free_Public_WiFi"
echo "   Security: Open"
echo ""
echo "🔧 Physical Controls:"
echo "   Boot Button: Toggle AP on/off"
echo "   Status LED:  Shows connection status"