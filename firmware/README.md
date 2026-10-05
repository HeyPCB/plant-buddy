# Sprout firmware (ATtiny412)

One file, [`main.c`](main.c), bare-metal C on avr-libc: no Arduino core, no libraries. The comments at
its top say what it does, pin by pin.

## Build

Any avr-gcc whose avr-libc knows the tinyAVR 1-series (`-mmcu=attiny412`, header `iotn412.h`):

```sh
make                       # or: make AVR_PREFIX=/path/to/avr-gcc/bin/
```

Compiled on 2026-10-05 with avr-gcc 15.1.0 (Microchip AVR 8-bit toolchain 4.0.0, the
`felias-fogg/avr-gcc-15` arm64 macOS build) under `-Wall -Wextra -Werror`:

```
   text    data     bss     dec     hex filename
   1340       0       6    1346     542 sprout.elf
```

1,340 of 4,096 bytes of flash. [`sprout.hex`](sprout.hex) is that build.

## Flash

The board has three UPDI pads (VCC, UPDI, GND) beside the cell holder. Any USB-serial adapter becomes
a UPDI programmer with a 4.7 kΩ resistor from its TX to UPDI and RX tied to UPDI (SerialUPDI). Take the
coin cell out and power the board from the adapter's 3.3 V:

```sh
make flash PORT=/dev/tty.usbserial-XXXX      # avrdude 7+: -c serialupdi -p t412
```

Fuses can stay at their factory values (20 MHz oscillator divided by 6 = 3.33 MHz, which `F_CPU` assumes).

## First use

1. Put a CR2032 in **with the stake in open air**: the first reading becomes "air" (it winks hello).
2. Push it into freshly watered soil up to the soil line, and hold the bud 3 s: the eyes flash three
   times, and that reading becomes "wet".
3. Done. A tear every 16 s means "water me"; a wink about once a minute means "all good".

## Status

Compiled, not yet run on hardware: no Sprout has been built. On the first prototypes, check the
charge-time counts in air, dry soil and wet soil (a debugger or a few extra `wink()`s) and tune
`THIRSTY_PCT` if the threshold sits too close to either end.

## License

MIT (see [`LICENSE`](LICENSE)).
