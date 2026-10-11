import contextlib
import io
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


def set_short(pdir, short, extensions=None):
    data = {"name": pdir.name, "version": "0.1.0"}
    data["extensions"] = extensions if extensions is not None else {
        "com.openai": {"interface": {"shortDescription": short}}}
    write(pdir / "plugin.json", json.dumps(data))


class ChatGPTProfileTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.pdir = make_plugin(self.root, "centroid-a")
        write_catalogs(self.root, ["centroid-a"])

    def tearDown(self):
        self._tmp.cleanup()

    def run_main(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cm.main([str(self.root), *args])
        return code, out.getvalue()

    def test_long_short_description_warns(self):
        set_short(self.pdir, "x" * 31)
        self.assertEqual(cm.chatgpt_warnings(self.root),
                         ["warning: centroid-a: shortDescription is 31 chars (ChatGPT target 30)"])

    def test_exactly_at_limit_is_not_warned(self):
        set_short(self.pdir, "x" * 30)
        self.assertEqual(cm.chatgpt_warnings(self.root), [])

    def test_max_short_changes_threshold(self):
        set_short(self.pdir, "x" * 12)
        self.assertEqual(cm.chatgpt_warnings(self.root, max_short=12), [])
        self.assertEqual(cm.chatgpt_warnings(self.root, max_short=11),
                         ["warning: centroid-a: shortDescription is 12 chars (ChatGPT target 11)"])

    def test_missing_or_malformed_extensions_skipped(self):
        self.assertEqual(cm.chatgpt_warnings(self.root), [])  # make_plugin writes no extensions
        set_short(self.pdir, None, extensions="not-a-dict")
        self.assertEqual(cm.chatgpt_warnings(self.root), [])
        set_short(self.pdir, None, extensions={"com.openai": {"interface": {"shortDescription": 7}}})
        self.assertEqual(cm.chatgpt_warnings(self.root), [])

    def test_profile_prints_warnings_and_exits_zero(self):
        set_short(self.pdir, "x" * 40)
        code, out = self.run_main("--profile", "chatgpt")
        self.assertEqual(code, 0)
        self.assertIn("warning: centroid-a: shortDescription is 40 chars (ChatGPT target 30)", out)
        self.assertIn("OK: catalogs and manifests agree", out)

    def test_profile_flag_on_cli_sets_limit(self):
        set_short(self.pdir, "x" * 40)
        code, out = self.run_main("--profile", "chatgpt", "--max-short", "50")
        self.assertEqual(code, 0)
        self.assertNotIn("warning:", out)

    def test_default_run_prints_no_warnings(self):
        set_short(self.pdir, "x" * 40)
        code, out = self.run_main()
        self.assertEqual(code, 0)
        self.assertNotIn("warning:", out)

    def test_profile_still_fails_on_real_problems(self):
        write_catalogs(self.root, ["centroid-a", "centroid-missing"])
        code, _ = self.run_main("--profile", "chatgpt")
        self.assertEqual(code, 1)

    def test_max_short_must_be_positive(self):
        for bad in ("0", "-3"):
            with self.assertRaises(SystemExit) as ctx, contextlib.redirect_stderr(io.StringIO()):
                cm.main([str(self.root), "--profile", "chatgpt", "--max-short", bad])
            self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
