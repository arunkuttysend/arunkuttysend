#!/usr/bin/env python3
"""Render the profile's static-but-animated SVG assets (dark + light variants).

Usage:
    python3 scripts/build_assets.py            # writes ./assets/*.svg

The output is deterministic: re-running with unchanged code produces
byte-identical files, so git diffs only show intentional changes.
"""
from __future__ import annotations

import logging
import math
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svgkit import MONO, SANS, THEMES, Theme, discrete_anim, esc, fmt, svg_doc  # noqa: E402

log = logging.getLogger("build_assets")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

Segment = tuple[str, str]  # (text, theme colour attribute name)


# --------------------------------------------------------------------------- #
# Hero banner
# --------------------------------------------------------------------------- #
HERO_PHRASES = (
    "building Sendpilots — AI-native outreach platform",
    "tuning MTAs: Postal · Postfix · Haraka · PowerMTA · KumoMTA",
    "enforcing SPF · DKIM · DMARC · BIMI · ARC · MTA-STS",
    "shipping Laravel · FastAPI · Next.js · Nuxt · Docker",
)
TICKER = (
    "220 ESMTP ready  ·  EHLO  ·  STARTTLS  ·  TLSv1.3  ·  MAIL FROM  ·  RCPT TO  ·  DATA  ·  "
    "250 2.0.0 OK queued  ·  spf=pass  ·  dkim=pass  ·  dmarc=pass  ·  arc=pass  ·  BIMI  ·  "
    "MTA-STS enforce  ·  TLS-RPT  ·  FBL processed  ·  bounce → suppress  ·  "
)


def hero(t: Theme) -> str:
    W, H = 1200, 380
    fs, cw = 17, 17 * 0.6            # typing line font size / fixed char advance
    tx, ty = 86, 246                 # typing text origin (after the "$ ")
    slot, type_s, hold_s = 4.0, 1.5, 1.9
    cycle = slot * len(HERO_PHRASES)

    # --- typing phrases: clip width steps char-by-char, cursor follows ---
    phrases, cursor_frames = [], [(0.0, tx)]
    for k, phrase in enumerate(HERO_PHRASES):
        n, start = len(phrase), k * slot
        frames = [(0.0, 0.0), (start, 0.0)]
        for i in range(1, n + 1):
            ts = start + type_s * i / n
            frames.append((ts, i * cw))
            cursor_frames.append((ts, tx + i * cw))
        frames += [(start + type_s + hold_s, 0.0)]
        cursor_frames.append((start + type_s + hold_s, tx))
        clip_id = f"ph{k}"
        phrases.append(
            f'<clipPath id="{clip_id}"><rect x="{tx}" y="{ty - 18}" height="26" width="0">'
            f'{discrete_anim("width", frames, cycle)}</rect></clipPath>'
            f'<text x="{tx}" y="{ty}" clip-path="url(#{clip_id})" font-family="{MONO}" font-size="{fs}" '
            f'fill="{t.green}" textLength="{fmt(n * cw)}" lengthAdjust="spacing">{esc(phrase)}</text>'
        )
    cursor = (
        f'<rect class="blink" y="{ty - 15}" width="{fmt(cw)}" height="19" rx="1" fill="{t.green}" x="{tx}">'
        f'{discrete_anim("x", cursor_frames, cycle)}</rect>'
    )

    # --- right side: API -> MTA hub -> ISP fan-out with moving packets ---
    hub_x, hub_y = 905, 172
    isps = (("Gmail", 78, t.red), ("Outlook", 142, t.blue), ("Yahoo", 206, t.purple), ("iCloud", 270, t.text))
    net = [
        f'<path id="p_api" d="M797 {hub_y} L869 {hub_y}" class="flow" stroke="{t.muted}" stroke-opacity=".55"/>',
        f'<rect x="723" y="{hub_y - 17}" width="74" height="34" rx="8" fill="{t.panel}" stroke="{t.border}"/>',
        f'<text x="760" y="{hub_y + 5}" text-anchor="middle" font-family="{MONO}" font-size="13" '
        f'font-weight="700" fill="{t.muted}">API</text>',
    ]
    for i, (name, y, color) in enumerate(isps):
        pid = f"p_isp{i}"
        net.append(
            f'<path id="{pid}" d="M941 {hub_y} C990 {hub_y}, 985 {y}, 1037 {y}" class="flow" stroke="{t.muted}" stroke-opacity=".55"/>'
            f'<rect x="1037" y="{y - 15}" width="104" height="30" rx="15" fill="{t.panel}" stroke="{t.border}"/>'
            f'<circle cx="1055" cy="{y}" r="4" fill="{color}"/>'
            f'<text x="1098" y="{y + 5}" text-anchor="middle" font-family="{SANS}" font-size="13" '
            f'font-weight="600" fill="{t.text}">{name}</text>'
        )
        for j in range(2):
            net.append(
                f'<circle r="3.6" fill="{color}" filter="url(#glow)" opacity="0">'
                f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="2.4s" '
                f'begin="-{fmt(0.3 * i + 1.2 * j)}s" repeatCount="indefinite"/>'
                f'<animateMotion dur="2.4s" begin="-{fmt(0.3 * i + 1.2 * j)}s" repeatCount="indefinite">'
                f'<mpath href="#{pid}"/></animateMotion></circle>'
            )
    net.append(
        f'<circle r="3.6" fill="{t.green}" filter="url(#glow)"><animateMotion dur="0.8s" repeatCount="indefinite">'
        f'<mpath href="#p_api"/></animateMotion></circle>'
    )
    for d in (0, 1.2):
        net.append(
            f'<circle cx="{hub_x}" cy="{hub_y}" r="36" fill="none" stroke="{t.blue}" stroke-width="1.5">'
            f'<animate attributeName="r" values="36;78" dur="2.4s" begin="{d}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".7;0" dur="2.4s" begin="{d}s" repeatCount="indefinite"/></circle>'
        )
    net.append(
        f'<circle cx="{hub_x}" cy="{hub_y}" r="36" fill="{t.panel}" stroke="url(#nameGrad)" stroke-width="2.5"/>'
        f'<text x="{hub_x}" y="{hub_y + 6}" text-anchor="middle" font-family="{MONO}" font-size="17" '
        f'font-weight="800" fill="{t.text}">MTA</text>'
    )

    # --- auth chips that light up in sequence ---
    chips, cx = [], 64
    for i, (label, color) in enumerate((("SPF pass", t.green), ("DKIM pass", t.green),
                                         ("DMARC p=reject", t.blue), ("BIMI ✓", t.purple), ("MTA-STS", t.amber))):
        w = len(label) * 7.8 + 30
        chips.append(
            f'<g class="chip" style="animation-delay:{fmt(i * 0.45)}s">'
            f'<rect x="{fmt(cx)}" y="272" width="{fmt(w)}" height="28" rx="14" fill="{t.panel}" stroke="{color}" stroke-opacity=".55"/>'
            f'<circle cx="{fmt(cx + 14)}" cy="286" r="3.5" fill="{color}"/>'
            f'<text x="{fmt(cx + 24)}" y="291" font-family="{MONO}" font-size="13" fill="{t.text}" '
            f'textLength="{fmt(len(label) * 7.8)}" lengthAdjust="spacingAndGlyphs">{esc(label)}</text></g>'
        )
        cx += w + 10

    # --- bottom ticker: two copies side by side, translate exactly one copy width ---
    tick_w = len(TICKER) * 7.6
    ticker = (
        f'<g clip-path="url(#frame)"><rect x="0" y="334" width="{W}" height="46" fill="{t.panel}" opacity=".85"/>'
        f'<line x1="0" x2="{W}" y1="334" y2="334" stroke="{t.border}"/>'
        f'<g><animateTransform attributeName="transform" type="translate" from="0 0" to="-{fmt(tick_w)} 0" '
        f'dur="40s" repeatCount="indefinite"/>'
        + "".join(
            f'<text x="{fmt(24 + i * tick_w)}" y="362" font-family="{MONO}" font-size="12.5" fill="{t.muted}" '
            f'textLength="{fmt(tick_w)}" lengthAdjust="spacing">{esc(TICKER)}</text>'
            for i in range(3)
        )
        + "</g></g>"
    )

    css = (
        f".flow{{fill:none;stroke-width:1.6;stroke-dasharray:4 6;animation:dash 1.2s linear infinite}}"
        f"@keyframes dash{{to{{stroke-dashoffset:-20}}}}"
        f".blink{{animation:blink 1s steps(1) infinite}}@keyframes blink{{50%{{opacity:0}}}}"
        f".chip{{animation:chip 4.5s ease-in-out infinite}}"
        f"@keyframes chip{{0%,100%{{opacity:.55}}12%{{opacity:1}}30%{{opacity:.55}}}}"
        f".pulse{{animation:pulse 2s ease-in-out infinite}}@keyframes pulse{{50%{{opacity:.25}}}}"
    )
    body = f"""
<defs>
  <clipPath id="frame"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20"/></clipPath>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t.bg0}"/><stop offset="1" stop-color="{t.bg1}"/></linearGradient>
  <radialGradient id="gA"><stop offset="0" stop-color="{t.blue}" stop-opacity="{t.glow_opacity}"/><stop offset="1" stop-color="{t.blue}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gB"><stop offset="0" stop-color="{t.purple}" stop-opacity="{t.glow_opacity}"/><stop offset="1" stop-color="{t.purple}" stop-opacity="0"/></radialGradient>
  <linearGradient id="nameGrad" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="520" y2="0" spreadMethod="repeat">
    <stop offset="0" stop-color="{t.blue}"/><stop offset=".33" stop-color="{t.purple}"/>
    <stop offset=".66" stop-color="{t.pink}"/><stop offset="1" stop-color="{t.blue}"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="520 0" dur="7s" repeatCount="indefinite"/>
  </linearGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{t.border}"/></pattern>
  <filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#dots)" opacity=".55"/>
  <circle cx="240" cy="40" r="320" fill="url(#gA)"><animateTransform attributeName="transform" type="translate" values="0 0;70 40;0 0" dur="16s" repeatCount="indefinite"/></circle>
  <circle cx="980" cy="330" r="340" fill="url(#gB)"><animateTransform attributeName="transform" type="translate" values="0 0;-80 -30;0 0" dur="18s" repeatCount="indefinite"/></circle>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="none" stroke="{t.border}"/>

<rect x="64" y="44" width="238" height="28" rx="14" fill="{t.panel}" stroke="{t.border}"/>
<circle class="pulse" cx="82" cy="58" r="4.5" fill="{t.green}"/>
<text x="94" y="63" font-family="{MONO}" font-size="12.5" fill="{t.muted}" letter-spacing=".5">ONLINE · IST (UTC+05:30)</text>

<text x="62" y="152" font-family="{SANS}" font-size="68" font-weight="800" letter-spacing="-2" fill="url(#nameGrad)">Arun Kumar</text>
<text x="64" y="194" font-family="{SANS}" font-size="21" font-weight="500" fill="{t.text}">Email Infrastructure Engineer <tspan fill="{t.muted}">·</tspan> Full-Stack Developer</text>

<text x="64" y="{ty}" font-family="{MONO}" font-size="{fs}" font-weight="700" fill="{t.muted}">$</text>
{''.join(phrases)}
{cursor}
{''.join(chips)}
{''.join(net)}
{ticker}
"""
    return svg_doc(W, H, body, title="Arun Kumar — Email Infrastructure Engineer & Full-Stack Developer", css=css)


# --------------------------------------------------------------------------- #
# SMTP terminal replay
# --------------------------------------------------------------------------- #
TERMINAL: tuple[tuple[str, list[Segment]], ...] = (
    ("cmd", [("$ ", "green"), ("swaks --to inbox@gmail.com --from hello@sendpilots.com --tls", "text")]),
    ("info", [("=== Trying gmail-smtp-in.l.google.com:25...", "muted")]),
    ("info", [("=== Connected to gmail-smtp-in.l.google.com.", "muted")]),
    ("server", [("<-  ", "muted"), ("220", "green"), (" mx.google.com ESMTP ready", "text")]),
    ("client", [(" -> ", "blue"), ("EHLO mta01.sendpilots.com", "text")]),
    ("server", [("<-  ", "muted"), ("250", "green"), ("-SIZE 157286400 · 8BITMIME · STARTTLS · ENHANCEDSTATUSCODES · PIPELINING · SMTPUTF8", "text")]),
    ("client", [(" -> ", "blue"), ("STARTTLS", "text")]),
    ("server", [("<-  ", "muted"), ("220", "green"), (" 2.0.0 Ready to start TLS", "text")]),
    ("info", [("=== ", "muted"), ("TLS started with cipher TLSv1.3:TLS_AES_256_GCM_SHA384:256", "purple")]),
    ("client", [(" ~> ", "blue"), ("MAIL FROM:<hello@sendpilots.com>", "text")]),
    ("server", [("<~  ", "muted"), ("250", "green"), (" 2.1.0 OK", "text")]),
    ("client", [(" ~> ", "blue"), ("RCPT TO:<inbox@gmail.com>", "text")]),
    ("server", [("<~  ", "muted"), ("250", "green"), (" 2.1.5 OK", "text")]),
    ("client", [(" ~> ", "blue"), ("DATA", "text")]),
    ("server", [("<~  ", "muted"), ("354", "amber"), (" Go ahead", "text")]),
    ("data", [(" ~> ", "blue"), ("DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed; d=sendpilots.com; s=sp1; bh=…", "muted")]),
    ("server", [("<~  ", "muted"), ("250", "green"), (" 2.0.0 OK queued  ", "text"), ("spf=pass dkim=pass dmarc=pass (p=REJECT)", "green")]),
    ("info", [("=== Connection closed · ", "muted"), ("✓ landed in Inbox", "green")]),
    ("prompt", [("$ ", "green")]),
)
CPS = {"cmd": 26.0, "client": 40.0, "data": 110.0}   # typing speed per line kind
PAUSE = {"cmd": 0.2, "client": 0.35, "data": 0.3, "server": 0.45, "info": 0.3, "prompt": 0.4}


def terminal(t: Theme) -> str:
    W, fs, lh, x0, top = 1200, 15, 25, 30, 44
    cw = fs * 0.6
    y0 = top + 36
    H = y0 + lh * (len(TERMINAL) - 1) + 28

    timeline: list[str] = []
    cursor: list[tuple[float, float, float]] = [(0.0, x0, y0)]  # (t, x, y)
    now = 0.6
    for idx, (kind, segs) in enumerate(TERMINAL):
        y = y0 + idx * lh
        now += PAUSE[kind]
        text = "".join(s for s, _ in segs)
        n = len(text)
        frames: list[tuple[float, float]] = [(0.0, 0.0)]
        if kind in CPS:
            per = 1.0 / CPS[kind]
            prefix = 2 if kind == "cmd" else 4       # prompt/arrow appears instantly
            frames.append((now, prefix * cw))
            cursor.append((now, x0 + prefix * cw, y))
            for i in range(prefix + 1, n + 1):
                now += per
                frames.append((now, i * cw))
                cursor.append((now, x0 + i * cw, y))
        else:
            frames.append((now, W))
        if kind == "prompt":
            cursor.append((now, x0 + n * cw, y))
        elif kind not in CPS:
            cursor.append((now, x0, y + lh))
        timeline.append((idx, y, segs, n, frames))  # type: ignore[arg-type]

    dur = now + 3.2
    fade_at = (dur - 1.0) / dur
    rows = []
    for idx, y, segs, n, frames in timeline:  # type: ignore[misc]
        # final width is generous so glyph fallbacks never get cropped
        frames = [*frames]
        frames[-1] = (frames[-1][0], W) if frames[-1][1] != W else frames[-1]
        spans = "".join(f'<tspan fill="{getattr(t, c)}">{esc(s)}</tspan>' for s, c in segs)
        rows.append(
            f'<clipPath id="l{idx}"><rect x="{x0}" y="{y - 17}" height="{lh}" width="0">'
            f'{discrete_anim("width", frames, dur)}</rect></clipPath>'
            f'<text x="{x0}" y="{y}" clip-path="url(#l{idx})" xml:space="preserve" style="white-space:pre" textLength="{fmt(n * cw)}" lengthAdjust="spacing">{spans}</text>'
        )
    cur_x = discrete_anim("x", [(ts, x) for ts, x, _ in cursor], dur)
    cur_y = discrete_anim("y", [(ts, y - 14) for ts, _, y in cursor], dur)

    css = ".blink{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
    body = f"""
<defs>
  <linearGradient id="tbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t.panel}"/><stop offset="1" stop-color="{t.bg0}"/></linearGradient>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="{t.text}" opacity=".035"/></pattern>
  <linearGradient id="sweep" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t.blue}" stop-opacity="0"/><stop offset=".5" stop-color="{t.blue}" stop-opacity=".07"/><stop offset="1" stop-color="{t.blue}" stop-opacity="0"/></linearGradient>
  <clipPath id="win"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14"/></clipPath>
</defs>
<g clip-path="url(#win)">
  <rect width="{W}" height="{H}" fill="url(#tbg)"/>
  <rect width="{W}" height="{top}" fill="{t.panel}"/>
  <line x1="0" x2="{W}" y1="{top}" y2="{top}" stroke="{t.border}"/>
  <rect width="{W}" height="{H}" fill="url(#scan)"/>
  <rect x="0" y="-120" width="{W}" height="120" fill="url(#sweep)"><animate attributeName="y" values="-120;{H}" dur="6s" repeatCount="indefinite"/></rect>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="none" stroke="{t.border}"/>
<circle cx="24" cy="22" r="6.5" fill="#ff5f57"/><circle cx="46" cy="22" r="6.5" fill="#febc2e"/><circle cx="68" cy="22" r="6.5" fill="#28c840"/>
<text x="{W / 2}" y="27" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{t.muted}">arun@sendpilots: ~ — smtp session · STARTTLS · TLS 1.3</text>
<g font-family="{MONO}" font-size="{fs}">
  <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{fmt(fade_at)};{fmt((dur - 0.35) / dur)};1" dur="{fmt(dur)}s" repeatCount="indefinite"/>
  {''.join(rows)}
  <rect class="blink" x="{x0}" y="{y0 - 14}" width="{fmt(cw)}" height="18" fill="{t.text}" opacity=".85">{cur_x}{cur_y}</rect>
</g>
"""
    return svg_doc(W, H, body, title="Animated SMTP session: EHLO, STARTTLS, MAIL FROM, RCPT TO, DATA, 250 OK", css=css)


# --------------------------------------------------------------------------- #
# Delivery pipeline
# --------------------------------------------------------------------------- #
PIPELINE = (
    ("Your App", "REST API · SMTP", "idempotency keys", "blue"),
    ("Queue", "Redis · Celery", "retry + backoff", "amber"),
    ("MTA Pool", "Postal · KumoMTA", "PowerMTA · Haraka", "purple"),
    ("Auth Layer", "SPF · DKIM · ARC", "DMARC p=reject", "green"),
    ("ISPs", "Gmail · Outlook", "Yahoo · iCloud", "pink"),
    ("Inbox", "seed placement", "Postmaster · SNDS", "green"),
)


def pipeline(t: Theme) -> str:
    W, H = 1200, 262
    bw, bh, gap, by = 164, 100, 30, 60
    x0 = (W - (len(PIPELINE) * bw + (len(PIPELINE) - 1) * gap)) / 2
    line_y = by + bh / 2
    L = len(PIPELINE) * bw + (len(PIPELINE) - 1) * gap
    D, n_packets = 6.0, 3
    period = D / n_packets

    boxes, glows = [], []
    centers = []
    for i, (title, l1, l2, ckey) in enumerate(PIPELINE):
        x = x0 + i * (bw + gap)
        cx = x + bw / 2
        centers.append(cx)
        color = getattr(t, ckey)
        arrive = D * (cx - x0) / L                     # when a packet reaches this node
        begin = arrive % period
        boxes.append(
            f'<rect x="{fmt(x)}" y="{by}" width="{bw}" height="{bh}" rx="12" fill="{t.panel}" stroke="{t.border}"/>'
            f'<rect x="{fmt(x)}" y="{by}" width="{bw}" height="{bh}" rx="12" fill="none" stroke="{color}" stroke-width="2" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;.18;1" dur="{fmt(period)}s" begin="{fmt(begin - period)}s" repeatCount="indefinite"/></rect>'
            f'<rect x="{fmt(x + 14)}" y="{by + 16}" width="6" height="18" rx="3" fill="{color}"/>'
            f'<text x="{fmt(x + 28)}" y="{by + 31}" font-family="{SANS}" font-size="16" font-weight="700" fill="{t.text}">{esc(title)}</text>'
            f'<text x="{fmt(x + 14)}" y="{by + 62}" font-family="{MONO}" font-size="12" fill="{t.muted}">{esc(l1)}</text>'
            f'<text x="{fmt(x + 14)}" y="{by + 82}" font-family="{MONO}" font-size="12" fill="{t.muted}">{esc(l2)}</text>'
        )
        if i < len(PIPELINE) - 1:
            ax = x + bw + gap / 2
            glows.append(f'<path d="M{fmt(ax - 4)} {fmt(line_y - 5)} l6 5 l-6 5" fill="none" stroke="{t.muted}" stroke-width="1.6"/>')

    packets = "".join(
        f'<rect x="-7" y="-4" width="14" height="8" rx="2" fill="{t.blue}" filter="url(#pg)">'
        f'<animateMotion path="M{fmt(x0)} {fmt(line_y)} H{fmt(x0 + L)}" dur="{fmt(D)}s" begin="-{fmt(k * period)}s" repeatCount="indefinite"/></rect>'
        for k in range(n_packets)
    )
    # bounce / FBL feedback loop: ISPs -> back to Queue
    ry = by + bh + 50
    ret = f"M{fmt(centers[4])} {by + bh} V{ry} H{fmt(centers[1])} V{by + bh}"
    bounce = (
        f'<path d="{ret}" fill="none" stroke="{t.border}" stroke-width="1.6" class="flow"/>'
        + "".join(
            f'<circle r="4" fill="{c}" filter="url(#pg)"><animateMotion path="{ret}" dur="4.5s" begin="-{b}s" repeatCount="indefinite"/></circle>'
            for c, b in ((t.amber, 0), (t.red, 2.25))
        )
        + f'<rect x="{fmt((centers[1] + centers[4]) / 2 - 250)}" y="{ry - 14}" width="500" height="28" rx="14" fill="{t.bg0}" stroke="{t.border}"/>'
        f'<text x="{fmt((centers[1] + centers[4]) / 2)}" y="{ry + 5}" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="{t.muted}">'
        f'<tspan fill="{t.amber}">4xx</tspan> → retry w/ backoff   ·   <tspan fill="{t.red}">5xx / FBL</tspan> → suppression list</text>'
    )
    css = (
        ".flow{stroke-dasharray:4 6;animation:dash 1.2s linear infinite}@keyframes dash{to{stroke-dashoffset:-20}}"
        ".pulse{animation:pulse 2s ease-in-out infinite}@keyframes pulse{50%{opacity:.25}}"
    )
    body = f"""
<defs><filter id="pg" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{t.bg0}" stroke="{t.border}"/>
<text x="{fmt(x0)}" y="38" font-family="{MONO}" font-size="12.5" letter-spacing="2" fill="{t.muted}">EMAIL DELIVERY PIPELINE</text>
<circle class="pulse" cx="{fmt(x0 + L - 66)}" cy="34" r="4.5" fill="{t.green}"/>
<text x="{fmt(x0 + L)}" y="38" text-anchor="end" font-family="{MONO}" font-size="12.5" fill="{t.muted}">flowing</text>
<line x1="{fmt(x0)}" x2="{fmt(x0 + L)}" y1="{fmt(line_y)}" y2="{fmt(line_y)}" stroke="{t.border}" stroke-width="1.6" class="flow"/>
{bounce}
{packets}
{''.join(boxes)}
{''.join(glows)}
"""
    return svg_doc(W, H, body, title="Email delivery pipeline: App → Queue → MTA pool → Auth → ISPs → Inbox, with bounce/FBL loop", css=css)


# --------------------------------------------------------------------------- #
# Project cards
# --------------------------------------------------------------------------- #
PROJECTS = {
    "sendpilots": (
        "SendPilots Flow AI",
        ("AI-native multi-channel outreach platform with an", "autonomous FlowGPT campaign agent."),
        ("Nuxt 4", "FastAPI", "Supabase", "Celery", "Redis", "Claude API"),
        "purple",
    ),
    "new_email_app": (
        "Email Campaign Platform",
        ("Campaigns, sequences, bounce handling & inbox", "management — Dockerized, queue-driven."),
        ("Laravel 12", "Livewire 3", "PostgreSQL", "Redis", "Meilisearch", "Caddy"),
        "blue",
    ),
}
REPO_ICON = ("M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 "
             "2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 "
             "0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z")


def project_card(repo: str) -> Callable[[Theme], str]:
    title, desc, tags, ckey = PROJECTS[repo]

    def render(t: Theme) -> str:
        W, H = 590, 210
        accent = getattr(t, ckey)
        per = 2 * (W - 4 + H - 4)
        pills, px = [], 24
        for tag in tags:
            w = len(tag) * 7.2 + 20
            if px + w > W - 24:
                break
            pills.append(
                f'<rect x="{fmt(px)}" y="150" width="{fmt(w)}" height="26" rx="13" fill="{t.panel}" stroke="{t.border}"/>'
                f'<text x="{fmt(px + 10)}" y="167.5" font-family="{MONO}" font-size="12" fill="{t.text}" '
                f'textLength="{fmt(len(tag) * 7.2)}" lengthAdjust="spacingAndGlyphs">{esc(tag)}</text>'
            )
            px += w + 8
        body = f"""
<defs>
  <linearGradient id="cg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t.bg0}"/><stop offset="1" stop-color="{t.panel}"/></linearGradient>
  <radialGradient id="cgl"><stop offset="0" stop-color="{accent}" stop-opacity="{t.glow_opacity}"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
  <clipPath id="cc"><rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="14"/></clipPath>
</defs>
<g clip-path="url(#cc)"><rect width="{W}" height="{H}" fill="url(#cg)"/>
  <circle cx="{W - 60}" cy="20" r="170" fill="url(#cgl)"><animateTransform attributeName="transform" type="translate" values="0 0;-40 30;0 0" dur="10s" repeatCount="indefinite"/></circle></g>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="14" fill="none" stroke="{t.border}"/>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="14" fill="none" stroke="{accent}" stroke-width="2"
      stroke-dasharray="140 {per - 140}" stroke-linecap="round">
  <animate attributeName="stroke-dashoffset" from="0" to="-{per}" dur="7s" repeatCount="indefinite"/></rect>
<g transform="translate(24 24)" fill="{t.muted}"><path d="{REPO_ICON}"/></g>
<text x="48" y="37" font-family="{MONO}" font-size="13" fill="{t.muted}">arunkuttysend/<tspan fill="{accent}" font-weight="700">{esc(repo)}</tspan></text>
<text x="24" y="80" font-family="{SANS}" font-size="24" font-weight="800" fill="{t.text}">{esc(title)}</text>
<text x="24" y="108" font-family="{SANS}" font-size="14.5" fill="{t.muted}">{esc(desc[0])}</text>
<text x="24" y="128" font-family="{SANS}" font-size="14.5" fill="{t.muted}">{esc(desc[1])}</text>
{''.join(pills)}
<text x="{W - 24}" y="37" text-anchor="end" font-family="{SANS}" font-size="13" font-weight="600" fill="{accent}">view repo →</text>
"""
        return svg_doc(W, H, body, title=f"{title} — {' '.join(desc)}")

    return render


# --------------------------------------------------------------------------- #
# Footer waves
# --------------------------------------------------------------------------- #
def _wave(amplitude: float, period: float, base: float, phase: float, width: float, height: float) -> str:
    pts = [
        f"{fmt(x)},{fmt(base + amplitude * math.sin(2 * math.pi * x / period + phase))}"
        for x in range(0, int(width + period) + 1, 20)
    ]
    return f"M0,{height} L{' L'.join(pts)} L{fmt(width + period)},{height} Z"


def footer(t: Theme) -> str:
    W, H, period = 1200, 170, 600
    layers = ((t.purple, 14, 118, 0.0, 22, 0.35), (t.blue, 10, 128, 1.7, 16, 0.45), (t.pink, 8, 140, 3.1, 12, 0.35))
    waves = "".join(
        f'<path d="{_wave(a, period, base, ph, W, H)}" fill="{c}" opacity="{op}">'
        f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-{period} 0" dur="{d}s" repeatCount="indefinite"/></path>'
        for c, a, base, ph, d, op in layers
    )
    body = f"""
<defs><clipPath id="fc"><rect width="{W}" height="{H}" rx="16"/></clipPath></defs>
<g clip-path="url(#fc)">{waves}</g>
<text x="{W / 2}" y="46" text-anchor="middle" font-family="{SANS}" font-size="22" font-weight="700" fill="{t.text}">Thanks for stopping by — let’s land some mail in the inbox.</text>
<text x="{W / 2}" y="76" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{t.muted}">arun@sendpilots.com  ·  sendpilots.com  ·  github.com/arunkuttysend</text>
"""
    return svg_doc(W, H, body, title="Thanks for visiting")


# --------------------------------------------------------------------------- #
ASSETS: dict[str, Callable[[Theme], str]] = {
    "hero": hero,
    "smtp-terminal": terminal,
    "pipeline": pipeline,
    "project-sendpilots": project_card("sendpilots"),
    "project-email-platform": project_card("new_email_app"),
    "footer": footer,
}


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    OUT.mkdir(parents=True, exist_ok=True)
    for name, render in ASSETS.items():
        for theme in THEMES:
            path = OUT / f"{name}-{theme.name}.svg"
            path.write_text(render(theme), encoding="utf-8")
            log.info("wrote %s (%.1f KB)", path.relative_to(ROOT), path.stat().st_size / 1024)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
