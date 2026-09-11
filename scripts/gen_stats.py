#!/usr/bin/env python3
"""Self-hosted GitHub stats cards (replaces rate-limited public Vercel widgets).

Pulls data from the GitHub GraphQL API and renders animated SVG cards:

    stats-{dark,light}.svg     contribution overview + 52-week sparkline
    langs-{dark,light}.svg     language mix by bytes across owned, non-fork repos
    activity-{dark,light}.svg  12-month heatmap with a travelling scan wave

Usage (CI):
    GITHUB_TOKEN=... python3 scripts/gen_stats.py --user arunkuttysend --out dist/stats

Offline / preview:
    python3 scripts/gen_stats.py --fixture sample.json --out /tmp/preview

Exit code is non-zero on any API failure and NO files are written in that
case, so the previously published cards stay online instead of breaking.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svgkit import MONO, SANS, THEMES, Theme, esc, fmt, svg_doc  # noqa: E402

log = logging.getLogger("gen_stats")
API = "https://api.github.com/graphql"
HEX = re.compile(r"^#[0-9a-fA-F]{3,8}$")

PROFILE_Q = """
query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){
    login name
    followers{totalCount}
    pullRequests{totalCount}
    issues{totalCount}
    contributionsCollection(from:$from,to:$to){
      totalCommitContributions restrictedContributionsCount
      totalPullRequestContributions totalPullRequestReviewContributions totalIssueContributions
      contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } }
    }
  }
}"""
REPOS_Q = """
query($login:String!,$cursor:String){
  user(login:$login){
    repositories(first:100,after:$cursor,ownerAffiliations:OWNER,isFork:false){
      totalCount pageInfo{hasNextPage endCursor}
      nodes{ stargazerCount forkCount
        languages(first:10,orderBy:{field:SIZE,direction:DESC}){ edges{ size node{ name color } } } }
    }
  }
}"""
COMMITS_Q = """
query($login:String!,$since:GitTimestamp!){
  user(login:$login){
    repositories(first:25,ownerAffiliations:OWNER,orderBy:{field:PUSHED_AT,direction:DESC}){
      nodes{ isFork defaultBranchRef{ target{ ... on Commit {
        history(first:100,since:$since){ nodes{ committedDate author{ user{ login } } } } } } } }
    }
  }
}"""
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
PULSE_DAYS = 90


# --------------------------------------------------------------------------- #
# Data access
# --------------------------------------------------------------------------- #
class GitHubError(RuntimeError):
    pass


def graphql(token: str, query: str, variables: dict[str, Any], *, attempts: int = 4) -> dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        API, data=payload, method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-stats-generator"},
    )
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.load(resp)
            if body.get("errors"):
                raise GitHubError(f"GraphQL errors: {body['errors']}")
            return body["data"]
        except urllib.error.HTTPError as exc:
            retryable = exc.code >= 500 or exc.code in (403, 429)   # 403/429 = secondary rate limit
            if not retryable or attempt == attempts:
                raise GitHubError(f"HTTP {exc.code}: {exc.read()[:300]!r}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == attempts:
                raise GitHubError(f"network error: {exc}") from exc
        delay = 2 ** attempt
        log.warning("GitHub API attempt %d/%d failed, retrying in %ss", attempt, attempts, delay)
        time.sleep(delay)
    raise AssertionError("unreachable")


def fetch(token: str, login: str) -> dict[str, Any]:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    frm = now - dt.timedelta(days=365)
    profile = graphql(token, PROFILE_Q, {"login": login, "from": frm.isoformat(), "to": now.isoformat()})["user"]
    if profile is None:
        raise GitHubError(f"user {login!r} not found")
    repos: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        page = graphql(token, REPOS_Q, {"login": login, "cursor": cursor})["user"]["repositories"]
        repos.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    profile["repos"] = repos
    profile["generated_at"] = now.isoformat()
    profile["commit_times"] = fetch_commit_times(token, login, now)
    return profile


def fetch_commit_times(token: str, login: str, now: dt.datetime) -> list[str]:
    """Commit timestamps (UTC ISO) authored by `login` on the 25 most recently pushed repos.

    Only timestamps leave this function — no repo names or messages — so private
    work contributes to the rhythm chart without being disclosed.
    """
    since = (now - dt.timedelta(days=PULSE_DAYS)).isoformat()
    data = graphql(token, COMMITS_Q, {"login": login, "since": since})["user"]["repositories"]["nodes"]
    out: list[str] = []
    for repo in data:
        target = (repo.get("defaultBranchRef") or {}).get("target") or {}
        for c in (target.get("history") or {}).get("nodes", []):
            user = (c.get("author") or {}).get("user") or {}
            if (user.get("login") or "").lower() == login.lower():
                out.append(c["committedDate"])
    return out


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #
@dataclass(slots=True)
class Stats:
    login: str
    generated: dt.date
    contributions: int
    commits: int
    prs: int
    reviews: int
    issues: int
    private: int
    stars: int
    followers: int
    repos: int
    current_streak: int
    longest_streak: int
    days: list[tuple[dt.date, int]] = field(default_factory=list)
    langs: list[tuple[str, str, float]] = field(default_factory=list)   # (name, colour, share)
    hours: list[int] = field(default_factory=lambda: [0] * 24)          # commits per IST hour
    weekdays: list[int] = field(default_factory=lambda: [0] * 7)        # Mon..Sun
    commits_90d: int = 0


def streaks(days: list[tuple[dt.date, int]], today: dt.date) -> tuple[int, int]:
    longest = run = 0
    for _, n in days:
        run = run + 1 if n > 0 else 0
        longest = max(longest, run)
    current = 0
    for d, n in reversed(days):
        if d == today and n == 0:      # today not over yet — don't break the streak
            continue
        if n == 0:
            break
        current += 1
    return current, longest


def aggregate(raw: dict[str, Any], exclude: set[str], top: int = 8) -> Stats:
    cc = raw["contributionsCollection"]
    days = sorted(
        (dt.date.fromisoformat(d["date"]), int(d["contributionCount"]))
        for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]
    )
    generated = dt.datetime.fromisoformat(raw["generated_at"]).date()
    cur, longest = streaks(days, generated)

    sizes: dict[str, int] = {}
    colours: dict[str, str] = {}
    for repo in raw["repos"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            if name.lower() in exclude:
                continue
            sizes[name] = sizes.get(name, 0) + int(edge["size"])
            colour = edge["node"].get("color") or "#8b949e"
            colours[name] = colour if HEX.match(colour) else "#8b949e"
    total = sum(sizes.values()) or 1
    ranked = sorted(sizes.items(), key=lambda kv: kv[1], reverse=True)
    langs = [(n, colours[n], s / total) for n, s in ranked[:top]]
    rest = sum(s for _, s in ranked[top:])
    if rest:
        langs.append(("Other", "#6e7681", rest / total))

    hours, weekdays = [0] * 24, [0] * 7
    times = raw.get("commit_times", [])
    for ts in times:
        local = dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(IST)
        hours[local.hour] += 1
        weekdays[local.weekday()] += 1

    return Stats(
        hours=hours, weekdays=weekdays, commits_90d=len(times),
        login=raw["login"], generated=generated,
        contributions=cc["contributionCalendar"]["totalContributions"],
        commits=cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        prs=raw["pullRequests"]["totalCount"], reviews=cc["totalPullRequestReviewContributions"],
        issues=raw["issues"]["totalCount"], private=cc["restrictedContributionsCount"],
        stars=sum(r["stargazerCount"] for r in raw["repos"]),
        followers=raw["followers"]["totalCount"], repos=len(raw["repos"]),
        current_streak=cur, longest_streak=longest, days=days, langs=langs,
    )


def human(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M".replace(".0M", "M")
    if n >= 10_000:
        return f"{n / 1000:.0f}k"
    if n >= 1_000:
        return f"{n / 1000:.1f}k".replace(".0k", "k")
    return str(n)


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
CARD_CSS = (
    # `both` + no base-state hiding: with reduced motion (animation:none) everything stays visible
    ".row{animation:rise .6s ease-out both}"
    "@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}"
    ".draw{stroke-dasharray:2000;animation:draw 2.4s ease-out .3s both}"
    "@keyframes draw{from{stroke-dashoffset:2000}to{stroke-dashoffset:0}}"
    ".pulse{animation:pulse 2s ease-in-out infinite}@keyframes pulse{50%{opacity:.3}}"
)


def _frame(t: Theme, W: int, H: int, title: str, right: str) -> str:
    return (
        f'<defs><linearGradient id="bgc" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t.bg0}"/>'
        f'<stop offset="1" stop-color="{t.panel}"/></linearGradient></defs>'
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="url(#bgc)" stroke="{t.border}"/>'
        f'<text x="24" y="36" font-family="{SANS}" font-size="16" font-weight="700" fill="{t.text}">{esc(title)}</text>'
        f'<text x="{W - 24}" y="36" text-anchor="end" font-family="{MONO}" font-size="11.5" fill="{t.muted}">{esc(right)}</text>'
    )


def stats_card(s: Stats, t: Theme) -> str:
    W, H = 590, 260
    items = (
        ("Contributions · 12 mo", human(s.contributions), t.blue),
        ("Commits", human(s.commits), t.green),
        ("Pull requests", human(s.prs), t.purple),
        ("Code reviews", human(s.reviews), t.pink),
        ("Current streak", f"{s.current_streak} d", t.amber),
        ("Longest streak", f"{s.longest_streak} d", t.amber),
        ("Stars earned", human(s.stars), t.amber),
        ("Repositories", human(s.repos), t.blue),
    )
    rows = []
    for i, (label, value, colour) in enumerate(items):
        col, row = i % 2, i // 2
        x, y = 24 + col * 280, 70 + row * 30
        rows.append(
            f'<g class="row" style="animation-delay:{fmt(0.08 * i)}s">'
            f'<circle cx="{x + 4}" cy="{y - 4}" r="3.5" fill="{colour}"/>'
            f'<text x="{x + 16}" y="{y}" font-family="{SANS}" font-size="13.5" fill="{t.muted}">{esc(label)}</text>'
            f'<text x="{x + 250}" y="{y}" text-anchor="end" font-family="{MONO}" font-size="14" font-weight="700" fill="{t.text}">{esc(value)}</text></g>'
        )

    # weekly sparkline
    weekly: list[int] = []
    for i in range(0, len(s.days), 7):
        weekly.append(sum(n for _, n in s.days[i:i + 7]))
    weekly = weekly[-52:] or [0]
    peak = max(weekly) or 1
    sx, sy, sw, sh = 24, 196, W - 48, 44
    pts = [(sx + sw * i / max(len(weekly) - 1, 1), sy + sh - sh * v / peak) for i, v in enumerate(weekly)]
    line = "M" + " L".join(f"{fmt(x)},{fmt(y)}" for x, y in pts)
    area = f"{line} L{fmt(sx + sw)},{sy + sh} L{sx},{sy + sh} Z"
    spark = (
        f'<defs><linearGradient id="sa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t.blue}" stop-opacity=".35"/>'
        f'<stop offset="1" stop-color="{t.blue}" stop-opacity="0"/></linearGradient></defs>'
        f'<text x="24" y="{sy - 8}" font-family="{MONO}" font-size="11" fill="{t.muted}">weekly contributions · peak {peak}</text>'
        f'<path d="{area}" fill="url(#sa)" class="row" style="animation-delay:.9s"/>'
        f'<path id="spark" d="{line}" fill="none" stroke="{t.blue}" stroke-width="2" stroke-linejoin="round" class="draw"/>'
        f'<circle r="4" fill="{t.blue}" stroke="{t.bg0}" stroke-width="2"><animateMotion dur="9s" repeatCount="indefinite">'
        f'<mpath href="#spark"/></animateMotion></circle>'
    )
    body = _frame(t, W, H, "Telemetry", f"updated {s.generated.isoformat()}") + "".join(rows) + spark
    return svg_doc(W, H, body, title=f"GitHub stats for {s.login}", css=CARD_CSS)


def langs_card(s: Stats, t: Theme) -> str:
    W, H = 590, 260
    bx, by, bw = 24, 62, W - 48
    segs, legend, x = [], [], float(bx)
    for i, (name, colour, share) in enumerate(s.langs):
        w = bw * share
        segs.append(
            f'<rect x="{fmt(x)}" y="{by}" height="12" width="0" fill="{colour}">'
            f'<animate attributeName="width" from="0" to="{fmt(w)}" dur=".7s" begin="{fmt(0.15 + i * 0.12)}s" fill="freeze" '
            f'calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect>'
        )
        x += w
        col, row = i % 2, i // 2
        lx, ly = 24 + col * 280, 110 + row * 30
        legend.append(
            f'<g class="row" style="animation-delay:{fmt(0.3 + 0.07 * i)}s">'
            f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{colour}"/>'
            f'<text x="{lx + 18}" y="{ly}" font-family="{SANS}" font-size="13.5" fill="{t.text}">{esc(name)}</text>'
            f'<text x="{lx + 250}" y="{ly}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{t.muted}">{share * 100:.1f}%</text></g>'
        )
    body = (
        _frame(t, W, H, "Languages", f"by bytes · {s.repos} repos")
        + f'<defs><clipPath id="bar"><rect x="{bx}" y="{by}" width="{bw}" height="12" rx="6"/></clipPath></defs>'
        + f'<rect x="{bx}" y="{by}" width="{bw}" height="12" rx="6" fill="{t.border}" opacity=".5"/>'
        + f'<g clip-path="url(#bar)">{"".join(segs)}</g>'
        + "".join(legend)
    )
    return svg_doc(W, H, body, title=f"Top languages for {s.login}", css=CARD_CSS)


def activity_card(s: Stats, t: Theme) -> str:
    W, H = 1200, 250
    cell, gap = 16, 4
    days = s.days[-371:]
    if not days:
        days = [(s.generated, 0)]
    first_dow = (days[0][0].weekday() + 1) % 7     # GitHub grid: Sunday = row 0
    peak = max(n for _, n in days) or 1
    ramp = [0.25, 0.5, 0.75, 1.0]
    ncols = (len(days) + first_dow + 6) // 7
    gx = round((W - ncols * (cell + gap) + gap) / 2)
    cols: dict[int, list[str]] = {}
    for i, (d, n) in enumerate(days):
        idx = i + first_dow
        c, r = idx // 7, idx % 7
        x, y = gx + c * (cell + gap), 62 + r * (cell + gap)
        if n == 0:
            fill, op = t.border, 0.55
        else:
            lvl = min(3, int(4 * n / (peak + 1)))
            fill, op = t.green, ramp[lvl]
        cols.setdefault(c, []).append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3.5" fill="{fill}" opacity="{op}">'
            f'<title>{d.isoformat()}: {n}</title></rect>'
        )
    wave = 6.0
    groups = "".join(
        f'<g class="col" style="animation-delay:{fmt(wave * c / ncols)}s">{"".join(rects)}</g>'
        for c, rects in sorted(cols.items())
    )
    # month labels
    months, seen = [], set()
    for i, (d, _) in enumerate(days):
        if d.day <= 7 and d.month not in seen and d.weekday() == 6:
            seen.add(d.month)
            c = (i + first_dow) // 7
            months.append(f'<text x="{gx + c * (cell + gap)}" y="54" font-family="{MONO}" font-size="11" fill="{t.muted}">{d.strftime("%b")}</text>')
    beam_w = 90
    css = (
        f".col{{animation:wave {fmt(wave)}s ease-in-out infinite}}"
        f"@keyframes wave{{0%,100%{{filter:none}}6%{{filter:brightness(1.9) saturate(1.3)}}14%{{filter:none}}}}"
    )
    legend = "".join(
        f'<rect x="{W - 150 + i * 20}" y="{H - 36}" width="14" height="14" rx="3" fill="{t.green if i else t.border}" opacity="{([0.55] + ramp)[i]}"/>'
        for i in range(5)
    )
    body = (
        _frame(t, W, H, "Contribution field · last 12 months",
               f"{s.contributions} contributions · streak {s.current_streak}d · best {s.longest_streak}d")
        + "".join(months) + groups
        + f'<defs><linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="{t.blue}" stop-opacity="0"/>'
          f'<stop offset=".5" stop-color="{t.blue}" stop-opacity=".18"/><stop offset="1" stop-color="{t.blue}" stop-opacity="0"/></linearGradient></defs>'
        + f'<rect y="58" width="{beam_w}" height="{7 * (cell + gap)}" fill="url(#beam)">'
          f'<animate attributeName="x" values="{gx - beam_w};{gx + ncols * (cell + gap)}" dur="{fmt(wave)}s" repeatCount="indefinite"/></rect>'
        + f'<text x="{W - 160}" y="{H - 25}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{t.muted}">less</text>'
        + legend
        + f'<text x="{W - 46}" y="{H - 25}" font-family="{MONO}" font-size="11" fill="{t.muted}">more</text>'
    )
    return svg_doc(W, H, body, title=f"Contribution heatmap for {s.login}", css=css)


def peak_window(hours: list[int], width: int = 3) -> int:
    """Start hour of the busiest `width`-hour window (wraps around midnight)."""
    return max(range(24), key=lambda h: sum(hours[(h + i) % 24] for i in range(width)))


def pulse_card(s: Stats, t: Theme) -> str:
    import math
    W, H = 1200, 304
    cx, cy, r0, rmax = 196, 176, 36, 94
    peak = max(s.hours) or 1
    bars = []
    for h, n in enumerate(s.hours):
        a = -math.pi / 2 + 2 * math.pi * (h + 0.5) / 24
        length = (rmax - r0) * n / peak if n else 2
        x1, y1 = cx + r0 * math.cos(a), cy + r0 * math.sin(a)
        x2, y2 = cx + (r0 + length) * math.cos(a), cy + (r0 + length) * math.sin(a)
        colour = t.purple if (h >= 22 or h < 5) else (t.cyan if h < 17 else t.pink)
        bars.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{colour}" stroke-width="9" stroke-linecap="round" '
            f'stroke-dasharray="{length + 2:.1f}" stroke-dashoffset="{length + 2:.1f}">'
            f'<animate attributeName="stroke-dashoffset" to="0" dur=".8s" begin="{0.03 * h:.2f}s" fill="freeze"/></line>'
        )
    labels = "".join(
        f'<text x="{cx + (rmax + 16) * math.cos(-math.pi / 2 + 2 * math.pi * h / 24):.1f}" '
        f'y="{cy + 4 + (rmax + 16) * math.sin(-math.pi / 2 + 2 * math.pi * h / 24):.1f}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="10.5" fill="{t.muted}">{h:02d}</text>'
        for h in (0, 6, 12, 18)
    )
    sweep = (
        f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - rmax - 4}" stroke="{t.text}" stroke-opacity=".5" stroke-width="1.5">'
        f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="12s" repeatCount="indefinite"/></line>'
        f'<circle cx="{cx}" cy="{cy}" r="{r0 - 8}" fill="{t.bg0}" stroke="{t.border}"/>'
        f'<text x="{cx}" y="{cy - 2}" text-anchor="middle" font-family="{MONO}" font-size="15" font-weight="800" fill="{t.text}">IST</text>'
        f'<text x="{cx}" y="{cy + 13}" text-anchor="middle" font-family="{MONO}" font-size="9" fill="{t.muted}">24h</text>'
    )
    # weekday bars
    wx, wy, wh, bw = 372, 256, 150, 34
    wpeak = max(s.weekdays) or 1
    wbars = []
    for i, (name, n) in enumerate(zip(("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"), s.weekdays)):
        h = max(3.0, wh * n / wpeak)
        x = wx + i * (bw + 14)
        wbars.append(
            f'<rect x="{x}" y="{wy - h:.1f}" width="{bw}" height="{h:.1f}" rx="6" fill="url(#wk)">'
            f'<animate attributeName="height" from="0" to="{h:.1f}" dur=".7s" begin="{0.3 + 0.06 * i:.2f}s" fill="freeze"/>'
            f'<animate attributeName="y" from="{wy}" to="{wy - h:.1f}" dur=".7s" begin="{0.3 + 0.06 * i:.2f}s" fill="freeze"/></rect>'
            f'<text x="{x + bw / 2}" y="{wy + 18}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{t.muted}">{name}</text>'
            f'<text x="{x + bw / 2}" y="{wy - h - 7:.1f}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{t.text}">{n}</text>'
        )
    start = peak_window(s.hours)
    night = sum(s.hours[h] for h in (22, 23, 0, 1, 2, 3, 4))
    total = sum(s.hours) or 1
    busiest_day = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")[max(range(7), key=lambda i: s.weekdays[i])]
    facts = (
        ("peak window", f"{start:02d}:00–{(start + 3) % 24:02d}:00 IST", t.cyan),
        (f"commits · last {PULSE_DAYS} days", str(s.commits_90d), t.text),
        ("busiest day", busiest_day, t.pink),
        ("after-hours share (22–05)", f"{100 * night / total:.0f}%", t.purple),
    )
    fx = 770
    frows = "".join(
        f'<g class="row" style="animation-delay:{0.5 + 0.1 * i:.1f}s">'
        f'<text x="{fx}" y="{104 + i * 46}" font-family="{SANS}" font-size="13" fill="{t.muted}">{esc(label)}</text>'
        f'<text x="{W - 32}" y="{104 + i * 46}" text-anchor="end" font-family="{MONO}" font-size="20" font-weight="800" fill="{colour}">{esc(value)}</text>'
        f'<line x1="{fx}" x2="{W - 32}" y1="{118 + i * 46}" y2="{118 + i * 46}" stroke="{t.border}"/></g>'
        for i, (label, value, colour) in enumerate(facts)
    )
    body = (
        f'<defs><linearGradient id="wk" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{t.cyan}"/>'
        f'<stop offset="1" stop-color="{t.purple}"/></linearGradient></defs>'
        + _frame(t, W, H, "Coding pulse · when I ship", f"commit rhythm · last {PULSE_DAYS} days · IST")
        + f'<circle cx="{cx}" cy="{cy}" r="{rmax}" fill="none" stroke="{t.border}" stroke-dasharray="2 5"/>'
        + "".join(bars) + labels + sweep + "".join(wbars) + frows
    )
    return svg_doc(W, H, body, title=f"Coding pulse for {s.login}: commits by hour of day (IST) and weekday", css=CARD_CSS)


# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--user", default=os.environ.get("GITHUB_USER", "arunkuttysend"))
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--fixture", type=Path, help="render from a saved JSON payload instead of the API")
    ap.add_argument("--dump", type=Path, help="also save the raw API payload (for fixtures/debugging)")
    ap.add_argument("--exclude", default=os.environ.get("EXCLUDE_LANGS", ""),
                    help="comma-separated languages to ignore, e.g. 'HTML,Blade'")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    try:
        if args.fixture:
            raw = json.loads(args.fixture.read_text(encoding="utf-8"))
        else:
            token = os.environ.get("GITHUB_TOKEN", "").strip()
            if not token:
                log.error("GITHUB_TOKEN is not set")
                return 2
            raw = fetch(token, args.user)
        stats = aggregate(raw, {x.strip().lower() for x in args.exclude.split(",") if x.strip()})
    except (GitHubError, KeyError, ValueError) as exc:
        log.error("could not build stats: %s", exc)
        return 1

    # Render everything in memory first; only touch disk once all cards succeeded.
    rendered = {
        f"{name}-{t.name}.svg": fn(stats, t)
        for name, fn in (("stats", stats_card), ("langs", langs_card), ("activity", activity_card), ("pulse", pulse_card))
        for t in THEMES
    }
    args.out.mkdir(parents=True, exist_ok=True)
    for fname, svg in rendered.items():
        (args.out / fname).write_text(svg, encoding="utf-8")
    if args.dump:
        args.dump.write_text(json.dumps(raw, indent=1), encoding="utf-8")
    log.info("wrote %d cards to %s (%d contributions, %d repos, %d languages)",
             len(rendered), args.out, stats.contributions, stats.repos, len(stats.langs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
