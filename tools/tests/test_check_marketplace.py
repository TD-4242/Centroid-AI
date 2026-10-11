import json
import tempfile
import unittest
from pathlib import Path

from tools.tests.helpers import make_plugin, write, write_catalogs
import check_marketplace as cm


class CheckMarketplaceTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_consistent_tree_passes(self):
        make_plugin(self.root, "centroid-a")
        write_catalogs(self.root, ["centroid-a"])
        self.assertEqual(cm.check_tree(self.root), [])

    def test_plugin_only_in_one_catalog(self):
        make_plugin(self.root, "centroid-a")
        make_plugin(self.root, "centroid-b")
        write_catalogs(self.root, ["centroid-a", "centroid-b"], codex_names=["centroid-a"])
        self.assertIn("plugin centroid-b is only in the Claude catalog", cm.check_tree(self.root))

    def test_manifest_name_mismatch(self):
        make_plugin(self.root, "centroid-a", codex_name="other")
        write_catalogs(self.root, ["centroid-a"])
        self.assertTrue(any("portable manifest name is 'other'" in p for p in cm.check_tree(self.root)))

    def test_version_mismatch(self):
        pdir = make_plugin(self.root, "centroid-a")
        write(pdir / "plugin.json", json.dumps({"name": "centroid-a", "version": "0.2.0"}))
        write_catalogs(self.root, ["centroid-a"])
        self.assertTrue(any("versions differ" in p for p in cm.check_tree(self.root)))

    def test_missing_source_dir(self):
        write_catalogs(self.root, ["centroid-a"])
        self.assertTrue(any("does not exist" in p for p in cm.check_tree(self.root)))

    def test_plugin_without_skills(self):
        make_plugin(self.root, "centroid-a", skills=())
        write_catalogs(self.root, ["centroid-a"])
        self.assertIn("centroid-a: no skills/*/SKILL.md", cm.check_tree(self.root))

    def test_skill_frontmatter_name_must_match_folder(self):
        pdir = make_plugin(self.root, "centroid-a")
        write(pdir / "skills" / "s1" / "SKILL.md", "---\nname: wrong\ndescription: x\n---\n")
        write_catalogs(self.root, ["centroid-a"])
        self.assertTrue(any("frontmatter name 'wrong'" in p for p in cm.check_tree(self.root)))

    def test_codex_entry_missing_policy(self):
        make_plugin(self.root, "centroid-a")
        write_catalogs(self.root, ["centroid-a"])
        path = self.root / ".agents" / "plugins" / "marketplace.json"
        data = json.loads(path.read_text())
        del data["plugins"][0]["policy"]
        path.write_text(json.dumps(data))
        self.assertIn("Codex entry centroid-a: missing policy", cm.check_tree(self.root))

    def test_invalid_json_reported(self):
        write(self.root / ".claude-plugin" / "marketplace.json", "{nope")
        write(self.root / ".agents" / "plugins" / "marketplace.json", "{}")
        self.assertTrue(any("invalid JSON" in p for p in cm.check_tree(self.root)))


if __name__ == "__main__":
    unittest.main()
