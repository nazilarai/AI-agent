#!/bin/bash

# ESP32 Captive Portal Log Parser Shell Script
# Quick CLI utilities for log analysis
# FOR AUTHORIZED TESTING ONLY

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

function print_header() {
    echo -e "${BLUE}🔒 ESP32 Captive Portal Log Analyzer${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${YELLOW}⚠️  FOR AUTHORIZED TESTING ONLY${NC}"
    echo ""
}

function print_usage() {
    echo "Usage: $0 [command] [logfile|port]"
    echo ""
    echo "Commands:"
    echo "  monitor <port>     - Real-time monitoring of serial port"
    echo "  parse <logfile>    - Parse saved log file"
    echo "  clients <logfile>  - Extract client connection data"
    echo "  logins <logfile>   - Extract login attempts"
    echo "  stats <logfile>    - Show quick statistics"
    echo "  unique <logfile>   - Show unique MAC addresses"
    echo "  rssi <logfile>     - Analyze signal strength"
    echo "  timeline <logfile> - Show connection timeline"
    echo "  export <logfile>   - Export data to CSV format"
    echo ""
    echo "Examples:"
    echo "  $0 monitor /dev/ttyUSB0"
    echo "  $0 parse capture.log"
    echo "  $0 stats esp32.log"
    echo "  $0 clients capture.log | grep -E '([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}'"
}

function monitor_port() {
    local port=$1
    
    echo -e "${GREEN}📡 Monitoring ESP32 on port: $port${NC}"
    echo -e "${CYAN}Press Ctrl+C to stop${NC}"
    echo ""
    
    # Check if port exists
    if [ ! -e "$port" ]; then
        echo -e "${RED}❌ Error: Port $port not found${NC}"
        echo "Common ports: /dev/ttyUSB0, /dev/ttyACM0, /dev/cu.usbserial-*"
        exit 1
    fi
    
    # Monitor with filtering
    stty -F "$port" 115200 cs8 -cstopb -parenb
    
    echo -e "${BLUE}[INFO]${NC} Started monitoring. Output will be filtered for important events."
    echo ""
    
    while IFS= read -r line < "$port"; do
        # Filter and highlight important log entries
        if echo "$line" | grep -q "CLIENT_LOG:"; then
            mac=$(echo "$line" | grep -oE '([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}')
            rssi=$(echo "$line" | grep -oE ',-?[0-9]+,' | tr -d ',')
            echo -e "${GREEN}[CLIENT]${NC} New connection: $mac | RSSI: ${rssi}dBm"
        elif echo "$line" | grep -q "Login attempt"; then
            username=$(echo "$line" | sed -n 's/.*Username: \([^,]*\).*/\1/p')
            ip=$(echo "$line" | sed -n 's/.*IP: \([^,]*\).*/\1/p')
            echo -e "${YELLOW}[LOGIN]${NC} Attempt from $ip | Username: $username"
        elif echo "$line" | grep -q "ALERT:"; then
            alert=$(echo "$line" | sed 's/.*ALERT: //')
            echo -e "${RED}[ALERT]${NC} $alert"
        elif echo "$line" | grep -q "Station.*connected"; then
            echo -e "${CYAN}[WIFI]${NC} $line"
        elif echo "$line" | grep -q "ERROR\|error"; then
            echo -e "${RED}[ERROR]${NC} $line"
        fi
    done
}

function parse_logfile() {
    local logfile=$1
    
    if [ ! -f "$logfile" ]; then
        echo -e "${RED}❌ Error: Log file '$logfile' not found${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}📂 Parsing log file: $logfile${NC}"
    echo ""
    
    # Use Python parser if available
    if command -v python3 >/dev/null 2>&1 && [ -f "log_parser.py" ]; then
        python3 log_parser.py -f "$logfile" -r text
    else
        # Fallback to shell parsing
        echo -e "${BLUE}📊 SUMMARY STATISTICS${NC}"
        echo "===================="
        
        local total_connections=$(grep -c "CLIENT_LOG:" "$logfile" 2>/dev/null || echo "0")
        local unique_clients=$(grep "CLIENT_LOG:" "$logfile" 2>/dev/null | cut -d',' -f2 | sort -u | wc -l)
        local login_attempts=$(grep -c "Login attempt" "$logfile" 2>/dev/null || echo "0")
        
        echo "Total Connections: $total_connections"
        echo "Unique Clients: $unique_clients"
        echo "Login Attempts: $login_attempts"
        echo ""
        
        if [ "$total_connections" -gt 0 ]; then
            echo -e "${BLUE}📱 TOP MAC ADDRESSES${NC}"
            echo "===================="
            grep "CLIENT_LOG:" "$logfile" | cut -d',' -f2 | sort | uniq -c | sort -nr | head -10
            echo ""
        fi
        
        if [ "$login_attempts" -gt 0 ]; then
            echo -e "${BLUE}👤 TOP USERNAMES${NC}"
            echo "================"
            grep "Login attempt" "$logfile" | sed -n 's/.*Username: \([^,]*\).*/\1/p' | sort | uniq -c | sort -nr | head -10
        fi
    fi
}

function extract_clients() {
    local logfile=$1
    
    echo -e "${GREEN}📱 Client Connection Data${NC}"
    echo "========================="
    echo "Timestamp,MAC Address,RSSI,Hostname,IP"
    echo "======================================="
    
    grep "CLIENT_LOG:" "$logfile" | while IFS= read -r line; do
        # Parse CLIENT_LOG format: timestamp,mac,rssi,hostname,ip
        echo "$line" | sed 's/.*CLIENT_LOG://' | tr ',' '\t' | \
        awk '{printf "%-12s %-17s %4s %-15s %s\n", $1, $2, $3, $4, $5}'
    done
}

function extract_logins() {
    local logfile=$1
    
    echo -e "${GREEN}🔐 Login Attempts${NC}"
    echo "================="
    echo "Timestamp,IP Address,Username,Device"
    echo "===================================="
    
    grep "Login attempt" "$logfile" | while IFS= read -r line; do
        timestamp=$(echo "$line" | grep -oE '^[^[]*' | tr -d ' ')
        ip=$(echo "$line" | sed -n 's/.*IP: \([^,]*\).*/\1/p')
        username=$(echo "$line" | sed -n 's/.*Username: \([^,]*\).*/\1/p')
        device=$(echo "$line" | sed -n 's/.*Device: \(.*\)/\1/p')
        
        printf "%-12s %-15s %-20s %s\n" "$timestamp" "$ip" "$username" "$device"
    done
}

function show_stats() {
    local logfile=$1
    
    echo -e "${CYAN}📊 Quick Statistics${NC}"
    echo "==================="
    
    local total_lines=$(wc -l < "$logfile")
    local client_logs=$(grep -c "CLIENT_LOG:" "$logfile" 2>/dev/null || echo "0")
    local login_attempts=$(grep -c "Login attempt" "$logfile" 2>/dev/null || echo "0")
    local alerts=$(grep -c "ALERT:" "$logfile" 2>/dev/null || echo "0")
    local unique_macs=$(grep "CLIENT_LOG:" "$logfile" 2>/dev/null | cut -d',' -f2 | sort -u | wc -l)
    
    echo "Total Log Lines: $total_lines"
    echo "Client Connections: $client_logs"
    echo "Unique MAC Addresses: $unique_macs"
    echo "Login Attempts: $login_attempts"
    echo "Alert Messages: $alerts"
    
    # Show time range if available
    local first_client=$(grep "CLIENT_LOG:" "$logfile" | head -1 | cut -d',' -f1 | tr -d 'CLIENT_LOG:')
    local last_client=$(grep "CLIENT_LOG:" "$logfile" | tail -1 | cut -d',' -f1 | tr -d 'CLIENT_LOG:')
    
    if [ ! -z "$first_client" ] && [ ! -z "$last_client" ]; then
        echo "Session Duration: $(date -d@$first_client) to $(date -d@$last_client)"
    fi
}

function show_unique_macs() {
    local logfile=$1
    
    echo -e "${GREEN}🔍 Unique MAC Addresses${NC}"
    echo "======================="
    
    grep "CLIENT_LOG:" "$logfile" | cut -d',' -f2 | sort -u | nl -v0 -nln
}

function analyze_rssi() {
    local logfile=$1
    
    echo -e "${CYAN}📶 Signal Strength Analysis${NC}"
    echo "==========================="
    
    # Extract RSSI values
    local rssi_values=$(grep "CLIENT_LOG:" "$logfile" | cut -d',' -f3)
    
    if [ -z "$rssi_values" ]; then
        echo "No RSSI data found."
        return
    fi
    
    # Calculate statistics using awk
    echo "$rssi_values" | awk '
    BEGIN { 
        min = 0; max = -100; sum = 0; count = 0 
    }
    {
        if (NF > 0) {
            rssi = $1
            if (rssi < min) min = rssi
            if (rssi > max) max = rssi
            sum += rssi
            count++
        }
    }
    END {
        if (count > 0) {
            avg = sum / count
            printf "Average RSSI: %.1f dBm\n", avg
            printf "Minimum RSSI: %d dBm\n", min
            printf "Maximum RSSI: %d dBm\n", max
            printf "Total Samples: %d\n", count
        }
    }'
    
    echo ""
    echo "RSSI Distribution:"
    echo "$rssi_values" | sort -n | uniq -c | awk '{printf "%4s connections at %s dBm\n", $1, $2}'
}

function show_timeline() {
    local logfile=$1
    
    echo -e "${BLUE}⏰ Connection Timeline${NC}"
    echo "====================="
    
    grep "CLIENT_LOG:" "$logfile" | while IFS= read -r line; do
        timestamp=$(echo "$line" | cut -d',' -f1 | tr -d 'CLIENT_LOG:')
        mac=$(echo "$line" | cut -d',' -f2)
        rssi=$(echo "$line" | cut -d',' -f3)
        
        # Convert timestamp to readable format
        readable_time=$(date -d@"$timestamp" 2>/dev/null || echo "Invalid timestamp")
        printf "%-19s %-17s %4s dBm\n" "$readable_time" "$mac" "$rssi"
    done
}

function export_csv() {
    local logfile=$1
    local basename=$(basename "$logfile" .log)
    
    echo -e "${GREEN}📄 Exporting to CSV format${NC}"
    
    # Export client data
    if grep -q "CLIENT_LOG:" "$logfile"; then
        echo "timestamp,mac_address,rssi,hostname,ip_address" > "${basename}_clients.csv"
        grep "CLIENT_LOG:" "$logfile" | sed 's/.*CLIENT_LOG://' >> "${basename}_clients.csv"
        echo "✅ Exported client data to ${basename}_clients.csv"
    fi
    
    # Export login data
    if grep -q "Login attempt" "$logfile"; then
        echo "timestamp,ip_address,username,device" > "${basename}_logins.csv"
        grep "Login attempt" "$logfile" | while IFS= read -r line; do
            timestamp=$(echo "$line" | grep -oE '^[^[]*' | tr -d ' ')
            ip=$(echo "$line" | sed -n 's/.*IP: \([^,]*\).*/\1/p')
            username=$(echo "$line" | sed -n 's/.*Username: \([^,]*\).*/\1/p')
            device=$(echo "$line" | sed -n 's/.*Device: \(.*\)/\1/p')
            echo "$timestamp,$ip,$username,$device"
        done >> "${basename}_logins.csv"
        echo "✅ Exported login data to ${basename}_logins.csv"
    fi
}

# Main script logic
if [ $# -eq 0 ]; then
    print_header
    print_usage
    exit 1
fi

command=$1
file_or_port=$2

print_header

case $command in
    "monitor")
        if [ -z "$file_or_port" ]; then
            echo -e "${RED}❌ Error: Please specify serial port${NC}"
            echo "Example: $0 monitor /dev/ttyUSB0"
            exit 1
        fi
        monitor_port "$file_or_port"
        ;;
    
    "parse")
        if [ -z "$file_or_port" ]; then
            echo -e "${RED}❌ Error: Please specify log file${NC}"
            exit 1
        fi
        parse_logfile "$file_or_port"
        ;;
    
    "clients")
        if [ -z "$file_or_port" ]; then
            echo -e "${RED}❌ Error: Please specify log file${NC}"
            exit 1
        fi
        extract_clients "$file_or_port"
        ;;
    
    "logins")
        if [ -z "$file_or_port" ]; then
            echo -e "${RED}❌ Error: Please specify log file${NC}"
            exit 1
        fi
        extract_logins "$file_or_port"
        ;;
    
    "stats")
        if [ -z "$file_or_port" ]; then
            echo -e "${RED}❌ Error: Please specify log file${NC}"
            exit 1
        fi
        show_stats "$file_or_port"
        ;;
    
    "unique")
        if [ -z "$file_or_port" ]; then
            echo -e "${RED}❌ Error: Please specify log file${NC}"
            exit 1
        fi
        show_unique_macs "$file_or_port"
        ;;
    
    "rssi")
        if [ -z "$file_or_port" ]; then
            echo -e "${RED}❌ Error: Please specify log file${NC}"
            exit 1
        fi
        analyze_rssi "$file_or_port"
        ;;
    
    "timeline")
        if [ -z "$file_or_port" ]; then
            echo -e "${RED}❌ Error: Please specify log file${NC}"
            exit 1
        fi
        show_timeline "$file_or_port"
        ;;
    
    "export")
        if [ -z "$file_or_port" ]; then
            echo -e "${RED}❌ Error: Please specify log file${NC}"
            exit 1
        fi
        export_csv "$file_or_port"
        ;;
    
    *)
        echo -e "${RED}❌ Error: Unknown command '$command'${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac

echo ""
echo -e "${YELLOW}⚠️  Remember: This tool is for authorized security testing only${NC}"