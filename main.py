#!/usr/bin/env python3
"""Front page for 26 November 2026 -- make.fun bounty news-image-20261126.

A pure-stdlib Python program. It draws a one-page newspaper front page
that sums up the world news of Thursday 26 November 2026 and saves it as
a 1024x1024 PNG at $MAKEFUN_OUTPUT_DIR/entry.png (/output/entry.png when
the variable is unset).

The day's stories, checked against reporting published around 26 November
2026 (Reuters, BBC, Financial Times, ESA, Xinhua and the wires):
  * Thanksgiving Day in the United States, Thursday 26 November 2026.
  * A special European Council and Euro Summit open in Brussels, centred
    on the 2028-2034 EU budget and financing for Ukraine.
  * India marks Constitution Day; Modi meets Germany's Chancellor Merz and
    New Delhi announces a Rs 15,000-crore package for Nepal.
  * Leaked Rosstat records, analysed by the BBC, put Russia's war dead at
    nearly 500,000.
  * Bangladesh lifts the minimum wage for garment workers by 36%.
  * World Chess Championship in Geneva: Gukesh against Sindarov.
  * Also noted: Mumbai marks 18 years since the 26/11 attacks; North
    Korea orders Switzerland to shut its Pyongyang office; 1,220 players
    register for the IPL auction; Real Madrid rout PSV.

The picture is painted with a hand-built 5x7 bitmap font and a small PNG
encoder written on zlib and struct. No network, no randomness, no
third-party code: running it twice writes byte-identical files.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 characters; '#' is ink, '.' is
# blank. Lowercase letters sit on the x-height with descenders on rows 6-7.
# ---------------------------------------------------------------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
}

FONT.update({
    "a": (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    "j": ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", "#...#", "#...#", "#...#", ".####", "....#", ".###."),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "&": (".###.", "#...#", "#...#", ".#.#.", "#.#..", "#.#..", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
})

# Normalise: every glyph must be exactly 7 rows of 5 columns.
for _k in list(FONT):
    _g = FONT[_k]
    if len(_g) > 7:
        FONT[_k] = _g[:7]
    elif len(_g) < 7:
        FONT[_k] = _g + (".....",) * (7 - len(_g))
    assert all(len(_r) == 5 for _r in FONT[_k]), _k


# ---------------------------------------------------------------------------
# Canvas: an RGB pixel buffer with flat-colour drawing primitives.
# ---------------------------------------------------------------------------
PAPER = (247, 243, 232)
INK = (22, 22, 22)
WHITE = (255, 255, 255)
RED = (178, 34, 34)
BLUE = (30, 64, 140)
NAVY = (18, 38, 84)
GOLD = (212, 160, 32)
GREEN = (34, 120, 60)
ORANGE = (214, 110, 30)
BROWN = (122, 72, 32)
SKY = (135, 190, 230)
GREY = (90, 90, 90)
LIGHT = (238, 232, 216)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if not (0 <= x < self.w and 0 <= y < self.h):
            return
        i = (y * self.w + x) * 3
        self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            row = bytes(c) * (x1 - x0)
            self.px[i:i + (x1 - x0) * 3] = row

    def frame(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            if t == 1:
                self.set(x, y, c)
            else:
                self.rect(x - t // 2, y - t // 2, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            outer = int(math.sqrt(max(0, r * r - dy * dy)))
            inner = int(math.sqrt(max(0, (r - t) * (r - t) - dy * dy))) if r - t > abs(dy) else 0
            self.rect(cx - outer, yy, outer - inner, 1, c)
            self.rect(cx + inner + 1, yy, outer - inner, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            dy = (yy - cy) / ry
            dx = int(rx * math.sqrt(max(0.0, 1.0 - dy * dy)))
            self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def polygon(self, pts, c):
        # Even-odd scanline fill.
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(math.ceil(xs[i])), y,
                          int(math.floor(xs[i + 1])) - int(math.ceil(xs[i])) + 1, 1, c)

    def star(self, cx, cy, r, c):
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.45
            pts.append((cx + int(rr * math.cos(ang)), cy + int(rr * math.sin(ang))))
        self.polygon(pts, c)

    # -- text ---------------------------------------------------------------
    def text_width(self, s, scale):
        if not s:
            return 0
        return (len(s) * 6 - 1) * scale

    def _stamp(self, x, y, glyph, scale, c):
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "#":
                    self.rect(x + col * scale, y + row * scale,
                              scale, scale, c)

    def text(self, x, y, s, scale, c):
        pen = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is not None:
                self._stamp(pen, y, glyph, scale, c)
            pen += 6 * scale
        return pen

    def text_centred(self, cx, y, s, scale, c):
        start = cx - self.text_width(s, scale) // 2
        self.text(start, y, s, scale, c)

    def text_wrapped(self, x, y, s, max_w, scale, c, leading=None):
        """Word-wrap s into lines of at most max_w px; returns y after text."""
        gap = leading if leading is not None else int(9 * scale)
        lines = wrap_text(self, s, max_w, scale)
        for line in lines:
            self.text(x, y, line, scale, c)
            y += gap
        return y


def png_bytes(cv):
    """Encode the canvas as a PNG: raw scanlines, one zlib stream."""
    scanlines = bytearray()
    row_bytes = cv.w * 3
    for start in range(0, cv.h * row_bytes, row_bytes):
        scanlines.append(0)  # filter type 0: no filtering
        scanlines += cv.px[start:start + row_bytes]

    def chunk(kind, data):
        packed = struct.pack(">I", len(data)) + kind + data
        packed += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return packed

    header = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(bytes(scanlines), 9))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# Illustrations (flat vector shapes, no images needed).
# ---------------------------------------------------------------------------
def draw_turkey(cv, x0, y0, x1, y1):
    """A fanned-tail turkey in the given box."""
    sky = (250, 214, 150)
    ground = (190, 150, 90)
    wing = (96, 56, 24)
    cv.rect(x0, y0, x1 - x0, y1 - y0, sky)
    cv.rect(x0, y1 - 28, x1 - x0, 28, ground)
    cx = (x0 + x1) // 2
    cy = y0 + 118
    fan_cols = [RED, ORANGE, GOLD, BROWN, RED, ORANGE]
    for step, col in enumerate(fan_cols):
        ang = math.radians(-62 + step * 25)
        fx = cx + int(54 * math.sin(ang))
        fy = cy - int(54 * math.cos(ang)) - 6
        cv.circle(fx, fy, 27, col)
    cv.ellipse(cx, cy + 32, 52, 58, BROWN)
    cv.ellipse(cx - 20, cy + 38, 26, 36, wing)
    cv.circle(cx, cy - 46, 24, BROWN)
    cv.polygon([(cx + 18, cy - 50), (cx + 18, cy - 38), (cx + 38, cy - 44)],
               ORANGE)
    cv.ellipse(cx + 18, cy - 30, 6, 10, RED)
    cv.rect(cx - 4, cy - 54, 5, 5, INK)
    for dx in (-15, 15):
        cv.line(cx + dx, cy + 88, cx + dx, cy + 108, ORANGE, 3)
    cv.line(cx - 22, cy + 108, cx - 8, cy + 108, ORANGE, 3)
    cv.line(cx + 8, cy + 108, cx + 22, cy + 108, ORANGE, 3)


def draw_eu_stars(cv, x0, y0, x1, y1):
    cv.rect(x0, y0, x1 - x0, y1 - y0, BLUE)
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    for n in range(12):
        ang = -math.pi / 2 + n * math.pi / 6
        sx = cx + int(34 * math.cos(ang))
        sy = cy + int(34 * math.sin(ang))
        cv.star(sx, sy, 6, GOLD)


def draw_india_flag(cv, x0, y0, x1, y1):
    band = (y1 - y0) // 3
    cv.rect(x0, y0, x1 - x0, band, (255, 153, 51))
    cv.rect(x0, y0 + band, x1 - x0, band, WHITE)
    cv.rect(x0, y0 + 2 * band, x1 - x0, y1 - y0 - 2 * band, (19, 136, 8))
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    cv.ring(cx, cy, 12, NAVY, 2)
    for n in range(8):
        ang = n * math.pi / 4
        ex = cx + int(12 * math.cos(ang))
        ey = cy + int(12 * math.sin(ang))
        cv.line(cx, cy, ex, ey, NAVY, 1)


def draw_ukraine_flag(cv, x0, y0, x1, y1):
    mid = (y0 + y1) // 2
    sky_blue = (0, 91, 187)
    wheat = (255, 213, 0)
    cv.rect(x0, y0, x1 - x0, mid - y0, sky_blue)
    cv.rect(x0, mid, x1 - x0, y1 - mid, wheat)
    cx = (x0 + x1) // 2
    cv.text_centred(cx, y0 + 12, "NEARLY 500,000", 2, WHITE)
    cv.text_centred(cx, mid + 12, "LOST, BY MOSCOW'S OWN COUNT", 1, NAVY)


def draw_shirt(cv, x0, y0, x1, y1):
    cv.rect(x0, y0, x1 - x0, y1 - y0, LIGHT)
    cx = (x0 + x1) // 2
    cv.line(cx, y0 + 14, cx, y0 + 44, GREEN, 4)
    cv.polygon([(cx - 13, y0 + 38), (cx + 13, y0 + 38), (cx, y0 + 22)], GREEN)
    offsets = [(-38, 62), (38, 62), (56, 88), (40, 102), (38, 158),
               (-38, 158), (-40, 102), (-56, 88)]
    outline = [(cx + dx, y0 + dy) for dx, dy in offsets]
    cv.polygon(outline, WHITE)
    for n in range(len(outline)):
        a = outline[n]
        b = outline[(n + 1) % len(outline)]
        cv.line(a[0], a[1], b[0], b[1], INK, 2)
    cv.text_centred(cx, y0 + 168, "36%", 3, GREEN)


def draw_chessboard(cv, x0, y0, x1, y1):
    cv.rect(x0, y0, x1 - x0, y1 - y0, LIGHT)
    cell = 18
    bx = x0 + (x1 - x0 - 8 * cell) // 2
    by = y0 + 8
    for row in range(8):
        for col in range(8):
            shade = WHITE if (row + col) % 2 == 0 else INK
            cv.rect(bx + col * cell, by + row * cell, cell, cell, shade)
    kx = bx + 4 * cell + cell // 2
    ky = by + 7 * cell + cell // 2
    cv.circle(kx, ky, 8, WHITE)
    cv.ring(kx, ky, 8, INK, 2)
    cv.line(kx - 4, ky, kx + 4, ky, INK, 2)
    cv.line(kx, ky - 4, kx, ky + 4, INK, 2)
    px = bx + 2 * cell + cell // 2
    py = by + 1 * cell + cell // 2
    cv.circle(px, py, 8, INK)
    cv.ring(px, py, 8, WHITE, 1)
    cv.text_centred((x0 + x1) // 2, by + 8 * cell + 8, "GENEVA", 2, INK)


# ---------------------------------------------------------------------------
# Front page. Stories are data; one renderer draws them all, so the page
# can grow without touching the drawing code.
# ---------------------------------------------------------------------------

MARGIN = 24
CONTENT_W = 976
ROW_Y = 434
ROW_H = 256
PANEL_W = 312
BODY_W = 288

TITLE = "THE WORLD IN ONE DAY"
DATE_LINE = "THURSDAY, 26 NOVEMBER 2026"
LEFT_STRAP = "ONE DAY - ONE IMAGE"
RIGHT_STRAP = "THE WORLD'S NEWS"

LEAD_STORY = {
    "kicker": "THANKSGIVING DAY - UNITED STATES",
    "lines": ("AMERICA GIVES", "THANKS"),
    "body": (
        "Thanksgiving falls on Thursday 26 November this year. "
        "Families gather from coast to coast for the harvest holiday, "
        "with travel, turkey and the parade, as the United States "
        "pauses to give thanks."
    ),
}

MIDDLE_STORIES = [
    {
        "x": 24,
        "kicker": "EUROPE - BRUSSELS",
        "lines": ("EU LEADERS MEET", "IN BRUSSELS"),
        "body": (
            "EU leaders open a special summit in Brussels on the "
            "budget and Ukraine financing."
        ),
        "art": draw_eu_stars,
    },
    {
        "x": 356,
        "kicker": "ASIA - NEW DELHI",
        "lines": ("INDIA MARKS", "CONSTITUTION DAY"),
        "body": (
            "India marks Samvidhan Divas. Modi meets Merz; Delhi "
            "pledges Rs 15,000 crore to Nepal."
        ),
        "art": draw_india_flag,
    },
    {
        "x": 688,
        "kicker": "THE WAR IN UKRAINE",
        "lines": ("MOSCOW COUNTS", "ITS WAR DEAD"),
        "body": (
            "Leaked Rosstat records analysed by the BBC put "
            "Russia's war dead at nearly 500,000."
        ),
        "art": draw_ukraine_flag,
    },
]


def draw_masthead(cv):
    cv.rect(0, 0, W, H, PAPER)
    cv.text_centred(W // 2, 20, TITLE, 6, INK)
    cv.rect(MARGIN, 70, CONTENT_W, 4, RED)
    cv.text_centred(W // 2, 82, DATE_LINE, 3, INK)
    cv.text(MARGIN, 112, LEFT_STRAP, 2, GREY)
    cv.text(W - MARGIN - cv.text_width(RIGHT_STRAP, 2), 112,
            RIGHT_STRAP, 2, GREY)
    cv.hline(MARGIN, 134, CONTENT_W, INK, 2)


def draw_lead(cv):
    top, height = 146, 272
    cv.frame(MARGIN, top, CONTENT_W, height, INK, 3)
    cv.text(MARGIN + 20, top + 16, LEAD_STORY["kicker"], 2, RED)
    y = top + 40
    for line in LEAD_STORY["lines"]:
        cv.text(MARGIN + 20, y, line, 5, INK)
        y += 40
    cv.text_wrapped(MARGIN + 20, top + 130, LEAD_STORY["body"], 600, 2, INK)
    draw_turkey(cv, MARGIN + 636, top + 20, MARGIN + 956, top + 252)


def draw_middle_row(cv):
    for story in MIDDLE_STORIES:
        x = story["x"]
        cv.frame(x, ROW_Y, PANEL_W, ROW_H, INK, 2)
        story["art"](cv, x + 2, ROW_Y + 2, x + 310, ROW_Y + 88)
        cv.text(x + 12, ROW_Y + 96, story["kicker"], 2, RED)
        y = ROW_Y + 118
        for line in story["lines"]:
            cv.text(x + 12, y, line, 3, INK)
            y += 22
        cv.text_wrapped(x + 12, ROW_Y + 168, story["body"], BODY_W, 2, INK)


def draw_page(cv):
    draw_masthead(cv)
    draw_lead(cv)
    draw_middle_row(cv)
    draw_lower_row(cv)
    draw_ticker(cv)

LOWER_STORIES = [
    {
        "x": 24,
        "art_box": (26, 708, 174, 904),
        "art": draw_shirt,
        "kicker": "ASIA - DHAKA",
        "lines": ("GARMENT WORKERS", "WIN 36% PAY RISE"),
        "body": (
            "Bangladesh raises the minimum wage for garment workers "
            "by 36 percent, a lift for millions in its biggest "
            "export industry."
        ),
    },
    {
        "x": 522,
        "art_box": (524, 708, 672, 904),
        "art": draw_chessboard,
        "kicker": "SPORT - GENEVA",
        "lines": ("GUKESH DEFENDS", "HIS CROWN"),
        "body": (
            "World champion D. Gukesh faces Javokhir Sindarov in "
            "Geneva as the World Chess Championship match plays on."
        ),
    },
]

TICKER_ITEMS = (
    "MUMBAI MARKS 18 YEARS SINCE 26/11",
    "NORTH KOREA ORDERS SWITZERLAND TO SHUT ITS PYONGYANG OFFICE",
    "IPL AUCTION: 1,220 PLAYERS",
    "REAL MADRID ROUT PSV",
)

CREDIT = (
    "SOURCES: REUTERS, BBC, FINANCIAL TIMES, ESA, XINHUA - "
    "REPORTS OF 26 NOVEMBER 2026"
)


def draw_lower_row(cv):
    for story in LOWER_STORIES:
        x = story["x"]
        cv.frame(x, 706, 478, 200, INK, 2)
        story["art"](cv, *story["art_box"])
        tx = x + 164
        cv.text(tx, 722, story["kicker"], 2, RED)
        y = 744
        for line in story["lines"]:
            cv.text(tx, y, line, 3, INK)
            y += 22
        cv.text_wrapped(tx, 796, story["body"], 302, 2, INK)


def wrap_text(cv, text, width, scale):
    words, lines, cur = text.split(" "), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if cv.text_width(trial, scale) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_ticker(cv):
    cv.rect(MARGIN, 918, CONTENT_W, 56, INK)
    ticker = "ALSO TODAY: " + " | ".join(TICKER_ITEMS)
    lines = wrap_text(cv, ticker, 970, 2)[:2]
    y = 928
    for line in lines:
        cv.text_centred(W // 2, y, line, 2, WHITE)
        y += 18
    cv.text_centred(W // 2, 984, CREDIT, 1, GREY)


def verify_png(path):
    """Check the written file is a whole 1024x1024 PNG under the 1 MiB cap."""
    with open(path, "rb") as handle:
        data = handle.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("not a PNG: " + path)
    w, h = struct.unpack(">II", data[16:24])
    if (w, h) != (1024, 1024):
        raise SystemExit(f"wrong size: {w}x{h}")
    if len(data) > 1024 * 1024:
        raise SystemExit(f"over the 1 MiB cap: {len(data)} bytes")
    return len(data)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    page = Canvas(W, H, PAPER)
    draw_page(page)
    data = png_bytes(page)
    target = os.path.join(outdir, "entry.png")
    with open(target, "wb") as handle:
        handle.write(data)
    size = verify_png(target)
    print(f"wrote {target}: {W}x{H} PNG, {size} bytes")


if __name__ == "__main__":
    main()
