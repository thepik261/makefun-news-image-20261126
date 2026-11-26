#!/usr/bin/env python3
"""News image for 26 November 2026 -- make.fun bounty news-image-20261126.

Pure Python standard library. Draws a one-page newspaper front page that sums
up the world news of Thursday 26 November 2026 and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png) as a 1024x1024 PNG.

The stories were researched from reports published on 26 November 2026
(Reuters, BBC, Financial Times, ESA, Xinhua and the day's wire round-ups):
  * Thanksgiving Day in the United States (Thursday 26 November 2026).
  * A special European Council and a Euro Summit open in Brussels, focused
    on the 2028-2034 EU budget and financing for Ukraine.
  * India marks Constitution Day; Modi meets Germany's Chancellor Merz and
    New Delhi unveils a Rs 15,000-crore package for Nepal.
  * Leaked Rosstat records analysed by the BBC put Russia's war dead at
    nearly 500,000; the US shelves a plan to trade business deals for peace.
  * Bangladesh raises the minimum wage for garment workers by 36%.
  * World Chess Championship in Geneva: Gukesh vs Sindarov.
  * Also: Mumbai marks 18 years since the 26/11 attacks; North Korea orders
    Switzerland to shut its Pyongyang office; 1,220 players register for the
    IPL auction; Real Madrid rout PSV in the Champions League.

Everything is drawn with a hand-built 5x7 bitmap font and a tiny PNG encoder
(zlib + struct). No network, no randomness, no third-party code: two runs
produce byte-identical output.
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
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
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
        return len(s) * 6 * scale - scale if s else 0

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                cx += 6 * scale
                continue
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "#":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_centred(self, cx, y, s, scale, c):
        self.text(cx - self.text_width(s, scale) // 2, y, s, scale, c)

    def text_wrapped(self, x, y, s, max_w, scale, c, leading=None):
        """Word-wrap s into lines of at most max_w px; returns y after text."""
        leading = leading or int(9 * scale)
        words, lines, cur = s.split(" "), [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if self.text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        for line in lines:
            self.text(x, y, line, scale, c)
            y += leading
        return y


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: None
        raw += cv.px[y * stride:(y + 1) * stride]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# Illustrations (flat vector shapes, no images needed).
# ---------------------------------------------------------------------------
def draw_turkey(cv, x0, y0, x1, y1):
    """A fanned-tail turkey in the given box."""
    cv.rect(x0, y0, x1 - x0, y1 - y0, (250, 214, 150))
    cv.rect(x0, y1 - 28, x1 - x0, 28, (190, 150, 90))
    cx, cy = (x0 + x1) // 2, y0 + 118
    fan = [RED, ORANGE, GOLD, BROWN, RED, ORANGE]
    for i, col in enumerate(fan):
        ang = math.radians(-62 + i * 25)
        tx = cx + int(54 * math.sin(ang))
        ty = cy - int(54 * math.cos(ang)) - 6
        cv.circle(tx, ty, 27, col)
    cv.ellipse(cx, cy + 32, 52, 58, BROWN)
    cv.ellipse(cx - 20, cy + 38, 26, 36, (96, 56, 24))
    cv.circle(cx, cy - 46, 24, BROWN)
    cv.polygon([(cx + 18, cy - 50), (cx + 18, cy - 38), (cx + 38, cy - 44)], ORANGE)
    cv.ellipse(cx + 18, cy - 30, 6, 10, RED)
    cv.rect(cx - 4, cy - 54, 5, 5, INK)
    cv.line(cx - 15, cy + 88, cx - 15, cy + 108, ORANGE, 3)
    cv.line(cx + 15, cy + 88, cx + 15, cy + 108, ORANGE, 3)
    cv.line(cx - 22, cy + 108, cx - 8, cy + 108, ORANGE, 3)
    cv.line(cx + 8, cy + 108, cx + 22, cy + 108, ORANGE, 3)


def draw_eu_stars(cv, x0, y0, x1, y1):
    cv.rect(x0, y0, x1 - x0, y1 - y0, BLUE)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for i in range(12):
        ang = -math.pi / 2 + i * math.pi / 6
        cv.star(cx + int(34 * math.cos(ang)), cy + int(34 * math.sin(ang)), 6, GOLD)


def draw_india_flag(cv, x0, y0, x1, y1):
    h = (y1 - y0) // 3
    cv.rect(x0, y0, x1 - x0, h, (255, 153, 51))
    cv.rect(x0, y0 + h, x1 - x0, h, WHITE)
    cv.rect(x0, y0 + 2 * h, x1 - x0, y1 - y0 - 2 * h, (19, 136, 8))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    cv.ring(cx, cy, 12, NAVY, 2)
    for i in range(8):
        ang = i * math.pi / 4
        cv.line(cx, cy, cx + int(12 * math.cos(ang)), cy + int(12 * math.sin(ang)), NAVY, 1)


def draw_ukraine_flag(cv, x0, y0, x1, y1):
    mid = (y0 + y1) // 2
    cv.rect(x0, y0, x1 - x0, mid - y0, (0, 91, 187))
    cv.rect(x0, mid, x1 - x0, y1 - mid, (255, 213, 0))
    cx = (x0 + x1) // 2
    cv.text_centred(cx, y0 + 12, "NEARLY 500,000", 2, WHITE)
    cv.text_centred(cx, mid + 12, "LOST, BY MOSCOW'S OWN COUNT", 1, NAVY)


def draw_shirt(cv, x0, y0, x1, y1):
    cv.rect(x0, y0, x1 - x0, y1 - y0, LIGHT)
    cx = (x0 + x1) // 2
    cv.line(cx, y0 + 14, cx, y0 + 44, GREEN, 4)
    cv.polygon([(cx - 13, y0 + 38), (cx + 13, y0 + 38), (cx, y0 + 22)], GREEN)
    shirt = [(cx - 38, y0 + 62), (cx + 38, y0 + 62), (cx + 56, y0 + 88),
             (cx + 40, y0 + 102), (cx + 38, y0 + 158), (cx - 38, y0 + 158),
             (cx - 40, y0 + 102), (cx - 56, y0 + 88)]
    cv.polygon(shirt, WHITE)
    for i in range(len(shirt)):
        a, b = shirt[i], shirt[(i + 1) % len(shirt)]
        cv.line(a[0], a[1], b[0], b[1], INK, 2)
    cv.text_centred(cx, y0 + 168, "36%", 3, GREEN)


def draw_chessboard(cv, x0, y0, x1, y1):
    cv.rect(x0, y0, x1 - x0, y1 - y0, LIGHT)
    s = 18
    bx, by = x0 + (x1 - x0 - 8 * s) // 2, y0 + 8
    for r in range(8):
        for c in range(8):
            if (r + c) % 2 == 0:
                cv.rect(bx + c * s, by + r * s, s, s, WHITE)
            else:
                cv.rect(bx + c * s, by + r * s, s, s, INK)
    kx, ky = bx + 4 * s + s // 2, by + 7 * s + s // 2
    cv.circle(kx, ky, 8, WHITE)
    cv.ring(kx, ky, 8, INK, 2)
    cv.line(kx - 4, ky, kx + 4, ky, INK, 2)
    cv.line(kx, ky - 4, kx, ky + 4, INK, 2)
    px, py = bx + 2 * s + s // 2, by + 1 * s + s // 2
    cv.circle(px, py, 8, INK)
    cv.ring(px, py, 8, WHITE, 1)
    cv.text_centred((x0 + x1) // 2, by + 8 * s + 8, "GENEVA", 2, INK)


# ---------------------------------------------------------------------------
# The front page.
# ---------------------------------------------------------------------------
def draw_page(cv):
    cv.rect(0, 0, W, H, PAPER)

    # Masthead.
    cv.text_centred(W // 2, 20, "THE WORLD IN ONE DAY", 6, INK)
    cv.rect(24, 70, 976, 4, RED)
    cv.text_centred(W // 2, 82, "THURSDAY, 26 NOVEMBER 2026", 3, INK)
    cv.text(24, 112, "ONE DAY - ONE IMAGE", 2, GREY)
    right = "THE WORLD'S NEWS"
    cv.text(1000 - cv.text_width(right, 2), 112, right, 2, GREY)
    cv.hline(24, 134, 976, INK, 2)

    # Lead story: Thanksgiving.
    cv.frame(24, 146, 976, 272, INK, 3)
    cv.text(44, 162, "THANKSGIVING DAY - UNITED STATES", 2, RED)
    cv.text(44, 186, "AMERICA GIVES", 5, INK)
    cv.text(44, 226, "THANKS", 5, INK)
    cv.text_wrapped(
        44, 276,
        "Thanksgiving falls on Thursday 26 November this year. Families "
        "gather from coast to coast for the harvest holiday, with travel, "
        "turkey and the parade, as the United States pauses to give thanks.",
        600, 2, INK)
    draw_turkey(cv, 660, 166, 980, 398)

    # Row of three stories.
    panels = [
        (24, "EUROPE - BRUSSELS", ("EU LEADERS MEET", "IN BRUSSELS"),
         "EU leaders open a special summit in Brussels on the budget and "
         "Ukraine financing.", draw_eu_stars),
        (356, "ASIA - NEW DELHI", ("INDIA MARKS", "CONSTITUTION DAY"),
         "India marks Samvidhan Divas. Modi meets Merz; Delhi pledges "
         "Rs 15,000 crore to Nepal.", draw_india_flag),
        (688, "THE WAR IN UKRAINE", ("MOSCOW COUNTS", "ITS WAR DEAD"),
         "Leaked Rosstat records analysed by the BBC put Russia's war "
         "dead at nearly 500,000.", draw_ukraine_flag),
    ]
    for px, kicker, headline, body, art in panels:
        cv.frame(px, 434, 312, 256, INK, 2)
        art(cv, px + 2, 436, px + 310, 522)
        cv.text(px + 12, 530, kicker, 2, RED)
        y = 552
        for line in headline:
            cv.text(px + 12, y, line, 3, INK)
            y += 22
        cv.text_wrapped(px + 12, 602, body, 288, 2, INK)

    # Row of two stories.
    cv.frame(24, 706, 478, 200, INK, 2)
    draw_shirt(cv, 26, 708, 174, 904)
    cv.text(188, 722, "ASIA - DHAKA", 2, RED)
    cv.text(188, 744, "GARMENT WORKERS", 3, INK)
    cv.text(188, 766, "WIN 36% PAY RISE", 3, INK)
    cv.text_wrapped(
        188, 796,
        "Bangladesh raises the minimum wage for garment workers by 36 "
        "percent, a lift for millions in its biggest export industry.",
        302, 2, INK)

    cv.frame(522, 706, 478, 200, INK, 2)
    draw_chessboard(cv, 524, 708, 672, 904)
    cv.text(686, 722, "SPORT - GENEVA", 2, RED)
    cv.text(686, 744, "GUKESH DEFENDS", 3, INK)
    cv.text(686, 766, "HIS CROWN", 3, INK)
    cv.text_wrapped(
        686, 796,
        "World champion D. Gukesh faces Javokhir Sindarov in Geneva as "
        "the World Chess Championship match plays on.",
        302, 2, INK)

    # Ticker.
    cv.rect(24, 918, 976, 56, INK)
    ticker = ("ALSO TODAY: MUMBAI MARKS 18 YEARS SINCE 26/11 | NORTH KOREA "
              "ORDERS SWITZERLAND TO SHUT ITS PYONGYANG OFFICE | IPL AUCTION: "
              "1,220 PLAYERS | REAL MADRID ROUT PSV")
    words, lines, cur = ticker.split(" "), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if cv.text_width(trial, 2) <= 970 or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    lines = lines[:2]  # the black band holds exactly two lines
    y = 928
    for line in lines:
        cv.text_centred(W // 2, y, line, 2, WHITE)
        y += 18

    # Credit line.
    cv.text_centred(
        W // 2, 984,
        "SOURCES: REUTERS, BBC, FINANCIAL TIMES, ESA, XINHUA - REPORTS OF "
        "26 NOVEMBER 2026", 1, GREY)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    cv = Canvas(W, H, PAPER)
    draw_page(cv)
    data = png_bytes(cv)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path}: {W}x{H} PNG, {len(data)} bytes")


if __name__ == "__main__":
    main()
