# -*- coding: utf-8 -*-
"""인쇄용 PDF 만들기 — 크롬 헤드리스로 교재·모의고사 PDF 를 생성한다.

    python tools/build.py

교재는 정답(details)을 펼친 사본을 만들어 변환하고,
모의고사는 JS 문항 데이터를 정적 HTML(문제+정답+3단 해설)로 뽑아 변환한다.
"""
import io, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QT, BS = '"', chr(92)
SYM = ['①', '②', '③', '④']

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/google-chrome", "/usr/bin/chromium",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]

def find_chrome():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    sys.exit("크롬(또는 엣지)을 찾지 못했습니다. CHROME_CANDIDATES 에 경로를 추가해 주세요.")

def to_pdf(chrome, src_html, out_pdf):
    profile = os.path.join(tempfile.gettempdir(), "jcg_pdf_profile")
    os.makedirs(profile, exist_ok=True)
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-first-run",
                    "--no-pdf-header-footer", "--user-data-dir=" + profile,
                    "--virtual-time-budget=28000",
                    "--print-to-pdf=" + out_pdf,
                    "file:///" + src_html.replace("\\", "/").replace(" ", "%20")],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ---------- 1) 교재 ----------
def build_textbook(chrome):
    src = os.path.join(ROOT, "textbook.html")
    if not os.path.exists(src):
        print("건너뜀: textbook.html 없음"); return
    s = io.open(src, encoding='utf-8').read().replace("<details>", "<details open>")
    tmp = os.path.join(ROOT, "_print_textbook.html")
    io.open(tmp, 'w', encoding='utf-8').write(s)
    out = os.path.join(ROOT, "정처기_필기_교재.pdf")
    to_pdf(chrome, tmp, out)
    os.remove(tmp)
    print("만듦:", os.path.basename(out), "%.1f MB" % (os.path.getsize(out) / 1048576))

# ---------- 2) 모의고사 해설본 ----------
def split_opts(inner):
    out, cur, inq, esc = [], '', False, False
    for ch in inner:
        if esc: cur += ch; esc = False; continue
        if ch == BS: cur += ch; esc = True; continue
        if ch == QT:
            inq = not inq
            if not inq: out.append(cur); cur = ''
            continue
        if inq: cur += ch
    return out

def field(blk, name):
    pat = name + ':"((?:[^"' + BS + BS + ']|' + BS + BS + '.)*)"'
    m = re.search(pat, blk, re.S)
    return m.group(1) if m else ''

def unesc(t):
    return t.replace(BS + '"', '"').replace(BS + 'n', '\n').replace(BS + BS, BS)

CSS = """<meta charset="utf-8"><title>정처기 실전 모의고사 (해설본)</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;600;700&family=Noto+Serif+KR:wght@700&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
@page{margin:14mm 12mm}
body{font-family:'IBM Plex Sans KR','Malgun Gothic',sans-serif;font-size:10.5pt;line-height:1.62;color:#191C2A;background:#fff}
h1{font-family:'Noto Serif KR',serif;font-size:22pt;margin:0 0 4px}
h2{font-family:'Noto Serif KR',serif;font-size:15pt;margin:22px 0 10px;padding:7px 12px;background:#EAEEF9;border-left:4px solid #33509C;border-radius:6px;break-after:avoid}
.lede{color:#454A60;font-size:10pt;margin:0 0 6px}
.q{break-inside:avoid;border:1px solid #E4E6F0;border-radius:9px;padding:11px 14px;margin:0 0 9px}
.qt{font-weight:600;margin:0 0 6px}
.n{display:inline-block;background:#33509C;color:#fff;border-radius:5px;padding:0 7px;margin-right:7px;font-family:'JetBrains Mono',monospace;font-size:9pt}
.tag{font-family:'JetBrains Mono',monospace;font-size:7.5pt;color:#2B437F;background:#EAEEF9;border:1px solid #D2D6E4;border-radius:4px;padding:1px 5px;margin-left:6px;font-weight:600}
ul{list-style:none;padding:0;margin:6px 0}
li{margin:2px 0;color:#454A60}
li.ok{color:#0A5F50;font-weight:700}
pre{background:#20243A;color:#E7E9F5;border-radius:8px;padding:9px 11px;font-size:8.6pt;line-height:1.5;white-space:pre-wrap;margin:7px 0}
pre code{font-family:'JetBrains Mono',monospace}
.key{color:#9FB4F2}.str{color:#8FD1B0}.num{color:#E0A96B}.cmt{color:#8B92B8}
.s{border-top:1px dashed #D2D6E4;margin-top:8px;padding-top:7px;font-size:9.8pt;color:#454A60}
.s p{margin:4px 0}
.ans{font-weight:700;color:#0A5F50}
.lb{font-family:'JetBrains Mono',monospace;font-size:7.5pt;font-weight:600;border-radius:4px;padding:1px 5px;margin-right:6px}
.lb.w{background:#E2F4EF;color:#0A5F50;border:1px solid #B4E0D5}
.lb.t{background:#FBE9E7;color:#B0322E;border:1px solid #EEC5C1}
.lb.c{background:#33509C;color:#fff}
.co{background:#F4F5F9;border:1px solid #E4E6F0;border-radius:7px;padding:8px 11px;margin-top:6px}
b{font-weight:700;color:#191C2A}
code{font-family:'JetBrains Mono',monospace;font-size:.9em;background:#F4F5F9;border:1px solid #E4E6F0;border-radius:4px;padding:0 4px}
</style>
<h1>정보처리기사 필기 실전 모의고사</h1>
<p class="lede">정답과 해설 포함본 &nbsp;|&nbsp; 합격 기준: 과목당 40점 이상, 평균 60점 이상</p>
"""

def build_exam(chrome):
    src = os.path.join(ROOT, "exam.html")
    if not os.path.exists(src):
        print("건너뜀: exam.html 없음"); return
    s = io.open(src, encoding='utf-8').read()
    mark = '앱 로직'
    mid = s[s.index('var EXAM'):s.index(mark)]
    html, n = [], 0
    for sec in re.split(r'\{s:"', mid)[1:]:
        name = sec[:sec.index(QT)]
        html.append('<h2>%s</h2>' % name)
        for blk in re.split(r'(?=\{t:")', sec)[1:]:
            m = re.search(r'o:\[(.*?)\], a:(\d)', blk, re.S)
            if not m: continue
            n += 1
            opts = [unesc(o) for o in split_opts(m.group(1))]
            a = int(m.group(2))
            o_html = ''.join('<li class="%s">%s %s</li>' % ('ok' if i == a else '', SYM[i], t)
                             for i, t in enumerate(opts))
            code = unesc(field(blk, 'code'))
            html.append(
                '<div class="q"><p class="qt"><b class="n">%d</b>%s<span class="tag">%s</span></p>%s'
                '<ul>%s</ul><div class="s"><p class="ans">정답 %s</p>'
                '<p><span class="lb w">정답 근거</span>%s</p>'
                '%s%s</div></div>' % (
                    n, unesc(field(blk, 'q')), unesc(field(blk, 't')),
                    ('<pre><code>%s</code></pre>' % code) if code else '',
                    o_html, SYM[a], unesc(field(blk, 'why')),
                    ('<p><span class="lb t">함정</span>%s</p>' % unesc(field(blk, 'trap'))) if field(blk, 'trap') else '',
                    ('<p class="co"><span class="lb c">강사 한마디</span>%s</p>' % unesc(field(blk, 'coach'))) if field(blk, 'coach') else ''))
    tmp = os.path.join(ROOT, "_print_exam.html")
    io.open(tmp, 'w', encoding='utf-8').write(CSS + '\n'.join(html))
    out = os.path.join(ROOT, "정처기_실전모의고사_해설본.pdf")
    to_pdf(chrome, tmp, out)
    os.remove(tmp)
    print("만듦:", os.path.basename(out), "%.1f MB" % (os.path.getsize(out) / 1048576), "· %d문항" % n)

if __name__ == "__main__":
    chrome = find_chrome()
    print("크롬:", chrome)
    build_textbook(chrome)
    build_exam(chrome)
    print("끝났습니다.")
