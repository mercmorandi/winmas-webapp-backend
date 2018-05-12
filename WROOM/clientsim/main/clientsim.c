#include <stdio.h>
#include <sys/socket.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/portmacro.h"
#include "sdkconfig.h"
#include "freertos/event_groups.h"
#include "esp_wifi.h"
#include "esp_wifi_internal.h"
#include "esp_system.h"
#include "esp_log.h"
#include "esp_event_loop.h"
#include "nvs_flash.h"
#include "freertos/FreeRTOS.h"
#include "esp_wifi.h"
#include "esp_wifi_internal.h"
#include "lwip/err.h"
#include "esp_system.h"
#include "esp_event.h"
#include "esp_event_loop.h"
#include "nvs_flash.h"
#include "driver/gpio.h"
#include "structs.h"
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
char *toBinary(unsigned char valore);
char *MACtoS(char* o, unsigned char mac[6]);
//static int openSocket();

Device_t device_array[20];
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
//	while (1) {
////		int socket;
////		while ((socket = openSocket()) < 0) {
////			printf("Retrying in...");
////			for (int i = 0; i< SOCK_RESET_TIME; i++) {
////				printf("%d\n", SOCK_RESET_TIME - i);
////				vTaskDelay(1000 / portTICK_PERIOD_MS);
////			}
////		}
////		char* stringa = "prova_socket";
////		send(socket, stringa, strlen(stringa),0);
////		printf("Connessione effettuata con successo\n");
////		close(socket);
//		vTaskDelay(600000 / portTICK_PERIOD_MS);
//	}
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


    ESP_ERROR_CHECK(esp_wifi_start() );
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));
    ESP_ERROR_CHECK(esp_wifi_set_channel(6, WIFI_SECOND_CHAN_NONE));
    wifi_promiscuous_filter_t filter;
        filter.filter_mask = WIFI_PROMIS_FILTER_MASK_MGMT;
	ESP_ERROR_CHECK(esp_wifi_set_promiscuous_filter(&filter));
	vTaskDelay(5000 / portTICK_PERIOD_MS);
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_rx_cb(&prom_handler));
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
//    ESP_LOGI("Altro","Chiamata all'handler\n");
    return ESP_OK;
}

void prom_handler(void *buf, wifi_promiscuous_pkt_type_t type){
	char TAG[] = "PROM";
	char buffer[19];
	wifi_promiscuous_pkt_t *p = buf;
	RadioTapHeader *rth = (RadioTapHeader *)p->payload;
	if (p->rx_ctrl.sig_len < rth->length) {
		ESP_LOGE(TAG, "Error on packet length. Header says %u but overall is %u", rth->length, p->rx_ctrl.sig_len);
		return;
	}
	MGMT_Header *h = (MGMT_Header *)&(p->payload[rth->length]);
	if (h->FC_L == 0x40) { // if it is a probe request
		ESP_LOGI(TAG, "Signal Strength: wroom=%d rt=%d", p->rx_ctrl.rssi, rth->ssi_signal);
		ESP_LOGI(TAG,"destination:\t%s ", MACtoS(buffer, h->destination));
		ESP_LOGI(TAG,"source:\t%s ", MACtoS(buffer, h->source));
		ESP_LOGI(TAG,"bssid:\t%s ", MACtoS(buffer, h->bssid));
		if (!(h->FC_H & PROTECTED_FLAG_MASK) && (h->tag_n == 0)) { // if content is not protected and first tag is SSID
			if (h->tag_length == 0)
				ESP_LOGI(TAG,"SSID: None");
			else {
				char ssid_buffer[h->tag_length +1];
				strncpy(ssid_buffer, &h->ssid_start, h->tag_length);
				ssid_buffer[h->tag_length] = '\0';
				ESP_LOGI(TAG,"SSID: %s", ssid_buffer);
			}
		}

	}
}

//	unsigned char header_l = p->payload[2];
//	unsigned char valore = p->payload[header_l];
//	printf("%s\n", toBinary(valore));

//	printf("%s\n", toBinary(h->FC_L));
//	if (h->FC_L != 0b00100000)
//		return;
//	unsigned char mac_mio[6] = {0x10,0x13,0x31,0x53,0x33,0x47};
//	bool sorgente_ok = true;
//	bool dest_ok = true;
//	for (int i=0; i<6; i++){
//		if (h->source[i] != mac_mio[i])
//			sorgente_ok = false;
//	}
//	for (int i=0; i<6; i++){
//		if (h->destination[i] != mac_mio[i])
//			dest_ok = false;
//	}
//	if (!sorgente_ok && !dest_ok)
//		return;
//	printf("%s %s\n", toBinary(h->FC_L), toBinary(h->FC_H));

//	if (valore != 0b01000000)
//		return;
//	unsigned char valore = 1024;
//	if ((valore != 0x04)) return;
//	if ((valore>>2 != 4) && (valore>>2 != 5)) return;
//	if (type != WIFI_PKT_MGMT) {
//		printf("non mgmt frame found\t");
//		return;
//	} else {
//		printf("mgmt: %s\n", toBinary(p->payload[0]));
//		return;
//	}
//	unsigned char *payload = p->payload;
//	printf("Catturata Probe-Request con i seguenti dati:\n"); fflush(stdout);

	/*
	printf("sorgente:\t\t");
	for (int i = 4; i< 10; i++) {
		printf("%02x ", payload[i]);
	}
	printf("\ndestinazione:\t\t");
	for (int i = 10; i< 16; i++) {
		printf("%02x ", payload[i]);
	}
	printf("\nBSSID:\t\t\t");
	for (int i = 16; i< 22; i++) {
		printf("%02x ", payload[i]);
	}
	printf("\nPayload:");
	for (int i = 22; i< p->rx_ctrl.sig_len; i++) {
		(i%16 == 0) ? printf("\n"):0;
		printf("%c ", payload[i]);

	}
	printf("\nLength=%d ", p->rx_ctrl.sig_len);
	printf("FC:%s %s %s %s",toBinary(payload[0]), toBinary(payload[1]), toBinary(payload[2]), toBinary(payload[3]));
	printf("\n\n");
	fflush(stdout);
}*/

char *toBinary(unsigned char valore){
	char *b = calloc(sizeof(unsigned char), 9);
	b[8] = '\0';
	b[0] = ((valore & 1)) + '0';
	b[1] = ((valore & 2)>>1) + '0';
	b[2] = ((valore & 4)>>2) + '0';
	b[3] = ((valore & 8)>>3) + '0';
	b[4] = ((valore & 16)>>4) + '0';
	b[5] = ((valore & 32)>>5) + '0';
	b[6] = ((valore & 64)>>6) + '0';
	b[7] = ((valore & 128)>>7) + '0';
	return b;
}

void populateFakeDevices(){
	for (int i=0; i<20; i++){
		Device_t d;
		for (int j=0; j<6; j++) {
			d.destination[j] = i*j;
			d.source[j] = 3*i*j;
		}
		d.timestamp = 0;
		d.signal_strength = -40;
		device_array[i] = d;
	}
}

char *MACtoS(char* o, unsigned char mac[6]) {
//	char *o = malloc(sizeof(char)*19); // we need 19 characters to display a mac address including the \0
	int num = sprintf(o,"%02x:%02x:%02x:%02x:%02x:%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
	if (num == 17) // sprintf doesn't count the \0
		return o;
	else
		ESP_LOGE("MACtoS", "returned %d instead of 17", num);
		return "Error displaying MAC address";
}

