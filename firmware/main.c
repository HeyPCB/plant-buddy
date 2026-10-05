/*
 * Sprout, the plant buddy - firmware for the ATtiny412 (heypcb.ai merch 01).
 *
 * What it does
 *   - Sleeps in power-down; the RTC's periodic interrupt (1 kHz internal oscillator) wakes it every 8 s.
 *   - Every 8th wake (about once a minute) it measures the soil: the stem's mask-covered electrode is
 *     charged through 1M and the MCU counts how long the electrode takes to reach the input's high
 *     threshold. Wetter soil = more capacitance = a longer count. The count is a ratio (RC / threshold),
 *     so it does not move as the coin cell runs down.
 *   - Thirsty: every other wake (16 s) the blue tear "drips" (a soft 120 ms fade). Happy: a double wink
 *     about once a minute.
 *   - Boop the bud (the button): it measures at once and answers (wink = fine, tear + droopy eyes = water me).
 *     Hold it 3 s in freshly watered soil and it learns "wet" (three eye flashes).
 *   - "Air" (the driest possible reading) is learned by itself: it is the lowest count ever seen, kept in
 *     EEPROM. Insert the cell with the stake in open air and that first reading is the baseline.
 *
 * Pins (from the board's netlist; KiCad symbol MCU_Microchip_ATtiny:ATtiny412-SS)
 *   PA1 (pin 4)  SENSE  input, the electrode through 1k
 *   PA2 (pin 5)  DRIVE  output, charges the electrode through 1M
 *   PA3 (pin 7)  EYES   output, both green eye LEDs (high = on, 100 ohm each)
 *   PA6 (pin 2)  TEAR   output, the blue tear LED (high = on, 100 ohm)
 *   PA7 (pin 3)  BOOP   input with pull-up, the button to GND
 *   PA0 (pin 6)  UPDI   programming only
 *
 * Power budget (see SPEC.md for the arithmetic): about 10 uA on average while the plant is happy (about
 * two years on a CR2032), about 17 uA while it cries (well over a year).
 *
 * Build: make      (avr-gcc with ATtiny412 support; see README.md)
 */
#include <avr/eeprom.h>
#include <avr/interrupt.h>
#include <avr/io.h>
#include <avr/sleep.h>
#include <stdint.h>
#include <util/delay.h>

#define SENSE PIN1_bm
#define DRIVE PIN2_bm
#define EYES PIN3_bm
#define TEAR PIN6_bm
#define BOOP PIN7_bm

#define SAMPLES 16            /* charge-time samples averaged per reading */
#define TIMEOUT 60000u        /* counts at 3.33 MHz: 18 ms, far beyond any soil */
#define THIRSTY_PCT 35u       /* thirsty below air + 35 % of the air-to-wet span */
#define HYST_PCT 6u           /* happy again only 6 % of the span above that */
#define HOLD_TO_LEARN_MS 3000u

/* EEPROM: the learned references (0xFFFF = never learned) */
#define EE_AIR ((uint16_t *)0)
#define EE_WET ((uint16_t *)2)

static volatile uint8_t boop_flag;
static uint16_t air, wet;
static uint8_t thirsty;

ISR(RTC_PIT_vect) { RTC.PITINTFLAGS = RTC_PI_bm; }

ISR(PORTA_PORT_vect)
{
    PORTA.INTFLAGS = BOOP;          /* PA7 is not fully asynchronous: BOTHEDGES is what wakes power-down */
    boop_flag = 1;
}

/* One charge time, in CPU clocks (3.33 MHz): discharge the electrode, then time it through 1M. */
static uint16_t charge_counts(void)
{
    PORTA.OUTCLR = DRIVE | SENSE;
    PORTA.DIRSET = DRIVE | SENSE;   /* both low: empty the electrode through the 1k */
    _delay_us(300);
    PORTA.DIRCLR = SENSE;           /* sense becomes a high-impedance input */
    cli();
    TCA0.SINGLE.CNT = 0;
    PORTA.OUTSET = DRIVE;           /* start charging */
    while (!(PORTA.IN & SENSE) && TCA0.SINGLE.CNT < TIMEOUT)
        ;
    uint16_t n = TCA0.SINGLE.CNT;
    sei();
    PORTA.OUTCLR = DRIVE;           /* leave it at 0 V: no floating input while asleep */
    return n;
}

static uint16_t measure(void)
{
    uint32_t sum = 0;
    TCA0.SINGLE.CTRLA = TCA_SINGLE_CLKSEL_DIV1_gc | TCA_SINGLE_ENABLE_bm;
    for (uint8_t i = 0; i < SAMPLES; i++)
        sum += charge_counts();
    TCA0.SINGLE.CTRLA = 0;          /* timer off again */
    return (uint16_t)(sum / SAMPLES);
}

static uint16_t span(void) { return (wet > air) ? (uint16_t)(wet - air) : 1u; }

/* Update the thirsty flag from one reading, with hysteresis; track the driest reading as "air". */
static void judge(uint16_t r)
{
    if (r < air) {
        air = r;
        eeprom_update_word(EE_AIR, air);    /* only ever goes down: a handful of writes in its life */
    }
    uint16_t low = air + (uint16_t)(((uint32_t)span() * THIRSTY_PCT) / 100u);
    uint16_t high = low + (uint16_t)(((uint32_t)span() * HYST_PCT) / 100u);
    if (r < low)
        thirsty = 1;
    else if (r > high)
        thirsty = 0;
}

/* ---- little LED animations (software PWM at about 1 kHz, a few mA for a few ms) ---- */
static void glow(uint8_t pin, uint8_t from, uint8_t to, uint8_t steps_ms)
{
    for (uint8_t t = 0; t < steps_ms; t++) {
        uint8_t level = from + (int16_t)(to - from) * t / steps_ms;     /* 0..32 */
        for (uint8_t k = 0; k < 32; k++) {
            if (k < level)
                PORTA.OUTSET = pin;
            else
                PORTA.OUTCLR = pin;
            _delay_us(30);
        }
    }
    PORTA.OUTCLR = pin;
}

static void tear_drip(void) { glow(TEAR, 0, 32, 40); glow(TEAR, 32, 0, 80); }

static void wink(void)
{
    PORTA.OUTSET = EYES; _delay_ms(30); PORTA.OUTCLR = EYES; _delay_ms(140);
    PORTA.OUTSET = EYES; _delay_ms(30); PORTA.OUTCLR = EYES;
}

static void droop(void) { glow(EYES, 20, 0, 250); }

static void learned(void)
{
    for (uint8_t i = 0; i < 3; i++) {
        PORTA.OUTSET = EYES; _delay_ms(70); PORTA.OUTCLR = EYES; _delay_ms(110);
    }
}

static void answer(void)
{
    if (thirsty) {
        PORTA.OUTSET = TEAR;
        droop();
        PORTA.OUTCLR = TEAR;
    } else {
        wink();
    }
}

static void on_boop(void)
{
    _delay_ms(25);                          /* debounce */
    if (PORTA.IN & BOOP)
        return;                             /* a release edge, or a bounce */
    uint16_t r = measure();
    judge(r);
    answer();
    uint16_t held = 0;
    while (!(PORTA.IN & BOOP) && held < HOLD_TO_LEARN_MS) {
        _delay_ms(10);
        held += 10;
    }
    if (held >= HOLD_TO_LEARN_MS) {
        wet = measure();                    /* freshly watered soil: the "wet" reference */
        if (wet <= air + 4)
            wet = air + 4;                  /* never a zero span */
        eeprom_update_word(EE_WET, wet);
        thirsty = 0;
        learned();
        while (!(PORTA.IN & BOOP))
            ;                               /* wait for the release */
    }
}

static void sleep_now(void)
{
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);
    sleep_enable();
    sleep_cpu();
    sleep_disable();
}

int main(void)
{
    /* outputs low, the button's pull-up and wake-up edge */
    PORTA.DIRSET = DRIVE | EYES | TEAR;
    PORTA.OUTCLR = DRIVE | EYES | TEAR;
    PORTA.PIN7CTRL = PORT_PULLUPEN_bm | PORT_ISC_BOTHEDGES_gc;

    /* RTC periodic interrupt: 1.024 kHz internal ULP, 8192 cycles = 8 s */
    while (RTC.STATUS > 0)
        ;
    RTC.CLKSEL = RTC_CLKSEL_INT1K_gc;
    while (RTC.PITSTATUS > 0)
        ;
    RTC.PITINTCTRL = RTC_PI_bm;
    RTC.PITCTRLA = RTC_PERIOD_CYC8192_gc | RTC_PITEN_bm;
    sei();

    /* references: air is the first reading after a fresh flash, wet a guess until it is taught */
    uint16_t first = measure();
    air = eeprom_read_word(EE_AIR);
    wet = eeprom_read_word(EE_WET);
    if (air == 0xFFFF || first < air) {
        air = first;
        eeprom_update_word(EE_AIR, air);
    }
    if (wet == 0xFFFF || wet <= air)
        wet = air * 3u;                     /* untaught: soil at three times the air capacitance */
    judge(first);
    wink();                                 /* hello */

    uint8_t tick = 0;
    for (;;) {
        sleep_now();
        if (boop_flag) {
            boop_flag = 0;
            on_boop();
            continue;
        }
        if ((++tick & 7u) == 0)             /* about once a minute */
            judge(measure());
        if (thirsty) {
            if (tick & 1u)                  /* a tear every 16 s: about 15 uA, see SPEC.md */
                tear_drip();
        } else if ((tick & 7u) == 4u) {
            wink();                         /* happy: a double wink about once a minute */
        }
    }
}
