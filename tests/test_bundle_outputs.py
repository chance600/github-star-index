from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from star_index import bundle as bundle_cmd
from star_index.corpus import category_rollup_records
from star_index.paths import default_output_paths


FIXTURE = Path(__file__).parent / "fixtures" / "sample-stars.raw.json"


class BundleOutputTests(unittest.TestCase):
    def test_default_bundle_path_is_user_scoped(self) -> None:
        paths = default_output_paths("sample-user", Path("data"))
        self.assertEqual(paths["bundle_dir"], Path("data") / "sample-user-corpus")

    def test_bundle_writes_repository_chunk_and_category_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            bundle_dir = Path(tmpdir) / "corpus"
            rc = bundle_cmd.main(
                [
                    "--raw-json",
                    str(FIXTURE),
                    "--bundle-dir",
                    str(bundle_dir),
                ]
            )
            self.assertEqual(rc, 0)

            repo_records = [json.loads(line) for line in (bundle_dir / "repos.jsonl").read_text(encoding="utf-8").splitlines()]
            chunk_records = [json.loads(line) for line in (bundle_dir / "chunks.jsonl").read_text(encoding="utf-8").splitlines()]
            category_records = [
                json.loads(line) for line in (bundle_dir / "categories.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            bundle_manifest = json.loads((bundle_dir / "bundle.manifest.json").read_text(encoding="utf-8"))

            self.assertEqual(len(repo_records), 2)
            self.assertGreaterEqual(len(chunk_records), 2)
            self.assertGreaterEqual(len(category_records), 1)
            self.assertEqual(bundle_manifest["repository_count"], len(repo_records))
            self.assertEqual(bundle_manifest["chunk_count"], len(chunk_records))
            self.assertEqual(bundle_manifest["category_count"], len(category_records))
            self.assertEqual(chunk_records[0]["record_type"], "repository_chunk")
            self.assertIn("chunk_index", chunk_records[0])
            self.assertEqual(category_records[0]["record_type"], "category_rollup")

    def test_category_rollups_deduplicate_same_repo_across_sources(self) -> None:
        repos = [
            {
                "full_name": "example/agent-memory-kit",
                "html_url": "https://github.com/example/agent-memory-kit",
                "description": "Toolkit for agent memory and retrieval experiments.",
                "stargazers_count": 420,
                "language": "Python",
                "topics": ["agent", "memory"],
            }
        ]
        category_by_repo = {
            "example/agent-memory-kit": [
                {"id": "rag-memory", "name": "RAG, Memory, and Knowledge Systems", "description": "", "source": "manual"},
                {"id": "rag-memory", "name": "RAG, Memory, and Knowledge Systems", "description": "", "source": "inferred"},
            ]
        }
        records = category_rollup_records(
            repos,
            category_by_repo=category_by_repo,
            source_user="sample-user",
            generated_at="2026-04-24T00:00:00+00:00",
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["repository_count"], 1)
        self.assertEqual(len(records[0]["top_repositories"]), 1)


if __name__ == "__main__":
    unittest.main()
