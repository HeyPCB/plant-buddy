# Sprout firmware: ATtiny412, avr-gcc with tinyAVR 1-series support (avr-libc's iotn412.h).
#   make                 build sprout.hex
#   make flash PORT=/dev/tty.usbserial-XXXX     program over SerialUPDI (avrdude 7+)
AVR_PREFIX ?=
CC      = $(AVR_PREFIX)avr-gcc
OBJCOPY = $(AVR_PREFIX)avr-objcopy
SIZE    = $(AVR_PREFIX)avr-size
MCU     = attiny412
F_CPU   = 3333333UL
CFLAGS  = -mmcu=$(MCU) -DF_CPU=$(F_CPU) -Os -std=gnu11 -Wall -Wextra -Werror \
          -ffunction-sections -fdata-sections
LDFLAGS = -mmcu=$(MCU) -Wl,--gc-sections
PORT   ?= /dev/ttyUSB0

all: sprout.hex

sprout.elf: main.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<
	$(SIZE) $@

sprout.hex: sprout.elf
	$(OBJCOPY) -O ihex -R .eeprom $< $@

flash: sprout.hex
	avrdude -c serialupdi -P $(PORT) -p t412 -U flash:w:sprout.hex:i

clean:
	rm -f sprout.elf sprout.hex

.PHONY: all flash clean
