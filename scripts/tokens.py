#!/usr/bin/env python3
"""Shared design tokens and SVG chrome for the self-hosted profile cards.

Every card imports from here so the header, language card and stats card read
as one system: same corner radius, padding, border, drop shadow, type scale
and colour ramp. Two themes are emitted per card (dark / light) because a
single SVG cannot follow GitHub's theme toggle through the camo proxy — the
README swaps them with <picture> + prefers-color-scheme instead.

Hard constraints these tokens respect (verified against the camo CSP
`default-src 'none'; img-src data:; style-src 'unsafe-inline'`):
  - no external fonts (system monospace stack only)
  - no external images (none used)
  - inline <style>/style= and SMIL animation are allowed
"""

RX = 12          # corner radius
PAD = 20         # inner padding
CARD_W = 390     # width that lets two cards sit side by side in the README

# System monospace stack — the only fonts guaranteed to resolve under camo.
MONO = ('ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,'
        '"Liberation Mono",monospace')

# Brand green ramp (dark theme accents).
RAMP = ["#00381a", "#007a24", "#00b32d", "#00ff41"]

THEMES = {
    "dark": {
        "bg0": "#1a1b27", "bg1": "#0d1117",
        "fg": "#c0caf5", "muted": "#7a88b8",
        "accent": "#00ff41", "accent_dim": "#1f6b33",
        "border": "#00ff41", "border_op": "0.30",
        "highlight": "#ffffff", "highlight_op": "0.06",
        "track": "#2a2e42",
    },
    "light": {
        "bg0": "#f6f8fa", "bg1": "#eef1f5",
        "fg": "#1f2328", "muted": "#656d76",
        "accent": "#1a7f37", "accent_dim": "#8fce9c",
        "border": "#1a7f37", "border_op": "0.45",
        "highlight": "#ffffff", "highlight_op": "0.55",
        "track": "#d0d7de",
    },
}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def open_svg(w, h, title, desc):
    """Root <svg> + accessibility metadata. Caller must append defs()/frame()."""
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        f'aria-labelledby="t d" font-family=\'{MONO}\'>',
        f'<title id="t">{esc(title)}</title>',
        f'<desc id="d">{esc(desc)}</desc>',
    ]


def defs(t, extra=""):
    """Shared gradient + drop shadow filter."""
    return (
        '<defs>'
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{t["bg0"]}"/>'
        f'<stop offset="1" stop-color="{t["bg1"]}"/>'
        f'</linearGradient>'
        f'<filter id="sh" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feDropShadow dx="0" dy="1" stdDeviation="2" '
        f'flood-color="#000000" flood-opacity="0.35"/>'
        f'</filter>'
        f'{extra}'
        '</defs>'
    )


def frame(t, w, h):
    """Rounded body: gradient fill, faint green stroke, 1px top highlight."""
    return [
        f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{RX}" '
        f'fill="url(#bg)" stroke="{t["border"]}" '
        f'stroke-opacity="{t["border_op"]}" filter="url(#sh)"/>',
        # 1px inner top highlight for a subtle raised edge.
        f'<rect x="2" y="2" width="{w-4}" height="1" rx="0.5" '
        f'fill="{t["highlight"]}" opacity="{t["highlight_op"]}"/>',
    ]


def header_row(t, prompt, y=PAD + 4):
    """A terminal-style command line used as each card's title."""
    return (
        f'<text x="{PAD}" y="{y}" font-size="12.5" fill="{t["muted"]}">'
        f'<tspan fill="{t["accent"]}">~/</tspan> {esc(prompt)}'
        f'<tspan fill="{t["accent"]}"> _</tspan></text>'
    )


def num(t, x, y, value, size=13, color=None, weight="600"):
    """Right-anchored tabular figure (never overflows when the value grows)."""
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
        f'fill="{color or t["accent"]}" text-anchor="end" '
        f'style="font-variant-numeric:tabular-nums">{esc(value)}</text>'
    )
