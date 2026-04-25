from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


CATEGORY_RULES: list[dict[str, Any]] = [
    {
        "id": "ai-agents",
        "name": "AI Agents and Orchestration",
        "description": "Agent frameworks, autonomous workflows, tool use, MCP, and multi-agent systems.",
        "keywords": [
            "agent",
            "agents",
            "agentic",
            "autonomous",
            "multi-agent",
            "mcp",
            "tool-use",
            "workflow",
            "orchestration",
            "computer-use",
        ],
        "llm_use": "Use as reference material for agent architecture, tool orchestration, and autonomous workflow design.",
    },
    {
        "id": "llm-apps",
        "name": "LLM Applications and Chat",
        "description": "Chat apps, copilots, prompt tooling, assistants, and applied LLM products.",
        "keywords": [
            "llm",
            "chatgpt",
            "chatbot",
            "assistant",
            "copilot",
            "prompt",
            "prompts",
            "openai",
            "claude",
            "gemini",
            "ollama",
            "litellm",
        ],
        "llm_use": "Use for product patterns, prompting approaches, and integration examples for LLM-facing applications.",
    },
    {
        "id": "rag-memory",
        "name": "RAG, Memory, and Knowledge Systems",
        "description": "Retrieval, vector search, embeddings, long-term memory, and knowledge graph systems.",
        "keywords": [
            "rag",
            "retrieval",
            "embedding",
            "embeddings",
            "vector",
            "vectors",
            "memory",
            "knowledge-graph",
            "semantic-search",
            "search",
            "index",
            "long-term-memory",
        ],
        "llm_use": "Use to design retrieval, memory, semantic indexing, and knowledge-grounded LLM systems.",
    },
    {
        "id": "code-devtools",
        "name": "Code Agents and Developer Tools",
        "description": "Coding assistants, CLIs, IDE tooling, code search, and software engineering automation.",
        "keywords": [
            "code",
            "coding",
            "developer-tools",
            "devtools",
            "cli",
            "ide",
            "vscode",
            "terminal",
            "git",
            "github",
            "testing",
            "lint",
        ],
        "llm_use": "Use for developer workflow automation, code agent design, and repo-level engineering references.",
    },
    {
        "id": "automation-browser",
        "name": "Automation, Browser, and Workflow Ops",
        "description": "Browser automation, RPA, schedulers, scrapers, and workflow automation platforms.",
        "keywords": [
            "automation",
            "automate",
            "browser",
            "playwright",
            "puppeteer",
            "selenium",
            "rpa",
            "n8n",
            "workflow",
            "scheduler",
            "scraper",
            "scraping",
        ],
        "llm_use": "Use to build operational automations, browser workflows, and repeatable task pipelines.",
    },
    {
        "id": "data-research",
        "name": "Data, Research, and Analytics",
        "description": "Research tooling, datasets, notebooks, analytics, data extraction, and evaluation.",
        "keywords": [
            "data",
            "dataset",
            "datasets",
            "analytics",
            "research",
            "paper",
            "papers",
            "benchmark",
            "eval",
            "evaluation",
            "notebook",
            "pandas",
            "etl",
        ],
        "llm_use": "Use for research workflows, data pipelines, benchmark design, and analysis references.",
    },
    {
        "id": "media-generation",
        "name": "Image, Video, and Generative Media",
        "description": "Image generation, video generation, diffusion, multimodal creation, and creative AI.",
        "keywords": [
            "image",
            "video",
            "diffusion",
            "stable-diffusion",
            "comfyui",
            "flux",
            "sdxl",
            "multimodal",
            "generative-ai",
            "text-to-image",
            "text-to-video",
            "3d",
            "graphics",
        ],
        "llm_use": "Use for multimodal generation stacks, creative pipelines, and image/video model references.",
    },
    {
        "id": "audio-speech",
        "name": "Audio, Speech, and Music",
        "description": "Speech, transcription, voice, music generation, audio processing, and listening systems.",
        "keywords": [
            "audio",
            "speech",
            "voice",
            "tts",
            "stt",
            "transcription",
            "music",
            "sound",
            "whisper",
            "podcast",
        ],
        "llm_use": "Use for speech interfaces, transcription systems, audio agents, and music-related AI workflows.",
    },
    {
        "id": "frontend-ui",
        "name": "Frontend, UI, and Design Systems",
        "description": "Frontend frameworks, UI components, visualization, and design systems.",
        "keywords": [
            "react",
            "nextjs",
            "next-js",
            "vue",
            "svelte",
            "frontend",
            "ui",
            "ux",
            "design-system",
            "tailwind",
            "component",
            "visualization",
            "threejs",
        ],
        "llm_use": "Use for UI implementation patterns, frontend architecture, and component/design references.",
    },
    {
        "id": "infra-platform",
        "name": "Infrastructure, Platform, and Observability",
        "description": "Deployment, cloud, databases, queues, observability, containers, and platform engineering.",
        "keywords": [
            "infrastructure",
            "platform",
            "cloud",
            "docker",
            "kubernetes",
            "database",
            "postgres",
            "redis",
            "serverless",
            "observability",
            "monitoring",
            "deploy",
            "deployment",
            "api",
        ],
        "llm_use": "Use for production architecture, deployment patterns, platform operations, and service integration.",
    },
    {
        "id": "security-privacy",
        "name": "Security and Privacy",
        "description": "Security research, privacy tools, auth, sandboxing, secrets, and defensive engineering.",
        "keywords": [
            "security",
            "privacy",
            "auth",
            "authentication",
            "oauth",
            "sandbox",
            "secret",
            "secrets",
            "pentest",
            "vulnerability",
        ],
        "llm_use": "Use for threat modeling, secure integration patterns, privacy review, and defensive automation.",
    },
    {
        "id": "science-bio",
        "name": "Science, Bio, and Healthcare",
        "description": "Biology, chemistry, medicine, health, scientific computing, and lab automation.",
        "keywords": [
            "bio",
            "biology",
            "protein",
            "medical",
            "health",
            "chemistry",
            "molecule",
            "science",
            "scientific",
            "lab",
            "genomics",
        ],
        "llm_use": "Use for scientific AI workflows, bio/health references, and research automation.",
    },
    {
        "id": "business-productivity",
        "name": "Business, Sales, and Productivity",
        "description": "Business automation, CRM, marketing, finance, productivity, and operations tooling.",
        "keywords": [
            "business",
            "marketing",
            "sales",
            "crm",
            "finance",
            "productivity",
            "email",
            "calendar",
            "notion",
            "slack",
            "spreadsheet",
        ],
        "llm_use": "Use for business workflow automation, operational copilots, and productivity systems.",
    },
    {
        "id": "education-content",
        "name": "Education, Docs, and Content",
        "description": "Documentation, learning resources, courses, publishing, and content tooling.",
        "keywords": [
            "docs",
            "documentation",
            "awesome",
            "course",
            "tutorial",
            "learning",
            "education",
            "content",
            "blog",
            "website",
            "personal-website",
        ],
        "llm_use": "Use as learning material, documentation source, and content/reference corpus for LLMs.",
    },
]


LANGUAGE_CATEGORY_HINTS = {
    "HTML": "frontend-ui",
    "CSS": "frontend-ui",
    "Vue": "frontend-ui",
    "Svelte": "frontend-ui",
    "Astro": "frontend-ui",
    "Jupyter Notebook": "data-research",
    "R": "data-research",
    "HCL": "infra-platform",
    "Dockerfile": "infra-platform",
    "Shell": "infra-platform",
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "uncategorized"


def text_blob(repo: dict[str, Any]) -> str:
    parts: list[str] = [
        repo.get("full_name") or "",
        repo.get("name") or "",
        repo.get("description") or "",
        repo.get("homepage") or "",
        repo.get("language") or "",
    ]
    parts.extend(repo.get("topics") or [])
    return " ".join(parts).lower()


def infer_categories(repo: dict[str, Any]) -> list[dict[str, str]]:
    blob = text_blob(repo)
    topics = {str(topic).lower() for topic in repo.get("topics") or []}
    scored: list[tuple[int, dict[str, Any]]] = []

    for rule in CATEGORY_RULES:
        score = 0
        for keyword in rule["keywords"]:
            keyword_l = keyword.lower()
            if keyword_l in topics:
                score += 4
            if keyword_l in blob:
                score += 1
        if score:
            scored.append((score, rule))

    language = repo.get("language")
    hint = LANGUAGE_CATEGORY_HINTS.get(language)
    if hint and not any(rule["id"] == hint for _, rule in scored):
        for rule in CATEGORY_RULES:
            if rule["id"] == hint:
                scored.append((1, rule))
                break

    scored.sort(key=lambda item: (-item[0], item[1]["name"]))
    selected = [rule for _, rule in scored[:4]]

    if not selected:
        selected = [
            {
                "id": "general-development",
                "name": "General Development",
                "description": "Useful repositories without a stronger category signal.",
                "llm_use": "Use as general reference material and inspect manually before deeper LLM ingestion.",
            }
        ]

    return [
        {
            "id": rule["id"],
            "name": rule["name"],
            "description": rule.get("description", ""),
            "source": "inferred",
            "llm_use": rule.get("llm_use", ""),
        }
        for rule in selected
    ]


def load_manual_categories(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {"repos": {}, "topic_categories": {}}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return {
        "repos": data.get("repos", {}),
        "topic_categories": data.get("topic_categories", {}),
    }


def manual_category_entries(repo: dict[str, Any], manual: dict[str, Any]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    full_name = repo.get("full_name") or ""
    repo_config = manual.get("repos", {}).get(full_name, {})

    for category in repo_config.get("categories", []):
        entries.append(
            {
                "id": slugify(category),
                "name": str(category),
                "description": "Manual category override.",
                "source": "manual",
                "llm_use": repo_config.get("llm_use", ""),
            }
        )

    topic_map = manual.get("topic_categories", {})
    for topic in repo.get("topics") or []:
        for category in topic_map.get(topic, []):
            entries.append(
                {
                    "id": slugify(category),
                    "name": str(category),
                    "description": f"Manual category mapped from topic '{topic}'.",
                    "source": "manual-topic",
                    "llm_use": "",
                }
            )

    deduped: dict[tuple[str, str], dict[str, str]] = {}
    for entry in entries:
        deduped[(entry["source"], entry["id"])] = entry
    return list(deduped.values())


def infer_llm_use(repo: dict[str, Any], categories: list[dict[str, str]]) -> str:
    manual = [cat.get("llm_use", "") for cat in categories if cat.get("source") == "manual" and cat.get("llm_use")]
    if manual:
        return manual[0]
    if categories and categories[0].get("llm_use"):
        return categories[0]["llm_use"]
    if repo.get("description"):
        return "Use as supporting context after inspecting the README and examples."
    return "Use as a pointer for manual inspection; metadata is sparse."


def categorize_repositories(repos: list[dict[str, Any]], manual: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    category_by_repo: dict[str, list[dict[str, str]]] = {}
    for repo in repos:
        categories = manual_category_entries(repo, manual) + infer_categories(repo)
        deduped: dict[str, dict[str, str]] = {}
        for category in categories:
            deduped.setdefault(f"{category['source']}:{category['id']}", category)
        category_by_repo[repo.get("full_name") or ""] = list(deduped.values())
    return category_by_repo
