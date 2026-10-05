"""Writes boards/merch_plant_buddy/board.json: Sprout, the plant buddy (heypcb.ai merch 01).

    "$KICAD_PYTHON" boards/merch_plant_buddy/make_brief.py

A sprout-shaped capacitive soil-moisture stake on one CR2032: two gold leaves, a round head with
LED eyes and a blue LED tear, the cell in its belly, and a mask-covered electrode down the stem.
Edit this file, not board.json. Frame: 50 x 134 mm, origin top-left, y down; every part locked.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import merch_kit as K  # noqa: E402

SLUG = "plant-buddy"
W, H = 50.0, 134.0
CX = W / 2

BLOCKS = [
    {"block": "merch_cr2032", "as": "bat", "title": "CR2032 in the belly"},
    {"block": "merch_mcu_attiny412", "as": "mcu", "title": "ATtiny412: measure, blink, sleep",
     "nets": {"VDD": "VBAT"},
     "pinNets": {"U?.4": "SENSE", "U?.5": "DRIVE", "U?.7": "EYES", "U?.2": "TEAR", "U?.3": "BOOP"}},
    {"block": "merch_soil_probe", "as": "probe", "title": "Soil probe: 1M charge, 1k sense",
     "nets": {"DRIVE": "DRIVE", "PROBE": "PROBE", "SENSE": "SENSE"}},
    {"block": "gpio_led", "as": "eye_l", "title": "Left eye (green)", "nets": {"SIG": "EYES"},
     "values": {"D?": "Green", "R?": "100"}},
    {"block": "gpio_led", "as": "eye_r", "title": "Right eye (green)", "nets": {"SIG": "EYES"},
     "values": {"D?": "Green", "R?": "100"}},
    {"block": "gpio_led", "as": "tear", "title": "Tear (blue): thirsty", "nets": {"SIG": "TEAR"},
     "values": {"D?": "Blue", "R?": "100"}},
    {"block": "merch_button", "as": "boop", "title": "Boop the bud: check now, or learn wet/dry",
     "nets": {"SIG": "BOOP"}},
]

# ---------------------------------------------------------------------------------------- outline
HEAD_C, HEAD_R = (CX, 31.0), 16.5
LEAF = [((14.5, 10.2), 28.0), ((W - 14.5, 10.2), -28.0)]      # (centre, axis angle), y down
LEAF_RX, LEAF_RY = 10.6, 5.1
BODY = (9.5, 44.0, 40.5, 87.0)
STEM_X0, STEM_X1, STEM_Y0, TIP_Y = 19.0, 31.0, 84.0, 132.0

head = K.Shape.circle(HEAD_C[0], HEAD_C[1], HEAD_R)
leaves = [K.Shape.ellipse(c[0], c[1], LEAF_RX, LEAF_RY, rot) for c, rot in LEAF]
body = K.Shape.rect(*BODY, r=6.0)
stem = K.Shape.poly([(STEM_X0, STEM_Y0), (STEM_X1, STEM_Y0), (STEM_X1, TIP_Y - 7.0), (CX, TIP_Y),
                     (STEM_X0, TIP_Y - 7.0)])
outline = (head | leaves[0] | leaves[1] | body | stem).rounded(1.2)

# ---------------------------------------------------------------------------------------- parts
parts = K.design_footprints(BLOCKS, os.path.join(os.path.dirname(HERE), "..", "blocks"))
L = K.Layout(parts)
EYE_Y = 30.0
L.lock("eye_l:D?", CX - 5.5, EYE_Y, 180, "left eye; anode (pad 2) toward the face's centre line")
L.lock("eye_r:D?", CX + 5.5, EYE_Y, 0, "right eye; anode toward the centre line")
L.lock("tear:D?", CX - 5.5, EYE_Y + 4.3, 180, "a tear under the left eye")
L.lock("boop:SW?", CX, 19.6, 0, "the bud between the leaves: boop it")
L.lock("bat:BT?", CX, 61.0, 0, "the cell in the belly, - face on the gold disc")
L.lock("bat:C?", CX + 9.0, 74.0, 90, "reservoir beside the holder's + tab")
L.lock("mcu:U?", CX, 78.0, 0, "MCU under the belly")
L.lock("mcu:C?", CX - 6.6, 74.4, 90, "bypass at VCC (pin 1)")
L.lock("mcu:TP1?", 12.6, 75.0, 0, "UPDI pads: VCC")
L.lock("mcu:TP2?", 12.6, 77.54, 0, "UPDI pads: UPDI")
L.lock("mcu:TP3?", 12.6, 80.08, 0, "UPDI pads: GND")
L.lock("eye_l:R?", CX + 8.6, 78.6, 90, "eye resistors beside the MCU")
L.lock("eye_r:R?", CX + 10.4, 78.6, 90, "")
L.lock("tear:R?", CX + 12.2, 78.6, 90, "")
L.lock("probe:R1?", CX - 2.0, 84.6, 0, "charge resistor at the top of the electrode")
L.lock("probe:R2?", CX + 2.0, 84.6, 0, "sense resistor at the top of the electrode")

# ---------------------------------------------------------------------------------------- art
art = []
# gold leaves with mask-green veins (no copper under a vein)
for (c, rot), lf in zip(LEAF, leaves):
    a = math.radians(rot)
    ux, uy = math.cos(a), math.sin(a)
    sign = -1 if c[0] < CX else 1                # the outer tip's direction along the axis
    inner = lf.offset(-1.0)
    veins = K.Shape.capsule(c[0] - sign * ux * 8.0, c[1] - sign * uy * 8.0, c[0] + sign * ux * 7.5,
                            c[1] + sign * uy * 7.5, 0.5)
    for t in (-4.5, -1.0, 2.5):
        bx, by = c[0] + sign * ux * t, c[1] + sign * uy * t
        for side in (-1, 1):
            # side veins sweep toward the tip
            vx = sign * ux * 3.2 - side * uy * 3.6
            vy = sign * uy * 3.2 + side * ux * 3.6
            veins = veins | K.Shape.capsule(bx, by, bx + vx, by + vy, 0.4)
    art += K.gold(inner - veins - head.offset(0.6), "leaf")
# gold blush cheeks
for sx in (-1, 1):
    art += K.gold(K.Shape.ellipse(CX + sx * 11.2, EYE_Y + 5.0, 2.6, 1.6), "cheek")
# silk face: eye rings, a smile, a bud mark
for sx in (-1, 1):
    art += K.silk_line(K.arc_points(CX + sx * 5.5, EYE_Y, 2.15, 0, 360, 36), "eye_ring", 0.2, closed=False)
art += K.silk_line(K.arc_points(CX, EYE_Y + 3.0, 3.2, 35, 145, 20), "smile", 0.25)
# soil line and the brand on the stem
wave = [(STEM_X0 + 0.9 + k * 0.25, 90.0 + 0.45 * math.sin(k * 0.25 * 2 * math.pi / 2.4)) for k in range(41)]
art += K.silk_line(wave, "soil_line", 0.2)
art += K.text("soil line", CX, 92.3, size=1.0, name="soil_text")
art += K.text("heypcb.ai", CX, 108.0, size=1.1, angle=90, name="brand_front")
# back: the QR to the board's page, how to use it, and the brand
art += K.qr(K.world_url(SLUG), CX, 58.0, size=12.0, side="B")
for i, line in enumerate(["1. pop in a CR2032 in open air", "2. stake me in freshly watered",
                          "soil, hold my bud 3 s", "boop the bud: am I thirsty?"]):
    art += K.text(line, CX, 25.0 + 1.9 * i, size=1.0, side="B", name="howto%d" % i)
art += K.text("heypcb.ai", CX, 72.5, size=1.4, side="B", bold=True, name="brand_back")
art += K.text("stem below the soil line,", CX, 100.0, size=1.0, side="B", angle=90, name="care0")
art += K.text("head and belly above it", CX + 2.0, 100.0, size=1.0, side="B", angle=90, name="care1")

# ---------------------------------------------------------------------------------------- checks
keep = {"probe": K.Shape.rect(STEM_X0, 88.0, STEM_X1, TIP_Y)}
for i, it in enumerate(a for a in art if "F.Cu" in a.get("layers", [])):
    keep["gold%d" % i] = K.Shape.poly(it["points"]).offset(0.3)
L.check(outline, edge=0.5, keep=keep)

brief = {
    "name": "plant_buddy",
    "title": "Sprout - plant buddy: capacitive soil-moisture stake, CR2032",
    "revision": "A",
    "brief": "A sprout-shaped capacitive soil-moisture stake that lives in a plant pot on one CR2032. An "
             "ATtiny412 wakes every 8 s, times the charge of a mask-covered electrode down the stem through "
             "1M, and blinks a blue LED tear under its green LED eyes when the soil is dry. A button on its "
             "bud checks on demand and learns wet and dry. 2 layers, single-sided SMT, green mask, ENIG.",
    "blocks": BLOCKS,
    "pwrFlags": ["GND", "VBAT"],
    "netClasses": [],
    "board": {
        "width": W, "height": H, "corner_radius": 0.0, "layers": 2, "origin": [100.0, 100.0],
        "shape": {"type": "polygon", "points": K.outline_points(outline), "fillet": 0},
        "rules": {"clearance": 0.2, "track": 0.2, "via": [0.6, 0.3], "edge_clearance": 0.5,
                  "hole_to_hole": 0.5, "min_through_hole": 0.3, "min_track": 0.15},
        "finish": {"mask": "Green", "silk": "White", "copper": "ENIG",
                   "why": "a plant is green; ENIG for the gold leaves and the coin cell's contact disc"},
        "unpoured": ["F.Cu"],
        "keepouts": [{"name": "stem", "rect": [STEM_X0, 88.0, STEM_X1, TIP_Y], "layers": "all",
                      "no": ["tracks", "vias"]}],
        "zones": [{"name": "electrode", "net": "PROBE", "layers": ["F.Cu"], "priority": 1,
                   "polygon": [[CX - 4.6, 83.4], [CX + 4.6, 83.4], [CX + 4.6, 123.0], [CX, 127.5],
                               [CX - 4.6, 123.0]]}],
        "notes": "2 layers. The stem carries only the PROBE electrode (F.Cu zone) over the GND pour (B.Cu); "
                 "tracks and vias are banned there so the measured capacitance is the soil's.",
    },
    "placement": L.locks,
    "route": {"passes": 30, "fanout": True, "solve_s": 240},
    "stitch_pitch": 6.0,
    "silk": {"designators": "hide",
             "title": [{"text": "Sprout", "y": 40.0, "size": 2.0, "bold": True},
                       {"text": "plant buddy  rev {revision}", "y": 43.0, "size": 1.0}]},
    "art": art,
    "captions": {"done_3d": "Sprout: gold leaves, LED eyes and tear, a CR2032 belly, a capacitive stem."},
}
K.write_brief(os.path.join(HERE, "board.json"), brief)
print("wrote board.json: %d outline points, %d art items, %d locks, QR -> %s"
      % (len(brief["board"]["shape"]["points"]), len(art), len(L.locks), K.world_url(SLUG)))
