#!/usr/bin/env python3
"""Generate assets/top-langs.svg from ALL repos, including private ones.

Third-party card services only see public repos, which badly misrepresents
this account (C++ lives in private repos). Requires `gh` to be authenticated
with the `repo` scope.
"""
import collections
import json
import pathlib
import subprocess

# GitHub Linguist colours.
COLORS = {
    "C++": "#f34b7d", "Python": "#3572A5", "C": "#555555", "HTML": "#e34c26",
    "JavaScript": "#f1e05a", "Shell": "#89e051", "PowerShell": "#012456",
    "CMake": "#DA3434", "Jinja": "#a52a22", "Makefile": "#427819",
    "CSS": "#563d7c", "PLpgSQL": "#336790", "Cypher": "#34c0eb",
    "Batchfile": "#C1F12E", "Xmake": "#22a6b3", "Go": "#00ADD8",
}
FALLBACK = "#8b949e"
TOP_N = 6
W, PAD, BAR_H = 420, 20, 10
BG, FG, MUTED, BORDER = "#1a1b27", "#c0caf5", "#a9b1d6", "#00ff41"


def gh(*args):
    out = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    return out.stdout


def collect():
    repos = gh("api", "user/repos", "--paginate", "--jq",
               ".[] | select(.fork==false) | .full_name").split()
    totals = collections.Counter()
    for full in repos:
        try:
            totals.update(json.loads(gh("api", f"repos/{full}/languages")))
        except subprocess.CalledProcessError:
            continue
    return totals


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(totals):
    total = sum(totals.values()) or 1
    top = totals.most_common(TOP_N)
    shown = sum(v for _, v in top)
    rows = [(k, v * 100.0 / total) for k, v in top]
    if total > shown:
        rows.append(("Other", (total - shown) * 100.0 / total))

    bar_w = W - 2 * PAD
    rows_per_col, col_w = (len(rows) + 1) // 2, bar_w // 2
    h = PAD + 26 + BAR_H + 18 + rows_per_col * 20 + PAD

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
         f'viewBox="0 0 {W} {h}" font-family="Segoe UI,Ubuntu,sans-serif">',
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="6" fill="{BG}" '
         f'stroke="{BORDER}" stroke-opacity="0.55"/>',
         f'<text x="{PAD}" y="{PAD+14}" fill="{BORDER}" font-size="15" '
         f'font-weight="600">Most Used Languages</text>',
         f'<text x="{W-PAD}" y="{PAD+14}" fill="{MUTED}" font-size="10" '
         f'text-anchor="end">public + private</text>']

    # Stacked bar.
    y = PAD + 26
    p.append(f'<mask id="m"><rect x="{PAD}" y="{y}" width="{bar_w}" '
             f'height="{BAR_H}" rx="5" fill="#fff"/></mask>')
    p.append(f'<g mask="url(#m)">')
    x = float(PAD)
    for name, pct in rows:
        seg = bar_w * pct / 100.0
        p.append(f'<rect x="{x:.2f}" y="{y}" width="{seg:.2f}" height="{BAR_H}" '
                 f'fill="{COLORS.get(name, FALLBACK)}"/>')
        x += seg
    p.append('</g>')

    # Two-column legend.
    ly = y + BAR_H + 26
    for i, (name, pct) in enumerate(rows):
        cx = PAD + (i // rows_per_col) * col_w
        cy = ly + (i % rows_per_col) * 20
        p.append(f'<circle cx="{cx+5}" cy="{cy-4}" r="5" '
                 f'fill="{COLORS.get(name, FALLBACK)}"/>')
        p.append(f'<text x="{cx+18}" y="{cy}" fill="{FG}" font-size="12">'
                 f'{esc(name)}</text>')
        p.append(f'<text x="{cx+col_w-34}" y="{cy}" fill="{MUTED}" font-size="12">'
                 f'{pct:.1f}%</text>')
    p.append('</svg>')
    return "\n".join(p)


if __name__ == "__main__":
    totals = collect()
    out = pathlib.Path(__file__).resolve().parent.parent / "assets" / "top-langs.svg"
    out.write_text(build(totals), encoding="utf-8")
    print(f"wrote {out}")
    for k, v in totals.most_common(TOP_N):
        print(f"  {k:<12} {v*100.0/sum(totals.values()):6.2f}%")
