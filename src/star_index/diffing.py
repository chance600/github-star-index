from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def compute_repo_diff(before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]) -> dict[str, Any]:
    added_names = sorted(set(after) - set(before))
    removed_names = sorted(set(before) - set(after))
    return {
        "before_count": len(before),
        "after_count": len(after),
        "added": [after[name] for name in added_names],
        "removed": [before[name] for name in removed_names],
    }


def repo_line(repo: dict[str, Any]) -> str:
    stars = repo.get("stars")
    language = repo.get("language") or "unknown"
    suffix = f"{stars} stars, {language}" if stars is not None else language
    return f"- [{repo['full_name']}]({repo.get('html_url')}) ({suffix})"


def write_refresh_markdown(path: Path, *, diff: dict[str, Any], user: str, refreshed_at: str) -> None:
    lines = [
        "# GitHub Star Index Refresh",
        "",
        f"- Refreshed: `{refreshed_at}`",
        f"- User: `{user}`",
        f"- Before: `{diff['before_count']}` repositories",
        f"- After: `{diff['after_count']}` repositories",
        f"- Added: `{len(diff['added'])}`",
        f"- Removed: `{len(diff['removed'])}`",
        "",
        "## Added Repositories",
        "",
    ]

    if diff["added"]:
        for repo in diff["added"]:
            lines.append(repo_line(repo))
    else:
        lines.append("No newly indexed repositories.")

    lines.extend(["", "## Removed Repositories", ""])
    if diff["removed"]:
        for repo in diff["removed"]:
            lines.append(repo_line(repo))
    else:
        lines.append("No repositories disappeared from the index.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_refresh_json(
    path: Path,
    *,
    diff: dict[str, Any],
    user: str,
    refreshed_at: str,
    raw_json_path: Path,
    report_path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "0.1.0",
        "generated_at": refreshed_at,
        "source_user": user,
        "before_count": diff["before_count"],
        "after_count": diff["after_count"],
        "added": diff["added"],
        "removed": diff["removed"],
        "artifacts": {
            "raw_json": str(raw_json_path),
            "report_markdown": str(report_path),
        },
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
