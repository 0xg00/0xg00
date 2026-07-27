#!/usr/bin/env python3
"""Generate assets/stats.svg counting private contributions too.

Unauthenticated card services report only public commits (~61 here) while
the real figure including private repos is ~1700. Requires `gh` authenticated
with the `repo` scope.
"""
import json
import pathlib
import subprocess

W, PAD = 420, 20
BG, FG, MUTED, BORDER, ACCENT = "#1a1b27", "#c0caf5", "#a9b1d6", "#00ff41", "#70a5fd"
START_YEAR, END_YEAR = 2021, 2026


def gh_json(query):
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={query}"],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)["data"]


def collect():
    commits = prs = issues = 0
    for year in range(START_YEAR, END_YEAR + 1):
        q = ('{viewer{contributionsCollection(from:"%d-01-01T00:00:00Z",'
             'to:"%d-12-31T23:59:59Z"){totalCommitContributions '
             'totalPullRequestContributions totalIssueContributions '
             'restrictedContributionsCount}}}' % (year, year))
        c = gh_json(q)["viewer"]["contributionsCollection"]
        # Restricted contributions are private ones the public API hides.
        commits += c["totalCommitContributions"] + c["restrictedContributionsCount"]
        prs += c["totalPullRequestContributions"]
        issues += c["totalIssueContributions"]

    q = ('{viewer{repositories(first:100,ownerAffiliations:OWNER,isFork:false)'
         '{totalCount nodes{stargazerCount}} followers{totalCount}}}')
    v = gh_json(q)["viewer"]
    return {
        "Total commits": commits,
        "Total repos": v["repositories"]["totalCount"],
        "Total stars": sum(n["stargazerCount"] for n in v["repositories"]["nodes"]),
        "Pull requests": prs,
        "Issues": issues,
        "Followers": v["followers"]["totalCount"],
    }


def build(stats):
    h = PAD + 26 + len(stats) * 22 + PAD
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
         f'viewBox="0 0 {W} {h}" font-family="Segoe UI,Ubuntu,sans-serif">',
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="6" fill="{BG}" '
         f'stroke="{BORDER}" stroke-opacity="0.55"/>',
         f'<text x="{PAD}" y="{PAD+14}" fill="{BORDER}" font-size="15" '
         f'font-weight="600">Contribution Stats</text>',
         f'<text x="{W-PAD}" y="{PAD+14}" fill="{MUTED}" font-size="10" '
         f'text-anchor="end">public + private</text>']
    y = PAD + 44
    for label, value in stats.items():
        p.append(f'<text x="{PAD}" y="{y}" fill="{FG}" font-size="12">{label}</text>')
        p.append(f'<text x="{W-PAD}" y="{y}" fill="{ACCENT}" font-size="13" '
                 f'font-weight="600" text-anchor="end">{value:,}</text>')
        y += 22
    p.append('</svg>')
    return "\n".join(p)


if __name__ == "__main__":
    stats = collect()
    out = pathlib.Path(__file__).resolve().parent.parent / "assets" / "stats.svg"
    out.write_text(build(stats), encoding="utf-8")
    print(f"wrote {out}")
    for k, v in stats.items():
        print(f"  {k:<16} {v:,}")
