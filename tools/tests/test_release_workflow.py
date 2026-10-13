import unittest

from tools.tests.helpers import REPO

WORKFLOW = REPO / ".github" / "workflows" / "release.yml"


class ReleaseWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_release_workflow_shape(self):
        lines = [line.strip() for line in self.text.splitlines()]
        self.assertIn('tags: ["v*"]', lines)
        self.assertIn("contents: write", lines)
        order = ["tools/check_marketplace.py", "tools/check_skill_links.py",
                 "tools/sync_shared.py --check", "unittest discover",
                 "tools/export_plugin.py --all --stable-name --out dist",
                 "sha256sum *.zip > SHA256SUMS.txt", "gh release create"]
        positions = [self.text.index(step) for step in order]
        self.assertEqual(positions, sorted(positions), "checks must run before export and publish")

    def test_release_uploads_only_zips_and_sums(self):
        create = next(line for line in self.text.splitlines() if "gh release create" in line)
        self.assertIn("dist/*.zip dist/SHA256SUMS.txt", create)
        self.assertNotIn("dist/*", create.replace("dist/*.zip", ""))
        self.assertIn("--notes-file dist/NOTES.md", create)
        self.assertIn("--generate-notes", create)
