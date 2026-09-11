"""Shared primitives for the profile's hand-built SVGs.

Everything here is stdlib-only and deterministic, so the generated assets are
reproducible and diff cleanly in git.

Why SVG + SMIL/CSS instead of GIFs or third-party widgets:
  * GitHub renders SVGs through its image proxy (camo) as <img>. Scripts are
    stripped, but CSS keyframes and SMIL animations still run.
  * Vector = crisp on retina, ~5-20 KB per asset, no external uptime risk.
"""
from __future__ import annotations

from dataclasses import dataclass
from xml.sax.saxutils import escape as _xml_escape

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"


@dataclass(frozen=True, slots=True)
class Theme:
    name: str
    bg0: str
    bg1: str
    panel: str
    border: str
    text: str
    muted: str
    blue: str
    purple: str
    green: str
    amber: str
    pink: str
    red: str
    glow_opacity: float


DARK = Theme(
    name="dark", bg0="#0d1117", bg1="#0b0f1a", panel="#161b22", border="#30363d",
    text="#e6edf3", muted="#8b949e", blue="#58a6ff", purple="#a371f7",
    green="#3fb950", amber="#d29922", pink="#f778ba", red="#f85149", glow_opacity=0.35,
)
LIGHT = Theme(
    name="light", bg0="#ffffff", bg1="#f6f8fa", panel="#f6f8fa", border="#d0d7de",
    text="#1f2328", muted="#59636e", blue="#0969da", purple="#8250df",
    green="#1a7f37", amber="#9a6700", pink="#bf3989", red="#cf222e", glow_opacity=0.16,
)
THEMES: tuple[Theme, ...] = (DARK, LIGHT)


def esc(text: object) -> str:
    """Escape any dynamic text before it lands in SVG markup (XSS / broken XML)."""
    return _xml_escape(str(text), {'"': "&quot;"})


def svg_doc(width: int, height: int, body: str, *, title: str, css: str = "") -> str:
    reduced = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">'
        f"<title>{esc(title)}</title>"
        f"<style>{css}{reduced}</style>"
        f"{body}</svg>\n"
    )


def fmt(x: float) -> str:
    """Compact number formatting for SVG attributes (keeps files small)."""
    return f"{x:.3f}".rstrip("0").rstrip(".") if isinstance(x, float) else str(x)


def discrete_anim(attr: str, frames: list[tuple[float, float]], dur: float, *, begin: str = "0s") -> str:
    """SMIL <animate> with calcMode=discrete from (time_seconds, value) frames.

    Used for true character-by-character typing (clip width steps) because
    CSS steps() cannot be combined per-keyframe reliably across browsers.
    """
    frames = sorted(frames, key=lambda f: f[0])
    if frames[0][0] > 0:
        frames.insert(0, (0.0, frames[0][1]))
    # dedupe identical timestamps (keep the last value written)
    dedup: dict[float, float] = {}
    for t, v in frames:
        dedup[round(t, 4)] = v
    times = sorted(dedup)
    key_times = ";".join(fmt(min(t / dur, 1.0)) for t in times)
    values = ";".join(fmt(dedup[t]) for t in times)
    return (
        f'<animate attributeName="{attr}" calcMode="discrete" dur="{fmt(dur)}s" begin="{begin}" '
        f'repeatCount="indefinite" keyTimes="{key_times}" values="{values}"/>'
    )
