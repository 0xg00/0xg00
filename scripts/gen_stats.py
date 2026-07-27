#!/usr/bin/env python3
"""Generate assets/stats-{dark,light}.svg — commit tempo, authenticated.

Shows the real commit volume including private work: the public API reports
~63 commits for this account while the authenticated figure is ~1,690, the
rest being private tooling. Deliberately shows NO stars, followers, PR or
issue counts, and NO streak — those are vanity-adjacent and, for a streak,
silently rot into a lie the day the refresh job dies.

Requires `gh` authenticated. Commit counts come from GraphQL
contributionsCollection (public + restrictedContributionsCount), which needs
no repo-contents access — Metadata-level auth is enough.
"""
import json
import pathlib
import subprocess

import tokens as tk

START_YEAR, END_YEAR = 2021, 2026


def gh_json(query):
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={query}"],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)["data"]


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True,
                          check=True).stdout


def collect():
    public = private = 0
    for year in range(START_YEAR, END_YEAR + 1):
        q = ('{viewer{contributionsCollection(from:"%d-01-01T00:00:00Z",'
             'to:"%d-12-31T23:59:59Z"){totalCommitContributions '
             'restrictedContributionsCount}}}' % (year, year))
        c = gh_json(q)["viewer"]["contributionsCollection"]
        public += c["totalCommitContributions"]
        private += c["restrictedContributionsCount"]

    repos = gh("api", "user/repos", "--paginate", "--jq",
               ".[] | select(.fork==false) | .private").splitlines()
    n_repos = len(repos)
    n_private = sum(1 for r in repos if r.strip() == "true")

    created = gh("api", "user", "--jq", ".created_at").strip()[:4]

    return {
        "public": public, "private": private, "total": public + private,
        "repos": n_repos, "repos_private": n_private, "since": created,
    }


def build(s, theme):
    t = tk.THEMES[theme]
    h = 150
    p = tk.open_svg(tk.CARD_W, h, "Commit tempo (authenticated)",
                    f'{s["total"]} total commits, {s["public"]} public and '
                    f'{s["private"]} in private tooling. {s["repos"]} non-fork '
                    f'repos, {s["repos_private"]} private. Active since '
                    f'{s["since"]}.')
    p.append(tk.defs(t))
    p += tk.frame(t, tk.CARD_W, h)
    p.append(tk.header_row(t, "ops.tempo --authenticated"))

    # Big total figure, right-anchored.
    p.append(f'<text x="{tk.PAD}" y="70" font-size="40" font-weight="700" '
             f'fill="{t["accent"]}" style="font-variant-numeric:tabular-nums">'
             f'{s["total"]:,}</text>')
    p.append(f'<text x="{tk.PAD}" y="88" font-size="11" fill="{t["muted"]}">'
             f'commits · public + private</text>')

    # Split mini-bar: public vs private.
    bx, by, bw = tk.PAD, 100, tk.CARD_W - 2 * tk.PAD
    frac = s["public"] / max(1, s["total"])
    pub_w = max(2.0, bw * frac)
    p.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="8" rx="4" '
             f'fill="{t["accent"]}"/>')
    p.append(f'<rect x="{bx}" y="{by}" width="{pub_w:.2f}" height="8" rx="4" '
             f'fill="{t["accent_dim"]}"/>')
    p.append(f'<text x="{bx}" y="{by+26}" font-size="10.5" '
             f'fill="{t["muted"]}">'
             f'<tspan fill="{t["accent_dim"]}">■</tspan> {s["public"]} public'
             f'   <tspan fill="{t["accent"]}">■</tspan> '
             f'{s["private"]:,} private</text>')
    p.append(tk.num(t, tk.CARD_W - tk.PAD, by + 26,
                    f'{s["repos"]} repos · {s["repos_private"]} private',
                    size=10.5, color=t["muted"], weight="400"))

    p.append(f'<text x="{tk.PAD}" y="{h-12}" font-size="9.5" '
             f'fill="{t["muted"]}">non-fork repos · active since '
             f'{s["since"]}</text>')
    p.append("</svg>")
    return "\n".join(p)


if __name__ == "__main__":
    s = collect()
    out_dir = pathlib.Path(__file__).resolve().parent.parent / "assets"
    for theme in ("dark", "light"):
        (out_dir / f"stats-{theme}.svg").write_text(build(s, theme),
                                                     encoding="utf-8")
    print("wrote stats-dark.svg + stats-light.svg")
    for k, v in s.items():
        print(f"  {k:<14} {v}")
