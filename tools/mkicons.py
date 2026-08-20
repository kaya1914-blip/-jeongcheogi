# -*- coding: utf-8 -*-
"""PWA 아이콘(192/512/180) 생성 — 남색 라운드 사각형 + 흰 '정'"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding='utf-8')

OUT = r"C:\Users\user\Desktop\정보처리기사 교재\icons"
os.makedirs(OUT, exist_ok=True)
NAVY = (51, 80, 156, 255)

# 한글이 나오는 폰트 찾기
CANDS = [r"C:\Windows\Fonts\malgunbd.ttf", r"C:\Windows\Fonts\malgun.ttf",
         r"C:\Windows\Fonts\gulim.ttc", r"C:\Windows\Fonts\batang.ttc"]
fontpath = next((p for p in CANDS if os.path.exists(p)), None)
print("폰트:", fontpath)

def make(size, radius_ratio=0.22, pad_ratio=0.0):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = int(size * radius_ratio)
    p = int(size * pad_ratio)
    d.rounded_rectangle([p, p, size - 1 - p, size - 1 - p], radius=r, fill=NAVY)
    if fontpath:
        fs = int(size * 0.56)
        try:
            f = ImageFont.truetype(fontpath, fs)
        except Exception:
            f = ImageFont.load_default()
        txt = "정"
        bbox = d.textbbox((0, 0), txt, font=f)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1]), txt,
               font=f, fill=(255, 255, 255, 255))
    return img

for s in (192, 512):
    make(s).save(os.path.join(OUT, "icon-%d.png" % s))
    print("생성 icon-%d.png" % s)
# iOS 홈화면용 (모서리를 iOS가 깎으므로 사각형 꽉 채움)
make(180, radius_ratio=0.0).save(os.path.join(OUT, "apple-touch-icon.png"))
print("생성 apple-touch-icon.png")
# 마스크 가능한 아이콘(안전 영역 확보)
make(512, radius_ratio=0.5, pad_ratio=0.0).save(os.path.join(OUT, "icon-maskable.png"))
print("생성 icon-maskable.png")
print("완료:", OUT)
