from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

from .taxonomy import CATEGORY_RULES, infer_llm_use


def text_el(parent: ET.Element, tag: str, text: Any, **attrs: Any) -> ET.Element:
    element = ET.SubElement(parent, tag, {key: str(value) for key, value in attrs.items() if value is not None})
    if text is not None:
        element.text = str(text)
    return element


def bool_attr(value: Any) -> str:
    return "true" if bool(value) else "false"


def repo_to_xml(parent: ET.Element, repo: dict[str, Any], categories: list[dict[str, str]]) -> None:
    license_data = repo.get("license") or {}
    owner = repo.get("owner") or {}
    repo_el = ET.SubElement(
        parent,
        "repository",
        {
            "id": str(repo.get("id") or ""),
            "node_id": str(repo.get("node_id") or ""),
            "full_name": str(repo.get("full_name") or ""),
            "owner": str(owner.get("login") or ""),
            "name": str(repo.get("name") or ""),
            "visibility": str(repo.get("visibility") or ""),
            "private": bool_attr(repo.get("private")),
            "fork": bool_attr(repo.get("fork")),
            "archived": bool_attr(repo.get("archived")),
            "disabled": bool_attr(repo.get("disabled")),
            "template": bool_attr(repo.get("is_template")),
        },
    )

    text_el(repo_el, "description", repo.get("description"))
    text_el(repo_el, "homepage", repo.get("homepage"))
    text_el(repo_el, "llm_use", infer_llm_use(repo, categories))

    urls_el = ET.SubElement(repo_el, "urls")
    text_el(urls_el, "html", repo.get("html_url"))
    text_el(urls_el, "clone_https", repo.get("clone_url"))
    text_el(urls_el, "clone_ssh", repo.get("ssh_url"))
    text_el(urls_el, "api", repo.get("url"))

    cats_el = ET.SubElement(repo_el, "categories")
    for rank, category in enumerate(categories, start=1):
        text_el(cats_el, "category", category["name"], id=category["id"], source=category["source"], rank=rank)

    topics_el = ET.SubElement(repo_el, "topics")
    for topic in repo.get("topics") or []:
        text_el(topics_el, "topic", topic)

    text_el(repo_el, "primary_language", repo.get("language"))
    ET.SubElement(
        repo_el,
        "license",
        {
            "key": str(license_data.get("key") or ""),
            "spdx_id": str(license_data.get("spdx_id") or ""),
            "name": str(license_data.get("name") or ""),
        },
    )
    ET.SubElement(
        repo_el,
        "metrics",
        {
            "stars": str(repo.get("stargazers_count") or 0),
            "watchers": str(repo.get("watchers_count") or 0),
            "forks": str(repo.get("forks_count") or repo.get("forks") or 0),
            "open_issues": str(repo.get("open_issues_count") or repo.get("open_issues") or 0),
            "size_kb": str(repo.get("size") or 0),
        },
    )
    ET.SubElement(
        repo_el,
        "activity",
        {
            "starred_at": str(repo.get("starred_at") or ""),
            "created_at": str(repo.get("created_at") or ""),
            "updated_at": str(repo.get("updated_at") or ""),
            "pushed_at": str(repo.get("pushed_at") or ""),
            "default_branch": str(repo.get("default_branch") or ""),
        },
    )
    ET.SubElement(
        repo_el,
        "features",
        {
            "issues": bool_attr(repo.get("has_issues")),
            "pull_requests": bool_attr(repo.get("has_pull_requests")),
            "projects": bool_attr(repo.get("has_projects")),
            "downloads": bool_attr(repo.get("has_downloads")),
            "wiki": bool_attr(repo.get("has_wiki")),
            "pages": bool_attr(repo.get("has_pages")),
            "discussions": bool_attr(repo.get("has_discussions")),
        },
    )


def build_xml(
    user: str,
    repos: list[dict[str, Any]],
    category_by_repo: dict[str, list[dict[str, str]]],
    generated_at: str,
    profile: dict[str, Any] | None,
) -> ET.ElementTree:
    category_counts: Counter[str] = Counter()
    language_counts: Counter[str] = Counter()
    topic_counts: Counter[str] = Counter()

    for repo in repos:
        categories = category_by_repo[repo.get("full_name") or ""]
        for category in categories:
            category_counts[category["name"]] += 1
        language_counts[repo.get("language") or "Unspecified"] += 1
        topic_counts.update(repo.get("topics") or [])

    root = ET.Element(
        "github_star_index",
        {
            "version": "1.0",
            "source_user": user,
            "generated_at": generated_at,
            "repository_count": str(len(repos)),
        },
    )

    meta = ET.SubElement(root, "metadata")
    text_el(meta, "source", "GitHub REST API starred repositories endpoint")
    text_el(
        meta,
        "list_limitation",
        "GitHub REST starring endpoints expose starred repositories and topics, but not user-created star lists.",
    )
    if profile:
        ET.SubElement(
            meta,
            "profile",
            {
                "login": str(profile.get("login") or user),
                "name": str(profile.get("name") or ""),
                "html_url": str(profile.get("html_url") or ""),
                "public_repos": str(profile.get("public_repos") or 0),
                "followers": str(profile.get("followers") or 0),
                "following": str(profile.get("following") or 0),
            },
        )

    taxonomy = ET.SubElement(root, "category_taxonomy")
    for rule in CATEGORY_RULES:
        ET.SubElement(taxonomy, "category", {"id": rule["id"], "name": rule["name"], "description": rule["description"]})
    ET.SubElement(
        taxonomy,
        "category",
        {"id": "general-development", "name": "General Development", "description": "Useful repositories without a stronger category signal."},
    )

    summary = ET.SubElement(root, "summary")
    ET.SubElement(
        summary,
        "totals",
        {
            "repositories": str(len(repos)),
            "archived": str(sum(1 for repo in repos if repo.get("archived"))),
            "forks": str(sum(1 for repo in repos if repo.get("fork"))),
            "templates": str(sum(1 for repo in repos if repo.get("is_template"))),
        },
    )

    categories_el = ET.SubElement(summary, "category_counts")
    for name, count in category_counts.most_common():
        ET.SubElement(categories_el, "category", {"name": name, "count": str(count)})

    languages_el = ET.SubElement(summary, "language_counts")
    for language, count in language_counts.most_common():
        ET.SubElement(languages_el, "language", {"name": language, "count": str(count)})

    topics_el = ET.SubElement(summary, "top_topics")
    for topic, count in topic_counts.most_common(75):
        ET.SubElement(topics_el, "topic", {"name": topic, "count": str(count)})

    repos_el = ET.SubElement(root, "repositories")
    for repo in repos:
        repo_to_xml(repos_el, repo, category_by_repo[repo.get("full_name") or ""])

    ET.indent(root, space="  ")
    return ET.ElementTree(root)


def write_raw_json(path: Path, user: str, generated_at: str, stars: list[dict[str, Any]], metadata: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": generated_at,
        "source_user": user,
        "metadata": metadata,
        "stars": stars,
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def load_raw_json(path: Path) -> tuple[str, list[dict[str, Any]], dict[str, Any], str]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return (
        payload.get("source_user", "unknown"),
        payload.get("stars", []),
        payload.get("metadata", {}),
        payload.get("generated_at", ""),
    )


def write_summary(path: Path, user: str, repos: list[dict[str, Any]], generated_at: str, xml_path: Path, raw_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    language_counts = Counter(repo.get("language") or "Unspecified" for repo in repos)
    topic_counts = Counter(topic for repo in repos for topic in (repo.get("topics") or []))
    archived = sum(1 for repo in repos if repo.get("archived"))
    forked = sum(1 for repo in repos if repo.get("fork"))
    top_starred = sorted(repos, key=lambda repo: repo.get("stargazers_count") or 0, reverse=True)[:25]
    recent = sorted(repos, key=lambda repo: repo.get("starred_at") or "", reverse=True)[:25]

    lines = [
        f"# GitHub Star Index: {user}",
        "",
        f"- Generated: `{generated_at}`",
        f"- Repositories: `{len(repos)}`",
        f"- Archived: `{archived}`",
        f"- Forks: `{forked}`",
        f"- XML: `{xml_path}`",
        f"- Raw JSON cache: `{raw_path}`",
        "",
        "## Maintenance",
        "",
        "```bash",
        f"python -m star_index build --user {user}",
        "```",
        "",
        "Set `GH_TOKEN` or `GITHUB_TOKEN` first if you hit GitHub API rate limits.",
        "",
        "## Top Languages",
        "",
    ]
    for language, count in language_counts.most_common(20):
        lines.append(f"- {language}: {count}")

    lines.extend(["", "## Top Topics", ""])
    for topic, count in topic_counts.most_common(30):
        lines.append(f"- {topic}: {count}")

    lines.extend(["", "## Highest-Starred Repositories", ""])
    for repo in top_starred:
        lines.append(
            f"- [{repo.get('full_name')}]({repo.get('html_url')}) "
            f"({repo.get('stargazers_count') or 0} stars, {repo.get('language') or 'unknown'})"
        )

    lines.extend(["", "## Most Recent Stars", ""])
    for repo in recent:
        lines.append(f"- `{repo.get('starred_at') or 'unknown'}` [{repo.get('full_name')}]({repo.get('html_url')})")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest(
    path: Path,
    *,
    user: str,
    generated_at: str,
    repo_count: int,
    xml_path: Path,
    raw_json_path: Path,
    summary_path: Path,
    manual_categories_path: Path | None,
    metadata: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "0.1.0",
        "generated_at": generated_at,
        "source_user": user,
        "repository_count": repo_count,
        "artifacts": {
            "xml": str(xml_path),
            "raw_json": str(raw_json_path),
            "summary": str(summary_path),
        },
        "inputs": {
            "manual_categories": str(manual_categories_path) if manual_categories_path else None,
        },
        "metadata": metadata,
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
