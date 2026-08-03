#!/usr/bin/env python3
"""Render a compact GitHub profile statistics card from GraphQL JSON."""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path


WIDTH = 495
HEIGHT = 195


def read_user(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    user = payload.get("data", {}).get("user")
    if not isinstance(user, dict):
        raise ValueError("GitHub GraphQL response does not contain data.user")
    return user


def total(node: object) -> int:
    if isinstance(node, dict):
        value = node.get("totalCount", 0)
        return int(value) if isinstance(value, (int, float)) else 0
    return 0


def render(user: dict) -> str:
    login = html.escape(str(user.get("login") or "GitHub user"))
    contributions = user.get("contributionsCollection") or {}
    calendar = contributions.get("contributionCalendar") or {}
    metrics = (
        ("Contributions", int(calendar.get("totalContributions") or 0)),
        ("Repositories", total(user.get("repositories"))),
        ("Pull requests", total(user.get("pullRequests"))),
        ("Issues", total(user.get("issues"))),
        ("Reviews", int(contributions.get("totalPullRequestReviewContributions") or 0)),
        ("Followers", total(user.get("followers"))),
    )

    cells: list[str] = []
    for index, (label, value) in enumerate(metrics):
        column = index % 3
        row = index // 3
        x = 25 + column * 158
        y = 88 + row * 61
        cells.append(
            f'<text class="value" x="{x}" y="{y}">{value:,}</text>'
            f'<text class="label" x="{x}" y="{y + 20}">{label}</text>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title description">
  <title id="title">{login} GitHub statistics</title>
  <desc id="description">Public GitHub activity statistics refreshed weekly.</desc>
  <style>
    .card {{ fill: #ffffff; stroke: #d0d7de; }}
    .heading {{ fill: #24292f; font: 600 18px -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif; }}
    .value {{ fill: #0969da; font: 600 17px -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif; }}
    .label {{ fill: #57606a; font: 12px -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif; }}
    @media (prefers-color-scheme: dark) {{
      .card {{ fill: #0d1117; stroke: #30363d; }}
      .heading {{ fill: #e6edf3; }}
      .value {{ fill: #58a6ff; }}
      .label {{ fill: #8b949e; }}
    }}
  </style>
  <rect class="card" width="494" height="194" x="0.5" y="0.5" rx="6"/>
  <text class="heading" x="25" y="39">{login}'s GitHub Stats</text>
  {''.join(cells)}
</svg>
'''


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: render_stats.py INPUT_JSON OUTPUT_SVG", file=sys.stderr)
        return 2

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render(read_user(input_path)), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
