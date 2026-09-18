import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def nav_targets(items):
    for item in items:
        for value in item.values():
            if isinstance(value, str):
                yield value
            else:
                yield from nav_targets(value)


class SiteStructureTest(unittest.TestCase):
    def test_navigation_targets_exist(self):
        config = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))
        missing = [target for target in nav_targets(config["nav"]) if not (DOCS / target).is_file()]
        self.assertEqual([], missing)

    def test_required_pages_and_assets_are_present(self):
        expected = [
            DOCS / "index.md",
            DOCS / "agent-development/index.md",
            DOCS / "agent-development/uv-langgraph-cli.md",
            DOCS / "assets/stylesheets/extra.css",
            DOCS / "assets/images/uv-langgraph-workflow.svg",
            DOCS / "assets/images/uv-langgraph-hero.png",
        ]
        self.assertEqual([], [str(path.relative_to(ROOT)) for path in expected if not path.is_file()])


if __name__ == "__main__":
    unittest.main()
