#!/usr/bin/env python3
"""Generate assets/lang-{dark,light}.svg — language ground truth.

Counts bytes across ALL of the user's non-fork repos, including private ones,
via authenticated `gh api`. This is the whole point: unauthenticated card
services see only public repos and report Python ~88% / C++ 0% for this
account, which is wrong — the C++ lives in private repos (tos-*).

Requires `gh` authenticated with a token that can read the private repos'
metadata + languages (fine-grained PAT with Metadata: read is enough).
"""
import collections
import json
import pathlib
import subprocess

import tokens as tk

# GitHub Linguist colours (theme-independent — languages own their colour).
COLORS = {
    "C++": "#f34b7d", "Python": "#3572A5", "C": "#555555", "HTML": "#e34c26",
    "JavaScript": "#f1e05a", "Shell": "#89e051", "PowerShell": "#012456",
    "CMake": "#DA3434", "Jinja": "#a52a22", "Makefile": "#427819",
    "CSS": "#563d7c", "PLpgSQL": "#336790", "Cypher": "#34c0eb",
    "Batchfile": "#C1F12E", "Xmake": "#22a6b3", "Go": "#00ADD8",
}
FALLBACK = "#8b949e"
TOP_N = 6
ROW_H = 26
BAR_X = 116          # where the bar track starts (after the language label)
PCT_X = tk.CARD_W - tk.PAD


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True,
                          check=True).stdout


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


def build(totals, theme):
    t = tk.THEMES[theme]
    total = sum(totals.values()) or 1
    rows = [(k, v * 100.0 / total) for k, v in totals.most_common(TOP_N)]

    top = PAD_TOP = tk.PAD + 22
    h = top + len(rows) * ROW_H + 30
    track_w = PCT_X - BAR_X - 46

    p = tk.open_svg(tk.CARD_W, h,
                    "Language ground truth",
                    "Byte share across all repos including private: " +
                    ", ".join(f"{k} {v:.2f}%" for k, v in rows) +
                    ". Public card services report Python 88% and 0% C++.")
    p.append(tk.defs(t))
    p += tk.frame(t, tk.CARD_W, h)
    p.append(tk.header_row(t, "lang.groundtruth --all-repos"))

    for i, (name, pct) in enumerate(rows):
        y = PAD_TOP + i * ROW_H
        col = COLORS.get(name, FALLBACK)
        bar = max(2.0, track_w * pct / 100.0)
        p.append(f'<text x="{tk.PAD}" y="{y+11}" font-size="12.5" '
                 f'fill="{t["fg"]}">{tk.esc(name)}</text>')
        # Track.
        p.append(f'<rect x="{BAR_X}" y="{y+2}" width="{track_w}" height="11" '
                 f'rx="5.5" fill="{t["track"]}"/>')
        # Fill, animated from 0 -> bar (width, not scaleX, so rx stays round).
        p.append(f'<rect x="{BAR_X}" y="{y+2}" height="11" rx="5.5" '
                 f'fill="{col}"><animate attributeName="width" from="0" '
                 f'to="{bar:.2f}" dur="0.9s" begin="{0.15*i:.2f}s" '
                 f'fill="freeze" calcMode="spline" '
                 f'keySplines="0.2 0.8 0.2 1" keyTimes="0;1" values="0;{bar:.2f}"/>'
                 f'</rect>')
        p.append(tk.num(t, PCT_X, y + 11, f"{pct:.2f}%", size=12,
                        color=t["fg"], weight="600"))

    p.append(f'<text x="{tk.PAD}" y="{h-12}" font-size="9.5" '
             f'fill="{t["muted"]}">all repos incl. private · public cards '
             f'report Python 88% / C++ 0%</text>')
    p.append("</svg>")
    return "\n".join(p)


if __name__ == "__main__":
    totals = collect()
    out_dir = pathlib.Path(__file__).resolve().parent.parent / "assets"
    for theme in ("dark", "light"):
        (out_dir / f"lang-{theme}.svg").write_text(build(totals, theme),
                                                    encoding="utf-8")
    print("wrote lang-dark.svg + lang-light.svg")
    tot = sum(totals.values())
    for k, v in totals.most_common(TOP_N):
        print(f"  {k:<12} {v*100.0/tot:6.2f}%")
