#!/usr/bin/env python3
"""
ESP32 Captive Portal Log Parser
Professional Red Team Testing Utility

FOR AUTHORIZED TESTING AND EDUCATIONAL PURPOSES ONLY

Features:
- Parse serial monitor output
- Extract client connection data
- Generate reports and statistics
- Export data in various formats
- Real-time monitoring
"""

import sys
import re
import json
import csv
import argparse
import datetime
from collections import defaultdict, Counter
import serial
import time

class CaptivePortalLogParser:
    def __init__(self):
        self.clients = []
        self.alerts = []
        self.logins = []
        self.stats = {
            'total_connections': 0,
            'unique_clients': set(),
            'peak_concurrent': 0,
            'login_attempts': 0,
            'start_time': None,
            'end_time': None
        }
    
    def parse_log_line(self, line):
        """Parse a single log line from ESP32 serial output"""
        timestamp = datetime.datetime.now()
        
        # Extract timestamp if present
        ts_match = re.search(r'(\d+\.\d+)', line)
        if ts_match:
            try:
                timestamp = datetime.datetime.fromtimestamp(float(ts_match.group(1)))
            except:
                pass
        
        # Parse client connection logs
        client_match = re.search(r'CLIENT_LOG:(\d+),([a-fA-F0-9:]{17}),(-?\d+),([^,]*),([^,\s]*)', line)
        if client_match:
            client_data = {
                'timestamp': int(client_match.group(1)),
                'mac_address': client_match.group(2),
                'rssi': int(client_match.group(3)),
                'hostname': client_match.group(4),
                'ip_address': client_match.group(5),
                'datetime': timestamp
            }
            self.clients.append(client_data)
            self.stats['total_connections'] += 1
            self.stats['unique_clients'].add(client_data['mac_address'])
            return ('client', client_data)
        
        # Parse alert messages
        alert_match = re.search(r'ALERT: (.+)', line)
        if alert_match:
            alert_data = {
                'timestamp': timestamp,
                'message': alert_match.group(1)
            }
            self.alerts.append(alert_data)
            return ('alert', alert_data)
        
        # Parse login attempts
        login_match = re.search(r'Login attempt - IP: ([^,]+), Username: ([^,]+), Device: (.+)', line)
        if login_match:
            login_data = {
                'timestamp': timestamp,
                'ip_address': login_match.group(1),
                'username': login_match.group(2),
                'device': login_match.group(3)
            }
            self.logins.append(login_data)
            self.stats['login_attempts'] += 1
            return ('login', login_data)
        
        return ('other', line.strip())
    
    def parse_file(self, filename):
        """Parse log file"""
        print(f"📂 Parsing log file: {filename}")
        
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        self.parse_log_line(line)
                    except Exception as e:
                        print(f"⚠️  Warning: Error parsing line {line_num}: {e}")
        except FileNotFoundError:
            print(f"❌ Error: File {filename} not found")
            return False
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
        
        self.calculate_stats()
        print(f"✅ Parsed {len(self.clients)} client records, {len(self.logins)} login attempts")
        return True
    
    def monitor_serial(self, port, baudrate=115200, timeout=1.0):
        """Monitor ESP32 serial output in real-time"""
        print(f"📡 Monitoring serial port: {port}")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            ser = serial.Serial(port, baudrate, timeout=timeout)
            print(f"✅ Connected to {port} at {baudrate} baud")
            
            while True:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        log_type, data = self.parse_log_line(line)
                        
                        if log_type == 'client':
                            print(f"🔍 NEW CLIENT: {data['mac_address']} | RSSI: {data['rssi']} dBm | IP: {data['ip_address']}")
                        elif log_type == 'login':
                            print(f"📝 LOGIN ATTEMPT: {data['username']} from {data['ip_address']} | Device: {data['device']}")
                        elif log_type == 'alert':
                            print(f"🚨 ALERT: {data['message']}")
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"⚠️  Serial error: {e}")
                    time.sleep(1)
                    
        except serial.SerialException as e:
            print(f"❌ Failed to connect to {port}: {e}")
            return False
        except KeyboardInterrupt:
            print("\n📊 Monitoring stopped by user")
        finally:
            if 'ser' in locals():
                ser.close()
                
        self.calculate_stats()
        return True
    
    def calculate_stats(self):
        """Calculate statistics from parsed data"""
        if self.clients:
            self.stats['start_time'] = min(c['datetime'] for c in self.clients)
            self.stats['end_time'] = max(c['datetime'] for c in self.clients)
    
    def generate_report(self, format='text'):
        """Generate analysis report"""
        if format == 'text':
            return self._generate_text_report()
        elif format == 'json':
            return self._generate_json_report()
        elif format == 'html':
            return self._generate_html_report()
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def _generate_text_report(self):
        """Generate text report"""
        report = []
        report.append("🔒 ESP32 Captive Portal Analysis Report")
        report.append("=" * 50)
        report.append("")
        
        # Summary statistics
        report.append("📊 SUMMARY STATISTICS")
        report.append("-" * 30)
        report.append(f"Total Connections:    {self.stats['total_connections']}")
        report.append(f"Unique Clients:       {len(self.stats['unique_clients'])}")
        report.append(f"Login Attempts:       {self.stats['login_attempts']}")
        
        if self.stats['start_time'] and self.stats['end_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
            report.append(f"Session Duration:     {duration}")
            report.append(f"Start Time:           {self.stats['start_time']}")
            report.append(f"End Time:             {self.stats['end_time']}")
        
        report.append("")
        
        # Client analysis
        if self.clients:
            report.append("📱 CLIENT ANALYSIS")
            report.append("-" * 30)
            
            # MAC addresses
            mac_counts = Counter(c['mac_address'] for c in self.clients)
            report.append("Top MAC Addresses:")
            for mac, count in mac_counts.most_common(10):
                report.append(f"  {mac}: {count} connections")
            
            report.append("")
            
            # RSSI distribution
            rssi_values = [c['rssi'] for c in self.clients if c['rssi'] != 0]
            if rssi_values:
                avg_rssi = sum(rssi_values) / len(rssi_values)
                min_rssi = min(rssi_values)
                max_rssi = max(rssi_values)
                report.append("Signal Strength (RSSI):")
                report.append(f"  Average: {avg_rssi:.1f} dBm")
                report.append(f"  Range:   {min_rssi} to {max_rssi} dBm")
            
            report.append("")
        
        # Login analysis
        if self.logins:
            report.append("🔐 LOGIN ANALYSIS")
            report.append("-" * 30)
            
            usernames = Counter(l['username'] for l in self.logins if l['username'])
            report.append("Top Usernames:")
            for username, count in usernames.most_common(10):
                report.append(f"  {username}: {count} attempts")
            
            devices = Counter(l['device'] for l in self.logins if l['device'])
            if devices:
                report.append("\nTop Devices:")
                for device, count in devices.most_common(10):
                    report.append(f"  {device}: {count} attempts")
            
            report.append("")
        
        # Security insights
        report.append("🛡️  SECURITY INSIGHTS")
        report.append("-" * 30)
        
        # Multiple connection attempts from same MAC
        repeat_clients = [mac for mac, count in Counter(c['mac_address'] for c in self.clients).items() if count > 1]
        if repeat_clients:
            report.append(f"Repeat Clients: {len(repeat_clients)} devices connected multiple times")
        
        # Quick reconnections (potential enumeration)
        if len(self.clients) > 1:
            quick_reconnects = 0
            sorted_clients = sorted(self.clients, key=lambda x: x['datetime'])
            for i in range(1, len(sorted_clients)):
                time_diff = (sorted_clients[i]['datetime'] - sorted_clients[i-1]['datetime']).total_seconds()
                if time_diff < 10:  # Less than 10 seconds
                    quick_reconnects += 1
            
            if quick_reconnects > 0:
                report.append(f"Quick Reconnections: {quick_reconnects} (potential automated activity)")
        
        # Common usernames (potential social engineering)
        if self.logins:
            common_usernames = ['admin', 'administrator', 'test', 'user', 'guest', 'demo']
            found_common = [u for l in self.logins for u in common_usernames if u.lower() in l['username'].lower()]
            if found_common:
                report.append(f"Common Username Attempts: {len(set(found_common))} detected")
        
        report.append("")
        report.append("⚠️  DISCLAIMER: This tool is for authorized security testing only")
        
        return "\n".join(report)
    
    def _generate_json_report(self):
        """Generate JSON report"""
        data = {
            'summary': {
                'total_connections': self.stats['total_connections'],
                'unique_clients': len(self.stats['unique_clients']),
                'login_attempts': self.stats['login_attempts'],
                'start_time': self.stats['start_time'].isoformat() if self.stats['start_time'] else None,
                'end_time': self.stats['end_time'].isoformat() if self.stats['end_time'] else None
            },
            'clients': self.clients,
            'logins': [
                {
                    'timestamp': l['timestamp'].isoformat(),
                    'ip_address': l['ip_address'],
                    'username': l['username'],
                    'device': l['device']
                } for l in self.logins
            ],
            'alerts': [
                {
                    'timestamp': a['timestamp'].isoformat(),
                    'message': a['message']
                } for a in self.alerts
            ]
        }
        return json.dumps(data, indent=2, default=str)
    
    def export_csv(self, filename_prefix='captive_portal'):
        """Export data to CSV files"""
        # Export clients
        if self.clients:
            with open(f'{filename_prefix}_clients.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['timestamp', 'mac_address', 'rssi', 'hostname', 'ip_address'])
                writer.writeheader()
                for client in self.clients:
                    writer.writerow({
                        'timestamp': client['timestamp'],
                        'mac_address': client['mac_address'],
                        'rssi': client['rssi'],
                        'hostname': client['hostname'],
                        'ip_address': client['ip_address']
                    })
            print(f"✅ Exported {len(self.clients)} client records to {filename_prefix}_clients.csv")
        
        # Export logins
        if self.logins:
            with open(f'{filename_prefix}_logins.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['timestamp', 'ip_address', 'username', 'device'])
                writer.writeheader()
                for login in self.logins:
                    writer.writerow({
                        'timestamp': login['timestamp'].isoformat(),
                        'ip_address': login['ip_address'],
                        'username': login['username'],
                        'device': login['device']
                    })
            print(f"✅ Exported {len(self.logins)} login records to {filename_prefix}_logins.csv")

def main():
    parser = argparse.ArgumentParser(
        description='ESP32 Captive Portal Log Parser - Professional Red Team Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse log file and generate report
  python3 log_parser.py -f esp32_logs.txt -r text

  # Monitor serial port in real-time
  python3 log_parser.py -s /dev/ttyUSB0 -b 115200

  # Parse and export to CSV
  python3 log_parser.py -f logs.txt -c output

  # Generate JSON report
  python3 log_parser.py -f logs.txt -r json -o report.json

⚠️  FOR AUTHORIZED TESTING ONLY
        """
    )
    
    parser.add_argument('-f', '--file', help='Log file to parse')
    parser.add_argument('-s', '--serial', help='Serial port to monitor (e.g., /dev/ttyUSB0, COM3)')
    parser.add_argument('-b', '--baud', type=int, default=115200, help='Serial baud rate (default: 115200)')
    parser.add_argument('-r', '--report', choices=['text', 'json', 'html'], default='text', help='Report format')
    parser.add_argument('-o', '--output', help='Output file for report')
    parser.add_argument('-c', '--csv', help='Export to CSV with given prefix')
    parser.add_argument('--stats', action='store_true', help='Show quick statistics only')
    
    args = parser.parse_args()
    
    if not args.file and not args.serial:
        parser.print_help()
        return
    
    # Initialize parser
    log_parser = CaptivePortalLogParser()
    
    print("🔒 ESP32 Captive Portal Log Parser")
    print("=" * 40)
    print("⚠️  FOR AUTHORIZED TESTING ONLY")
    print("")
    
    # Parse input
    if args.file:
        if not log_parser.parse_file(args.file):
            return
    elif args.serial:
        if not log_parser.monitor_serial(args.serial, args.baud):
            return
    
    # Generate report
    if args.stats:
        print(f"\n📊 Quick Statistics:")
        print(f"   Total Connections: {log_parser.stats['total_connections']}")
        print(f"   Unique Clients: {len(log_parser.stats['unique_clients'])}")
        print(f"   Login Attempts: {log_parser.stats['login_attempts']}")
    else:
        report = log_parser.generate_report(args.report)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"✅ Report saved to {args.output}")
        else:
            print("\n" + report)
    
    # Export CSV if requested
    if args.csv:
        log_parser.export_csv(args.csv)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)