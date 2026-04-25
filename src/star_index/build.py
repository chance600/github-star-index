#!/usr/bin/env python3
"""Build a structured index from a GitHub user's starred repositories."""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .artifacts import build_xml, load_raw_json, write_manifest, write_raw_json, write_summary
from .github_api import fetch_starred_repositories, normalize_star_items
from .paths import DEFAULT_CONFIG_PATH, default_output_paths
from .taxonomy import categorize_repositories, load_manual_categories


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_user(user: str | None, offline: bool, raw_json: Path) -> str:
    candidate = user or os.environ.get("STAR_INDEX_USER")
    if candidate:
        return candidate
    if offline and raw_json.exists():
        cached_user, _, _, _ = load_raw_json(raw_json)
        return cached_user
    raise SystemExit("A GitHub user is required. Pass --user or set STAR_INDEX_USER.")


def resolve_build_paths(
    *,
    user: str | None,
    output_dir: Path,
    xml: Path | None,
    raw_json: Path | None,
    summary: Path | None,
    manifest: Path | None,
) -> dict[str, Path]:
    defaults = default_output_paths(user, output_dir)
    return {
        "xml": xml or defaults["xml"],
        "raw_json": raw_json or defaults["raw_json"],
        "summary": summary or defaults["summary"],
        "manifest": manifest or defaults["manifest"],
    }


def run_build(
    *,
    user: str,
    xml_path: Path,
    raw_json_path: Path,
    summary_path: Path,
    manifest_path: Path,
    manual_categories_path: Path | None,
    offline: bool = False,
) -> dict[str, Any]:
    generated_at = utc_now()

    if offline:
        user, stars, metadata, generated_at = load_raw_json(raw_json_path)
    else:
        stars, metadata = fetch_starred_repositories(user)
        write_raw_json(raw_json_path, user, generated_at, stars, metadata)

    repos = normalize_star_items(stars)
    manual = load_manual_categories(manual_categories_path)
    category_by_repo = categorize_repositories(repos, manual)
    tree = build_xml(user, repos, category_by_repo, generated_at, metadata.get("profile") if isinstance(metadata, dict) else None)
    xml_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    write_summary(summary_path, user, repos, generated_at, xml_path, raw_json_path)
    write_manifest(
        manifest_path,
        user=user,
        generated_at=generated_at,
        repo_count=len(repos),
        xml_path=xml_path,
        raw_json_path=raw_json_path,
        summary_path=summary_path,
        manual_categories_path=manual_categories_path,
        metadata=metadata,
    )

    return {
        "user": user,
        "generated_at": generated_at,
        "repository_count": len(repos),
        "repos": repos,
        "metadata": metadata,
        "paths": {
            "xml": xml_path,
            "raw_json": raw_json_path,
            "summary": summary_path,
            "manifest": manifest_path,
        },
        "category_by_repo": category_by_repo,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build XML/JSON indexes of a GitHub user's starred repositories.")
    parser.add_argument("--user", help="GitHub username whose stars should be indexed.")
    parser.add_argument("--output-dir", type=Path, default=Path("data"), help="Directory for generated artifacts.")
    parser.add_argument("--xml", type=Path, help="XML output path override.")
    parser.add_argument("--raw-json", type=Path, help="Raw JSON cache path override.")
    parser.add_argument("--summary", type=Path, help="Markdown summary path override.")
    parser.add_argument("--manifest", type=Path, help="Manifest JSON path override.")
    parser.add_argument(
        "--manual-categories",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Optional JSON file with manual category overrides.",
    )
    parser.add_argument("--offline", action="store_true", help="Rebuild artifacts from --raw-json without calling GitHub.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    initial_defaults = default_output_paths(args.user, args.output_dir)
    raw_json_path = args.raw_json or initial_defaults["raw_json"]
    user = resolve_user(args.user, args.offline, raw_json_path)
    paths = resolve_build_paths(
        user=user,
        output_dir=args.output_dir,
        xml=args.xml,
        raw_json=raw_json_path,
        summary=args.summary,
        manifest=args.manifest,
    )
    result = run_build(
        user=user,
        xml_path=paths["xml"],
        raw_json_path=paths["raw_json"],
        summary_path=paths["summary"],
        manifest_path=paths["manifest"],
        manual_categories_path=args.manual_categories,
        offline=args.offline,
    )

    print(f"Wrote {result['paths']['xml']} ({result['repository_count']} repositories)")
    if args.offline:
        print(f"Used cached raw JSON {result['paths']['raw_json']}")
    else:
        print(f"Wrote {result['paths']['raw_json']}")
    print(f"Wrote {result['paths']['summary']}")
    print(f"Wrote {result['paths']['manifest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
