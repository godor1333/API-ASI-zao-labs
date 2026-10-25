#!/usr/bin/env python3
"""Рендер реального текста консоли в PNG, похожий на окно терминала.
Использование: term2png.py input.txt output.png [--title "pytest -v"] [--width 110]
Текст берётся из файла как есть (никакого редактирования содержимого).
ANSI-коды цвета поддерживаются частично (красный/зелёный/жёлтый/жирный), остальные вырезаются.
"""
import sys, re, argparse
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

COLORS = {
    "30": (60, 60, 60), "31": (255, 85, 85), "32": (80, 250, 123), "33": (241, 250, 140),
    "34": (98, 160, 255), "35": (255, 121, 198), "36": (139, 233, 253), "37": (248, 248, 242),
    "90": (150, 150, 150), "91": (255, 110, 110), "92": (120, 255, 150), "93": (255, 255, 160),
}
ANSI = re.compile(r"\x1b\[([0-9;]*)m")


def parse_line(line):
    """Возвращает список (text, color, bold)."""
    segs, pos, color, bold = [], 0, None, False
    for m in ANSI.finditer(line):
        if m.start() > pos:
            segs.append((line[pos:m.start()], color, bold))
        codes = m.group(1).split(";") if m.group(1) else ["0"]
        for c in codes:
            if c in ("0", ""):
                color, bold = None, False
            elif c == "1":
                bold = True
            elif c in COLORS:
                color = COLORS[c]
        pos = m.end()
    if pos < len(line):
        segs.append((line[pos:], color, bold))
    return segs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--title", default="Terminal")
    ap.add_argument("--width", type=int, default=110, help="символов в строке")
    ap.add_argument("--size", type=int, default=15)
    ap.add_argument("--light", action="store_true", help="светлая тема (как cmd/PowerShell светлый)")
    a = ap.parse_args()

    raw = open(a.inp, encoding="utf-8", errors="replace").read().rstrip("\n").split("\n")
    # мягкий перенос длинных строк
    lines = []
    for ln in raw:
        plain = ANSI.sub("", ln)
        if len(plain) <= a.width:
            lines.append(ln)
        else:
            # переносим по ширине, теряя цвет на переносе (допустимо)
            for i in range(0, len(plain), a.width):
                lines.append(plain[i:i + a.width])

    font = ImageFont.truetype(FONT, a.size)
    fontb = ImageFont.truetype(FONT_B, a.size)
    cw = font.getlength("M")
    lh = int(a.size * 1.45)
    pad = 14
    title_h = 34
    W = int(cw * a.width + pad * 2)
    H = title_h + pad * 2 + lh * len(lines)

    if a.light:
        bg, fg, tbg, tfg = (255, 255, 255), (20, 20, 20), (240, 240, 240), (40, 40, 40)
    else:
        bg, fg, tbg, tfg = (30, 30, 30), (220, 220, 220), (60, 60, 60), (230, 230, 230)

    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, title_h], fill=tbg)
    # кнопки окна
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([12 + i * 20, 10, 26 + i * 20, 24], fill=c)
    d.text((80, 8), a.title, font=font, fill=tfg)

    y = title_h + pad
    for ln in lines:
        x = pad
        for text, color, bold in parse_line(ln):
            f = fontb if bold else font
            d.text((x, y), text, font=f, fill=color or fg)
            x += f.getlength(text)
        y += lh
    img.save(a.out)
    print(a.out, img.size)


if __name__ == "__main__":
    main()
