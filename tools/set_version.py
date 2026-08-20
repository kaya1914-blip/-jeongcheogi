# -*- coding: utf-8 -*-
"""판(버전) 올리기 — 모든 파일의 판 번호를 한 번에 맞춘다.

    python tools/set_version.py          판을 1 올린다  (v2 → v3)
    python tools/set_version.py 5        판을 5 로 지정한다
    python tools/set_version.py --show   지금 판만 보여준다

고치는 곳
    index.html · textbook.html · exam.html   화면에 보이는 판·날짜
    sw.js                                    캐시 판 (이걸 올려야 폰이 새 파일을 받는다)
"""
import io, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["index.html", "textbook.html", "exam.html"]
SW = "sw.js"

def read(p):  return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def write(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(s)

def current():
    """sw.js 의 판을 기준으로 삼는다"""
    m = re.search(r"const VERSION = 'jcg-v(\d+)'", read(SW))
    return int(m.group(1)) if m else 1

def apply(ver):
    today = datetime.date.today().isoformat()
    # 1) 서비스 워커 캐시 판
    s = read(SW)
    s = re.sub(r"const VERSION = 'jcg-v\d+'", "const VERSION = 'jcg-v%d'" % ver, s)
    write(SW, s)
    # 2) 화면에 보이는 판·날짜
    for p in PAGES:
        if not os.path.exists(os.path.join(ROOT, p)):
            continue
        s = read(p)
        if "var APP_VERSION" not in s:
            print("  건너뜀(판 표시 없음):", p); continue
        s = re.sub(r"var APP_VERSION\s*=\s*'v\d+'", "var APP_VERSION = 'v%d'" % ver, s)
        s = re.sub(r"var APP_BUILT\s*=\s*'[\d-]*'", "var APP_BUILT = '%s'" % today, s)
        write(p, s)
        print("  맞춤:", p)
    return ver, today

if __name__ == "__main__":
    cur = current()
    if "--show" in sys.argv:
        print("지금 판: v%d" % cur); sys.exit()
    nums = [a for a in sys.argv[1:] if a.isdigit()]
    new = int(nums[0]) if nums else cur + 1
    v, d = apply(new)
    print("판을 v%d 로 올렸습니다 (%s)" % (v, d))
    print("※ 올린 뒤 폰에서 앱을 열면 '갱신됨' 알림이 뜹니다.")
