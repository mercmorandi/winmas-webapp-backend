/*
 * structs.h
 *
 *  Created on: 11 mag 2018
 *      Author: z
 */

#ifndef MAIN_STRUCTS_H_
#define MAIN_STRUCTS_H_

typedef unsigned char byte;

typedef struct {
	byte JarJar[2]; 		//header revision and pad; useless
	byte length; 			// radiotap header length
	byte JarJarBinks[11]; 	// other radiotap header stuff
	signed char ssi_signal;		// signal strength as captured by radiotap
} __attribute__((packed)) RadioTapHeader;

typedef struct {
	byte FC_L; 				// must be 0x40 for probe request
	byte FC_H;				// contains many flags, only interesting one is 'protected' to be tested
							// with the PROTECTED_FLAG_MASK below.
	byte DI[2]; 			// useless
	byte destination[6];
	byte source[6];
	byte bssid[6];
	byte frag_n__seq_n[2]; 	// useless data
	byte tag_n;				// tipically first tag is SSID, must check if 0
	byte tag_length;		// length of the SSID field
	char ssid_start;		// only if tag_length != 0
	// other tags, not interesting
} __attribute__((packed)) MGMT_Header;

#define PROTECTED_FLAG_MASK 0b01000000

// To-Do: maybe save MACs as strings?
typedef struct {
	unsigned long timestamp;
	char *destination;
	char *source;
	char *bssid;
	char *ssid;
	signed signal_strength_wroom;
	signed signal_strength_rt;
} Device_t;
#define MAX_DEVICES_IN_QUEUE 200
#define DEVICE_ID "EspWroom01"
#define MAX_WIFI_NAME_LENGTH 32 // according to 802.11 spec as in https://www.iith.ac.in/~tbr/teaching/docs/802.11-2007.pdf
								// page 101 (149 in the pdf) section "7.3.2.1 SSID element"
//********************************************* stuff needed for wifi ***************************************
#define DEFAULT_SSID "ssid"
#define DEFAULT_PWD "password."
#define SERVER_IP "192.168.1.7"
#define SERVER_PORT 9876
#define SOCK_RESET_TIME 5		// if server is not available we wait 5 seconds and retry

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


#endif /* MAIN_STRUCTS_H_ */
