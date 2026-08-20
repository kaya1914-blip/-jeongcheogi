# -*- coding: utf-8 -*-
"""앱 아이콘 생성 — 모니터(CBT) + 체크

    python tools/mkicons.py

icons/ 폴더에 아래 파일을 만든다.
  icon-192.png / icon-512.png   : 안드로이드·PWA 일반 아이콘 (둥근 모서리)
  apple-touch-icon.png (180)    : iOS 홈화면 (iOS 가 알아서 모서리를 깎으므로 꽉 채움)
  icon-maskable.png (512)       : 안드로이드 적응형 (여백을 넉넉히 둬 잘리지 않게)
"""
import os, sys, math
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "icons")
os.makedirs(OUT, exist_ok=True)

SS = 4                      # 초과표본(가장자리를 매끄럽게)
NAVY_L = (79, 112, 198)     # 그라데이션 밝은 쪽
NAVY_D = (26, 43, 88)       # 그라데이션 어두운 쪽
SCREEN = (23, 38, 78)       # 화면 안쪽
WHITE  = (255, 255, 255)
MINT   = (86, 214, 186)     # 체크

def lin_grad(size, c0, c1, deg=125):
    a = math.radians(deg); dx, dy = math.cos(a), math.sin(a)
    g = Image.new("RGB", (size, size)); px = g.load()
    pr = [(x * dx + y * dy) for x in (0, size - 1) for y in (0, size - 1)]
    lo, hi = min(pr), max(pr); sp = (hi - lo) or 1
    for y in range(size):
        yd = y * dy
        for x in range(size):
            t = ((x * dx + yd) - lo) / sp
            px[x, y] = (int(c0[0] + (c1[0] - c0[0]) * t),
                        int(c0[1] + (c1[1] - c0[1]) * t),
                        int(c0[2] + (c1[2] - c0[2]) * t))
    return g

def rmask(size, r):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=255)
    return m

def thick(d, pts, w, fill):
    """둥근 끝을 가진 굵은 선"""
    d.line(pts, fill=fill, width=w, joint="curve")
    r = w // 2
    for (x, y) in pts:
        d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

def draw_icon(size, corner=0.225, scale=1.0):
    """corner=0 이면 모서리를 깎지 않음(iOS·마스커블용).
       scale<1 이면 모니터를 작게 그려 여백을 둔다(마스커블용)."""
    W = size * SS
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    bg = lin_grad(W, NAVY_L, NAVY_D)
    img.paste(bg, (0, 0), rmask(W, int(W * corner)) if corner > 0 else None)
    d = ImageDraw.Draw(img)

    c = W * 0.5
    def sx(v): return c + (v - 0.5) * W * scale      # 가운데 기준으로 축소

    x0, y0, x1, y1 = sx(0.175), sx(0.225), sx(0.825), sx(0.650)
    rad = int(W * 0.052 * scale)
    d.rounded_rectangle([x0, y0, x1, y1], radius=rad, fill=WHITE)          # 본체
    p = W * 0.048 * scale
    d.rounded_rectangle([x0 + p, y0 + p, x1 - p, y1 - p],
                        radius=int(W * 0.026 * scale), fill=SCREEN)        # 화면
    nw = W * 0.055 * scale
    d.rectangle([c - nw, y1 - W * 0.004 * scale, c + nw, sx(0.742)], fill=WHITE)  # 목
    bw, bh = W * 0.165 * scale, W * 0.030 * scale
    d.rounded_rectangle([c - bw, sx(0.742), c + bw, sx(0.742) + bh],
                        radius=int(bh / 2), fill=WHITE)                    # 받침

    cy = (y0 + y1) / 2                                                     # 화면 안 체크
    thick(d, [(sx(0.352), cy + W * 0.008 * scale),
              (sx(0.443), cy + W * 0.093 * scale),
              (sx(0.648), cy - W * 0.100 * scale)],
          int(W * 0.066 * scale), MINT)
    return img.resize((size, size), Image.LANCZOS)

if __name__ == "__main__":
    draw_icon(192).save(os.path.join(OUT, "icon-192.png"));            print("만듦 icon-192.png")
    draw_icon(512).save(os.path.join(OUT, "icon-512.png"));            print("만듦 icon-512.png")
    draw_icon(180, corner=0).save(os.path.join(OUT, "apple-touch-icon.png")); print("만듦 apple-touch-icon.png")
    draw_icon(512, corner=0, scale=0.78).save(os.path.join(OUT, "icon-maskable.png")); print("만듦 icon-maskable.png")
    print("끝났습니다:", OUT)
