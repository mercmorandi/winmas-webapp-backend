/*
 * ConnectionManager.cpp
 *
 *  Created on: 10 mag 2018
 *      Author: z
 */

#include "ConnectionManager.h"

#include <stdio.h>
#include <sys/socket.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/portmacro.h"
#include "sdkconfig.h"
#include "freertos/event_groups.h"
#include "esp_wifi.h"
#include "esp_log.h"
#include "esp_event_loop.h"
#include "nvs_flash.h"
//#include "/home/z/esp/esp-idf/components/tcpip_adapter/include/tcpip_adapter.h"


static esp_err_t event_handler(void *ctx, system_event_t *event);
ConnectionManager::ConnectionManager() {
}
