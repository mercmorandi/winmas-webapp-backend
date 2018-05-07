deps_config := \
	/home/z/esp/esp-idf/components/app_trace/Kconfig \
	/home/z/esp/esp-idf/components/aws_iot/Kconfig \
	/home/z/esp/esp-idf/components/bt/Kconfig \
	/home/z/esp/esp-idf/components/driver/Kconfig \
	/home/z/esp/esp-idf/components/esp32/Kconfig \
	/home/z/esp/esp-idf/components/esp_adc_cal/Kconfig \
	/home/z/esp/esp-idf/components/ethernet/Kconfig \
	/home/z/esp/esp-idf/components/fatfs/Kconfig \
	/home/z/esp/esp-idf/components/freertos/Kconfig \
	/home/z/esp/esp-idf/components/heap/Kconfig \
	/home/z/esp/esp-idf/components/libsodium/Kconfig \
	/home/z/esp/esp-idf/components/log/Kconfig \
	/home/z/esp/esp-idf/components/lwip/Kconfig \
	/home/z/esp/esp-idf/components/mbedtls/Kconfig \
	/home/z/esp/esp-idf/components/openssl/Kconfig \
	/home/z/esp/esp-idf/components/pthread/Kconfig \
	/home/z/esp/esp-idf/components/spi_flash/Kconfig \
	/home/z/esp/esp-idf/components/spiffs/Kconfig \
	/home/z/esp/esp-idf/components/tcpip_adapter/Kconfig \
	/home/z/esp/esp-idf/components/wear_levelling/Kconfig \
	/home/z/esp/esp-idf/components/bootloader/Kconfig.projbuild \
	/home/z/esp/esp-idf/components/esptool_py/Kconfig.projbuild \
	/home/z/esp/winmas/WROOM/clientsim/main/Kconfig.projbuild \
	/home/z/esp/esp-idf/components/partition_table/Kconfig.projbuild \
	/home/z/esp/esp-idf/Kconfig

include/config/auto.conf: \
	$(deps_config)


$(deps_config): ;
