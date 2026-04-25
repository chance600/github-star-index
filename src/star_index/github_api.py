from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from typing import Any


API_ROOT = "https://api.github.com"
USER_AGENT = "github-star-index/1.0"


def gh_cli_token() -> str | None:
    if not shutil.which("gh"):
        return None
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    token = result.stdout.strip()
    if result.returncode != 0 or not token:
        return None
    return token


def auth_headers() -> dict[str, str]:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or gh_cli_token()
    headers = {
        "Accept": "application/vnd.github.star+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_json(url: str, headers: dict[str, str], retries: int = 4) -> tuple[Any, dict[str, str]]:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=45) as response:
                payload = json.load(response)
                return payload, dict(response.headers.items())
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", "replace")
            if error.code == 403:
                remaining = error.headers.get("x-ratelimit-remaining", "unknown")
                reset = error.headers.get("x-ratelimit-reset", "unknown")
                raise RuntimeError(
                    f"GitHub API returned 403. Rate remaining={remaining}, reset={reset}. "
                    "Set GH_TOKEN or GITHUB_TOKEN and rerun. Response: "
                    f"{body[:300]}"
                ) from error
            if error.code in {500, 502, 503, 504} and attempt < retries - 1:
                last_error = error
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"GitHub API returned HTTP {error.code}: {body[:500]}") from error
        except urllib.error.URLError as error:
            last_error = error
            if attempt < retries - 1:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"Network error fetching {url}: {error}") from error
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def parse_next_link(link_header: str | None) -> str | None:
    if not link_header:
        return None
    for part in link_header.split(","):
        section = part.strip()
        if 'rel="next"' not in section:
            continue
        if section.startswith("<") and ">" in section:
            return section[1 : section.index(">")]
    return None


def fetch_starred_repositories(user: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    headers = auth_headers()
    url = f"{API_ROOT}/users/{user}/starred?per_page=100&sort=created&direction=desc"
    stars: list[dict[str, Any]] = []
    page = 1
    rate: dict[str, Any] = {}

    while url:
        payload, response_headers = fetch_json(url, headers)
        if not isinstance(payload, list):
            raise RuntimeError(f"Expected a list from GitHub starred API, got: {type(payload).__name__}")
        stars.extend(payload)
        rate = {
            "limit": response_headers.get("x-ratelimit-limit"),
            "remaining": response_headers.get("x-ratelimit-remaining"),
            "reset": response_headers.get("x-ratelimit-reset"),
        }
        print(f"Fetched page {page}: {len(payload)} repositories")
        url = parse_next_link(response_headers.get("Link"))
        page += 1
        if url:
            time.sleep(0.2)

    profile, _ = fetch_json(f"{API_ROOT}/users/{user}", headers)
    return stars, {"rate": rate, "profile": profile}


def normalize_star_items(stars: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in stars:
        if "repo" in item:
            repo = dict(item["repo"])
            repo["starred_at"] = item.get("starred_at")
        else:
            repo = dict(item)
            repo["starred_at"] = item.get("starred_at")
        normalized.append(repo)
    normalized.sort(key=lambda repo: (repo.get("starred_at") or "", repo.get("full_name") or ""), reverse=True)
    return normalized
