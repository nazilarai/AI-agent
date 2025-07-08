idf_component_register(SRCS "main.cpp"
                      INCLUDE_DIRS "."
                      REQUIRES esp_wifi esp_netif esp_http_server esp_event nvs_flash spiffs fatfs driver esp_timer json mdns lwip)