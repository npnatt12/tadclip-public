#!/usr/bin/env python3
"""Transcribe the WHOLE recording (every take) with whisper word timestamps
and print the segment table: the take map you choose takes from.

    transcribe.py <project>/assets/talk.mp4 --out <project>/build/words.whisper.json \
        [--model turbo] [--lang en] [--raw existing.json] [--backend whisper|mlx] [--mlx-model ~/.cache/mlxw-turbo]

Times are ORIGINAL-recording seconds, the unit reel.json uses. Product names
get mangled; fix them in reel.json -> captions.fixes, not here.
Backends: whisper = the openai-whisper CLI on PATH (or $WHISPER); mlx = mlx_whisper large-v3-turbo (Apple silicon; when
this python lacks mlx_whisper the script re-runs itself in $MLXW_PY or ~/.venvs/mlxw/bin/python). The audio goes in as
16 kHz mono. Both decode anti-merge: no conditioning on previous text (else a retake is merged into one clean
sentence), temperature fallback 0/0.2/0.4 (the CLI cannot cap it: 0..1 in steps of 0.2), no_speech 0.6, compression
ratio 2.2, hallucination_silence_threshold 1.0. The fallback samples: the mlx and python-API paths seed it (repeatable
runs); the whisper CLI cannot be seeded.
Importable: load_words(path) (islands.json / whisper json / flat list -> [{w, a, b, p}]), asr(lang) for the per-piece
transcribers (islands_tx.py, subcheck.py).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

RESTART = re.compile(r"(okay,? again|let me (do|say) that again|one more time|take two|from the top|let's try again|wait,? no)", re.I)
MLXW_PY = os.path.expanduser(os.environ.get("MLXW_PY", "~/.venvs/mlxw/bin/python"))
# Windows (no MLX): faster-whisper, the same large-v3-turbo weights converted for CTranslate2, CPU int8. Thai CER on
# IMG_2260: 1.4 % vs mlx 1.5 % (runs/2026-11-12-release/windows/PORT.md)
FW_PY = os.path.expanduser(os.environ.get("FW_PY", "~/.venvs/fw/Scripts/python.exe" if os.name == "nt" else "~/.venvs/fw/bin/python"))
FW_MODEL = os.environ.get("FW_MODEL", "large-v3-turbo")
# a converted copy in ~/.cache/mlxw-turbo when someone made one, else the Hugging Face repo (setup.sh downloads it at
# install). 11-09: the old default was that folder alone; no fresh install has it, and the first reel crashed mid-run,
# then downloaded 1.5 GB while the user waited.
MLX_REPO = "mlx-community/whisper-large-v3-turbo"
MLX_MODEL = "~/.cache/mlxw-turbo" if os.path.isdir(os.path.expanduser("~/.cache/mlxw-turbo")) else MLX_REPO
ANTI_MERGE = dict(condition_on_previous_text=False, temperature=(0.0, 0.2, 0.4), no_speech_threshold=0.6,
                  compression_ratio_threshold=2.2, hallucination_silence_threshold=1.0)


def find_whisper():
    w = os.environ.get("WHISPER") or shutil.which("whisper")
    if not w:
        sys.exit("whisper not found: pip install openai-whisper (or set WHISPER=/path/to/whisper)")
    return w


def has_mlx():
    try:
        import mlx_whisper  # noqa: F401
        return True
    except ImportError:
        return False


def has_fw():
    try:
        import faster_whisper  # noqa: F401
        return True
    except ImportError:
        return False


def ensure_mlx(script):
    """re-run `script` (same argv) in a python with a Thai engine: mlx_whisper (Mac) or faster-whisper (Windows);
    returns False when there is none"""
    if has_mlx() or has_fw():
        return True
    py = next((p for p in (MLXW_PY, FW_PY) if os.path.exists(p)), None)
    if os.environ.get("_MLXW_REEXEC") or not py:
        return False
    os.environ["_MLXW_REEXEC"] = "1"
    if os.name == "nt":   # Windows' execv starts a new process and the old one exits 0 at once: the caller would read "done"
        sys.exit(subprocess.run([py, os.path.abspath(script)] + sys.argv[1:]).returncode)
    os.execv(py, [py, os.path.abspath(script)] + sys.argv[1:])


def seed(backend, n=0):
    """fix the sampling PRNG: the temperature fallback samples, so unseeded runs differ (one 3-min take: 156, 200, 207 words)"""
    if backend == "mlx":
        import mlx.core as mx
        mx.random.seed(n)
    elif backend == "fw":
        import ctranslate2
        ctranslate2.set_random_seed(n)
    else:
        import torch
        torch.manual_seed(n)


def asr(lang, mlx_model=MLX_MODEL, whisper_model="turbo"):
    """-> (backend name, f(audio path or 16 kHz float32 array, **decode) -> whisper result dict); mlx first"""
    if has_mlx():
        import mlx_whisper
        seed("mlx")
        path = os.path.expanduser(mlx_model)
        return "mlx", lambda x, **kw: mlx_whisper.transcribe(x, path_or_hf_repo=path, language=lang, **kw)
    if has_fw():
        seed("fw")
        return "fw", fw_run(lang)
    import whisper
    seed("whisper")
    m = whisper.load_model(whisper_model)
    return "whisper", lambda x, **kw: m.transcribe(x, language=lang, fp16=False, **kw)


def load_words(path):
    """islands.json ([{a, b, text, words: [{w, a, b, p}]}]), a whisper json ({segments: [{words: [{word, start, end}]}]})
    or a flat [{w|word, a|start, b|end}] list -> [{w, a, b, p}] in time order"""
    d = json.load(open(path))
    if isinstance(d, dict):
        return [{"w": x["word"].strip(), "a": x["start"], "b": x["end"], "p": x.get("probability", 1)}
                for s in d["segments"] for x in s.get("words") or []]
    if d and "words" in d[0]:
        return [{"w": x["w"], "a": x["a"], "b": x["b"], "p": x.get("p", 1)} for i in d for x in i["words"]]
    return [{"w": (x.get("w") or x.get("word", "")).strip(), "a": x.get("a", x.get("start")), "b": x.get("b", x.get("end")),
             "p": x.get("p", x.get("probability", 1))} for x in d]


def read16k(src):
    """16 kHz mono float32 through ffmpeg (newer PyAV breaks faster-whisper's own file decoding)"""
    import numpy as np
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                                        capture_output=True, check=True).stdout, np.float32)


def fw_run(lang, model=FW_MODEL):
    """faster-whisper behind mlx_whisper's call shape: f(audio path or 16 kHz array, **whisper decode options) -> the
    same result dict (text, segments with words), so every caller works unchanged"""
    from faster_whisper import WhisperModel
    # CPU float32 by default: int8 math differs by CPU (FLEURS 40: 12.28-13.27 % on four runners), float32 gave the Mac's
    # words exactly on an AMD runner (12.33 %, all 40 clips identical), ~1.6x int8's time (FW_COMPUTE=int8 to trade back). device="cuda" when an NVIDIA buyer shows up
    m = WhisperModel(model, device="cpu", compute_type=os.environ.get("FW_COMPUTE", "float32"))

    def run(x, word_timestamps=False, condition_on_previous_text=True, temperature=0.0, sample_len=None, initial_prompt=None,
            verbose=None, **kw):
        if isinstance(x, str):
            x = read16k(x)
        o = dict(language=lang, word_timestamps=word_timestamps, condition_on_previous_text=condition_on_previous_text,
                 temperature=list(temperature) if isinstance(temperature, (list, tuple)) else [temperature],
                 initial_prompt=initial_prompt, vad_filter=False, beam_size=5)   # beam 5: what measured 1.4 % CER
        if sample_len:
            o["max_new_tokens"] = min(int(sample_len), 440)   # whisper's 448-token window, less the prompt
        o.update({k: v for k, v in kw.items() if k in ("no_speech_threshold", "compression_ratio_threshold", "hallucination_silence_threshold")})
        segs, info = m.transcribe(x, **o)
        out = [{"start": s.start, "end": s.end, "text": s.text, "no_speech_prob": s.no_speech_prob,
                "words": [{"word": w.word, "start": w.start, "end": w.end, "probability": w.probability} for w in (s.words or [])]} for s in segs]
        return {"text": "".join(s["text"] for s in out), "segments": out, "language": info.language}
    return run


def transcribe(src, model, lang, backend="whisper", mlx_model=MLX_MODEL):
    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "audio.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
        if backend == "mlx":   # "this machine's Thai engine": mlx_whisper on a Mac, faster-whisper on Windows
            return asr(lang, mlx_model)[1](wav, word_timestamps=True, **ANTI_MERGE)
        cmd = [find_whisper(), wav, "--model", model, "--word_timestamps", "True",
               "--output_format", "json", "--output_dir", td, "--fp16", "False",
               "--condition_on_previous_text", "False", "--temperature", "0", "--temperature_increment_on_fallback", "0.2",
               "--no_speech_threshold", "0.6", "--compression_ratio_threshold", "2.2", "--hallucination_silence_threshold", "1.0"]
        if lang:
            cmd += ["--language", lang]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        return json.load(open(os.path.join(td, "audio.json")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="turbo")
    ap.add_argument("--lang", default=None)
    ap.add_argument("--raw", help="reuse an existing whisper json")
    ap.add_argument("--backend", choices=("whisper", "mlx"), default="whisper")
    ap.add_argument("--mlx-model", default=MLX_MODEL, help="mlx_whisper model dir (large-v3-turbo)")
    a = ap.parse_args()
    if a.backend == "mlx" and not a.raw and not ensure_mlx(__file__):
        sys.exit(f"--backend mlx: no mlx_whisper or faster-whisper in this python, {MLXW_PY} or {FW_PY} (set MLXW_PY / FW_PY)")
    data = json.load(open(a.raw)) if a.raw else transcribe(a.src, a.model, a.lang, a.backend, a.mlx_model)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(data, open(a.out, "w"))
    print("\n  start    end   gap  text   (original seconds; * = restart marker)")
    prev = 0.0
    for s in data["segments"]:
        t = s["text"].strip()
        if not t:
            continue
        ws = s.get("words") or []
        st = ws[0]["start"] if ws else s["start"]
        en = ws[-1]["end"] if ws else s["end"]
        mark = "*" if RESTART.search(t) else " "
        print(f"{st:7.2f} {en:7.2f} {st - prev:5.1f} {mark}{t}")
        prev = en
    n = sum(len(s.get("words") or []) for s in data["segments"])
    print(f"\n{n} words -> {a.out}")


if __name__ == "__main__":
    main()
