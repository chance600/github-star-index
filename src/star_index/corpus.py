from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .taxonomy import infer_llm_use, slugify


def repository_text_sections(repo: dict[str, Any], categories: list[dict[str, str]], llm_use: str) -> list[dict[str, str]]:
    metrics = [
        f"Stars: {repo.get('stargazers_count') or 0}",
        f"Forks: {repo.get('forks_count') or repo.get('forks') or 0}",
        f"Watchers: {repo.get('watchers_count') or 0}",
        f"Open issues: {repo.get('open_issues_count') or repo.get('open_issues') or 0}",
    ]
    sections = [
        {
            "kind": "overview",
            "text": "\n".join(
                part
                for part in [
                    repo.get("full_name") or "",
                    repo.get("description") or "",
                    f"Homepage: {repo.get('homepage')}" if repo.get("homepage") else "",
                    f"Primary language: {repo.get('language') or 'Unspecified'}",
                    f"Topics: {', '.join(repo.get('topics') or [])}" if repo.get("topics") else "",
                ]
                if part
            ),
        },
        {
            "kind": "classification",
            "text": "\n".join(
                part
                for part in [
                    "Categories: " + ", ".join(category["name"] for category in categories) if categories else "",
                    f"Suggested LLM use: {llm_use}",
                    "Category sources: "
                    + ", ".join(sorted({category["source"] for category in categories}))
                    if categories
                    else "",
                ]
                if part
            ),
        },
        {
            "kind": "activity",
            "text": "\n".join(
                part
                for part in [
                    "Metrics: " + ", ".join(metrics),
                    f"Starred at: {repo.get('starred_at') or 'unknown'}",
                    f"Updated at: {repo.get('updated_at') or 'unknown'}",
                    f"Pushed at: {repo.get('pushed_at') or 'unknown'}",
                    f"Default branch: {repo.get('default_branch') or 'unknown'}",
                ]
                if part
            ),
        },
    ]
    return [section for section in sections if section["text"]]


def repository_record(
    repo: dict[str, Any],
    *,
    categories: list[dict[str, str]],
    source_user: str,
    generated_at: str,
) -> dict[str, Any]:
    llm_use = infer_llm_use(repo, categories)
    return {
        "schema_version": "0.1.0",
        "record_type": "repository",
        "source_user": source_user,
        "generated_at": generated_at,
        "repository": {
            "id": repo.get("id"),
            "node_id": repo.get("node_id"),
            "full_name": repo.get("full_name"),
            "html_url": repo.get("html_url"),
            "description": repo.get("description"),
            "homepage": repo.get("homepage"),
            "language": repo.get("language"),
            "topics": repo.get("topics") or [],
            "starred_at": repo.get("starred_at"),
            "stargazers_count": repo.get("stargazers_count"),
            "forks_count": repo.get("forks_count") or repo.get("forks"),
            "watchers_count": repo.get("watchers_count"),
        },
        "categories": categories,
        "llm_use": llm_use,
        "provenance": {
            "metadata": "github-rest-stars",
            "category_sources": sorted({category["source"] for category in categories}),
        },
        "text": "\n".join(section["text"] for section in repository_text_sections(repo, categories, llm_use)),
    }


def chunk_records(
    repo: dict[str, Any],
    *,
    categories: list[dict[str, str]],
    source_user: str,
    generated_at: str,
) -> list[dict[str, Any]]:
    llm_use = infer_llm_use(repo, categories)
    sections = repository_text_sections(repo, categories, llm_use)
    full_name = repo.get("full_name") or "unknown"
    repo_slug = slugify(full_name)
    chunk_count = len(sections)
    return [
        {
            "schema_version": "0.1.0",
            "record_type": "repository_chunk",
            "source_user": source_user,
            "generated_at": generated_at,
            "chunk_id": f"{repo_slug}:{index}",
            "repository_full_name": full_name,
            "repository_url": repo.get("html_url"),
            "chunk_index": index,
            "chunk_count": chunk_count,
            "chunk_kind": section["kind"],
            "categories": categories,
            "llm_use": llm_use,
            "provenance": {
                "text_source": "github-rest-stars-metadata",
                "category_sources": sorted({category["source"] for category in categories}),
            },
            "text": section["text"],
        }
        for index, section in enumerate(sections)
    ]


def category_rollup_records(
    repos: list[dict[str, Any]],
    *,
    category_by_repo: dict[str, list[dict[str, str]]],
    source_user: str,
    generated_at: str,
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}

    for repo in repos:
        full_name = repo.get("full_name") or ""
        for category in category_by_repo.get(full_name, []):
            bucket = grouped.setdefault(
                category["id"],
                {
                    "category": {
                        "id": category["id"],
                        "name": category["name"],
                        "description": category.get("description", ""),
                    },
                    "sources": set(),
                    "repos": [],
                    "topics": Counter(),
                    "languages": Counter(),
                },
            )
            bucket["sources"].add(category["source"])
            bucket["repos"].append(repo)
            bucket["topics"].update(repo.get("topics") or [])
            bucket["languages"][repo.get("language") or "Unspecified"] += 1

    records: list[dict[str, Any]] = []
    for category_id, bucket in sorted(grouped.items(), key=lambda item: item[1]["category"]["name"]):
        unique_repos = {
            repo.get("full_name") or f"repo-{index}": repo for index, repo in enumerate(bucket["repos"])
        }
        repos_for_category = sorted(
            unique_repos.values(),
            key=lambda repo: ((repo.get("stargazers_count") or 0), repo.get("full_name") or ""),
            reverse=True,
        )
        records.append(
            {
                "schema_version": "0.1.0",
                "record_type": "category_rollup",
                "source_user": source_user,
                "generated_at": generated_at,
                "category": bucket["category"],
                "repository_count": len(repos_for_category),
                "top_repositories": [
                    {
                        "full_name": repo.get("full_name"),
                        "html_url": repo.get("html_url"),
                        "description": repo.get("description"),
                        "stargazers_count": repo.get("stargazers_count") or 0,
                        "language": repo.get("language"),
                    }
                    for repo in repos_for_category[:25]
                ],
                "top_topics": [
                    {"name": name, "count": count}
                    for name, count in bucket["topics"].most_common(15)
                ],
                "top_languages": [
                    {"name": name, "count": count}
                    for name, count in bucket["languages"].most_common(10)
                ],
                "provenance": {
                    "metadata": "github-rest-stars",
                    "category_sources": sorted(bucket["sources"]),
                },
            }
        )
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_bundle_manifest(
    path: Path,
    *,
    source_user: str,
    generated_at: str,
    repository_count: int,
    chunk_count: int,
    category_count: int,
    artifacts: dict[str, Path],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "0.1.0",
        "generated_at": generated_at,
        "source_user": source_user,
        "repository_count": repository_count,
        "chunk_count": chunk_count,
        "category_count": category_count,
        "artifacts": {name: str(artifact) for name, artifact in artifacts.items()},
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
