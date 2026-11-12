#!/usr/bin/env python3
"""TadClip's own sound effects, made by code: no recording, no licence to track. They replace the Mixkit kit, whose
User Terms (cl. 9) forbid collating its Items or fetching them by script, so a sold TadClip can't ship or fetch it.
Every sound is deterministic (seeded): the same file on every machine, so setup can make them instead of downloading.

    sfx_synth.py list                  the sounds this makes
    sfx_synth.py build [--only a,b]    write library/sfx/own-<slug>.wav (48 kHz stereo, peak -1 dBFS) + merge manifest.json
    sfx_synth.py page                  library/sfx/audition-synth.html to listen to them all

Names are the old kit's slugs, so recipes and briefs that ask for "whoosh-1" or "impact-2" keep working.
Dedicated to the public domain (CC0 1.0) like the rest of TadClip's own sound library."""
import argparse
import json
import os
import sys
import wave

import numpy as np
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.abspath(os.path.join(HERE, "..", "library", "sfx"))
SR = 48000
LICENCE = "TadClip original: synthesized by scripts/sfx_synth.py, CC0 1.0 (no recording, no third-party source)"


# ---------- building blocks ----------
def t_(d):
    return np.arange(int(d * SR)) / SR


def rng(seed):
    return np.random.default_rng(seed)


def noise(d, seed, color="white"):
    n = rng(seed).standard_normal(int(d * SR))
    if color == "pink":  # 1/f via a cascade of leaky integrators (Paul Kellet's approximation, simplified)
        b, a = [0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400]
        n = signal.lfilter(b, a, n)
    elif color == "brown":
        n = np.cumsum(n); n -= signal.savgol_filter(n, 4801, 1)
    return n / (np.abs(n).max() + 1e-9)


def env(d, a, r, shape=2.0):
    """attack a s, then a power decay to 0 over the rest"""
    t = t_(d); e = np.ones_like(t)
    ai = int(a * SR)
    if ai: e[:ai] = (t[:ai] / a) ** 0.7
    rest = t[ai:] - a
    e[ai:] = np.clip(1 - rest / max(r, 1e-6), 0, 1) ** shape
    return e


def bell_env(d, peak):
    """swell to peak (0..1 of d) and back: a whoosh's shape"""
    t = t_(d) / d
    up = np.clip(t / peak, 0, 1) ** 2
    down = np.clip((1 - t) / (1 - peak), 0, 1) ** 1.6
    return np.minimum(up, down)


def sweep_bp(x, f0, f1, q=1.2, curve=1.0):
    """band-pass whose centre glides f0 -> f1 (log), processed in 5 ms blocks"""
    out = np.zeros_like(x); blk = 240; zi = None
    n = len(x)
    for i in range(0, n, blk):
        p = (i / n) ** curve
        fc = f0 * (f1 / f0) ** p
        lo, hi = fc / (1 + 1 / (2 * q)), min(fc * (1 + 1 / (2 * q)), SR / 2 - 100)
        sos = signal.butter(2, [lo, hi], btype="band", fs=SR, output="sos")
        if zi is None: zi = signal.sosfilt_zi(sos) * 0
        out[i:i + blk], zi = signal.sosfilt(sos, x[i:i + blk], zi=zi)
    return out


def lp(x, fc, order=4):
    return signal.sosfilt(signal.butter(order, fc, fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, btype="high", fs=SR, output="sos"), x)


def osc(freq, d, kind="sine", phase=0.0):
    """freq: number or per-sample array"""
    f = np.full(int(d * SR), float(freq)) if np.isscalar(freq) else freq
    ph = 2 * np.pi * np.cumsum(f) / SR + phase
    if kind == "sine": return np.sin(ph)
    if kind == "saw": return 2 * ((ph / (2 * np.pi)) % 1) - 1
    if kind == "square": return np.sign(np.sin(ph))
    if kind == "tri": return 2 * np.abs(2 * ((ph / (2 * np.pi)) % 1) - 1) - 1
    raise ValueError(kind)


def glide(f0, f1, d, curve=1.0):
    p = np.linspace(0, 1, int(d * SR)) ** curve
    return f0 * (f1 / f0) ** p


def fm_bell(f, d, ratio=2.76, index=3.0, decay=1.2, seed=0):
    t = t_(d)
    m = np.sin(2 * np.pi * f * ratio * t) * index * np.exp(-t * 3 / decay)
    return np.sin(2 * np.pi * f * t + m) * np.exp(-t * 3 / decay)


def reverb(x, size=1.2, mix=0.25, seed=7):
    """convolution with a decaying stereo noise tail"""
    n = int(size * SR); t = np.arange(n) / SR
    irs = [noise(size, seed + k) * np.exp(-t * 6 / size) for k in (0, 1)]
    irs = [lp(ir, 6000) for ir in irs]
    L = len(x) + n
    wet = [np.pad(c, (0, max(0, L - len(c))))[:L] for c in (signal.fftconvolve(x, ir) for ir in irs)]
    dry = np.pad(x, (0, n))
    w = np.stack(wet); w /= np.abs(w).max() + 1e-9
    return np.stack([dry, dry]) * (1 - mix) + w * mix


def pan(x, p):
    """mono -> stereo; p: -1..1 or per-sample array"""
    p = np.clip(p, -1, 1); a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)])


def stereo(x):
    return x if x.ndim == 2 else np.stack([x, x])


def seq(parts, d):
    """[(start s, stereo or mono array), ...] mixed into d seconds"""
    out = np.zeros((2, int(d * SR)))
    for at, x in parts:
        x = stereo(x); i = int(at * SR); j = min(out.shape[1], i + x.shape[1])
        out[:, i:j] += x[:, : j - i]
    return out


def crush(x, bits=6, hold=4):
    q = 2 ** (bits - 1); y = np.round(x * q) / q
    return np.repeat(y[::hold], hold)[: len(x)]


def kick(f0=120, f1=40, d=0.5, seed=0):
    t = t_(d); f = glide(f0, f1, d, 0.25)
    return osc(f, d) * np.exp(-t * 7) + 0.3 * noise(d, seed) * np.exp(-t * 60)


def snare(d=0.25, seed=0, tone=190):
    t = t_(d)
    return 0.6 * hp(noise(d, seed), 1500) * np.exp(-t * 22) + 0.5 * osc(tone, d) * np.exp(-t * 30)


def cymbal(d=1.5, seed=0):
    t = t_(d); x = hp(noise(d, seed), 6000)
    for f in (3150, 4870, 6210, 7720):
        x += 0.15 * osc(f, d, "square")
    return hp(x, 5000) * np.exp(-t * 3.2 / d * 2)


def click(d=0.03, seed=0, fc=3000):
    t = t_(d)
    return sweep_bp(noise(d, seed), fc, fc * 0.8, q=3) * np.exp(-t * 180) * 3


# ---------- the sounds ----------
def whoosh(d, f0, f1, peak, q=1.0, seed=1, low=0.0, pan_sweep=0.8):
    x = sweep_bp(noise(d, seed, "pink"), f0, f1, q=q) * bell_env(d, peak)
    if low: x += low * osc(glide(f0 / 4, f1 / 4, d), d) * bell_env(d, peak)
    return pan(x, np.linspace(-pan_sweep, pan_sweep, len(x)))


def riser(d, seed, f0=150, f1=1800, tone=True):
    t = t_(d); e = (t / d) ** 2.2
    x = sweep_bp(noise(d, seed, "pink"), 400, 8000, q=0.8, curve=2) * e
    if tone:
        f = glide(f0, f1, d, 2.2)
        x += 0.35 * lp(osc(f, d, "saw") + osc(f * 1.01, d, "saw"), 5000) * e
    x[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
    return stereo(x)


def boom(d, seed, f0=90, f1=30, bright=0.4, rv=1.5):
    t = t_(d)
    sub = osc(glide(f0, f1, d, 0.35), d) * np.exp(-t * 2.2)
    hit = bright * lp(noise(d, seed), 2500) * np.exp(-t * 25)
    return reverb(sub + hit, rv, 0.3, seed)[:, : int(d * SR)]


def cine_hit(d, seed):
    t = t_(d)
    metal = fm_bell(110, d, 3.41, 6, 0.9) * 0.5 + fm_bell(73, d, 2.01, 4, 1.2) * 0.4
    x = boom(d, seed, 70, 28, 0.7, 2.0) + stereo(metal * np.exp(-t * 1.5))
    return x


def heartbeat(seed):
    def thump(f):
        dd = 0.18; tt = t_(dd)
        return lp(osc(glide(f, f * 0.7, dd), dd) * np.exp(-tt * 22), 200)
    return seq([(0.0, thump(60)), (0.2, 0.8 * thump(50))], 0.455)


def glitch(d, seed, sweep=False):
    r = rng(seed); out = np.zeros(int(d * SR)); i = 0
    while i < len(out):
        n = int(r.uniform(0.01, 0.05) * SR)
        f = r.uniform(80, 2500)
        if sweep: f *= 1 + 2 * i / len(out)
        seg = r.choice([0, 1, 2])
        tt = np.arange(min(n, len(out) - i)) / SR
        x = [np.sign(np.sin(2 * np.pi * f * tt)), r.standard_normal(len(tt)), np.sin(2 * np.pi * f * tt)][seg]
        out[i:i + len(tt)] = x * r.uniform(0.3, 1) * (r.random() > 0.15)
        i += len(tt)
    return pan(crush(out, 5, 6), rng(seed + 1).uniform(-0.5, 0.5, 1)[0])


def buzzer():
    d = 1.2; t = t_(d)
    x = osc(110 * (1 + 0.004 * np.sin(2 * np.pi * 6 * t)), d, "square") + osc(116.5, d, "square")
    return stereo(lp(x, 1800) * env(d, 0.01, 1.19, 0.4))


def chime(notes, gap, d, seed=0, dec=0.9, ratio=3.5, idx=1.2):
    return seq([(i * gap, 0.7 * fm_bell(f, d - i * gap, ratio, idx, dec)) for i, f in enumerate(notes)], d)


def kaching(seed):
    d = 0.726
    mech = click(0.04, seed, 1800) * 1.5
    coins = [(0.08 + k * 0.045, 0.35 * fm_bell(f, 0.5, 1.41, 2.5, 0.25)) for k, f in enumerate([2600, 3150, 2880, 3500, 2950, 3320])]
    return seq([(0.0, mech), (0.05, 0.6 * fm_bell(1760, 0.6, 2.0, 1.5, 0.6))] + coins, d)


def shutter(seed, whine=False):
    d = 0.444 if not whine else 0.347
    parts = [(0.0, click(0.05, seed, 2500) * 1.2), (0.09 if not whine else 0.05, click(0.06, seed + 1, 1600))]
    if whine:
        parts.append((0.1, 0.2 * osc(glide(2000, 9000, 0.24), 0.24) * np.linspace(1, 0, int(0.24 * SR))))
    return seq(parts, d)


def typing(d, rate, seed):
    r = rng(seed); parts = []; at = 0.02
    while at < d - 0.06:
        parts.append((at, click(0.035, int(r.integers(1e6)), r.uniform(1800, 3800)) * r.uniform(0.5, 1)))
        at += r.exponential(1 / rate) + 0.02
    return seq(parts, d)


def boing():
    d = 0.487; t = t_(d)
    f = 220 * (1 + 0.5 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 6)) * glide(1.4, 1.0, d)
    return stereo(osc(f, d) * env(d, 0.005, d, 1.2) + 0.3 * osc(f * 2, d, "tri") * env(d, 0.005, d, 2))


def slide_whistle():
    d = 2.0; t = t_(d)
    f = glide(1800, 300, d, 0.8) * (1 + 0.012 * np.sin(2 * np.pi * 5.5 * t))
    x = osc(f, d) + 0.08 * lp(noise(d, 3), 3000)
    return stereo(x * env(d, 0.03, 1.97, 0.6))


def drum_roll(seed):
    d = 3.0; parts = []; at = 0.0; k = 0
    while at < 2.45:
        parts.append((at, snare(0.12, seed + k, 200) * (0.25 + 0.6 * at / 2.45)))
        at += 0.045; k += 1
    parts += [(2.5, snare(0.3, seed + 999) * 1.2), (2.5, kick(110, 45, 0.5)), (2.5, 0.6 * cymbal(0.5, seed))]
    return seq(parts, d)


def rimshot(seed):
    d = 1.841
    tom = lambda f: (lambda tt: osc(glide(f, f * 0.8, 0.3), 0.3) * np.exp(-tt * 12))(t_(0.3))
    return seq([(0.0, 0.8 * tom(180)), (0.16, 0.8 * tom(130)), (0.42, snare(0.15, seed)), (0.42, 0.7 * cymbal(1.4, seed))], d)


def fail_trombone():
    """wah wah wah waaah: a saw through a mouth-like low-pass that opens and closes on each note"""
    notes = [(0.0, 0.5, 311), (0.55, 0.5, 293), (1.1, 0.5, 277), (1.65, 1.3, 262)]
    d = 3.0; out = np.zeros(int(d * SR))
    for at, dd, f in notes:
        t = t_(dd); vib = 1 + (0.02 * np.sin(2 * np.pi * 5 * t) if dd > 1 else 0)
        x = osc(f * vib * glide(1.02, 0.97, dd), dd, "saw")
        wah = 500 + 1600 * np.sin(np.pi * np.clip(t / min(dd, 0.45), 0, 1)) ** 2
        y = np.zeros_like(x)
        for i in range(0, len(x), 240):
            sos = signal.butter(2, wah[i], fs=SR, output="sos"); y[i:i + 240] = signal.sosfilt(sos, x[i:i + 240])
        y *= env(dd, 0.04, dd - 0.04, 0.5)
        i = int(at * SR); out[i:i + len(y)] += y[: len(out) - i]
    return stereo(out)


def tape_rewind():
    d = 1.5; t = t_(d)
    f = glide(400, 3200, d, 0.6) * (1 + 0.08 * np.sin(2 * np.pi * 23 * t))
    x = 0.5 * osc(f, d, "tri") + 0.5 * sweep_bp(noise(d, 11), 800, 6000, q=2)
    return stereo(x * env(d, 0.05, d - 0.05, 0.3))


def cartoon_pop(seed):
    d = 0.6
    pop = (lambda tt: osc(glide(300, 1400, 0.06), 0.06) * np.exp(-tt * 40))(t_(0.06))
    sparkle = [(0.06 + k * 0.05, 0.25 * fm_bell(f, 0.3, 2.0, 1.0, 0.2)) for k, f in enumerate([2093, 2637, 3136, 4186])]
    return seq([(0, pop)] + sparkle, d)


def bubble_pop(f=500, d=0.14):
    t = t_(d)
    return stereo(osc(glide(f, f * 2.6, d, 0.5), d) * np.exp(-t * 35))


def applause(d, seed, density=60):
    r = rng(seed); parts = []
    for k in range(int(d * density)):
        at = r.uniform(0, d - 0.05)
        c = sweep_bp(noise(0.03, int(r.integers(1e6))), r.uniform(900, 2400), r.uniform(700, 2000), q=1.5)
        parts.append((at, pan(c * np.exp(-t_(0.03) * 120) * r.uniform(0.2, 0.6), r.uniform(-0.8, 0.8))))
    x = seq(parts, d)
    return x * env(d, 0.15, d - 0.15, 0.8)


def alarm_bell():
    d = 3.5; parts = []; at = 0.0; k = 0
    while at < 3.2:
        parts.append((at, pan(0.5 * fm_bell(1320 if k % 2 else 1180, 0.25, 2.4, 2.0, 0.3), -0.3 if k % 2 else 0.3)))
        at += 1 / 18; k += 1
    return seq(parts, d)


def scribble(d, seed, strokes, f=(2500, 5500), tone=0.0):
    r = rng(seed); parts = []; at = 0.0
    while at < d - 0.05:
        sd = r.uniform(0.06, 0.18)
        x = sweep_bp(noise(sd, int(r.integers(1e6))), r.uniform(*f), r.uniform(*f), q=1.6) * bell_env(sd, 0.3)
        if tone: x += tone * osc(r.uniform(1800, 2600), sd) * bell_env(sd, 0.3)
        parts.append((at, x * r.uniform(0.5, 1))); at += sd + r.uniform(0.0, d / strokes)
    return seq(parts, d)


def saw_strokes(d, seed):
    r = rng(seed); parts = []; at = 0.0; k = 0
    while at < d - 0.2:
        sd = 0.28
        x = sweep_bp(noise(sd, seed + k), 1200 if k % 2 else 900, 2200 if k % 2 else 1600, q=1.4) * bell_env(sd, 0.5)
        x += 0.3 * lp(osc(r.uniform(90, 130), sd, "saw"), 600) * bell_env(sd, 0.5)
        parts.append((at, x)); at += 0.3; k += 1
    return seq(parts, d)


def wood_knock(seed, d=0.235):
    t = t_(d)
    modes = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * dec) for f, a, dec in [(420, 1, 45), (1130, 0.6, 70), (2310, 0.35, 110)])
    tap = np.pad(0.4 * click(0.01, seed, 2200), (0, len(t) - int(0.01 * SR)))
    return stereo(modes + tap)


def workshop_room(d, seed):
    base = 0.25 * lp(noise(d, seed, "brown"), 400) + 0.03 * lp(noise(d, seed + 1, "pink"), 3000)
    r = rng(seed); parts = [(0, stereo(base))]
    for k in range(int(d / 2.2)):
        parts.append((r.uniform(0.5, d - 0.4), pan(0.35 * wood_knock(seed + k)[0], r.uniform(-0.6, 0.6))))
    return seq(parts, d)


def sanding(d, seed):
    t = t_(d)
    stroke = 0.5 + 0.5 * np.sin(2 * np.pi * 2.2 * t) ** 2
    return stereo(sweep_bp(noise(d, seed, "pink"), 1800, 2600, q=0.7) * stroke * env(d, 0.1, d - 0.1, 0.5))


def notification():
    return seq([(0, 0.8 * fm_bell(1568, 0.2, 2.0, 0.8, 0.2)), (0.1, 0.8 * fm_bell(2093, 0.3, 2.0, 0.8, 0.25))], 0.405)


def ui_error():
    d = 0.358
    b = lambda f: (lambda tt: lp(osc(f, 0.13, "square"), 2500) * env(0.13, 0.003, 0.127, 0.8))(t_(0.13))
    return seq([(0.0, 0.6 * b(440)), (0.15, 0.6 * b(330))], d)


S = {
    "whoosh-1": ("whoosh", ["zoom", "transition", "card-in"], "airy noise sweep, left to right", lambda: whoosh(0.9, 400, 3500, 0.55, 1.0, 1)),
    "whoosh-2": ("whoosh", ["zoom", "transition", "card-in"], "deep cinematic sweep with a low tone", lambda: whoosh(0.9, 180, 1500, 0.6, 0.8, 2, low=0.35)),
    "whoosh-3": ("whoosh", ["zoom", "transition", "card-in"], "fast sweep, quick attack", lambda: whoosh(0.9, 600, 5000, 0.3, 1.3, 3)),
    "whoosh-cine": ("whoosh", ["text-slam", "reveal"], "short arrow pass", lambda: whoosh(0.313, 1500, 7000, 0.6, 1.6, 4, pan_sweep=1)),
    "pop-1": ("ui", ["chip", "emoji", "list-item"], "bubble pop", lambda: bubble_pop(480, 0.2)),
    "pop-2": ("ui", ["chip", "emoji", "list-item"], "tiny message pop", lambda: bubble_pop(900, 0.05)),
    "pop-3": ("ui", ["chip", "emoji", "list-item"], "hard pop click", lambda: bubble_pop(650, 0.14) + stereo(np.pad(click(0.02, 5, 3000), (0, int(0.12 * SR))))),
    "click-1": ("ui", ["ui", "cursor"], "soft UI click", lambda: stereo(np.pad(click(0.04, 6, 2600), (0, int(0.21 * SR))))),
    "tick-1": ("ui", ["typing"], "single key tick", lambda: stereo(np.pad(click(0.03, 7, 3400), (0, int(0.17 * SR))))),
    "typing-1": ("ui", ["typing", "prompt"], "slow typing", lambda: typing(2.5, 7, 8)),
    "tech-keyboard-burst": ("ui", ["typing", "prompt", "code"], "fast keyboard burst", lambda: typing(2.0, 16, 9)),
    "impact-1": ("impact", ["text-slam", "number", "stamp"], "trailer boom with a tail", lambda: boom(1.6, 10, 95, 32, 0.6, 1.4)),
    "impact-2": ("impact", ["text-slam", "number", "stamp"], "big hit, brighter", lambda: boom(1.2, 11, 120, 38, 0.9, 1.0)),
    "cinematic-deep-boom": ("impact", ["text-slam", "reveal", "number"], "deep boom, long tail", lambda: boom(2.5, 12, 70, 25, 0.35, 2.2)),
    "cinematic-cine-hit": ("impact", ["title", "stamp", "reveal"], "layered metallic trailer hit", lambda: cine_hit(2.0, 13)),
    "cinematic-heartbeat": ("impact", ["tension", "pause", "stakes"], "one heartbeat (lub-dub)", lambda: heartbeat(14)),
    "riser-1": ("whoosh", ["build-up"], "noise and saw riser", lambda: riser(1.705, 15)),
    "cinematic-rumble-riser": ("whoosh", ["build-up", "tension"], "low rumble rising", lambda: riser(3.0, 16, 50, 600) + stereo(0.4 * lp(noise(3.0, 17, "brown"), 200) * (t_(3.0) / 3.0))),
    "cinematic-drone-swell": ("whoosh", ["tension", "bed", "reveal"], "detuned drone that opens and swells",
                              lambda: stereo(lp(sum(osc(f * k, 4.0, "saw") for f in (55, 55.4, 82.4) for k in (1,)), 900) * bell_env(4.0, 0.7) * 0.6)),
    "cinematic-film-flash": ("whoosh", ["flash", "cut", "transition"], "reverse swell into a short hit",
                             lambda: seq([(0, whoosh(0.7, 300, 6000, 0.97, 1.0, 18)), (0.7, boom(0.3, 19, 160, 60, 1.0, 0.3))], 1.0)),
    "tech-glitch-1": ("ui", ["glitch", "cut", "error"], "digital stutter", lambda: glitch(0.688, 20)),
    "tech-glitch-2": ("whoosh", ["glitch", "transition"], "glitch that sweeps up", lambda: glitch(0.585, 21, sweep=True)),
    "tech-digital-whoosh": ("whoosh", ["zoom", "transition", "tech"], "bit-crushed sweep with a saw", lambda: np.stack([crush(c, 7, 3) for c in whoosh(1.2, 300, 4000, 0.5, 1.1, 22, low=0.3)])),
    "send-swoosh": ("ui", ["send", "message", "imessage", "swoosh"], "bright upward swoosh", lambda: whoosh(0.639, 800, 6000, 0.35, 1.4, 23)),
    "ding-1": ("ui", ["win", "check"], "bell ding", lambda: chime([1760], 0, 0.885, dec=0.8, ratio=3.5, idx=1.5)),
    "reaction-ding-ding": ("meme", ["correct", "idea", "win"], "service bell, twice", lambda: chime([2349, 2349], 0.35, 0.875, dec=0.4, ratio=2.76, idx=3)),
    "tech-ui-confirm": ("ui", ["check", "win", "done"], "two-note confirm chime", lambda: chime([1047, 1568], 0.12, 1.0, dec=0.6, ratio=2.0, idx=0.8)),
    "tech-notification-2": ("ui", ["notification", "chip", "alert"], "high double blip", notification),
    "tech-ui-error": ("ui", ["wrong", "myth", "reject"], "two falling square blips", ui_error),
    "buzzer-1": ("meme", ["wrong", "dismiss", "myth"], "game-show wrong buzzer", buzzer),
    "kaching-1": ("impact", ["money", "price", "win"], "register click, bell and coins", lambda: kaching(24)),
    "shutter-1": ("ui", ["screenshot", "save", "freeze"], "camera shutter", lambda: shutter(25)),
    "tech-camera-flash": ("ui", ["screenshot", "flash", "freeze"], "shutter with a flash whine", lambda: shutter(26, whine=True)),
    "reaction-boing": ("meme", ["absurd", "bounce", "flex"], "spring boing", boing),
    "reaction-rimshot": ("meme", ["punchline", "bad-joke"], "ba-dum-tss", lambda: rimshot(27)),
    "reaction-fail-trombone": ("meme", ["fail", "sad", "pity"], "wah wah wah waaah", fail_trombone),
    "reaction-drum-roll": ("meme", ["build-up", "reveal", "suspense"], "snare roll to a hit", lambda: drum_roll(28)),
    "reaction-applause-short": ("meme", ["win", "flex", "sarcastic"], "small group applause", lambda: applause(3.0, 29)),
    "reaction-tape-rewind": ("meme", ["wait", "freeze-frame", "twist"], "tape rewind squeal", tape_rewind),
    "reaction-cartoon-pop": ("meme", ["emoji", "idea", "light"], "pop with a sparkle", lambda: cartoon_pop(30)),
    "reaction-slide-whistle": ("meme", ["fail", "drop", "falling"], "slide whistle down", slide_whistle),
    "alarm-bell": ("foley", ["alarm", "clock", "wake-up", "ring"], "twin-bell alarm clock", alarm_bell),
    "marker-scribble": ("foley", ["whiteboard", "write", "draw", "doodle"], "felt marker strokes", lambda: scribble(0.543, 31, 3, (2000, 4500))),
    "pencil-write": ("foley", ["whiteboard", "write", "notebook"], "pencil on paper", lambda: scribble(1.866, 32, 10, (3500, 7000))),
    "wood-hit": ("impact", ["craft", "wood", "turn", "hit"], "wood knock", lambda: wood_knock(33)),
    "wood-saw": ("foley", ["craft", "wood", "workshop"], "hand saw strokes", lambda: saw_strokes(1.2, 34)),
    "wood-sanding": ("foley", ["craft", "wood", "workshop"], "sanding strokes", lambda: sanding(4.0, 35)),
    "wood-ambience": ("ambience", ["craft", "workshop", "room-tone"], "workshop room tone, a few knocks", lambda: workshop_room(14.0, 36)),
}


def finish(x, fade=0.01):
    x = stereo(np.asarray(x, dtype=np.float64))
    x = x - x.mean(axis=1, keepdims=True)
    n = int(fade * SR)
    if x.shape[1] > n: x[:, -n:] *= np.linspace(1, 0, n)
    pk = np.abs(x).max()
    return x * (10 ** (-1 / 20) / pk) if pk > 0 else x


def write_wav(path, x):
    y = (np.clip(x.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes())


def build(only):
    os.makedirs(SFX, exist_ok=True)
    mp = os.path.join(SFX, "manifest.json")
    man = json.load(open(mp)) if os.path.exists(mp) else {}
    for slug, (role, tags, what, fn) in S.items():
        if only and slug not in only: continue
        x = finish(fn())
        write_wav(os.path.join(SFX, f"own-{slug}.wav"), x)
        man[slug] = {"file": f"own-{slug}.wav", "role": role, "tags": tags, "duration": round(x.shape[1] / SR, 3), "peak_db": -1.0,
                     "source": f"scripts/sfx_synth.py: {what}", "licence": LICENCE, "licensed": True, "synth": True}
        print(f"ok  {slug:<26} {x.shape[1] / SR:5.2f}s  {what}")
    json.dump(man, open(mp, "w"), indent=2, ensure_ascii=False)


def page():
    rows = "".join(f'<tr><td>{s}</td><td>{S[s][0]}</td><td>{S[s][2]}</td><td><audio controls preload="none" src="own-{s}.wav"></audio></td></tr>' for s in S)
    p = os.path.join(SFX, "audition-synth.html")
    open(p, "w").write(f"<!doctype html><meta charset=utf-8><title>TadClip synth SFX</title><style>body{{font:14px system-ui;margin:24px}}td{{padding:4px 10px}}</style>"
                      f"<h2>TadClip's own sounds ({len(S)})</h2><table>{rows}</table>")
    print(p)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list"); b = sub.add_parser("build"); b.add_argument("--only", default=""); sub.add_parser("page")
    a = ap.parse_args()
    if a.cmd == "list":
        for s, (role, tags, what, _) in S.items(): print(f"{s:<26} {role:<8} {what}")
    elif a.cmd == "build":
        build(set(filter(None, a.only.split(","))))
    else:
        page()
