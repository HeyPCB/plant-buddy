# 01 · Sprout, the plant buddy: SPEC

## Who it's for, and the use case

Anyone with houseplants who forgets to water them or drowns them. Sprout lives in the pot. It tells you
when the soil is dry, on the plant itself, with a face you'll notice walking past. It needs no app, no
Wi-Fi and no charging: one coin cell lasts about two years.

## The cute concept

A sprout pushing out of the soil: two gold leaves, a round green head with LED eyes and blush cheeks,
the coin cell in its belly, and a stem that goes into the soil. When the soil dries out, a blue LED
**tear** drips under its left eye every 16 seconds. When the plant is fine, it winks every minute or so.
Boop the bud between its leaves and it answers at once.

## Features

| | |
|---|---|
| Sensing | Capacitive soil moisture: a mask-covered electrode down the stem (no metal touches the soil, so nothing corrodes), timed by the MCU through 1 MΩ. Wet soil reads several times dry air. |
| Calibration | "Air" is learned automatically: the driest reading it has ever seen, in EEPROM. "Wet": push it into freshly watered soil and hold the bud 3 s (three eye flashes). Thirsty = below 35 % of the way from air to wet, with 6 % hysteresis. |
| Face | 2 green LED eyes (wink = happy), 1 blue LED tear (thirsty), gold blush cheeks, silk smile |
| Button | The bud (TS-1187A): boop to check now, hold 3 s to learn "wet" |
| MCU | ATtiny412 (SOIC-8), 1.8-5.5 V; RTC wake every 8 s, soil measured about once a minute |
| Power | One CR2032 in a Keystone 3034 SMT holder |
| Board | 2 layers, green mask, white silk, ENIG; single-sided SMT, 13 placed parts; QR on the back links to its page |

## Power budget and battery life

Assumptions (datasheet typical values, rounded up): ATtiny412 asleep in power-down with the RTC's
periodic interrupt ≈ 1.5 µA budgeted; awake at 3.33 MHz ≈ 1 mA; a green LED through 100 Ω from 3.0 V
≈ 2.7 mA, the blue one ≈ 2 mA. CR2032: 225 mAh nominal, 180 mAh usable (80 %). The LED currents are
upper bounds: both dies are InGaN, about 2.8 V at 1-2 mA, so from a 3.0 V cell the eyes draw nearer
1-1.5 mA (bright enough for an InGaN die) and dim first as the cell runs down; the life below is
then a little longer.

| Activity | How often | Charge each | Average |
|---|---|---|---|
| Sleep (power-down + RTC) | always | | 1.5 µA |
| Soil reading (16 charge times, ~10 ms awake) | every 64 s | 10 µC | 0.16 µA |
| Happy double wink (2 eyes x 60 ms, ~200 ms awake) | every 64 s | 0.32 mC LEDs + 0.2 mC CPU | 8.1 µA |
| Thirsty tear drip (120 ms fade, ~50 % duty, awake) | every 16 s | 0.12 mC LED + 0.12 mC CPU | 15 µA |

- **Plant watered (happy): ≈ 9.8 µA → about 2.1 years.**
- **Plant thirsty the whole time: ≈ 16.7 µA → about 15 months.** A thirsty plant is rarely left that long.
- A boop costs about 0.5 mC, so 10 boops a day is another 0.06 µA.

These are design estimates from datasheet typicals, not measurements of a built board (none has been built).

## BOM (100 units, live JLC/LCSC prices read 2026-10-05)

| Refs | Value | Qty | LCSC | MPN | Class | Unit @100 | Line |
|---|---|---|---|---|---|---|---|
| BT1 | CR2032 holder | 1 | C5213768 | 3034TR | extended | $0.3602 | $0.3602 |
| C1 | 10uF | 1 | C15850 | CL21A106KAYNNNE | basic | $0.0773 | $0.0773 |
| C2 | 100nF | 1 | C14663 | CC0603KRX7R9BB104 | basic | $0.0106 | $0.0106 |
| D1,D2 | Green | 2 | C12624 | KT-0603G | extended | $0.0122 | $0.0244 |
| D3 | Blue | 1 | C84266 | NCD0603B1 | extended | $0.0170 | $0.0170 |
| R1 | 1M | 1 | C22935 | 0603WAF1004T5E | basic | $0.0019 | $0.0019 |
| R2 | 1k | 1 | C21190 | 0603WAF1001T5E | basic | $0.0039 | $0.0039 |
| R3,R4,R5 | 100 | 3 | C22775 | 0603WAF1000T5E | basic | $0.0023 | $0.0069 |
| SW1 | TS-1187A | 1 | C318884 | TS-1187A-B-A-B | basic | $0.0197 | $0.0197 |
| U1 | ATtiny412 | 1 | C1337190 | ATTINY412-SSNR | extended | $0.5060 | $0.5060 |
| | **Parts** | | | | | | **$1.03** |
| | Extended-part loading fee ($3 x 4 / 100 boards) | | | | | | $0.12 |
| | **BOM per board @100** | | | | | | **$1.15** |

Not in the BOM: the PCB itself (2 layers, ENIG, 40.4 x 128 mm), assembly labour, and the CR2032 cell.
TP1-TP3 are copper pads, not parts. Machine-readable: [`bom_cost.json`](bom_cost.json).

## Dimensions

40.4 x 128.0 mm (Edge.Cuts bounding box, read by pcbnew), 29.3 cm², 1.6 mm FR4. The stem below the
soil line is 12 mm wide and 42 mm long. Tallest part: the CR2032 holder.

## Mounting plan (no enclosure)

It's a plant stake. Push the stem into the soil up to the silk **soil line**; the head, belly and
electronics stay above it. Nothing else is needed. Optional: a coat of clear nail varnish on the stem's
cut edges keeps the fibreglass edge from wicking water over years.

## Safety

3 V coin cell only; no mains, no LiPo. Every corner of the outline is rounded (1.2 mm radius or more,
leaf tips included); the stem's tip is rounded too. The electrode is under solder mask, so no current
flows into the soil or the plant. The coin cell is held by its holder; keep spare cells away from
children.

**Coin cell, launch blocker.** A swallowed coin cell is a medical emergency. In the US, Reese's Law
(16 CFR part 1263, in force since March 2024) requires a consumer product's button or coin cell to be
secured so that it takes a tool, or two independent simultaneous hand movements, to remove, and it adds
warning-label and packaging requirements. A bare Keystone 3034 holder does not meet that. Before selling
this board assembled with a cell, add a screwed retainer over the cell (or ship it without one) and have
the product and its labels reviewed for compliance. Not done in rev A.

## Verification (measured by KiCad 10.0.6 on the files in this folder)

ERC 0 errors / 0 warnings · netlist round trip identical (12 nets) · routing 26 → 0 open (104 tracks,
22 vias) · DRC 0 errors / 0 warnings / 0 unconnected / 0 parity · DFM `jlcpcb_2layer` 0 errors (1
warning: stock footprint silk at 0.12 mm, printed at the fab's 0.15 mm) · fab gate ready. Full numbers:
[`report.json`](report.json), [`measured.json`](measured.json).

**Not built yet.** It has not been fabricated, assembled or powered; the firmware has been compiled, not
run on hardware. Check the stem's sensitivity in real soil on the first prototypes and adjust
`THIRSTY_PCT` in the firmware if needed.
