from __future__ import annotations

import json
import unittest
from pathlib import Path

from star_index.github_api import normalize_star_items
from star_index.taxonomy import categorize_repositories, load_manual_categories


FIXTURE = Path(__file__).parent / "fixtures" / "sample-stars.raw.json"


class NormalizationTaxonomyTests(unittest.TestCase):
    def test_normalize_and_categorize_fixture_repositories(self) -> None:
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        repos = normalize_star_items(payload["stars"])
        self.assertEqual(repos[0]["full_name"], "example/agent-memory-kit")
        self.assertEqual(repos[1]["full_name"], "example/playwright-ops")

        categories = categorize_repositories(repos, load_manual_categories(Path("missing.json")))
        first_ids = {entry["id"] for entry in categories["example/agent-memory-kit"]}
        second_ids = {entry["id"] for entry in categories["example/playwright-ops"]}

        self.assertIn("rag-memory", first_ids)
        self.assertIn("ai-agents", first_ids)
        self.assertIn("automation-browser", second_ids)


if __name__ == "__main__":
    unittest.main()
