"""Text in images, the same on a Mac and on Windows: macOS Vision (ocr_text.js through osascript) or Windows' own OCR
(ocr_text.ps1, Windows.Media.Ocr). Used by own_brand.py (brand sheets' colour codes), broll_qa.py (captions burned into
stock) and format_spec.py (text zones).
    ocr.lines(paths, langs="th-TH,en-US") -> {path: {"img", "w", "h", "lines": [{"text", "conf", "box": [x, y, w, h]}]}}
None when this machine has no OCR (Linux), so a caller can say so instead of reading "no text"."""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def available():
    return sys.platform in ("darwin", "win32")


def lines(paths, langs=None, timeout=900):
    if not available():
        return None
    env = {**os.environ, **({"OCR_LANGS": langs} if langs else {})}
    out = {}
    for i in range(0, len(paths), 40):
        chunk = list(paths[i:i + 40])
        if sys.platform == "darwin":
            cmd = ["osascript", "-l", "JavaScript", os.path.join(HERE, "ocr_text.js"), *chunk]
        else:
            cmd = ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", os.path.join(HERE, "ocr_text.ps1"), *chunk]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, env=env)
        except (OSError, subprocess.TimeoutExpired) as e:
            r = subprocess.CompletedProcess(cmd, 1, "", str(e))
        for ln in r.stdout.splitlines():
            ln = ln.strip().lstrip("﻿")
            if not ln.startswith("{"):
                continue
            try:
                j = json.loads(ln); out[j["img"]] = j
            except (json.JSONDecodeError, KeyError):
                pass
        for p in chunk:   # an image the OCR never answered for: say why, instead of "no text"
            out.setdefault(p, {"img": p, "lines": [], "error": (r.stderr or "no output").strip()[-300:]})
    return out


if __name__ == "__main__":   # python3 scripts/ocr.py img... : what this machine reads
    for p, j in (lines(sys.argv[1:], os.environ.get("OCR_LANGS", "th-TH,en-US")) or {}).items():
        print(p, json.dumps([x["text"] for x in j.get("lines", [])], ensure_ascii=False), j.get("error", ""))
