#!/usr/bin/env python3
"""Refresh auto-managed sections of README.md from upstream activity.

Reads the latest commit subject and total commit count from a target repo via
the public GitHub REST API, then rewrites two things in README.md:

  1. The block between <!-- AUTO:START --> and <!-- AUTO:END --> markers.
  2. The first inline `<N> commits` token (the receipt line for OpenCodeIntel).

Stdlib only, no third-party dependencies. Idempotent: writes the file only when
the content actually changes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
README = Path("README.md")


def http_get(url: str, token: str | None) -> tuple[dict[str, str], bytes]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "devanshuneu-readme-bot",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return dict(resp.headers), resp.read()


def latest_commit(repo: str, token: str | None) -> tuple[str, str]:
    # Pull a small window so we can skip merge commits, whose subjects
    # ("Merge pull request #N from ...") are bureaucratic noise.
    _, body = http_get(f"{API}/repos/{repo}/commits?per_page=20", token)
    payload = json.loads(body)
    if not payload:
        raise RuntimeError(f"no commits returned for {repo}")
    for entry in payload:
        subject = entry["commit"]["message"].splitlines()[0].strip()
        if subject.startswith("Merge "):
            continue
        date = entry["commit"]["author"]["date"][:10]
        return date, subject
    first = payload[0]
    return (
        first["commit"]["author"]["date"][:10],
        first["commit"]["message"].splitlines()[0].strip(),
    )


def total_commits(repo: str, token: str | None) -> int:
    # Trick: per_page=1 gives a Link header whose last-page number equals the
    # total commit count. Cheap and accurate.
    headers, _ = http_get(f"{API}/repos/{repo}/commits?per_page=1", token)
    link = headers.get("Link") or headers.get("link") or ""
    match = re.search(r'page=(\d+)>;\s*rel="last"', link)
    return int(match.group(1)) if match else 1


def replace_block(content: str, marker: str, inner: str) -> str:
    pattern = rf"(<!-- {marker}:START -->)(.*?)(<!-- {marker}:END -->)"
    return re.sub(
        pattern,
        lambda m: f"{m.group(1)}\n{inner}\n{m.group(3)}",
        content,
        flags=re.DOTALL,
    )


def truncate(text: str, limit: int = 80) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="OpenCodeIntel/opencodeintel")
    parser.add_argument("--token", default=None)
    args = parser.parse_args()

    try:
        date, subject = latest_commit(args.repo, args.token)
        count = total_commits(args.repo, args.token)
    except (urllib.error.URLError, urllib.error.HTTPError, RuntimeError) as exc:
        print(f"upstream fetch failed: {exc}", file=sys.stderr)
        return 1

    subject = truncate(subject)

    content = README.read_text(encoding="utf-8")
    new_content = replace_block(content, "AUTO", f"**{date}** · {subject}")
    new_content = re.sub(
        r"`\d+\s+commits`",
        f"`{count} commits`",
        new_content,
        count=1,
    )

    if new_content == content:
        print("no changes")
        return 0

    README.write_text(new_content, encoding="utf-8")
    print(f"updated: {date} | {subject} | {count} commits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
