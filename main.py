"""Draw the 22 November 2026 front page.

Self-contained, standard library only: no network, no clock, no
randomness. Writes /output/entry.png, exactly 1024x1024.

Stories (each re-verified against a source dated 22 Nov 2026):
 1. COP31, Antalya -- Reuters dateline Nov 22: talks approached a
    final deal on Sunday; a new text was put forward that the COP31
    President said all parties could agree upon; an approval session
    was due on Sunday morning. Labelled as NEARS a deal, never agreed.
 2. Hong Kong -- info.gov.hk: Election Committee Subsector Ordinary
    Elections on Sunday 22 Nov, polls 9am-6pm; 856 candidates
    contesting 723 seats in 31 subsectors for the 1,500-member
    Election Committee.
 3. Liberia -- AFP, Monrovia dateline Nov 22: 25 migrants deported
    from the US had arrived in Liberia, including two women; they
    landed on Friday and the commission told AFP on Saturday.
    Labelled REPORTED TODAY; the landing is not dated to 22 Nov.
Fixtures (taking place on 22 Nov, no results invented):
 F1 Las Vegas GP, 04:00 GMT (20:00 Saturday local time), Verstappen
 on pole; Liverpool v Manchester United, 16:30 GMT, Pochettino's
 first match as Manchester United coach.

Text uses a small 5x7 bitmap alphabet defined below, drawn as
filled rectangles, so the program needs no font file and is
byte-identical on every run. Pictures are flat vector shapes.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# Palette: paper, ink, accents. Flat fills keep the PNG small.
PAPER = (247, 243, 232)
WHITE = (255, 255, 255)
INK = (18, 18, 18)
RED = (183, 28, 28)
GOLD = (232, 193, 90)
TEAL = (31, 122, 110)
SKY = (191, 227, 224)
BLUE = (32, 84, 160)
LIGHT_BLUE = (140, 190, 230)
GREEN = (46, 125, 50)
LIGHT_GREEN = (165, 214, 167)
ORANGE = (232, 122, 38)
SAND = (238, 214, 165)
NAVY = (22, 38, 66)
GREY = (90, 90, 90)
DARK_GREY = (60, 60, 60)

# 5x7 glyphs, written for this entry. "#" is on, "." is off.
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00110", "00110"),
    ",": ("00000", "00000", "00000", "00000", "00110", "00100", "01000"),
    ":": ("00000", "00110", "00110", "00000", "00110", "00110", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color, t=1):
        self.fill_rect(x, y, w, t, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            if t <= 1:
                self.set(x, y, color)
            else:
                self.fill_circle(x, y, t // 2, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def circle(self, cx, cy, r, color, t=2):
        for k in range(t):
            rr = r - k
            if rr < 1:
                break
            for deg in range(0, 360):
                import math

                a = math.radians(deg)
                self.set(cx + int(rr * math.cos(a)), cy + int(rr * math.sin(a)), color)

    def fill_ellipse(self, cx, cy, rx, ry, color):
        for dy in range(-ry, ry + 1):
            dx = int(rx * (1 - (dy * dy) / float(ry * ry)) ** 0.5) if ry else 0
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def fill_polygon(self, pts, color):
        # Even-odd scanline fill.
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / float(y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(int(round(xs[i])), y, int(round(xs[i + 1])) - int(round(xs[i])) + 1, 1, color)

    # ---- text ----
    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale

    def draw_text(self, x, y, text, scale, color):
        text = text.upper()
        cx = x
        for ch in text:
            glyph = GLYPHS.get(ch, GLYPHS[" "])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        self.fill_rect(cx + col * scale, y + row * scale, scale, scale, color)
            cx += 6 * scale
        return cx

    def draw_text_center(self, cx, y, text, scale, color):
        x = cx - self.text_width(text, scale) // 2
        return self.draw_text(x, y, text, scale, color)

    def draw_block(self, x, y, lines, scale, color, gap=None):
        if gap is None:
            gap = scale
        yy = y
        for line in lines:
            self.draw_text(x, yy, line, scale, color)
            yy += 7 * scale + gap
        return yy


def wrap(text, max_chars):
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_globe(c, cx, cy, r):
    c.fill_circle(cx, cy, r, LIGHT_BLUE)
    c.fill_ellipse(cx, cy, r, r, LIGHT_BLUE)
    # Land blobs: simple rounded shapes.
    c.fill_circle(cx - r // 3, cy - r // 4, r // 4, GREEN)
    c.fill_circle(cx + r // 3, cy + r // 5, r // 5, GREEN)
    c.fill_circle(cx + r // 5, cy - r // 2, r // 6, GREEN)
    c.fill_circle(cx - r // 2, cy + r // 3, r // 6, GREEN)
    # Meridians and parallels, clipped to chords of the circle.
    import math

    c.circle(cx, cy, r, INK, 3)
    for k in (-2, -1, 0, 1, 2):
        dy = k * r // 3
        half = int((r * r - dy * dy) ** 0.5) - 6
        c.line(cx - half, cy + dy, cx + half, cy + dy, INK, 1)
    c.line(cx, cy - r + 4, cx, cy + r - 4, INK, 1)
    # Redraw land so the globe stays readable.
    c.fill_circle(cx - r // 3, cy - r // 4, r // 4, GREEN)
    c.fill_circle(cx + r // 3, cy + r // 5, r // 5, GREEN)
    c.circle(cx, cy, r, INK, 3)


def draw_lead_picture(c, x, y, w, h):
    c.fill_rect(x, y, w, h, SKY)
    c.fill_circle(x + 52, y + 44, 26, GOLD)
    c.circle(x + 52, y + 44, 26, INK, 2)
    draw_globe(c, x + w // 2 + 30, y + h // 2 - 6, 92)
    # Document with COP31, bottom left.
    dx, dy, dw, dh = x + 22, y + h - 128, 168, 104
    c.fill_rect(dx, dy, dw, dh, WHITE)
    c.rect(dx, dy, dw, dh, INK, 3)
    c.fill_rect(dx, dy, dw, 30, TEAL)
    c.draw_text(dx + 14, dy + 5, "COP31", 3, WHITE)
    for i in range(3):
        c.fill_rect(dx + 14, dy + 42 + i * 18, dw - 28, 7, DARK_GREY)
    # Ground.
    c.fill_rect(x, y + h - 26, w, 26, GREEN)
    c.fill_rect(x, y + h - 26, w, 4, INK)


def draw_hk_picture(c, x, y, w, h):
    c.fill_rect(x, y, w, h, LIGHT_BLUE)
    # Skyline.
    heights = [52, 78, 60, 88, 66, 80, 56]
    bx = x + 16
    for ht in heights:
        bw = (w - 32) // len(heights) - 4
        c.fill_rect(bx, y + h - ht - 18, bw, ht, NAVY)
        bx += bw + 4
    c.fill_rect(x, y + h - 18, w, 18, DARK_GREY)
    # Ballot box, right side, in front of skyline.
    bx, by, bw, bh = x + w - 150, y + 22, 118, 84
    c.fill_rect(bx, by, bw, bh, BLUE)
    c.rect(bx, by, bw, bh, INK, 3)
    c.fill_rect(bx + 18, by + 8, bw - 36, 8, INK)
    # Ballot paper with a tick, clear of the box.
    px, py = bx - 108, y + 6
    c.fill_rect(px, py, 52, 62, WHITE)
    c.rect(px, py, 52, 62, INK, 2)
    c.line(px + 10, py + 34, px + 22, py + 48, RED, 5)
    c.line(px + 22, py + 48, px + 42, py + 12, RED, 5)


def draw_liberia_picture(c, x, y, w, h):
    c.fill_rect(x, y, w, h, SAND)
    c.fill_circle(x + w - 52, y + 30, 22, GOLD)
    # Runway.
    c.fill_rect(x, y + h - 22, w, 22, DARK_GREY)
    for i in range(6):
        c.fill_rect(x + 18 + i * 62, y + h - 13, 30, 4, WHITE)
    # Aeroplane, side view: long fuselage, one wing below the
    # middle, tail fin up at the rear, nose to the right.
    cx, cy = x + w // 2 - 10, y + 46
    c.fill_polygon(
        [(cx - 96, cy - 10), (cx - 80, cy - 16), (cx + 62, cy - 16), (cx + 96, cy - 4), (cx + 62, cy + 12), (cx - 80, cy + 12)],
        WHITE,
    )
    c.rect(cx - 96, cy - 16, 192, 28, INK, 1)
    # Wing below the fuselage.
    c.fill_polygon([(cx - 18, cy + 10), (cx + 8, cy + 10), (cx + 28, cy + 32), (cx + 2, cy + 32)], BLUE)
    # Tail fin above the rear.
    c.fill_polygon([(cx - 96, cy - 14), (cx - 78, cy - 44), (cx - 58, cy - 44), (cx - 56, cy - 14)], RED)
    for i in range(5):
        c.fill_circle(cx - 52 + i * 26, cy - 2, 5, BLUE)
    # Big 25 marker.
    c.fill_circle(x + 44, y + h - 52, 26, RED)
    c.draw_text(x + 24, y + h - 68, "25", 3, WHITE)


def draw_car(c, x, y, color):
    # Simple racing car silhouette.
    c.fill_polygon([(x, y + 26), (x + 18, y + 10), (x + 62, y + 8), (x + 92, y + 20), (x + 108, y + 26), (x + 108, y + 34), (x, y + 34)], color)
    c.fill_rect(x + 4, y + 2, 26, 12, color)
    c.fill_circle(x + 26, y + 36, 13, INK)
    c.fill_circle(x + 84, y + 36, 13, INK)
    c.fill_circle(x + 26, y + 36, 5, WHITE)
    c.fill_circle(x + 84, y + 36, 5, WHITE)


def draw_ball(c, x, y, r):
    c.fill_circle(x, y, r, WHITE)
    c.circle(x, y, r, INK, 2)
    c.fill_circle(x, y, r // 3, INK)
    for dx, dy in ((-r // 2, -r // 2), (r // 2, -r // 2), (-r // 2, r // 2), (r // 2, r // 2), (0, -r + 8)):
        c.fill_circle(x + dx, y + dy, 5, INK)


def build():
    c = Canvas(W, H, PAPER)
    # Masthead.
    c.fill_rect(0, 0, W, 148, INK)
    c.hline(0, 148, W, RED, 6)
    c.draw_text_center(W // 2, 26, "SUNDAY 22 NOVEMBER 2026", 6, WHITE)
    c.draw_text_center(W // 2, 84, "THE WORLD IN ONE DAY", 4, GOLD)
    # Kicker strip.
    c.draw_text_center(W // 2, 160, "ANTALYA - HONG KONG - MONROVIA - PLUS SPORT TODAY", 2, RED)

    # Lead panel.
    lx, ly, lw, lh = 24, 186, 976, 372
    c.fill_rect(lx, ly, lw, lh, WHITE)
    c.rect(lx, ly, lw, lh, INK, 4)
    draw_lead_picture(c, lx + 12, ly + 12, 430, lh - 24)
    tx = lx + 462
    c.draw_text(tx, ly + 22, "CLIMATE - ANTALYA", 3, RED)
    c.draw_text(tx, ly + 62, "COP31 NEARS", 4, INK)
    c.draw_text(tx, ly + 96, "A DEAL", 4, INK)
    c.hline(tx, ly + 136, 480, INK, 3)
    body = wrap(
        "NEW TEXT OFFERED IN ANTALYA. TALKS APPROACHED A FINAL DEAL "
        "ON SUNDAY. THE PRESIDENT SAID IT WAS A TEXT ALL PARTIES "
        "COULD AGREE ON. APPROVAL SESSION DUE SUNDAY MORNING.",
        27,
    )
    c.draw_block(tx, ly + 152, body, 3, INK)
    c.draw_text(tx, ly + lh - 36, "NOT YET AGREED - NEARS A DEAL", 2, RED)

    # Middle row.
    my, mh = 574, 264
    # Hong Kong.
    hx, hw = 24, 476
    c.fill_rect(hx, my, hw, mh, WHITE)
    c.rect(hx, my, hw, mh, INK, 4)
    draw_hk_picture(c, hx + 10, my + 10, hw - 20, 96)
    c.draw_text(hx + 18, my + 118, "HONG KONG VOTES", 4, INK)
    hk_body = wrap("856 CANDIDATES CONTEST 723 SEATS, 31 SUBSECTORS. POLLS 9AM-6PM.", 25)
    c.draw_block(hx + 18, my + 156, hk_body, 3, INK)
    c.draw_text(hx + 18, my + mh - 26, "1,500-MEMBER COMMITTEE", 2, RED)
    # Liberia.
    rx, rw = 524, 476
    c.fill_rect(rx, my, rw, mh, WHITE)
    c.rect(rx, my, rw, mh, INK, 4)
    draw_liberia_picture(c, rx + 10, my + 10, rw - 20, 96)
    c.draw_text(rx + 18, my + 118, "REPORTED TODAY", 3, RED)
    c.draw_text(rx + 18, my + 146, "25 ARRIVE IN LIBERIA", 3, INK)
    lb_body = wrap("25 MIGRANTS DEPORTED FROM THE US ARRIVED, INCLUDING 2 WOMEN. LANDED FRIDAY.", 25)
    c.draw_block(rx + 18, my + 178, lb_body, 3, INK)

    # Fixtures strip.
    fy, fh = 854, 112
    c.fill_rect(24, fy, 976, fh, NAVY)
    c.draw_text_center(W // 2, fy + 10, "SPORT TODAY - FIXTURES ONLY", 3, GOLD)
    c.hline(48, fy + 44, 928, WHITE, 2)
    # F1 column.
    draw_car(c, 48, fy + 56, RED)
    c.draw_text(170, fy + 54, "F1: LAS VEGAS GP", 3, WHITE)
    c.draw_text(170, fy + 80, "04:00 GMT - VERSTAPPEN ON POLE", 2, WHITE)
    # Football column.
    draw_ball(c, 560, fy + 76, 18)
    c.draw_text(592, fy + 54, "LIVERPOOL V MAN UTD", 3, WHITE)
    c.draw_text(592, fy + 80, "16:30 GMT - POCHETTINO FIRST MATCH", 2, WHITE)

    # Footer sources.
    c.draw_text_center(
        W // 2, 978, "SOURCES: REUTERS - INFO.GOV.HK - AFP - ALL REPORTED 22 NOV 2026", 2, GREY
    )
    return c


def png_bytes(c):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw.extend(c.px[y * stride : (y + 1) * stride])
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")


def main():
    canvas = build()
    data = png_bytes(canvas)
    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.png", "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
