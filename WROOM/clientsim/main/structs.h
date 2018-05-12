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
	byte timestamp;
	byte destination[6];
	byte source[6];
	signed signal_strength;
} Device_t;

#endif /* MAIN_STRUCTS_H_ */
