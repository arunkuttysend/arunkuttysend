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
    "building Sendpilots — deliverability-first email SaaS",
    "prototyping Mailcore — a Rust SMTP/IMAP/JMAP server",
    "shipping LeadQ — Go SMTP/IMAP engine, queue-driven",
    "enforcing SPF · DKIM · DMARC · BIMI · ARC · MTA-STS",
    "wiring AI agents: reply triage · A/B · flow optimizer",
    "vibe-coding with a fleet: Claude · Cursor · Codex · Hermes",
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
            f'<circle cx="{hub_x}" cy="{hub_y}" r="36" fill="none" stroke="{t.cyan}" stroke-width="1.5">'
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
    <stop offset="0" stop-color="{t.cyan}"/><stop offset=".33" stop-color="{t.purple}"/>
    <stop offset=".66" stop-color="{t.pink}"/><stop offset="1" stop-color="{t.cyan}"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="520 0" dur="7s" repeatCount="indefinite"/>
  </linearGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{t.border}"/></pattern>
  <linearGradient id="aur" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t.cyan}"/><stop offset=".5" stop-color="{t.purple}"/><stop offset="1" stop-color="{t.pink}"/></linearGradient>
  <linearGradient id="aur2" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="{t.green}"/><stop offset=".6" stop-color="{t.cyan}"/><stop offset="1" stop-color="{t.purple}"/></linearGradient>
  <filter id="soft" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="26"/></filter>
  <filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g filter="url(#soft)" opacity="{fmt(min(1.0, t.glow_opacity * 1.5))}">
    <path d="M-120 150 C160 40 420 210 700 120 S1120 40 1340 150 L1340 215 C1100 130 820 280 600 205 S120 190 -120 240 Z" fill="url(#aur)">
      <animateTransform attributeName="transform" type="translate" values="0 0;-70 18;0 0" dur="15s" repeatCount="indefinite"/></path>
    <path d="M-120 300 C220 220 520 330 820 260 S1160 230 1340 290 L1340 330 C1080 300 820 370 560 320 S140 330 -120 350 Z" fill="url(#aur2)" opacity=".7">
      <animateTransform attributeName="transform" type="translate" values="0 0;80 -14;0 0" dur="19s" repeatCount="indefinite"/></path>
  </g>
  <rect width="{W}" height="{H}" fill="url(#dots)" opacity=".5"/>
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
# Global delivery mesh (dot-matrix world map + animated routes)
# --------------------------------------------------------------------------- #
MASK_FILE = Path(__file__).resolve().parent / "data" / "land-mask.txt"
ORIGIN = ("IST · India", 21.0, 78.5)
RELAYS = {                      # illustrative relay regions on the clouds I run
    "eu": ("EU relay · Hetzner", 50.5, 12.4),
    "us": ("US-East relay · AWS", 38.9, -77.4),
    "ap": ("APAC relay · DigitalOcean", 1.35, 103.8),
}
PROVIDERS = (                   # (label, lat, lon, via-relay, label-anchor)
    ("Gmail", 37.4, -122.1, "us", "end"),
    ("Outlook", 47.6, -122.3, "us", "end"),
    ("Yahoo", 42.5, -72.5, "us", "start"),
    ("UOL", -23.5, -46.6, "us", "start"),
    ("GMX · Web.de", 58.0, 2.0, "eu", "end"),
    ("Naver", 37.5, 127.0, "ap", "start"),
    ("QQ Mail", 22.5, 114.0, "ap", "end"),
    ("Yahoo JP", 35.7, 139.7, "ap", "start"),
    ("Telstra", -33.9, 151.2, "ap", "start"),
    ("Zoho", 12.9, 80.2, "", "start"),
)


def _load_mask() -> tuple[float, float, list[str]]:
    lines = MASK_FILE.read_text(encoding="utf-8").splitlines()
    meta = dict(kv.split("=") for kv in lines[0].lstrip("# ").split() if "=" in kv)
    step = float(meta["step"])
    lat_max = float(meta["lat"].split("..")[0])
    return step, lat_max, [ln for ln in lines[1:] if ln]


def global_mesh(t: Theme) -> str:
    W, top, left = 1200, 86, 20
    step, lat_max, rows = _load_mask()
    px = (W - 2 * left) / (360 / step)            # px per cell
    H = int(top + len(rows) * px + 56)

    def proj(lat: float, lon: float) -> tuple[float, float]:
        return left + (lon + 180) / step * px, top + (lat_max - lat) / step * px + px / 2

    dots, twinkle = [], []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "1":
                x, y = left + (c + 0.5) * px, top + (r + 0.5) * px
                (twinkle if (r * 31 + c * 17) % 23 == 0 else dots).append(f"M{fmt(round(x, 1))} {fmt(round(y, 1))}h0")

    def arc(a: tuple[float, float], b: tuple[float, float], lift: float = 0.22) -> str:
        (x1, y1), (x2, y2) = a, b
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        d = math.hypot(x2 - x1, y2 - y1)
        return f"M{fmt(round(x1, 1))} {fmt(round(y1, 1))} Q{fmt(round(mx, 1))} {fmt(round(my - d * lift, 1))} {fmt(round(x2, 1))} {fmt(round(y2, 1))}"

    o = proj(ORIGIN[1], ORIGIN[2])
    routes, comets, marks = [], [], []
    k = 0

    def route(pid: str, d: str, colour: str, width: float, dur: float) -> None:
        nonlocal k
        begin = -(k * 0.37) % dur
        routes.append(
            f'<path id="{pid}" d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" stroke-opacity=".28"/>'
            f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width + 0.6}" stroke-linecap="round" '
            f'stroke-dasharray="36 1400" filter="url(#mg)">'
            f'<animate attributeName="stroke-dashoffset" from="36" to="-1400" dur="{fmt(dur)}s" begin="{fmt(begin)}s" repeatCount="indefinite"/></path>'
        )
        comets.append(
            f'<circle r="{fmt(width + 1.4)}" fill="{colour}" filter="url(#mg)"><animateMotion dur="{fmt(dur * 0.45)}s" '
            f'begin="{fmt(begin)}s" repeatCount="indefinite"><mpath href="#{pid}"/></animateMotion></circle>'
        )
        k += 1

    relay_xy = {}
    for key, (label, lat, lon) in RELAYS.items():
        relay_xy[key] = proj(lat, lon)
        route(f"r_{key}", arc(o, relay_xy[key], 0.28), t.cyan, 1.8, 4.2)
    colours = (t.pink, t.purple, t.amber, t.green, t.blue)
    for i, (label, lat, lon, via, anchor) in enumerate(PROVIDERS):
        p = proj(lat, lon)
        src = relay_xy.get(via, o)
        route(f"p_{i}", arc(src, p, 0.18 if via else 0.6), colours[i % len(colours)], 1.2, 3.2)
        dx = -9 if anchor == "end" else 9
        marks.append(
            f'<circle cx="{fmt(round(p[0], 1))}" cy="{fmt(round(p[1], 1))}" r="3.6" fill="{colours[i % len(colours)]}"/>'
            f'<circle cx="{fmt(round(p[0], 1))}" cy="{fmt(round(p[1], 1))}" r="4" fill="none" stroke="{colours[i % len(colours)]}">'
            f'<animate attributeName="r" values="4;13" dur="2.6s" begin="-{fmt(i * 0.29)}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".8;0" dur="2.6s" begin="-{fmt(i * 0.29)}s" repeatCount="indefinite"/></circle>'
            f'<text x="{fmt(round(p[0] + dx, 1))}" y="{fmt(round(p[1] + 4, 1))}" text-anchor="{anchor}" font-family="{SANS}" '
            f'font-size="12" font-weight="600" fill="{t.text}" stroke="{t.bg0}" stroke-width="3" paint-order="stroke">{esc(label)}</text>'
        )
    for key, (label, lat, lon) in RELAYS.items():
        x, y = relay_xy[key]
        marks.append(
            f'<rect x="{fmt(round(x - 6, 1))}" y="{fmt(round(y - 6, 1))}" width="12" height="12" rx="2" transform="rotate(45 {fmt(round(x, 1))} {fmt(round(y, 1))})" '
            f'fill="{t.bg0}" stroke="{t.cyan}" stroke-width="2"/>'
            f'<text x="{fmt(round(x, 1))}" y="{fmt(round(y + 22, 1))}" text-anchor="middle" font-family="{MONO}" font-size="11" '
            f'fill="{t.cyan}" stroke="{t.bg0}" stroke-width="3" paint-order="stroke">{esc(label)}</text>'
        )
    ox, oy = o
    origin = (
        "".join(
            f'<circle cx="{fmt(round(ox, 1))}" cy="{fmt(round(oy, 1))}" r="8" fill="none" stroke="{t.green}" stroke-width="1.5">'
            f'<animate attributeName="r" values="8;34" dur="3s" begin="{d}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".9;0" dur="3s" begin="{d}s" repeatCount="indefinite"/></circle>'
            for d in (0, -1, -2)
        )
        + f'<circle cx="{fmt(round(ox, 1))}" cy="{fmt(round(oy, 1))}" r="7" fill="{t.green}" filter="url(#mg)"/>'
        f'<text x="{fmt(round(ox - 14, 1))}" y="{fmt(round(oy - 14, 1))}" text-anchor="end" font-family="{MONO}" font-size="12" font-weight="700" '
        f'fill="{t.green}" stroke="{t.bg0}" stroke-width="3" paint-order="stroke">{esc(ORIGIN[0])}</text>'
    )
    map_h = len(rows) * px
    css = ".tw{animation:tw 3.2s ease-in-out infinite}@keyframes tw{50%{stroke-opacity:.15}}"
    body = f"""
<defs>
  <linearGradient id="gbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t.bg1}"/><stop offset="1" stop-color="{t.bg0}"/></linearGradient>
  <radialGradient id="gglow" cx=".62" cy=".45" r=".6"><stop offset="0" stop-color="{t.purple}" stop-opacity="{fmt(t.glow_opacity * 0.6)}"/><stop offset="1" stop-color="{t.purple}" stop-opacity="0"/></radialGradient>
  <linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="{t.cyan}" stop-opacity="0"/><stop offset=".8" stop-color="{t.cyan}" stop-opacity=".07"/><stop offset="1" stop-color="{t.cyan}" stop-opacity=".3"/></linearGradient>
  <filter id="mg" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="gc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#gc)">
  <rect width="{W}" height="{H}" fill="url(#gbg)"/><rect width="{W}" height="{H}" fill="url(#gglow)"/>
  <path d="{''.join(dots)}" stroke="{t.muted}" stroke-opacity=".38" stroke-width="{fmt(round(px * 0.46, 2))}" stroke-linecap="round"/>
  <path class="tw" d="{''.join(twinkle)}" stroke="{t.cyan}" stroke-opacity=".75" stroke-width="{fmt(round(px * 0.5, 2))}" stroke-linecap="round"/>
  <rect y="{top}" width="70" height="{fmt(round(map_h, 1))}" fill="url(#beam)">
    <animate attributeName="x" values="-70;{W}" dur="9s" repeatCount="indefinite"/></rect>
  {''.join(routes)}{''.join(comets)}{''.join(marks)}{origin}
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="none" stroke="{t.border}"/>
<text x="28" y="40" font-family="{MONO}" font-size="12.5" letter-spacing="2.5" fill="{t.muted}">GLOBAL DELIVERY MESH</text>
<text x="28" y="64" font-family="{SANS}" font-size="15" fill="{t.text}">Origin <tspan fill="{t.green}" font-weight="700">IST</tspan> → <tspan fill="{t.cyan}" font-weight="700">3 relay regions</tspan> → <tspan fill="{t.pink}" font-weight="700">10 mailbox providers</tspan> · TLS 1.3 on every hop</text>
<g font-family="{MONO}" font-size="11" fill="{t.muted}">
  <circle cx="{W - 330}" cy="{H - 26}" r="4" fill="{t.green}"/><text x="{W - 320}" y="{H - 22}">origin</text>
  <rect x="{W - 262}" y="{H - 31}" width="9" height="9" rx="1.5" transform="rotate(45 {W - 257.5} {H - 26.5})" fill="none" stroke="{t.cyan}" stroke-width="1.6"/><text x="{W - 246}" y="{H - 22}">relay</text>
  <circle cx="{W - 190}" cy="{H - 26}" r="4" fill="{t.pink}"/><text x="{W - 180}" y="{H - 22}">mailbox provider</text>
</g>
<text x="28" y="{H - 22}" font-family="{MONO}" font-size="11" fill="{t.muted}">illustrative topology · map: Natural Earth (public domain)</text>
"""
    return svg_doc(W, H, body, title="Global delivery mesh: routes from India through EU, US-East and APAC relays to mailbox providers worldwide", css=css)


# --------------------------------------------------------------------------- #
# Deliverability 2026 rulebook (research panel)
# Sources: Google sender guidelines FAQ, Microsoft Defender for O365 blog
# (Apr 2025), BIMI Group CMC announcement — cited in README.
# --------------------------------------------------------------------------- #
RULEBOOK = (
    ("Gmail", "pink", "550 5.7.26 · hard rejects since Nov 2025", (
        "SPF and DKIM both pass",
        "DMARC published (p=none minimum), aligned",
        "Spam rate < 0.1% · never ≥ 0.3%",
        "One-click unsubscribe (RFC 8058) · ≤ 2 days",
        "Valid PTR / FCrDNS · TLS on the connection",
    )),
    ("Yahoo", "purple", "enforced since Feb 2024", (
        "SPF and DKIM both pass",
        "DMARC published (p=none minimum), aligned",
        "Complaint rate < 0.3%",
        "One-click unsubscribe (RFC 8058) · ≤ 2 days",
        "Valid forward + reverse DNS",
    )),
    ("Outlook", "blue", "550 5.7.515 · rejects since 5 May 2025", (
        "SPF passes for the sending domain",
        "DKIM passes",
        "DMARC p=none minimum, aligned (SPF or DKIM)",
        "Recommended: working unsubscribe link",
        "Recommended: list hygiene · valid P2 From",
    )),
)
TIMELINE = (
    ("Feb 2024", "Gmail + Yahoo bulk-sender rules"),
    ("Jun 2024", "one-click unsubscribe enforced"),
    ("May 2025", "Outlook: SPF/DKIM/DMARC or reject"),
    ("Nov 2025", "Gmail escalates to 5xx rejects"),
    ("2026", "all three: full enforcement"),
)


def rulebook(t: Theme) -> str:
    W, H = 1200, 604
    cw, cg, cy, ch = 368, 20, 118, 262
    cards = []
    for ci, (name, ckey, foot, rules) in enumerate(RULEBOOK):
        x = 28 + ci * (cw + cg)
        colour = getattr(t, ckey)
        rows = []
        for ri, rule in enumerate(rules):
            y = cy + 70 + ri * 32
            delay = 0.25 + ci * 0.18 + ri * 0.12
            optional = rule.startswith("Recommended")
            mark = (f'<circle cx="{x + 26}" cy="{y - 5}" r="9" fill="none" stroke="{t.muted}" stroke-dasharray="3 3"/>'
                    if optional else
                    f'<circle cx="{x + 26}" cy="{y - 5}" r="9" fill="{t.green}" fill-opacity=".16" stroke="{t.green}"/>'
                    f'<path d="M{x + 21.5} {y - 5} l3 3 l6 -6" fill="none" stroke="{t.green}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
            rows.append(
                f'<g class="rule" style="animation-delay:{fmt(round(delay, 2))}s">{mark}'
                f'<text x="{x + 44}" y="{y}" font-family="{SANS}" font-size="13.5" fill="{t.muted if optional else t.text}">{esc(rule)}</text></g>'
            )
        cards.append(
            f'<rect x="{x}" y="{cy}" width="{cw}" height="{ch}" rx="14" fill="{t.panel}" stroke="{t.border}"/>'
            f'<rect x="{x}" y="{cy}" width="{cw}" height="4" rx="2" fill="{colour}"/>'
            f'<text x="{x + 20}" y="{cy + 38}" font-family="{SANS}" font-size="20" font-weight="800" fill="{t.text}">{esc(name)}</text>'
            f'<text x="{x + cw - 20}" y="{cy + 37}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{t.muted}">5,000+/day</text>'
            + "".join(rows)
            + f'<line x1="{x + 16}" x2="{x + cw - 16}" y1="{cy + ch - 38}" y2="{cy + ch - 38}" stroke="{t.border}"/>'
            f'<text x="{x + 20}" y="{cy + ch - 14}" font-family="{MONO}" font-size="12" fill="{colour}">{esc(foot)}</text>'
        )

    # spam-rate gauge: 0 … 0.5 %
    gx, gy, gw = 28, 430, 560
    def gxp(pct: float) -> float:
        return gx + gw * pct / 0.5
    needle = ";".join(fmt(round(gxp(v), 1)) for v in (0.03, 0.07, 0.05, 0.09, 0.04, 0.03))
    gauge = (
        f'<text x="{gx}" y="{gy - 20}" font-family="{MONO}" font-size="12" letter-spacing="1.5" fill="{t.muted}">USER-REPORTED SPAM RATE</text>'
        f'<rect x="{gx}" y="{gy}" width="{fmt(gxp(0.1) - gx)}" height="14" rx="7" fill="{t.green}" opacity=".85"/>'
        f'<rect x="{fmt(gxp(0.1))}" y="{gy}" width="{fmt(gxp(0.3) - gxp(0.1))}" height="14" fill="{t.amber}" opacity=".8"/>'
        f'<rect x="{fmt(gxp(0.3))}" y="{gy}" width="{fmt(gx + gw - gxp(0.3))}" height="14" rx="7" fill="{t.red}" opacity=".85"/>'
        + "".join(
            f'<text x="{fmt(gxp(v))}" y="{gy + 34}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{t.muted}">{v:.1f}%</text>'
            for v in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5)
        )
        + f'<text x="{fmt((gx + gxp(0.1)) / 2)}" y="{gy + 54}" text-anchor="middle" font-family="{SANS}" font-size="12" fill="{t.green}">target</text>'
        f'<text x="{fmt((gxp(0.1) + gxp(0.3)) / 2)}" y="{gy + 54}" text-anchor="middle" font-family="{SANS}" font-size="12" fill="{t.amber}">throttling · reputation hit</text>'
        f'<text x="{fmt((gxp(0.3) + gx + gw) / 2)}" y="{gy + 54}" text-anchor="middle" font-family="{SANS}" font-size="12" fill="{t.red}">hard enforcement</text>'
        f'<g><animateTransform attributeName="transform" type="translate" values="{";".join(f"{fmt(round(gxp(v) - gx, 1))} 0" for v in (0.03, 0.07, 0.05, 0.09, 0.04, 0.03))}" '
        f'dur="8s" calcMode="spline" keySplines=".4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1" repeatCount="indefinite"/>'
        f'<path d="M{gx} {gy - 4} l-6 -10 h12 z" fill="{t.text}"/>'
        f'<line x1="{gx}" x2="{gx}" y1="{gy - 2}" y2="{gy + 16}" stroke="{t.text}" stroke-width="2"/></g>'
        f'<text x="{gx + gw}" y="{gy - 20}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{t.text}">my ops ceiling: <tspan fill="{t.green}" font-weight="700">&lt; 0.08%</tspan></text>'
    )
    _ = needle
    # BIMI box
    bx, by, bw, bh = 620, 398, 552, 96
    bimi = (
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="14" fill="{t.panel}" stroke="{t.border}"/>'
        f'<rect x="{bx}" y="{by}" width="4" height="{bh}" rx="2" fill="url(#rbAur)"/>'
        f'<text x="{bx + 22}" y="{by + 30}" font-family="{SANS}" font-size="16" font-weight="800" fill="{t.text}">BIMI · verified logo in the inbox</text>'
        f'<text x="{bx + 22}" y="{by + 55}" font-family="{SANS}" font-size="13.5" fill="{t.muted}">Needs DMARC at enforcement (p=quarantine or p=reject)</text>'
        f'<text x="{bx + 22}" y="{by + 77}" font-family="{SANS}" font-size="13.5" fill="{t.muted}">+ a <tspan fill="{t.text}" font-weight="600">VMC</tspan> (trademarked logo) or <tspan fill="{t.text}" font-weight="600">CMC</tspan> (no trademark — Gmail supports it)</text>'
    )
    # enforcement timeline
    ty, tx0, tx1 = 552, 130, 1070
    step = (tx1 - tx0) / (len(TIMELINE) - 1)
    ticks = []
    for i, (when, what) in enumerate(TIMELINE):
        x = tx0 + i * step
        colour = t.red if i == len(TIMELINE) - 1 else t.cyan
        ticks.append(
            f'<circle cx="{fmt(x)}" cy="{ty}" r="6" fill="{t.bg0}" stroke="{colour}" stroke-width="2"/>'
            f'<circle cx="{fmt(x)}" cy="{ty}" r="6" fill="{colour}" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.05;.8;1" dur="7s" begin="{fmt(round(i * 7 / len(TIMELINE) * 0.9, 2))}s" repeatCount="indefinite"/></circle>'
            f'<text x="{fmt(x)}" y="{ty - 16}" text-anchor="middle" font-family="{MONO}" font-size="12" font-weight="700" fill="{colour}">{esc(when)}</text>'
            f'<text x="{fmt(x)}" y="{ty + 26}" text-anchor="middle" font-family="{SANS}" font-size="12" fill="{t.muted}">{esc(what)}</text>'
        )
    timeline = (
        f'<line x1="{tx0}" x2="{tx1}" y1="{ty}" y2="{ty}" stroke="{t.border}" stroke-width="2"/>'
        f'<line x1="{tx0}" x2="{tx1}" y1="{ty}" y2="{ty}" stroke="url(#rbAur)" stroke-width="2.5" stroke-dasharray="{tx1 - tx0}" stroke-dashoffset="{tx1 - tx0}">'
        f'<animate attributeName="stroke-dashoffset" values="{tx1 - tx0};0;0" keyTimes="0;.85;1" dur="7s" repeatCount="indefinite"/></line>'
        + "".join(ticks)
    )
    css = (
        ".rule{animation:ruleIn .5s ease-out both}"
        "@keyframes ruleIn{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}"
    )
    body = f"""
<defs>
  <linearGradient id="rbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t.bg0}"/><stop offset="1" stop-color="{t.bg1}"/></linearGradient>
  <linearGradient id="rbAur" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t.cyan}"/><stop offset=".5" stop-color="{t.purple}"/><stop offset="1" stop-color="{t.pink}"/></linearGradient>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="url(#rbg)" stroke="{t.border}"/>
<text x="28" y="44" font-family="{MONO}" font-size="12.5" letter-spacing="2.5" fill="{t.muted}">DELIVERABILITY RESEARCH · 2026 BULK-SENDER RULEBOOK</text>
<text x="28" y="76" font-family="{SANS}" font-size="20" font-weight="800" fill="{t.text}">Authentication isn’t a best practice anymore — it’s the <tspan fill="url(#rbAur)">entry ticket</tspan>.</text>
<text x="28" y="100" font-family="{SANS}" font-size="13.5" fill="{t.muted}">Applies at 5,000+ messages/day to a provider. Non-compliance is now a permanent 5xx reject, not a spam-folder nudge.</text>
{''.join(cards)}
{gauge}
{bimi}
{timeline}
"""
    return svg_doc(W, H, body, title="2026 bulk-sender rules for Gmail, Yahoo and Outlook, spam-rate thresholds, BIMI and enforcement timeline", css=css)


# --------------------------------------------------------------------------- #
# AI-native builder: agent fleet orbit + engineering guardrails
# --------------------------------------------------------------------------- #
AGENTS_INNER = ("Claude Code", "Cursor", "Codex CLI", "Gemini CLI", "Hermes Agent", "Kiro")
AGENTS_OUTER = ("Grok CLI", "Cline", "Goose", "Copilot", "Kimi Code", "OpenCode", "Factory Droid", "Antigravity")
AGENT_FLOW = (
    ("SPEC", "PRDs · ADRs · CLAUDE.md · AGENTS.md · GEMINI.md"),
    ("PARALLEL AGENTS", "Claude Code + Cursor + Codex on isolated branches"),
    ("MCP TOOLS", "Supabase · Figma · Chrome · Serena · infra via MCP"),
    ("GUARDRAILS", "tests (Mailcore: 242) · CI · types · security review"),
    ("SHIP", "Docker → AWS ECS · Hetzner · Vercel, observability on"),
)


def agent_fleet(t: Theme) -> str:
    W, H = 1200, 540
    cx, cy, r1, r2 = 312, 282, 128, 214
    ex1, ex2 = 1.2, 1.2      # horizontal stretch of the rings (ellipses)
    palette = (t.cyan, t.purple, t.pink, t.green, t.amber, t.blue)

    def ring(names: tuple[str, ...], radius: float, phase: float, size: float, key: str, stretch: float) -> tuple[str, str]:
        spokes, chips = [], []
        for i, name in enumerate(names):
            a = phase + 2 * math.pi * i / len(names)
            x, y = cx + radius * stretch * math.cos(a), cy + radius * math.sin(a)
            colour = palette[i % len(palette)]
            pid = f"sp_{key}{i}"
            begin = -((i * 0.55) % 3.3)
            spokes.append(
                f'<path id="{pid}" d="M{cx} {cy} L{fmt(round(x, 1))} {fmt(round(y, 1))}" stroke="{colour}" stroke-opacity=".22" stroke-width="1.2"/>'
                f'<circle r="3" fill="{colour}" filter="url(#ag)"><animateMotion dur="3.3s" begin="{fmt(round(begin, 2))}s" repeatCount="indefinite" '
                f'keyPoints="0;1" keyTimes="0;1"><mpath href="#{pid}"/></animateMotion></circle>'
            )
            w = len(name) * size * 0.56 + 26
            chips.append(
                f'<g class="chip" style="animation-delay:{fmt(round(-begin, 2))}s">'
                f'<rect x="{fmt(round(x - w / 2, 1))}" y="{fmt(round(y - size, 1))}" width="{fmt(round(w, 1))}" height="{fmt(size * 2)}" rx="{fmt(size)}" '
                f'fill="{t.panel}" stroke="{colour}" stroke-opacity=".7"/>'
                f'<circle cx="{fmt(round(x - w / 2 + 12, 1))}" cy="{fmt(round(y, 1))}" r="3.5" fill="{colour}"/>'
                f'<text x="{fmt(round(x + 6, 1))}" y="{fmt(round(y + size * 0.36, 1))}" text-anchor="middle" font-family="{SANS}" '
                f'font-size="{fmt(size)}" font-weight="600" fill="{t.text}">{esc(name)}</text></g>'
            )
        return "".join(spokes), "".join(chips)

    s_in, c_in = ring(AGENTS_INNER, r1, -math.pi / 2, 13, "i", ex1)
    s_out, c_out = ring(AGENTS_OUTER, r2, -math.pi / 2 + math.pi / 8, 11.5, "o", ex2)
    hexagon = " ".join(f"{fmt(round(cx + 50 * math.cos(math.pi / 6 + k * math.pi / 3), 1))},{fmt(round(cy + 50 * math.sin(math.pi / 6 + k * math.pi / 3), 1))}" for k in range(6))
    radar = (
        f'<g><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="10s" repeatCount="indefinite"/>'
        f'<path d="M{cx} {cy} L{cx + r2 + 30} {cy} A{r2 + 30} {r2 + 30} 0 0 0 {fmt(round(cx + (r2 + 30) * math.cos(-0.7), 1))} {fmt(round(cy + (r2 + 30) * math.sin(-0.7), 1))} Z" fill="url(#radar)"/></g>'
    )
    rings = "".join(
        f'<ellipse cx="{cx}" cy="{cy}" rx="{fmt(round(r * ex1, 1))}" ry="{r}" fill="none" stroke="{t.border}" stroke-dasharray="{d}">'
        f'<animate attributeName="stroke-dashoffset" from="0" to="{sign}120" dur="{dur / 4}s" repeatCount="indefinite"/></ellipse>'
        for r, d, sign, dur in ((r1, "2 7", "", 40), (r2, "3 9", "-", 60), (r2 + 30, "1 5", "", 90))
    )

    fx, fy, fstep = 640, 196, 58
    flow = [f'<line x1="{fx + 14}" x2="{fx + 14}" y1="{fy - 6}" y2="{fy + fstep * (len(AGENT_FLOW) - 1) + 6}" stroke="{t.border}" stroke-width="2"/>',
            f'<circle cx="{fx + 14}" r="5" fill="{t.cyan}" filter="url(#ag)"><animate attributeName="cy" values="{fy};{fy + fstep * (len(AGENT_FLOW) - 1)}" '
            f'dur="6s" repeatCount="indefinite"/></circle>']
    for i, (head, desc) in enumerate(AGENT_FLOW):
        y = fy + i * fstep
        flow.append(
            f'<g class="step" style="animation-delay:{fmt(i * 1.2)}s">'
            f'<circle cx="{fx + 14}" cy="{y}" r="13" fill="{t.panel}" stroke="{palette[i]}" stroke-width="2"/>'
            f'<text x="{fx + 14}" y="{y + 4.5}" text-anchor="middle" font-family="{MONO}" font-size="12" font-weight="800" fill="{palette[i]}">{i + 1}</text>'
            f'<text x="{fx + 40}" y="{y - 3}" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="1.5" fill="{palette[i]}">{esc(head)}</text>'
            f'<text x="{fx + 40}" y="{y + 16}" font-family="{SANS}" font-size="14" fill="{t.text}">{esc(desc)}</text></g>'
        )
    css = (
        ".chip{animation:chip 3.3s ease-in-out infinite}@keyframes chip{0%,100%{opacity:.78}10%{opacity:1}}"
        ".step{animation:step 6s ease-in-out infinite}@keyframes step{0%,100%{opacity:.62}8%,22%{opacity:1}}"
    )
    body = f"""
<defs>
  <linearGradient id="afbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t.bg0}"/><stop offset="1" stop-color="{t.bg1}"/></linearGradient>
  <radialGradient id="afglow" cx=".26" cy=".52" r=".45"><stop offset="0" stop-color="{t.purple}" stop-opacity="{fmt(t.glow_opacity * 0.8)}"/><stop offset="1" stop-color="{t.purple}" stop-opacity="0"/></radialGradient>
  <radialGradient id="radar" cx="{cx}" cy="{cy}" r="{r2 + 30}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{t.cyan}" stop-opacity=".0"/><stop offset="1" stop-color="{t.cyan}" stop-opacity="{fmt(t.glow_opacity * 0.32)}"/></radialGradient>
  <linearGradient id="afAur" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t.cyan}"/><stop offset=".5" stop-color="{t.purple}"/><stop offset="1" stop-color="{t.pink}"/></linearGradient>
  <filter id="ag" x="-150%" y="-150%" width="400%" height="400%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="afc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#afc)"><rect width="{W}" height="{H}" fill="url(#afbg)"/><rect width="{W}" height="{H}" fill="url(#afglow)"/>{radar}</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="none" stroke="{t.border}"/>
{rings}{s_out}{s_in}
<polygon points="{hexagon}" fill="{t.panel}" stroke="url(#afAur)" stroke-width="2.5"/>
<text x="{cx}" y="{cy - 2}" text-anchor="middle" font-family="{SANS}" font-size="17" font-weight="800" fill="{t.text}">ARUN</text>
<text x="{cx}" y="{cy + 16}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{t.muted}">orchestrator</text>
{c_out}{c_in}
<text x="{fx}" y="60" font-family="{MONO}" font-size="12.5" letter-spacing="2.5" fill="{t.muted}">AI-NATIVE BUILDER · AGENT FLEET</text>
<text x="{fx}" y="98" font-family="{SANS}" font-size="30" font-weight="800" fill="{t.text}">Vibe-coding, <tspan fill="url(#afAur)">engineered.</tspan></text>
<text x="{fx}" y="130" font-family="{SANS}" font-size="14.5" fill="{t.muted}">I ship with a fleet of AI coding agents running in parallel —</text>
<text x="{fx}" y="151" font-family="{SANS}" font-size="14.5" fill="{t.muted}">and keep them honest with specs, tests, CI and review.</text>
{''.join(flow)}
<text x="{fx}" y="{H - 26}" font-family="{MONO}" font-size="11" fill="{t.muted}">14 agent platforms · context files live in the repos, not in my head</text>
"""
    return svg_doc(W, H, body, title="AI-native builder: an orchestrated fleet of coding agents (Claude Code, Cursor, Codex, Gemini CLI, Hermes, Kiro and more) with spec, test and review guardrails", css=css)


# --------------------------------------------------------------------------- #
# The Lab — private-repo case studies
# --------------------------------------------------------------------------- #
LAB = (  # (name, status, line1, line2, metric, metric_label, stack, colour)
    ("Mailcore", "R&D", "All-in-one mail server in Rust:", "SMTP · IMAP · JMAP · POP3 · Sieve", "242", "tests · 24 crates", ("Rust", "SQLx", "Redis", "Postgres"), "pink"),
    ("LeadQ v2", "BUILDING", "Queue-driven outreach engine: Go", "SMTP/IMAP pool, 8-check pre-flight", "5/8", "phases shipped", ("Go", "Docker", "CI", "RBAC"), "cyan"),
    ("FlowMail AI", "BUILDING", "Deliverability-first automation:", "visual flows, SMTP rotation, warmup", "4", "AI agents + CRM", ("Next.js", "Supabase", "Python", "Claude API"), "purple"),
    ("SendPilots", "LIVE", "Cold-email + deliverability SaaS", "with Razorpay billing", "AWS", "ECS · Sentry · Grafana · Loki", ("Django 5", "Celery", "React 19", "AWS ECS"), "green"),
    ("SendPilot Flow", "BUILDING", "AI multi-channel outreach:", "email · voice · LinkedIn", "3", "channels", ("Next.js 16", "Django 5", "Redis"), "blue"),
    ("Nova Warmup", "R&D", "Mailbox warmup & reputation", "engine for Gmail · Yahoo · Outlook", "3", "mailbox providers", ("Laravel", "Python", "Docker"), "amber"),
    ("Postal × SP", "R&D", "Customised Postal MTA wired to", "Sendpilots webhooks", "MTA", "self-hosted, webhook-wired", ("Ruby", "Postal", "Docker"), "pink"),
    ("Realtime SaaS", "R&D", "Multi-tenant outreach with", "WebSockets + ClickHouse analytics", "RT", "live dashboards", ("Django", "Next.js 15", "Celery"), "cyan"),
    ("Engagement", "R&D", "Self-hosted engagement platform:", "email · SMS · push · WhatsApp · Slack", "5", "channels", ("TypeScript", "microservices"), "purple"),
)


def lab(t: Theme) -> str:
    W, cols, gap, tw, th, top = 1200, 3, 16, 370, 190, 92
    rows = math.ceil(len(LAB) / cols)
    H = top + rows * th + (rows - 1) * gap + 28
    status_col = {"LIVE": t.green, "BUILDING": t.amber, "R&D": t.purple}
    tiles = []
    for i, (name, status, l1, l2, metric, mlabel, stack, ckey) in enumerate(LAB):
        c, r = i % cols, i // cols
        x, y = 28 + c * (tw + gap), top + r * (th + gap)
        colour, sc = getattr(t, ckey), status_col[status]
        chips, px = [], x + 18
        for tag in stack:
            w = len(tag) * 6.6 + 16
            chips.append(f'<rect x="{fmt(round(px, 1))}" y="{y + th - 36}" width="{fmt(round(w, 1))}" height="21" rx="10.5" fill="{t.bg0}" stroke="{t.border}"/>'
                         f'<text x="{fmt(round(px + 8, 1))}" y="{y + th - 21.5}" font-family="{MONO}" font-size="11" fill="{t.muted}" '
                         f'textLength="{fmt(round(len(tag) * 6.6, 1))}" lengthAdjust="spacingAndGlyphs">{esc(tag)}</text>')
            px += w + 6
        tiles.append(
            f'<g class="tile" style="animation-delay:{fmt(round(i * 0.08, 2))}s">'
            f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="14" fill="{t.panel}" stroke="{t.border}"/>'
            f'<rect x="{x + 1}" y="{y + 18}" width="3" height="30" rx="1.5" fill="{colour}"/>'
            f'<text x="{x + 18}" y="{y + 40}" font-family="{SANS}" font-size="18" font-weight="800" fill="{t.text}">{esc(name)}</text>'
            f'<circle class="led" cx="{x + tw - 86}" cy="{y + 34}" r="4" fill="{sc}" style="animation-delay:{fmt(round(i * 0.3, 2))}s"/>'
            f'<text x="{x + tw - 76}" y="{y + 38}" font-family="{MONO}" font-size="10.5" font-weight="700" letter-spacing="1" fill="{sc}">{esc(status)}</text>'
            f'<text x="{x + 18}" y="{y + 70}" font-family="{SANS}" font-size="13" fill="{t.muted}">{esc(l1)}</text>'
            f'<text x="{x + 18}" y="{y + 89}" font-family="{SANS}" font-size="13" fill="{t.muted}">{esc(l2)}</text>'
            f'<text x="{x + 18}" y="{y + 126}" font-family="{MONO}" font-size="22" font-weight="800" fill="{colour}">{esc(metric)}'
            f'<tspan dx="10" font-size="11.5" font-weight="400" fill="{t.muted}">{esc(mlabel)}</tspan></text>'
            + "".join(chips) + "</g>"
        )
    css = (
        ".tile{animation:tin .6s ease-out both}@keyframes tin{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
        ".led{animation:led 1.8s ease-in-out infinite}@keyframes led{50%{opacity:.25}}"
    )
    body = f"""
<defs>
  <linearGradient id="lbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t.bg0}"/><stop offset="1" stop-color="{t.bg1}"/></linearGradient>
  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t.text}" stop-opacity="0"/><stop offset=".5" stop-color="{t.text}" stop-opacity=".06"/><stop offset="1" stop-color="{t.text}" stop-opacity="0"/></linearGradient>
  <clipPath id="lc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18"/></clipPath>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="url(#lbg)" stroke="{t.border}"/>
<text x="28" y="44" font-family="{MONO}" font-size="12.5" letter-spacing="2.5" fill="{t.muted}">THE LAB · EXPERIMENTS &amp; CASE STUDIES</text>
<text x="28" y="72" font-family="{SANS}" font-size="15" fill="{t.text}">Most of my work lives in private repos — here’s what’s inside, without the code.</text>
<g font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1">
  <circle cx="{W - 262}" cy="40" r="4" fill="{t.green}"/><text x="{W - 252}" y="44" fill="{t.green}">LIVE</text>
  <circle cx="{W - 200}" cy="40" r="4" fill="{t.amber}"/><text x="{W - 190}" y="44" fill="{t.amber}">BUILDING</text>
  <circle cx="{W - 106}" cy="40" r="4" fill="{t.purple}"/><text x="{W - 96}" y="44" fill="{t.purple}">R&amp;D</text>
</g>
{''.join(tiles)}
<g clip-path="url(#lc)"><rect y="{top}" width="220" height="{H - top}" fill="url(#shine)" transform="skewX(-18)">
  <animate attributeName="x" values="-400;{W + 300}" dur="7s" repeatCount="indefinite"/></rect></g>
"""
    return svg_doc(W, H, body, title="The Lab: case studies from private repos — Mailcore, LeadQ v2, FlowMail AI, SendPilots, SendPilot Flow, Nova Warmup and more", css=css)


# --------------------------------------------------------------------------- #
# Build log timeline (from repo creation dates)
# --------------------------------------------------------------------------- #
BUILD_LOG = (  # (month index from Aug 2025, lane, title, subtitle)  lanes: -2/-1 above, 1/2 below
    (0, -1, "Engagement platform", "multi-channel, self-hosted"),
    (1, 1, "Gmail automation R&D", "browser-driven flows"),
    (2, -2, "Yahoo/Outlook warmup", "reputation experiments"),
    (5, 1, "Nova Warmup", "+ Laravel email platform"),
    (7, -1, "Mailcore (Rust)", "+ Postal fork"),
    (8, 2, "SendPilots v2 → v3", "Django + React rebuild"),
    (9, -2, "FlowMail AI", "agent services · sendpilots.com"),
    (10, 1, "SendPilot Flow", "email · voice · LinkedIn"),
    (11, -1, "Mailu research", "containerised mail stack"),
    (12, 2, "LeadQ v2 (Go)", "SMTP/IMAP engine"),
    (13, -2, "now", "LeadQ phase 5/8 ✓"),
)
MONTHS = ("Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep")


def build_log(t: Theme) -> str:
    W, H, x0, x1, ay = 1200, 360, 60, 1140, 186
    step = (x1 - x0) / (len(MONTHS) - 1)
    dur = 9.0
    palette = (t.cyan, t.purple, t.pink, t.green, t.amber, t.blue)
    ticks = "".join(
        f'<line x1="{fmt(round(x0 + i * step, 1))}" x2="{fmt(round(x0 + i * step, 1))}" y1="{ay - 5}" y2="{ay + 5}" stroke="{t.border}" stroke-width="1.5"/>'
        f'<text x="{fmt(round(x0 + i * step, 1))}" y="{ay + 22}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{t.muted}">{m}</text>'
        for i, m in enumerate(MONTHS)
    )
    years = (f'<text x="{x0}" y="{ay + 40}" font-family="{MONO}" font-size="10.5" font-weight="700" fill="{t.muted}">2025</text>'
             f'<text x="{fmt(round(x0 + 5 * step, 1))}" y="{ay + 40}" text-anchor="middle" font-family="{MONO}" font-size="10.5" font-weight="700" fill="{t.muted}">2026</text>')
    events = []
    for i, (mi, lane, title, sub) in enumerate(BUILD_LOG):
        x = x0 + mi * step
        up = lane < 0
        colour = t.green if title == "now" else palette[i % len(palette)]
        ly = {-2: ay - 100, -1: ay - 56, 1: ay + 66, 2: ay + 110}[lane]
        arrive = dur * 0.8 * mi / (len(MONTHS) - 1)
        anchor = "start" if x < 140 else ("end" if x > 1060 else "middle")
        events.append(
            f'<line x1="{fmt(round(x, 1))}" x2="{fmt(round(x, 1))}" y1="{ay}" y2="{ly + (14 if up else -26)}" stroke="{colour}" stroke-opacity=".45" stroke-dasharray="2 3"/>'
            f'<circle cx="{fmt(round(x, 1))}" cy="{ay}" r="6.5" fill="{t.bg0}" stroke="{colour}" stroke-width="2"/>'
            f'<circle cx="{fmt(round(x, 1))}" cy="{ay}" r="6.5" fill="{colour}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{fmt(round(arrive / dur, 3))};{fmt(round(min(arrive / dur + 0.02, 0.97), 3))};.97;1" dur="{fmt(dur)}s" repeatCount="indefinite"/></circle>'
            f'<text x="{fmt(round(x, 1))}" y="{ly}" text-anchor="{anchor}" font-family="{SANS}" font-size="13.5" font-weight="700" fill="{t.text}">{esc(title)}</text>'
            f'<text x="{fmt(round(x, 1))}" y="{ly + 17}" text-anchor="{anchor}" font-family="{SANS}" font-size="12" fill="{t.muted}">{esc(sub)}</text>'
        )
    end_x = x0 + 13 * step
    body = f"""
<defs>
  <linearGradient id="blbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t.bg0}"/><stop offset="1" stop-color="{t.bg1}"/></linearGradient>
  <linearGradient id="blAur" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t.cyan}"/><stop offset=".5" stop-color="{t.purple}"/><stop offset="1" stop-color="{t.pink}"/></linearGradient>
  <filter id="bg2" x="-150%" y="-150%" width="400%" height="400%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="url(#blbg)" stroke="{t.border}"/>
<text x="28" y="40" font-family="{MONO}" font-size="12.5" letter-spacing="2.5" fill="{t.muted}">BUILD LOG · AUG 2025 → NOW</text>
<text x="{W - 28}" y="40" text-anchor="end" font-family="{MONO}" font-size="11.5" fill="{t.muted}">from my repo history</text>
<line x1="{x0}" x2="{x1}" y1="{ay}" y2="{ay}" stroke="{t.border}" stroke-width="3" stroke-linecap="round"/>
<line x1="{x0}" x2="{fmt(round(end_x, 1))}" y1="{ay}" y2="{ay}" stroke="url(#blAur)" stroke-width="3.5" stroke-linecap="round" stroke-dasharray="{fmt(round(end_x - x0, 1))}" stroke-dashoffset="{fmt(round(end_x - x0, 1))}">
  <animate attributeName="stroke-dashoffset" values="{fmt(round(end_x - x0, 1))};0;0" keyTimes="0;.8;1" dur="{fmt(dur)}s" repeatCount="indefinite"/></line>
<circle r="6" cy="{ay}" fill="{t.text}" filter="url(#bg2)"><animate attributeName="cx" values="{x0};{fmt(round(end_x, 1))};{fmt(round(end_x, 1))}" keyTimes="0;.8;1" dur="{fmt(dur)}s" repeatCount="indefinite"/></circle>
{ticks}{years}{''.join(events)}
<circle cx="{fmt(round(end_x, 1))}" cy="{ay}" r="9" fill="none" stroke="{t.green}"><animate attributeName="r" values="9;24" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values=".9;0" dur="2s" repeatCount="indefinite"/></circle>
"""
    return svg_doc(W, H, body, title="Build log from August 2025 to now: engagement platform, warmup R&D, Nova Warmup, Mailcore in Rust, SendPilots rebuild, FlowMail AI, SendPilot Flow, LeadQ v2")


# --------------------------------------------------------------------------- #
ASSETS: dict[str, Callable[[Theme], str]] = {
    "hero": hero,
    "smtp-terminal": terminal,
    "pipeline": pipeline,
    "project-sendpilots": project_card("sendpilots"),
    "project-email-platform": project_card("new_email_app"),
    "footer": footer,
    "global-mesh": global_mesh,
    "rulebook-2026": rulebook,
    "agent-fleet": agent_fleet,
    "lab": lab,
    "build-log": build_log,
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
