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
#define DEFAULT_SSID "nome_rete"
#define DEFAULT_PWD "psw."
#define SERVER_IP "192.168.1.7"
#define SERVER_PORT 9876
#define SOCK_RESET_TIME 5

#if CONFIG_WIFI_ALL_CHANNEL_SCAN
#define DEFAULT_SCAN_METHOD WIFI_ALL_CHANNEL_SCAN
#elif CONFIG_WIFI_FAST_SCAN
#define DEFAULT_SCAN_METHOD WIFI_FAST_SCAN
#else
#define DEFAULT_SCAN_METHOD WIFI_FAST_SCAN
#endif /*CONFIG_SCAN_METHOD*/

#if CONFIG_WIFI_CONNECT_AP_BY_SIGNAL
#define DEFAULT_SORT_METHOD WIFI_CONNECT_AP_BY_SIGNAL
#elif CONFIG_WIFI_CONNECT_AP_BY_SECURITY
#define DEFAULT_SORT_METHOD WIFI_CONNECT_AP_BY_SECURITY
#else
#define DEFAULT_SORT_METHOD WIFI_CONNECT_AP_BY_SIGNAL
#endif /*CONFIG_SORT_METHOD*/

#if CONFIG_FAST_SCAN_THRESHOLD
#define DEFAULT_RSSI CONFIG_FAST_SCAN_MINIMUM_SIGNAL
#if CONFIG_EXAMPLE_OPEN
#define DEFAULT_AUTHMODE WIFI_AUTH_OPEN
#elif CONFIG_EXAMPLE_WEP
#define DEFAULT_AUTHMODE WIFI_AUTH_WEP
#elif CONFIG_EXAMPLE_WPA
#define DEFAULT_AUTHMODE WIFI_AUTH_WPA_PSK
#elif CONFIG_EXAMPLE_WPA2
#define DEFAULT_AUTHMODE WIFI_AUTH_WPA2_PSK
#else
#define DEFAULT_AUTHMODE WIFI_AUTH_OPEN
#endif
#else
#define DEFAULT_RSSI -127
#define DEFAULT_AUTHMODE WIFI_AUTH_OPEN
#endif /*CONFIG_FAST_SCAN_THRESHOLD*/

//static bool connesso = false;
static void wifi_scan(void);
static esp_err_t event_handler(void *ctx, system_event_t *event);
void prom_handler(void *buf, wifi_promiscuous_pkt_type_t type);
//static int openSocket();


void app_main()
{
	printf("WinMAS avviato\n");
	esp_err_t ret = nvs_flash_init();
	if (ret == ESP_ERR_NVS_NO_FREE_PAGES) {
		ESP_ERROR_CHECK(nvs_flash_erase());
		ret = nvs_flash_init();
	}
	ESP_ERROR_CHECK( ret );
	wifi_scan();
	while (1) {
//		int socket;
//		while ((socket = openSocket()) < 0) {
//			printf("Retrying in...");
//			for (int i = 0; i< SOCK_RESET_TIME; i++) {
//				printf("%d\n", SOCK_RESET_TIME - i);
//				vTaskDelay(1000 / portTICK_PERIOD_MS);
//			}
//		}
//		char* stringa = "prova_socket";
//		send(socket, stringa, strlen(stringa),0);
//		printf("Connessione effettuata con successo\n");
//		close(socket);
		vTaskDelay(1000 / portTICK_PERIOD_MS);
		fflush(stdout);
	}
}


//static int openSocket(){
//	int socketFD = socket(AF_INET,SOCK_STREAM,0);
//	struct sockaddr_in addr;
////	memset(&addr, '0', sizeof(addr));
//	addr.sin_family = AF_INET;
//	addr.sin_port = htons(SERVER_PORT);
//	if(inet_pton(AF_INET, SERVER_IP, &addr.sin_addr)<=0) {
//		printf("IP del server non valido\n");
//		close(socketFD);
//		return -1;
//	}
//	if (connect(socketFD, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
//	    perror("Impossibile raggiungere il server\n");
//	    close(socketFD);
//	    return -1;
//	}
//	return socketFD;
//}

static void wifi_scan(void)
{
    tcpip_adapter_init();
    ESP_ERROR_CHECK(esp_event_loop_init(event_handler, NULL));


    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_wifi_set_event_mask(WIFI_EVENT_MASK_NONE));
    wifi_promiscuous_filter_t filter;
    filter.filter_mask = WIFI_PROMIS_FILTER_MASK_MGMT;
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_filter(&filter));
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_rx_cb(&prom_handler));

    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));
    ESP_ERROR_CHECK(esp_wifi_set_channel(6, WIFI_SECOND_CHAN_NONE));
//    wifi_config_t wifi_config = {
//        .sta = {
//            .ssid = DEFAULT_SSID,
//            .password = DEFAULT_PWD,
//            .scan_method = DEFAULT_SCAN_METHOD,
//            .sort_method = DEFAULT_SORT_METHOD,
//            .threshold.rssi = DEFAULT_RSSI,
//            .threshold.authmode = DEFAULT_AUTHMODE,
//        },
//    };
//    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
//    ESP_ERROR_CHECK(esp_wifi_set_config(ESP_IF_WIFI_STA, &wifi_config));
//    ESP_ERROR_CHECK(esp_wifi_start());
}
static esp_err_t event_handler(void *ctx, system_event_t *event)
{
	const char *TAG = "scan";
    switch (event->event_id) {
        case SYSTEM_EVENT_STA_START:
            ESP_LOGI(TAG, "SYSTEM_EVENT_STA_START");
//            ESP_ERROR_CHECK(esp_wifi_connect());
            break;
        case SYSTEM_EVENT_STA_GOT_IP:
            ESP_LOGI(TAG, "SYSTEM_EVENT_STA_GOT_IP");
            ESP_LOGI(TAG, "Got IP: %s\n",
                     ip4addr_ntoa(&event->event_info.got_ip.ip_info.ip));
            break;
        case SYSTEM_EVENT_STA_DISCONNECTED:
            ESP_LOGI(TAG, "SYSTEM_EVENT_STA_DISCONNECTED");
//            ESP_ERROR_CHECK(esp_wifi_connect());
            break;
        case SYSTEM_EVENT_AP_PROBEREQRECVED:
        	ESP_LOGI(TAG, "Probe request received:\n");
        	printf("Signal strength: %d ", event->event_info.ap_probereqrecved.rssi);
        	uint8_t *mac =  event->event_info.ap_probereqrecved.mac;
        	printf("from MAC ");
        	for (int i=0; i< 6; i++)
        		printf(" %02x",mac[i]);
        	printf("\n\n");
        	break;
        default:
        	ESP_LOGI(TAG,"other event: %d", event->event_id);
            break;
    }
    ESP_LOGI("Altro","Chiamata all'handler\n");
    return ESP_OK;
}

void prom_handler(void *buf, wifi_promiscuous_pkt_type_t type){
	wifi_promiscuous_pkt_t *p = buf;
	unsigned char valore = p->payload[0];
//	unsigned char valore = 1024;
//	if (valore == 0x00000080) return;
	char b[9]; b[8]='\0';
	b[7] = ((valore & 1)) + '0';
	b[6] = ((valore & 2)>>1) + '0';
	b[5] = ((valore & 4)>>2) + '0';
	b[4] = ((valore & 8)>>3) + '0';
	b[3] = ((valore & 16)>>4) + '0';
	b[2] = ((valore & 32)>>5) + '0';
	b[1] = ((valore & 64)>>6) + '0';
	b[0] = ((valore & 128)>>7) + '0';
	if ((valore>>2 != 4)) return;
	unsigned char *payload = p->payload;
//	printf("Catturata Probe-Request con i seguenti dati:\n"); fflush(stdout);
	printf("sorgente:\t\t");
	for (int i = 4; i< 10; i++) {
		printf("%02x ", payload[i]);
	}
	printf("\ndestinazione:\t\t");
	for (int i = 10; i< 16; i++) {
		printf("%02x ", payload[i]);
	}
	printf("\nterzo_indirizzo:\t");
	for (int i = 16; i< 22; i++) {
		printf("%02x ", payload[i]);
	}
	printf("\nquarto_indirizzo:\t");
	for (int i = 24; i< 30; i++) {
		printf("%02x ", payload[i]);
	}
	printf("\n\n");
	fflush(stdout);
}






