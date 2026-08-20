# -*- coding: utf-8 -*-
"""판 올리고 → PDF 다시 만들고 → 업로드 폴더까지 준비하는 한 번에 도구.

    python tools/release.py          판을 1 올린다 (v2 → v3)
    python tools/release.py 5        판을 5 로 지정한다
    python tools/release.py --show   지금 판만 본다

끝나면 `2_깃허브_업로드용` 폴더를 그대로 깃허브에 올리면 된다.
"""
import io, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 1_작업폴더
UPLOAD = os.path.join(os.path.dirname(ROOT), "2_깃허브_업로드용")
PY = sys.executable

COPY_FILES = ["index.html", "textbook.html", "exam.html",
              "manifest.webmanifest", "sw.js", "README.md", ".gitignore"]
COPY_DIRS = ["icons", "tools"]

def run(script, args=()):
    # 하위 도구도 UTF-8 로 내보내게 맞춘다(안 맞추면 한글이 깨져 보인다)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([PY, os.path.join(ROOT, "tools", script), *args],
                       cwd=ROOT, capture_output=True, text=True,
                       encoding='utf-8', errors='replace', env=env)
    if r.stdout: print("   " + r.stdout.strip().replace("\n", "\n   "))
    if r.returncode != 0:
        print("   [!] 실패:", (r.stderr or "").strip()[:400])
    return r.returncode == 0

def refresh_upload():
    if os.path.isdir(UPLOAD):
        shutil.rmtree(UPLOAD, ignore_errors=True)
    os.makedirs(UPLOAD, exist_ok=True)
    n = 0
    for f in COPY_FILES:
        src = os.path.join(ROOT, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(UPLOAD, f)); n += 1
    for d in COPY_DIRS:
        src = os.path.join(ROOT, d)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(UPLOAD, d),
                            ignore=shutil.ignore_patterns('__pycache__'))
            n += sum(len(fs) for _, _, fs in os.walk(os.path.join(UPLOAD, d)))
    for f in os.listdir(ROOT):
        if f.lower().endswith(".pdf"):
            shutil.copy2(os.path.join(ROOT, f), os.path.join(UPLOAD, f)); n += 1
    return n

if __name__ == "__main__":
    if "--show" in sys.argv:
        run("set_version.py", ["--show"]); sys.exit()

    print("\n============================================")
    print("  정처기 교재 · 새 판 준비")
    print("============================================\n")

    print("[1/3] 판 올리는 중...")
    if not run("set_version.py", [a for a in sys.argv[1:] if a.isdigit()]):
        sys.exit("중단했습니다.")

    print("\n[2/3] 인쇄용 PDF 다시 만드는 중... (30초쯤 걸립니다)")
    run("build.py")

    print("\n[3/3] 업로드 폴더 준비 중...")
    cnt = refresh_upload()
    print("   파일 %d개 준비 완료" % cnt)

    print("\n============================================")
    print("  다 됐습니다!")
    print()
    print("  이제 아래 폴더를 통째로 깃허브에 올리세요")
    print("   ", UPLOAD)
    print()
    print("  올리는 곳")
    print("    https://github.com/kaya1914-blip/-jeongcheogi/upload/main")
    print("============================================\n")
