# Proximity SE Ultimate - ESP-IDF CMakeLists.txt
cmake_minimum_required(VERSION 3.16)

# Project Information
set(PROJECT_NAME "proximity_se_ultimate")
set(PROJECT_VER "2.0.0")
set(PROJECT_DESCRIPTION "Advanced Social Engineering & Penetration Testing Platform")

# ESP-IDF Version Requirements
set(SUPPORTED_TARGETS esp32 esp32s2 esp32s3 esp32c3 esp32c6)

# Include ESP-IDF CMake
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

# Project Definition
project(${PROJECT_NAME})

# Component Dependencies
set(COMPONENT_REQUIRES
    nvs_flash
    wifi_provisioning
    protocomm
    bt
    esp_wifi
    esp_event
    esp_netif
    esp_http_server
    esp_https_server
    spiffs
    fatfs
    wear_levelling
    esp_websocket_client
    json
    mdns
    esp_timer
    driver
    esp_adc
    esp_pm
    esp_sleep
    bootloader_support
    esp_ota_ops
    esp_partition
    mbedtls
    lwip
    freertos
    log
    esp_system
    heap
    soc
    hal
    esp_rom
    esp_common
    newlib
    xtensa
    pthread
    esp_ringbuf
    esp_mm
    spi_flash
    esp_app_format
    bootloader
    app_update
    esp_https_ota
    tcp_transport
    esp_http_client
    esp_tls
    esp_crt_bundle
    console
    vfs
    esp_psram
    esp_eth
    ulp
    unity
    esp_gdbstub
    esp_app_trace
    perfmon
    esp_hw_support
    esp_ipc
    esp_lcd
    esp_local_ctrl
    esp_serial_slave_link
    sdmmc
    esp_coex
    wpa_supplicant
    esp_phy
    esp-dsp
    esp-sr
    espcoredump
    esptool_py
    esp_insight
    rmaker_common
    esp_diagnostics
    esp_schedule
    esp_rainmaker
    qr_code
    cbor
    esp_delta_ota
    esp_encrypted_img
    esp_secure_cert_mgr
    esp_zigbee_lib
    esp_matter
    esp_protocol_mqtt
    protobuf-c
    expat
    esp_modem
    esp_modbus
    freemodbus
)

# Compiler Flags
target_compile_options(${COMPONENT_LIB} PRIVATE
    -Wall
    -Wextra
    -Werror=all
    -Wno-error=unused-function
    -Wno-error=unused-variable
    -Wno-error=deprecated-declarations
    -Wno-unused-parameter
    -Wno-sign-compare
    -ggdb
    -Os
    -freorder-blocks
    -fstrict-volatile-bitfields
    -fno-jump-tables
    -fno-tree-switch-conversion
)

# Linker Flags
target_link_libraries(${COMPONENT_LIB} 
    "-Wl,--gc-sections"
    "-Wl,--cref"
    "-Wl,--Map=${BUILD_DIR}/${PROJECT_NAME}.map"
    "-Wl,--start-group"
    "-Wl,--end-group"
    "-Wl,--undefined=uxTopUsedPriority"
)

# Custom Build Configurations
if(CONFIG_COMPILER_OPTIMIZATION_SIZE)
    target_compile_options(${COMPONENT_LIB} PRIVATE -Os)
elseif(CONFIG_COMPILER_OPTIMIZATION_PERF)
    target_compile_options(${COMPONENT_LIB} PRIVATE -O2)
elseif(CONFIG_COMPILER_OPTIMIZATION_DEBUG)
    target_compile_options(${COMPONENT_LIB} PRIVATE -Og)
endif()

# Memory Management
if(CONFIG_SPIRAM_SUPPORT)
    target_compile_definitions(${COMPONENT_LIB} PRIVATE
        CONFIG_SPIRAM_SUPPORT=1
        CONFIG_SPIRAM_USE_MALLOC=1
    )
endif()

# Security Features
if(CONFIG_SECURE_BOOT)
    target_compile_definitions(${COMPONENT_LIB} PRIVATE CONFIG_SECURE_BOOT=1)
endif()

if(CONFIG_SECURE_FLASH_ENC_ENABLED)
    target_compile_definitions(${COMPONENT_LIB} PRIVATE CONFIG_SECURE_FLASH_ENC_ENABLED=1)
endif()

# WiFi Configuration
target_compile_definitions(${COMPONENT_LIB} PRIVATE
    CONFIG_ESP32_WIFI_AMPDU_TX_ENABLED=1
    CONFIG_ESP32_WIFI_AMPDU_RX_ENABLED=1
    CONFIG_ESP32_WIFI_NVS_ENABLED=1
    CONFIG_ESP32_WIFI_SOFTAP_BEACON_MAX_LEN=752
    CONFIG_ESP32_WIFI_MGT_SBUF_NUM=32
    CONFIG_ESP32_WIFI_RX_BA_WIN=6
    CONFIG_ESP32_WIFI_TX_BA_WIN=6
    CONFIG_ESP32_WIFI_DYNAMIC_RX_BUFFER_NUM=32
    CONFIG_ESP32_WIFI_DYNAMIC_TX_BUFFER_NUM=32
    CONFIG_ESP32_WIFI_STATIC_RX_BUFFER_NUM=10
    CONFIG_ESP32_WIFI_STATIC_TX_BUFFER_NUM=16
)

# Bluetooth Configuration
target_compile_definitions(${COMPONENT_LIB} PRIVATE
    CONFIG_BT_ENABLED=1
    CONFIG_BTDM_CTRL_MODE_BLE_ONLY=1
    CONFIG_BTDM_CTRL_BLE_MAX_CONN=3
    CONFIG_BTDM_CTRL_BLE_MAX_CONN_EFF=3
    CONFIG_BTDM_SCAN_DUPL_TYPE_DEVICE=1
    CONFIG_BTDM_SCAN_DUPL_CACHE_SIZE=100
    CONFIG_BTDM_BLE_ADV_REPORT_DISCARD_THRSHOLD=20
    CONFIG_BT_RESERVE_DRAM=0x10000
)

# HTTP Server Configuration
target_compile_definitions(${COMPONENT_LIB} PRIVATE
    CONFIG_HTTPD_MAX_REQ_HDR_LEN=1024
    CONFIG_HTTPD_MAX_URI_LEN=1024
    CONFIG_HTTPD_ERR_RESP_NO_DELAY=1
    CONFIG_HTTPD_PURGE_BUF_LEN=32
    CONFIG_HTTPD_LOG_PURGE_DATA=1
    CONFIG_HTTPD_WS_SUPPORT=1
)

# SPIFFS Configuration
target_compile_definitions(${COMPONENT_LIB} PRIVATE
    CONFIG_SPIFFS_MAX_PARTITIONS=3
    CONFIG_SPIFFS_CACHE=1
    CONFIG_SPIFFS_CACHE_WR=1
    CONFIG_SPIFFS_CACHE_STATS=1
    CONFIG_SPIFFS_PAGE_CHECK=1
    CONFIG_SPIFFS_GC_MAX_RUNS=10
    CONFIG_SPIFFS_GC_STATS=1
    CONFIG_SPIFFS_PAGE_SIZE=256
    CONFIG_SPIFFS_OBJ_NAME_LEN=32
    CONFIG_SPIFFS_USE_MAGIC=1
    CONFIG_SPIFFS_USE_MAGIC_LENGTH=1
    CONFIG_SPIFFS_META_LENGTH=4
    CONFIG_SPIFFS_USE_MTIME=1
)

# FreeRTOS Configuration
target_compile_definitions(${COMPONENT_LIB} PRIVATE
    CONFIG_FREERTOS_UNICORE=0
    CONFIG_FREERTOS_CORETIMER_0=1
    CONFIG_FREERTOS_HZ=1000
    CONFIG_FREERTOS_ASSERT_ON_UNTESTED_FUNCTION=1
    CONFIG_FREERTOS_CHECK_STACKOVERFLOW_PTRVAL=1
    CONFIG_FREERTOS_THREAD_LOCAL_STORAGE_POINTERS=1
    CONFIG_FREERTOS_IDLE_TASK_STACKSIZE=1536
    CONFIG_FREERTOS_ISR_STACKSIZE=1536
    CONFIG_FREERTOS_LEGACY_HOOKS=1
    CONFIG_FREERTOS_MAX_TASK_NAME_LEN=16
    CONFIG_FREERTOS_SUPPORT_STATIC_ALLOCATION=1
    CONFIG_FREERTOS_TIMER_TASK_PRIORITY=1
    CONFIG_FREERTOS_TIMER_TASK_STACK_DEPTH=2048
    CONFIG_FREERTOS_TIMER_QUEUE_LENGTH=10
    CONFIG_FREERTOS_QUEUE_REGISTRY_SIZE=0
    CONFIG_FREERTOS_USE_TRACE_FACILITY=1
    CONFIG_FREERTOS_USE_STATS_FORMATTING_FUNCTIONS=1
    CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=1
    CONFIG_FREERTOS_DEBUG_INTERNALS=1
)

# Logging Configuration
target_compile_definitions(${COMPONENT_LIB} PRIVATE
    CONFIG_LOG_DEFAULT_LEVEL=3
    CONFIG_LOG_DEFAULT_LEVEL_INFO=1
    CONFIG_LOG_MAXIMUM_EQUALS_DEFAULT=1
    CONFIG_LOG_COLORS=1
    CONFIG_LOG_TIMESTAMP_SOURCE_RTOS=1
)

# Partition Table
set(PARTITION_TABLE_CUSTOM_FILENAME "partitions.csv")
set(PARTITION_TABLE_CUSTOM_APP_BIN_OFFSET "0x10000")

# Application Configuration
target_compile_definitions(${COMPONENT_LIB} PRIVATE
    PROJECT_NAME="${PROJECT_NAME}"
    PROJECT_VERSION="${PROJECT_VER}"
    PROJECT_DESCRIPTION="${PROJECT_DESCRIPTION}"
    PROXIMITY_SE_ULTIMATE=1
    MAX_DEVICES=100
    MAX_NETWORKS=50
    MAX_CREDENTIALS=100
    SYSTEM_LOG_SIZE=8192
    BLE_SCAN_TIME=5
    BEACON_ROTATION_TIME=8
    GEOFENCE_THRESHOLD=-55
    ATTACK_QUEUE_SIZE=10
    LOG_QUEUE_SIZE=20
)

# Custom Build Targets
add_custom_target(flash_monitor
    COMMAND ${CMAKE_COMMAND} -E env "IDF_PATH=${IDF_PATH}" 
    ${IDF_PATH}/tools/idf.py -p ${ESPPORT} -b ${ESPBAUD} flash monitor
    DEPENDS ${PROJECT_NAME}.elf
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Flashing and monitoring ${PROJECT_NAME}"
)

add_custom_target(size_analysis
    COMMAND ${CMAKE_COMMAND} -E env "IDF_PATH=${IDF_PATH}"
    ${IDF_PATH}/tools/idf.py size
    DEPENDS ${PROJECT_NAME}.elf
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Analyzing memory usage"
)

add_custom_target(menuconfig_gui
    COMMAND ${CMAKE_COMMAND} -E env "IDF_PATH=${IDF_PATH}"
    ${IDF_PATH}/tools/idf.py menuconfig
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Opening configuration menu"
)

# Documentation
add_custom_target(docs
    COMMAND doxygen ${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Generating documentation"
)

# Static Analysis
add_custom_target(cppcheck
    COMMAND cppcheck --enable=all --inconclusive --xml --xml-version=2 
    --output-file=${BUILD_DIR}/cppcheck_report.xml 
    ${CMAKE_CURRENT_SOURCE_DIR}/main
    COMMENT "Running static analysis with cppcheck"
)

# Unit Tests
add_custom_target(test
    COMMAND ${CMAKE_COMMAND} -E env "IDF_PATH=${IDF_PATH}"
    ${IDF_PATH}/tools/idf.py -C ${CMAKE_CURRENT_SOURCE_DIR}/test build
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Building and running unit tests"
)

# Clean Extended
add_custom_target(clean_all
    COMMAND ${CMAKE_COMMAND} -E env "IDF_PATH=${IDF_PATH}"
    ${IDF_PATH}/tools/idf.py fullclean
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${BUILD_DIR}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Full clean including build artifacts"
)

# Version Information
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/main/version.h.in
    ${CMAKE_CURRENT_BINARY_DIR}/version.h
    @ONLY
)

# Include Build Directory
target_include_directories(${COMPONENT_LIB} PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/main
    ${CMAKE_CURRENT_SOURCE_DIR}/components
)

# Print Configuration Summary
message(STATUS "========================================")
message(STATUS "Proximity SE Ultimate Build Configuration")
message(STATUS "========================================")
message(STATUS "Project: ${PROJECT_NAME}")
message(STATUS "Version: ${PROJECT_VER}")
message(STATUS "Target: ${IDF_TARGET}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "IDF Path: $ENV{IDF_PATH}")
message(STATUS "IDF Version: ${IDF_VER}")
message(STATUS "Compiler: ${CMAKE_C_COMPILER}")
message(STATUS "Build Directory: ${BUILD_DIR}")
message(STATUS "========================================")

# Warnings for Security
if(NOT CONFIG_SECURE_BOOT)
    message(WARNING "Secure boot is disabled - enable for production use")
endif()

if(NOT CONFIG_SECURE_FLASH_ENC_ENABLED)
    message(WARNING "Flash encryption is disabled - enable for production use")
endif()

# Size Optimization Warnings
math(EXPR TOTAL_FLASH_SIZE "${CONFIG_ESPTOOLPY_FLASHSIZE_DETECT} * 1024 * 1024")
message(STATUS "Flash Size: ${TOTAL_FLASH_SIZE} bytes")

if(CONFIG_COMPILER_OPTIMIZATION_DEBUG)
    message(WARNING "Debug optimization enabled - code size will be larger")
endif()

# Platform-Specific Configurations
if(IDF_TARGET STREQUAL "esp32")
    target_compile_definitions(${COMPONENT_LIB} PRIVATE ESP32_PLATFORM=1)
    message(STATUS "Configuring for ESP32 (dual-core)")
elseif(IDF_TARGET STREQUAL "esp32s2")
    target_compile_definitions(${COMPONENT_LIB} PRIVATE ESP32S2_PLATFORM=1)
    message(STATUS "Configuring for ESP32-S2 (single-core, USB)")
elseif(IDF_TARGET STREQUAL "esp32s3")
    target_compile_definitions(${COMPONENT_LIB} PRIVATE ESP32S3_PLATFORM=1)
    message(STATUS "Configuring for ESP32-S3 (dual-core, USB)")
elseif(IDF_TARGET STREQUAL "esp32c3")
    target_compile_definitions(${COMPONENT_LIB} PRIVATE ESP32C3_PLATFORM=1)
    message(STATUS "Configuring for ESP32-C3 (single-core, RISC-V)")
endif()

# Final Build Information
message(STATUS "Configuration complete. Available targets:")
message(STATUS "  build       - Build the project")
message(STATUS "  flash       - Flash to device")
message(STATUS "  monitor     - Monitor serial output")
message(STATUS "  flash_monitor - Flash and monitor")
message(STATUS "  size        - Show memory usage")
message(STATUS "  size_analysis - Detailed memory analysis")
message(STATUS "  menuconfig  - Configuration menu")
message(STATUS "  clean       - Clean build files")
message(STATUS "  clean_all   - Full clean")
message(STATUS "  docs        - Generate documentation")
message(STATUS "  test        - Run unit tests")
message(STATUS "========================================")