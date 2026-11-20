#!/usr/bin/env python3
"""Draw the renewal front page for 19 November 2026, 1024x1024.

Deterministic: fixed geometry, fixed palette, no clock, no randomness.
Writes entry.png next to this script.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (245, 241, 230)
INK = (26, 26, 26)
RED = (164, 30, 34)
GREY = (90, 86, 76)
RULE = (60, 58, 50)
SKY = (198, 220, 232)
SEA = (38, 84, 122)
NIGHT = (18, 24, 54)
NEON_PINK = (255, 64, 170)
NEON_CYAN = (64, 224, 255)

FD = "/usr/share/fonts/truetype/dejavu"
FN = "/usr/share/fonts/truetype/noto"


def font(name, size):
    for p in (os.path.join(FD, name), os.path.join(FN, name)):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
ITALIC = lambda s: font("NotoSerif-Italic.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


class ScaleDraw:
    """Coordinate-scaling wrapper around ImageDraw, for supersampling.

    Scales every positional coordinate (flat [x0,y0,x1,y1] boxes and
    [(x,y),...] point lists alike: even indices by kx, odd by ky),
    line `width` by the mean scale, and recreates truetype fonts at
    kx so a tile drawn in a small coordinate space renders at 4x and
    downscales with LANCZOS. Colours, angles and other kwargs pass
    through untouched; textlength stays consistent (font is scaled).
    """
    def __init__(self, draw, kx, ky=None):
        self._d = draw
        self._kx = kx
        self._ky = ky if ky is not None else kx

    def _pair(self, v):
        if isinstance(v, (list, tuple)):
            if v and all(isinstance(x, (int, float)) and not isinstance(x, bool)
                         for x in v):
                # PIL's C draw calls need ints; at 4x, rounding costs <0.25px.
                return type(v)(int(round(x * (self._kx if i % 2 == 0 else self._ky)))
                               for i, x in enumerate(v))
            return type(v)(self._pair(x) for x in v)
        return v

    def __getattr__(self, name):
        fn = getattr(self._d, name)

        def wrap(*a, **kw):
            a = tuple(self._pair(x) for x in a)
            if 'width' in kw and isinstance(kw['width'], (int, float)):
                kw['width'] = max(1, int(round(
                    kw['width'] * (self._kx + self._ky) / 2)))
            if 'font' in kw:
                f = kw['font']
                path = getattr(f, 'path', None)
                size = getattr(f, 'size', None)
                if path and size:
                    kw['font'] = ImageFont.truetype(
                        path, max(1, int(round(size * self._kx))))
            return fn(*a, **kw)

        return wrap


def wrap(draw, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, width, fill=INK, leading=None):
    lines = wrap(draw, text, fnt, width)
    lh = leading or int(fnt.size * 1.22)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def hline(draw, x0, x1, y, w=2, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=w)


# ---------------- visuals ----------------

def draw_summit(d, x, y, w, h):
    """Three leaders at a long table, Shenzhen skyline behind."""
    d.rectangle([x, y, x + w, y + h], fill=SKY, outline=RULE, width=2)
    # skyline
    for bx, bw, bh in [(0, 46, 70), (52, 34, 96), (92, 40, 60), (138, 30, 110),
                       (174, 44, 78), (224, 36, 120), (266, 42, 66), (314, 38, 92),
                       (358, 44, 58), (408, 36, 104), (450, 40, 70), (496, 44, 88),
                       (546, 30, 60)]:
        d.rectangle([x + bx, y + h - 78 - bh, x + bx + bw, y + h - 78],
                    fill=(74, 88, 104))
        for wy in range(y + h - 78 - bh + 8, y + h - 86, 12):
            for wx in range(x + bx + 6, x + bx + bw - 6, 12):
                d.rectangle([wx, wy, wx + 4, wy + 5], fill=(250, 220, 120))
    # sun
    d.ellipse([x + w - 78, y + 16, x + w - 26, y + 68], fill=(250, 214, 110))
    # flags behind the table
    for i, col in enumerate([(178, 34, 52), (222, 41, 16), (0, 57, 166)]):
        fx = x + 118 + i * 170
        d.line([(fx, y + 62), (fx, y + 118)], fill=(60, 58, 50), width=3)
        d.rectangle([fx, y + 62, fx + 52, y + 88], fill=col, outline=RULE)
        d.text((fx + 4, y + 66), "*", font=SANS_B(16), fill=(255, 255, 255))
    # table
    d.rectangle([x + 20, y + h - 78, x + w - 20, y + h - 44], fill=(122, 72, 40))
    d.rectangle([x + 20, y + h - 78, x + w - 20, y + h - 70], fill=(150, 96, 56))
    # three seated figures
    for i, suit in enumerate([(30, 42, 66), (64, 64, 64), (120, 30, 30)]):
        cx = x + 118 + i * 170
        d.ellipse([cx - 16, y + h - 128, cx + 16, y + h - 96], fill=(232, 196, 160))
        d.rectangle([cx - 30, y + h - 98, cx + 30, y + h - 78], fill=suit)
        d.polygon([(cx - 6, y + h - 98), (cx + 6, y + h - 98), (cx, y + h - 76)],
                  fill=(255, 255, 255))
    # microphones / papers
    for i in range(3):
        cx = x + 118 + i * 170
        d.line([(cx + 26, y + h - 78), (cx + 40, y + h - 92)], fill=INK, width=2)
        d.ellipse([cx + 36, y + h - 98, cx + 46, y + h - 88], fill=INK)
        d.rectangle([cx - 44, y + h - 74, cx - 8, y + h - 66], fill=(255, 255, 255))


def draw_vice_city(d, x, y, w, h):
    """Neon Vice City skyline at dusk."""
    d.rectangle([x, y, x + w, y + h], fill=NIGHT, outline=RULE, width=2)
    d.ellipse([x + w - 70, y + 12, x + w - 18, y + 64], fill=(255, 214, 130))
    import math
    for bx, bw, bh, col in [(0, 40, 74, (52, 66, 120)), (44, 30, 100, (40, 52, 96)),
                            (78, 46, 62, (64, 80, 140)), (128, 34, 112, (46, 58, 110)),
                            (166, 40, 80, (58, 72, 128)), (210, 30, 96, (42, 54, 100)),
                            (244, 44, 66, (62, 76, 134)), (292, 36, 104, (48, 60, 112)),
                            (332, 40, 72, (56, 70, 126))]:
        d.rectangle([x + bx, y + h - 26 - bh, x + bx + bw, y + h - 26],
                    fill=col)
        for wy in range(y + h - 26 - bh + 7, y + h - 32, 11):
            for wx in range(x + bx + 5, x + bx + bw - 5, 11):
                d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 220, 120))
    # neon strip + palm silhouettes
    d.rectangle([x, y + h - 26, x + w, y + h - 22], fill=NEON_PINK)
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(10, 14, 34))
    for px in (30, 340):
        d.line([(x + px, y + h), (x + px, y + h - 34)], fill=(8, 60, 30), width=4)
        for a in range(5):
            ang = math.pi * (0.15 + a * 0.175)
            d.line([(x + px, y + h - 34),
                    (x + px + int(22 * math.cos(ang)), y + h - 34 - int(14 * math.sin(ang)))],
                   fill=(8, 60, 30), width=3)
    d.text((x + 12, y + h - 20), "VICE CITY", font=SANS_B(13), fill=NEON_CYAN)


def draw_gulf(d, x, y, w, h):
    """Missile streak over a dark gulf, carrier silhouette."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 34, 52), outline=RULE, width=2)
    d.rectangle([x, y + h - 34, x + w, y + h], fill=SEA)
    d.polygon([(x + 8, y + h - 34), (x + 70, y + h - 34), (x + 62, y + h - 20),
               (x + 16, y + h - 20)], fill=(40, 44, 52))
    d.rectangle([x + 30, y + h - 52, x + 36, y + h - 34], fill=(40, 44, 52))
    d.rectangle([x + 52, y + h - 48, x + 58, y + h - 34], fill=(40, 44, 52))
    # missile + trail
    d.line([(x + 150, y + 22), (x + 60, y + 78)], fill=(255, 180, 60), width=3)
    d.polygon([(x + 150, y + 22), (x + 138, y + 26), (x + 142, y + 34)], fill=(255, 220, 120))
    d.ellipse([x + 52, y + 70, x + 66, y + 84], fill=(255, 140, 40))
    d.ellipse([x + 44, y + 62, x + 74, y + 92], fill=(255, 90, 20))
    # stars
    for sx, sy in [(20, 14), (90, 30), (200, 12), (120, 44), (180, 52)]:
        d.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3], fill=(255, 255, 255))


def draw_capitol(d, x, y, w, h):
    """US Capitol dome, simple silhouette."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 226, 238), outline=RULE, width=2)
    d.rectangle([x, y + h - 28, x + w, y + h], fill=(120, 128, 110))
    cx = x + w // 2
    d.rectangle([cx - 52, y + h - 46, cx + 52, y + h - 28], fill=(240, 240, 232))
    d.ellipse([cx - 34, y + 22, cx + 34, y + 66], fill=(240, 240, 232))
    d.rectangle([cx - 34, y + 56, cx + 34, y + h - 46], fill=(240, 240, 232))
    d.line([(cx, y + 12), (cx, y + 22)], fill=INK, width=3)
    d.ellipse([cx - 3, y + 8, cx + 3, y + 14], fill=INK)
    for wy in (y + h - 40,):
        for wx in (cx - 44, cx - 24, cx - 4, cx + 16, cx + 36):
            d.rectangle([wx, wy, wx + 6, wy + 8], fill=(90, 96, 110))
    d.rectangle([x + 12, y + h - 40, cx - 60, y + h - 28], fill=(226, 228, 220))
    d.rectangle([cx + 60, y + h - 40, x + w - 12, y + h - 28], fill=(226, 228, 220))


def draw_cyclone(d, x, y, w, h):
    """Cyclone spiral over the Bay of Bengal."""
    d.rectangle([x, y, x + w, y + h], fill=(190, 210, 224), outline=RULE, width=2)
    d.rectangle([x, y + h - 40, x + w, y + h], fill=(112, 140, 96))
    d.polygon([(x + 8, y + h - 40), (x + 60, y + h - 40), (x + 46, y + h - 22),
               (x + 22, y + h - 22)], fill=(96, 122, 84))
    cx, cy = x + w // 2 + 22, y + h // 2 - 6
    import math
    for ring, col in [(46, (255, 255, 255)), (36, (232, 240, 248)),
                      (26, (255, 255, 255)), (16, (220, 232, 242))]:
        d.arc([cx - ring, cy - ring, cx + ring, cy + ring],
              start=20, end=320, fill=col, width=7)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(70, 90, 110))
    d.line([(x + 12, y + 16), (x + 60, y + 30)], fill=(255, 255, 255), width=3)
    d.line([(x + 12, y + 30), (x + 58, y + 42)], fill=(255, 255, 255), width=3)


def draw_voyager(d, x, y, w, h):
    """Voyager probe among the stars, one light-day out."""
    d.rectangle([x, y, x + w, y + h], fill=(8, 10, 28), outline=RULE, width=2)
    for sx, sy, r in [(16, 14, 2), (52, 40, 1), (96, 12, 2), (150, 30, 1),
                      (196, 16, 2), (30, 66, 1), (120, 58, 1), (180, 62, 2),
                      (70, 76, 1), (210, 44, 1)]:
        d.ellipse([x + sx, y + sy, x + sx + r, y + sy + r], fill=(255, 255, 255))
    cx, cy = x + w // 2, y + h // 2 + 6
    d.polygon([(cx - 26, cy - 6), (cx + 26, cy - 6), (cx + 18, cy + 8),
               (cx - 18, cy + 8)], fill=(200, 200, 210))
    d.polygon([(cx - 40, cy - 14), (cx - 26, cy - 6), (cx - 26, cy + 8),
               (cx - 40, cy + 2)], fill=(150, 150, 165))
    d.line([(cx + 26, cy), (cx + 44, cy - 12)], fill=(220, 220, 230), width=2)
    d.ellipse([cx + 42, cy - 16, cx + 50, cy - 8], fill=(240, 240, 250))
    d.line([(cx, cy + 8), (cx, cy + 26)], fill=(220, 220, 230), width=2)
    d.ellipse([cx - 3, cy + 24, cx + 3, cy + 30], fill=(240, 240, 250))
    d.text((x + 10, y + h - 20), "1 LIGHT-DAY", font=SANS_B(12), fill=(255, 220, 120))


# Renewal: retain v1's palette, font/wrapping helpers and flat illustration idiom.
from pathlib import Path


def label(d, x, y, text, size=12, fill=RED):
    d.text((x, y), text, font=SANS_B(size), fill=fill)


def fitted(d, x, y, text, font_fn, size, width, fill=INK):
    while d.textlength(text, font=font_fn(size)) > width:
        size -= 1
    d.text((x, y), text, font=font_fn(size), fill=fill)


def art(img, fn, x, y, w, h):
    # Hermes workflow: supersampling 4x + LANCZOS. The art functions draw
    # in a 576x218 coordinate space; render that space at 1264x340
    # (4x the 316x85 display) via ScaleDraw, then downscale.
    tile = Image.new('RGB', (1264, 340), PAPER)
    fn(ScaleDraw(ImageDraw.Draw(tile), 1264 / 576, 340 / 218), 0, 0, 576, 218)
    img.paste(tile.resize((w, h), Image.Resampling.LANCZOS), (x, y))


def map_tile(w, h):
    # World map, supersampled 4x + LANCZOS: world() draws in a 266x204
    # space; render at 1064x816, then downscale to the display size.
    tile = Image.new('RGB', (1064, 816), (224, 233, 230))
    world(ScaleDraw(ImageDraw.Draw(tile), 4, 4), 0, 0)
    return tile.resize((w, h), Image.Resampling.LANCZOS)


def court(d, x, y, w, h):
    d.rectangle((x,y,x+w,y+h), fill=(204,220,218))
    d.ellipse((x+420,y+14,x+490,y+84),fill=(238,213,146))
    d.polygon([(x+80,y+65),(x+288,y+10),(x+496,y+65)],fill=SEA)
    d.rectangle((x+80,y+69,x+496,y+81),fill=INK)
    for xx in range(x+102,x+480,69):
        d.rectangle((xx,y+85,xx+28,y+179), fill=(248,244,225))
        d.rectangle((xx-7,y+84,xx+35,y+93),fill=INK)
    d.rectangle((x+65,y+180,x+510,y+195),fill=SEA)
    d.line((x+288,y+87,x+288,y+164),fill=RED,width=7)
    d.line((x+230,y+108,x+346,y+108),fill=RED,width=5)
    for xx in (x+237,x+339):
        d.line((xx,y+108,xx-20,y+140),fill=RED,width=3)
        d.line((xx,y+108,xx+20,y+140),fill=RED,width=3)
        d.arc((xx-23,y+127,xx+23,y+153),0,180,fill=RED,width=5)


SECONDARY = [
 ('GULF WAR WIDENS','Iran fires on Kuwait after US Qeshm strike.','missile','REPORTED'),
 ('CRIMEAN BRIDGE HIT','Ukraine strikes: third time this week.','bridge','REPORTED'),
 ('GAZA GROUND PUSH','Israel moves beyond central Gaza Yellow Line.','tank','REPORTED'),
 ('ANTHROPIC’S RECORD IPO','Nasdaq ANT debuts at $83 a share.','chart','REPORTED'),
 ('JEFFRIES NOMINATED','251–11; House floor vote set for Jan 3.','dome','REPORTED'),
 ('AKVAN NEARS INDIA','Andhra: 7 districts on red alert; Friday landfall.','storm','FORECAST'),
 ('VOYAGER: A LIGHT-DAY','NASA probe reaches milestone after 48 years.','probe','REPORTED'),
 ('FED MINUTES HAWKISH','October hold a close call; S&P loses again.','chart','REPORTED'),
 ('EU’S €45BN LOAN PLAN','Ukraine proposal as allies meet in Berlin.','flag','REPORTED'),
 ('NVIDIA HALTS H200 SALES','China cutoff as US chip rule takes effect.','chip','REPORTED'),
 ('SOMALIA EXPELS ENVOY','UAE ambassador given 72 hours to leave.','flag','REPORTED'),
 ('INDONESIA ASSET LAW','Forfeiture law passes; Cepu blast kills worker.','refinery','REPORTED'),
]
# One numbered line is one additional story; locations match the map pins.
# Pins loosened (Hermes blind review): no two pins closer than ~20px,
# so the cluster around Europe / the East Med reads at small sizes.
BRIEFS = [
 ('Denmark: Greenland defence pact, 109–0.',(150,40)),
 ('Bulgaria: Gas Husky sinks after projectile hit.',(128,86)),
 ('Bangladesh: unrest over Hasina’s return.',(188,111)),
 ('IAEA: Yongbyon uranium enrichment expands.',(212,87)),
 ('US asks top court to block Venezuelan TPS.',(54,87)),
 ('UK opens latest renewables auction.',(112,72)),
 ('UniCredit agrees €41bn Commerzbank terms.',(140,62)),
 ('Five EU nations plan Rwanda asylum transfers.',(128,44)),
 ('Ethiopia, Eritrea mass troops on border.',(160,125)),
 ('Sudan: aid for displaced amid drone toll.',(138,116)),
 ('Riyadh missile threat: coalition CLAIM.',(176,94)),
 ('Fiji, Tonga: El Niño drought emergencies.',(247,147)),
 ('589m children in conflict zones: 2025 report.',(25,155)),
 ('US loses measles elimination status.',(39,66)),
 ('DR Congo to trial strain-specific Ebola shots.',(133,140)),
 ('Waymo pulls US taxis from freeways.',(21,103)),
 ('Australia unemployment rises to 4.9%.',(222,158)),
 ('IMF deal to unlock $2.3bn for Egypt.',(160,102)),
 ('EU governments approve Indonesia trade deal.',(199,135)),
 ('Seoul, Beijing expand cultural exchange.',(227,72)),
 ('Atmospheric river brings California record rain.',(15,81)),
 ('Turkey court sentences Imamoglu + 8 others.',(168,72)),
 ('S. Korea exam held under AI cheating curbs.',(229,103)),
 ('Webb confirms rare two-star merger.',(25,179)),
 ('Antarctic blue whales up tenfold since whaling.',(160,188)),
 ('Cambridge names “human” word of the year.',(100,50)),
]


def icon(d,x,y,kind):
    bg=(226,230,220)
    d.rectangle((x,y,x+34,y+30),fill=bg)
    if kind=='missile':
        d.line((x+3,y+26,x+27,y+6),fill=RED,width=3)
        d.polygon([(x+32,y+2),(x+19,y+7),(x+27,y+15)],fill=INK)
    elif kind=='bridge':
        d.line((x+1,y+20,x+33,y+20),fill=SEA,width=4)
        for a in (8,26): d.line((x+a,y+3,x+a,y+29),fill=INK,width=2)
        d.line([(x,y+16),(x+8,y+6),(x+17,y+16),(x+26,y+6),(x+34,y+16)],fill=INK,width=2)
    elif kind=='storm':
        for r in (13,8): d.arc((x+17-r,y+15-r,x+17+r,y+15+r),20,320,fill=SEA,width=3)
    elif kind=='chart':
        d.line((x+3,y+3,x+3,y+27,x+32,y+27),fill=INK,width=2)
        d.line([(x+5,y+22),(x+13,y+15),(x+20,y+18),(x+31,y+5)],fill=RED,width=3)
    elif kind=='chip':
        d.rectangle((x+8,y+5,x+26,y+25),fill=SEA)
        for a in range(6,29,6): d.line((x+3,y+a,x+31,y+a),fill=INK,width=1)
    elif kind=='probe':
        d.ellipse((x+7,y+4,x+27,y+17),fill=SEA)
        d.line((x+17,y+10,x+17,y+28),fill=INK,width=2)
        d.line((x+6,y+26,x+29,y+15),fill=INK,width=2)
    elif kind=='flag':
        d.line((x+7,y+2,x+7,y+28),fill=INK,width=2)
        d.polygon([(x+8,y+3),(x+30,y+5),(x+26,y+17),(x+8,y+14)],fill=SEA)
    elif kind=='dome':
        d.pieslice((x+7,y+2,x+27,y+24),180,360,fill=SEA)
        d.rectangle((x+4,y+15,x+30,y+27),fill=SEA)
        for a in (9,16,23): d.line((x+a,y+17,x+a,y+26),fill=PAPER,width=2)
    elif kind=='tank':
        d.rounded_rectangle((x+2,y+16,x+32,y+27),radius=5,fill=INK)
        d.rectangle((x+11,y+10,x+24,y+19),fill=SEA)
        d.line((x+21,y+12,x+34,y+8),fill=INK,width=3)
    else:
        for a in (5,15,25): d.rectangle((x+a,y+7,x+a+5,y+28),fill=SEA)
        d.line((x+2,y+28,x+33,y+28),fill=INK,width=2)


def world(d,x,y):
    d.rectangle((x,y,x+266,y+204),fill=(224,233,230))
    shapes=[[(8,55),(35,39),(66,42),(85,66),(69,90),(50,94),(49,114),(31,94),(19,90)],[(60,110),(83,120),(89,142),(74,176),(64,154)],[(102,29),(128,25),(131,44),(114,51)],[(113,59),(150,55),(166,65),(203,50),(240,66),(248,87),(228,109),(201,100),(194,126),(173,117),(158,90),(138,87),(122,80)],[(119,91),(144,90),(164,118),(150,155),(130,159),(116,125)],[(206,142),(229,136),(248,153),(238,173),(213,169)],[(65,191),(103,184),(156,188),(207,183),(249,195)]]
    for pts in shapes: d.polygon([(x+a,y+b) for a,b in pts],fill=(183,198,182),outline=(127,148,135))
    for n,(_, (a,b)) in enumerate(BRIEFS,1):
        cx,cy=x+a,y+b
        d.ellipse((cx-8,cy-8,cx+8,cy+8),fill=RED,outline=PAPER)
        st=str(n); f=SANS_B(8)
        d.text((cx-d.textlength(st,font=f)/2,cy-5),st,font=f,fill='white')


def main():
    img=Image.new('RGB',(W,H),PAPER); d=ImageDraw.Draw(img)
    d.rectangle((9,9,1014,1014),outline=RULE,width=2)
    # Masthead, 3 levels (Hermes workflow / top-1 pattern: the DATE is the
    # headline — largest element on the page, bigger than the paper name).
    fitted(d,24,12,'THE WORLD IN ONE DAY',SERIF_B,34,976)
    fitted(d,24,48,'19 NOVEMBER 2026',SERIF_B,64,976,RED)
    day='THURSDAY · 41 STORIES · 6 REGIONS · ONE PAGE'; f=SANS_B(16)
    d.text(((W-d.textlength(day,font=f))/2,114),day,font=f,fill=RED)
    hline(d,24,1000,134,3)
    stats=[('19.05m','GTA VI copies¹'),('$83','Anthropic IPO'),('589m','children in conflict²'),('251–11','Jeffries vote'),('109–0','Denmark vote'),('−561','Dow points · Wed'),('$3,726','gold'),('120–130','km/h · Akvan³')]
    for i,(v,cap) in enumerate(stats):
        x=24+i*122
        fitted(d,x,140,v,SANS_B,24,110,RED)
        fitted(d,x,166,cap,SANS,11,110)
    label(d,24,180,'¹ Sensor Tower est.    ² In 2025, reported today    ³ Forecast winds',10,GREY)
    hline(d,24,1000,194,1)
    label(d,24,200,'THE DAY / UTC',11)
    times=[
      '00:00 GTA VI: rolling local-midnight unlocks  •  01:46 Trump on Fox: raised Huang “briefly” with Xi',
      '04:30 Cepu blast reported  •  04:50 Indonesia law passes  •  05:12 Japan auto standards  •  Morning: Shenzhen summit',
      'Midday: ICJ ruling  •  13:06 Sensor Tower update  •  14:18 UK auction  •  16:28 Take-Two / Reuters  •  Evening: ANT debut']
    for i,t in enumerate(times): fitted(d,137,198+i*15,t,SANS,12,861)
    hline(d,24,1000,244,2)
    heroes=[(draw_summit,'REPORTED · SHENZHEN',['TRUMP, XI & PUTIN','FIRST SUMMIT'],['First three-way summit: arms, Ukraine, Iran.','Joint text on nuclear risks and UN reform.']),
      (draw_vice_city,'CLAIM · SALES ESTIMATE',['VICE CITY','OPENS'],['GTA VI goes on sale after a 13-year wait.','Sensor Tower est.: 19.05m copies / $1.84bn.']),
      (court,'REPORTED · ICJ RULING',['MYANMAR','COMMITTED','GENOCIDE'],['ICJ rules Myanmar’s military committed','genocide against the Rohingya.'])]
    for i,(fn,tag,heads,summary) in enumerate(heroes):
        x=24+i*330
        label(d,x,250,tag,11)
        art(img,fn,x,268,316,74)
        for j,line in enumerate(heads):
            fitted(d,x,(346+j*24) if len(heads)==3 else (352+j*32),line,SERIF_B,27 if len(heads)==3 else 29,316)
        for j,line in enumerate(summary): fitted(d,x,424+j*17,line,SANS,13,316)
        if i<2: d.line((x+323,250,x+323,458),fill=RULE)
    hline(d,24,1000,460,2)
    for i,(head,summary,kind,tag) in enumerate(SECONDARY):
        col=i%3; row=i//3; x=24+col*330; y=470+row*48
        icon(d,x,y+2,kind)
        label(d,x+42,y,head,12)
        fitted(d,x+42,y+17,summary,SANS,11,274)
        label(d,x+42,y+32,tag,8,GREY)
        if row<3: hline(d,x,x+316,y+45,1, (204,199,185))
    hline(d,24,1000,668,2)
    label(d,24,674,'26 MORE / A WORLD IN BRIEF',13)
    label(d,310,676,'REPORTED · MAP NUMBERS KEY TO THE BRIEFS',10,GREY)
    img.paste(map_tile(266,184),(24,696))
    for i,(text,_) in enumerate(BRIEFS):
        col=i//13; row=i%13; x=310+col*348; y=696+row*16
        label(d,x,y,f'{i+1:02}',10)
        fitted(d,x+23,y,text,SANS,12,300)
    hline(d,24,1000,904,2)
    label(d,24,910,'VERDICT',11)
    verdict='A day of firsts: the first Trump–Xi–Putin summit, the ICJ genocide ruling, and the biggest game launch ever (est.) — all on one Thursday.'
    text_block(d,24,926,verdict,SERIF(12),450,leading=14)
    d.line((500,912,500,956),fill=RULE)
    label(d,514,910,'MARKETS · WED CLOSE',11)
    for i,t in enumerate(['Dow 50,198 −1.11% · S&P 7,324 −0.23% · Nasdaq 24,430 +0.42%',
      'Gold $3,726 · WTI $82 · Brent ~$89 · BTC $63,479 · US 10Y 5.07%']):
        fitted(d,514,928+i*16,t,SANS,11,460)
    # DATE CHECK, 6 spot checks (was one line): every dated claim audited,
    # with the two non-19-Nov dates labelled as what they are.
    label(d,24,960,'DATE CHECK — 6 SPOT CHECKS · DATES VERIFIED',11,RED)
    checks=[('SUMMIT · SHENZHEN','19 NOV'),('ICJ RULING','19 NOV'),('GTA VI LAUNCH','19 NOV'),
            ('ANTHROPIC IPO','19 NOV'),('MARKETS','WED 18 NOV CLOSE'),('AKVAN','FORECAST FRI 20 NOV')]
    for i,(what,when) in enumerate(checks):
        col=i%3; row=i//3; x=24+col*324; y=976+row*14
        d.text((x,y),'✓',font=SANS_B(10),fill=RED)
        fitted(d,x+14,y,f'{what} — {when}',SANS_B,10,296)
    fitted(d,24,1002,'Sources: Reuters · AP · BBC · CBS · NPR · IMD · NASA · Sensor Tower (est.) — 19 November 2026',SANS,10,940,GREY)
    img.save(Path(__file__).resolve().with_name('entry.png'),'PNG',optimize=True)
    print('entry.png: 41 stories (3 heroes + 12 secondary + 26 numbered briefs)')


if __name__=='__main__':
    main()
