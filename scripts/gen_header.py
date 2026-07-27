#!/usr/bin/env python3
"""Generate assets/header-{dark,light}.svg — the one bespoke, write-once banner.

This is the element templated profiles cannot copy: a hand-authored dossier
header instead of a capsule-render waving banner. Static content (edited only
when focus/languages change), but carries a subtle terminal grid and a
blinking cursor so it feels alive without any third-party service.

Self-contained per the camo CSP: system monospace only, SMIL cursor blink,
no external fonts or images. Rendered at width="100%", swapped dark/light via
<picture> in the README.

The wordmark stays <text> (not <path>): it is a single centred/left-anchored
line with nothing to misalign against, so per-OS metric drift is cosmetic only,
and keeping it as text preserves the exact "0xg00" casing and stays editable.
"""
import pathlib

import tokens as tk

W, H = 860, 200

WORDMARK = "0xg00"
SUBTITLE = "OFFENSIVE SECURITY · ACTIVE DIRECTORY & WINDOWS INTERNALS"
DOSSIER = [
    ("FOCUS", "AD CS · Kerberos · DACL/ACL abuse · dMSA (Server 2025)"),
    ("LANG",  "C/C++ · Python · PowerShell"),
    ("TZ",    "UTC+2"),
]


def build(theme):
    t = tk.THEMES[theme]
    grid = t["accent"]
    # A faint terminal grid clipped to the rounded body.
    grid_lines = []
    for gx in range(40, W, 40):
        grid_lines.append(f'<line x1="{gx}" y1="0" x2="{gx}" y2="{H}"/>')
    for gy in range(40, H, 40):
        grid_lines.append(f'<line x1="0" y1="{gy}" x2="{W}" y2="{gy}"/>')
    grid_svg = (f'<g clip-path="url(#clip)" stroke="{grid}" '
                f'stroke-opacity="0.05" stroke-width="1">'
                + "".join(grid_lines) + '</g>')

    extra = (f'<clipPath id="clip"><rect x="1" y="1" width="{W-2}" '
             f'height="{H-2}" rx="{tk.RX}"/></clipPath>')

    p = tk.open_svg(W, H, f"{WORDMARK} — offensive security",
                    f"{WORDMARK}. {SUBTITLE}. "
                    + " ".join(f"{k}: {v}." for k, v in DOSSIER))
    p.append(tk.defs(t, extra))
    p += tk.frame(t, W, H)
    p.append(grid_svg)

    left = 40
    # Small shell prompt above the wordmark.
    p.append(f'<text x="{left}" y="46" font-size="14" fill="{t["muted"]}">'
             f'<tspan fill="{t["accent"]}">0xg00@red</tspan>:~$ whoami</text>')

    # Wordmark + blinking cursor.
    p.append(f'<text x="{left}" y="104" font-size="58" font-weight="700" '
             f'fill="{t["accent"]}" letter-spacing="1">{tk.esc(WORDMARK)}</text>')
    # Cursor block, blinking via SMIL (allowed under camo CSP).
    p.append(f'<rect x="{left + 178}" y="80" width="22" height="30" '
             f'fill="{t["accent"]}"><animate attributeName="opacity" '
             f'values="1;1;0;0" dur="1.1s" keyTimes="0;0.5;0.5;1" '
             f'repeatCount="indefinite"/></rect>')

    # Subtitle.
    p.append(f'<text x="{left+2}" y="132" font-size="13" fill="{t["muted"]}" '
             f'letter-spacing="2.5">{tk.esc(SUBTITLE)}</text>')

    # Faint rule.
    p.append(f'<line x1="{left}" y1="146" x2="{W-40}" y2="146" '
             f'stroke="{t["border"]}" stroke-opacity="{t["border_op"]}"/>')

    # Dossier lines, evenly spaced on their own rows.
    y = 166
    for label, value in DOSSIER:
        p.append(f'<text x="{left}" y="{y}" font-size="12.5">'
                 f'<tspan fill="{t["accent"]}" font-weight="600">{label}</tspan>'
                 f'<tspan fill="{t["muted"]}">   </tspan>'
                 f'<tspan fill="{t["fg"]}">{tk.esc(value)}</tspan></text>')
        y += 16

    p.append("</svg>")
    return "\n".join(p)


if __name__ == "__main__":
    out_dir = pathlib.Path(__file__).resolve().parent.parent / "assets"
    for theme in ("dark", "light"):
        (out_dir / f"header-{theme}.svg").write_text(build(theme),
                                                      encoding="utf-8")
    print("wrote header-dark.svg + header-light.svg")
