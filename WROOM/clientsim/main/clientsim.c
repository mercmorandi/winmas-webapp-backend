#include <stdio.h>
#include <sys/socket.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/portmacro.h"
#include "freertos/event_groups.h"

#include "sdkconfig.h"

#include "esp_wifi.h"
#include "esp_wifi_internal.h"
#include "esp_system.h"
#include "esp_log.h"
#include "esp_event_loop.h"
#include "esp_event.h"

#include "nvs_flash.h"
#include "lwip/err.h"
#include "driver/gpio.h"

#include "structs.h"
#include "queue.h"

int openSocket();
void wifi_init_winmas();
void wifi_promiscuousON();
void wifi_promiscuousOFF();
void wifi_turn_on();
static esp_err_t event_handler(void *ctx, system_event_t *event);
static void prom_handler(void *buf, wifi_promiscuous_pkt_type_t type);
char *toBinary(unsigned char valore);
char *MACtoS(char* o, unsigned char mac[6]);
unsigned long getTime();
Device_t Device(unsigned long timestamp,
				char *destination,
				char *source,
				char *bssid,
				char *ssid,
				signed signal_strength_wroom,
				signed signal_strength_rt);


Q CapturedDevices;
bool DataSent;
void app_main()
{
	printf("WinMAS avviato\n");
	esp_err_t ret = nvs_flash_init();
	if (ret == ESP_ERR_NVS_NO_FREE_PAGES) {
		ESP_ERROR_CHECK(nvs_flash_erase());
		ret = nvs_flash_init();
	}
	ESP_ERROR_CHECK( ret );
	CapturedDevices = QueueInit(MAX_DEVICES_IN_QUEUE);
	wifi_init_winmas();
	while (1) {
		wifi_promiscuousON();
		vTaskDelay(30000 / portTICK_PERIOD_MS); // send data every 60 seconds
		ESP_LOGI("Main", "Sending data now");
		wifi_promiscuousOFF();
		DataSent = false;
		wifi_turn_on(); // data is sent when the wroom receives an IP
		while(!DataSent) // wait for data to be sent before going back to promiscuous mode
			vTaskDelay(2000 / portTICK_PERIOD_MS);
	}
}


int openSocket(){
	int socketFD = socket(AF_INET,SOCK_STREAM,0);
	struct sockaddr_in addr;
//	memset(&addr, '0', sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_port = htons(SERVER_PORT);
	if(inet_pton(AF_INET, SERVER_IP, &addr.sin_addr)<=0) {
		printf("IP del server non valido\n");
		close(socketFD);
		return -1;
	}
	if (connect(socketFD, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
	    perror("Impossibile raggiungere il server\n");
	    close(socketFD);
	    return -1;
	}
	return socketFD;
}

void wifi_init_winmas() {
	tcpip_adapter_init();
	ESP_ERROR_CHECK(esp_event_loop_init(event_handler, NULL));

	wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
	ESP_ERROR_CHECK(esp_wifi_init(&cfg));
}

void wifi_promiscuousON() {
    ESP_ERROR_CHECK(esp_wifi_set_event_mask(WIFI_EVENT_MASK_NONE));
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));
    ESP_ERROR_CHECK(esp_wifi_set_channel(6, WIFI_SECOND_CHAN_NONE));
    wifi_promiscuous_filter_t filter;
	filter.filter_mask = WIFI_PROMIS_FILTER_MASK_MGMT;
	ESP_ERROR_CHECK(esp_wifi_set_promiscuous_filter(&filter));
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_rx_cb(&prom_handler));

}

void wifi_promiscuousOFF() {
	ESP_ERROR_CHECK(esp_wifi_set_promiscuous(false));
}

void wifi_turn_on() {
	wifi_config_t wifi_config = {
		.sta = {
			.ssid = DEFAULT_SSID,
			.password = DEFAULT_PWD,
			.scan_method = DEFAULT_SCAN_METHOD,
			.sort_method = DEFAULT_SORT_METHOD,
			.threshold.rssi = DEFAULT_RSSI,
			.threshold.authmode = DEFAULT_AUTHMODE,
		},
	};
	ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
	ESP_ERROR_CHECK(esp_wifi_set_config(ESP_IF_WIFI_STA, &wifi_config));
	ESP_ERROR_CHECK(esp_wifi_start());
}
static esp_err_t event_handler(void *ctx, system_event_t *event)
{
	const char *TAG = "scan";
    switch (event->event_id) {
        case SYSTEM_EVENT_STA_START:
            ESP_LOGI(TAG, "SYSTEM_EVENT_STA_START");
            ESP_ERROR_CHECK(esp_wifi_connect());
            break;
        case SYSTEM_EVENT_STA_GOT_IP:
            ESP_LOGI(TAG, "SYSTEM_EVENT_STA_GOT_IP");
            ESP_LOGI(TAG, "Got IP: %s\n",
                     ip4addr_ntoa(&event->event_info.got_ip.ip_info.ip));
            ESP_LOGI(TAG, "Sending info to server");
            //ToDo pop and send info

			int socket;
			while ((socket = openSocket()) < 0) {
				ESP_LOGE(TAG, "Can't connect, retrying in...\n");
				for (int i = 0; i< SOCK_RESET_TIME; i++) {
					ESP_LOGE(TAG, "%d\n", SOCK_RESET_TIME - i);
					vTaskDelay(1000 / portTICK_PERIOD_MS);
				}
			}
			char stringa[1000]; //ToDo: 1000 should be high enough but it looks bad. maybe change with smart malloc?

			sprintf(stringa, "%s,%d\n", DEVICE_ID, QueueGetSize(CapturedDevices));
			send(socket, stringa, strlen(stringa),0);

			Device_t device;
			while(QueuePop(CapturedDevices, &device)) {
				//ToDo: Maybe sanitize strings before sending them?
				sprintf(stringa, "%lu,%s,%s,%s,%s,%d,%d\n",
						device.timestamp,
						device.destination,
						device.source,
						device.bssid,
						device.ssid,
						device.signal_strength_wroom,
						device.signal_strength_rt);
				send(socket, stringa, strlen(stringa),0);
			}
			ESP_LOGI(TAG,"Data sent to server");
			close(socket);
			DataSent = true;	// we unlock the main thread so the wroom goes back to promiscuous
			ESP_ERROR_CHECK(esp_wifi_disconnect());
            break;
        default:
            break;
    }
    return ESP_OK;
}

static void prom_handler(void *buf, wifi_promiscuous_pkt_type_t type){
	char TAG[] = "PROM";
	char buffer[19]; // used for hex to string on MAC address
	char *ssid_buffer = malloc(sizeof(char)*(MAX_WIFI_NAME_LENGTH +1));
	wifi_promiscuous_pkt_t *p = buf;
	RadioTapHeader *rth = (RadioTapHeader *)p->payload;
	if (p->rx_ctrl.sig_len < rth->length) {
		ESP_LOGE(TAG, "Error on packet length. RadioTap header %u long but captured frame is %u. Discarding", rth->length, p->rx_ctrl.sig_len);
		return;
	}
	MGMT_Header *h = (MGMT_Header *)&(p->payload[rth->length]);
	if (h->FC_L == 0x40) { // if it is a probe request
		ESP_LOGI(TAG,"Signal Strength: wroom=%d rt=%d", p->rx_ctrl.rssi, rth->ssi_signal);
		ESP_LOGI(TAG,"destination:\t%s ", MACtoS(buffer, h->destination));
		ESP_LOGI(TAG,"source:\t%s ", MACtoS(buffer, h->source));
		ESP_LOGI(TAG,"bssid:\t%s ", MACtoS(buffer, h->bssid));
		if (!(h->FC_H & PROTECTED_FLAG_MASK) && (h->tag_n == 0)) { // if content is not protected and first tag is SSID
			if ((h->tag_length == 0) || (h->tag_length > MAX_WIFI_NAME_LENGTH)) {
				strcpy(ssid_buffer, "None");
			} else {
				strncpy(ssid_buffer, &h->ssid_start, h->tag_length);
				ssid_buffer[h->tag_length] = '\0';
			}
			ESP_LOGI(TAG,"SSID: %s", ssid_buffer);
		}
		ESP_LOGI(TAG,"\n");
		QueuePush(CapturedDevices,Device(	getTime(),
											MACtoS(NULL, h->destination),
											MACtoS(NULL, h->source),
											MACtoS(NULL, h->bssid),
											ssid_buffer,
											p->rx_ctrl.rssi,
											rth->ssi_signal
										));
	}
}


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

char *MACtoS(char* o, unsigned char mac[6]) {
	if (o == NULL)
		o = malloc(sizeof(char)*18);
	int num = sprintf(o,"%02x:%02x:%02x:%02x:%02x:%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
	if (num == 17) // sprintf doesn't count the \0
		return o;
	else
		ESP_LOGE("MACtoS", "returned %d instead of 17", num);
		return "Error displaying MAC address";
}

unsigned long getTime() {
	return esp_log_timestamp(); //ToDo
}

Device_t Device(unsigned long timestamp,
				char *destination,
				char *source,
				char *bssid,
				char *ssid,
				signed signal_strength_wroom,
				signed signal_strength_rt) {

	Device_t t = {	timestamp,
					destination,
					source,
					bssid,
					ssid,
					signal_strength_wroom,
					signal_strength_rt};
	return t;
}
