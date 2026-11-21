"""Render the profile's repository snapshot from paginated GitHub REST data."""

import json
import sys
from collections import Counter
from html import escape
from pathlib import Path


def render(repos, dark):
    ink, muted, track, violet = (
        ("#e6edf3", "#a5afb9", "#262c36", "#b799ff") if dark
        else ("#1f2328", "#59636e", "#eaeef2", "#7952d2")
    )
    counts = Counter(r["language"] for r in repos if r["language"])
    top = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))[:4]
    stars = sum(r["stargazers_count"] for r in repos)
    summary = f'{len(repos):,} public repositories · {stars:,} stars'
    detail = ', '.join(f'{name}: {n}' for name, n in top)
    height = 66 + 25 * max(len(top), 1)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="440" height="{height}" viewBox="0 0 440 {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{summary}</title>',
        f'<desc id="desc">Top primary languages by number of public non-fork repositories: {escape(detail) or "none reported"}.</desc>',
        f'<g font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" fill="{ink}">',
        f'<text x="0" y="24" font-size="21" font-weight="600">{summary}</text>',
        f'<text x="0" y="48" fill="{muted}" font-size="14">Top languages by repository count · forks excluded</text>',
    ]
    for i, (name, count) in enumerate(top):
        y = 74 + 25 * i
        width = 245 * count / top[0][1]
        label = name if len(name) <= 14 else name[:13] + '…'
        svg.extend([
            f'<text x="0" y="{y}" font-size="16">{escape(label)}</text>',
            f'<rect x="141" y="{y-8}" width="245" height="6" rx="3" fill="{track}"/>',
            f'<rect x="141" y="{y-8}" width="{width:.2f}" height="6" rx="3" fill="{violet}"/>',
            f'<text x="434" y="{y}" text-anchor="end" font-size="16" fill="{muted}">{count:,}</text>',
        ])
    if not top:
        svg.append(f'<text x="0" y="74" fill="{muted}" font-size="16">No primary languages reported yet.</text>')
    return '\n'.join([*svg, '</g></svg>']) + '\n'


if __name__ == '__main__':
    pages = json.load(sys.stdin)
    repos = [r for page in pages for r in page if not r['fork'] and not r['private']]
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for mode in ('light', 'dark'):
        (out / f'repos-{mode}.svg').write_text(render(repos, mode == 'dark'), encoding='utf-8')
