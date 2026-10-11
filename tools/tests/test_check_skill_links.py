import tempfile
import unittest
from pathlib import Path

from tools.tests.helpers import make_plugin, write
import check_skill_links as csl


class CheckSkillLinksTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.a = make_plugin(self.root, "centroid-a", skills=("centroid-alpha",))
        self.b = make_plugin(self.root, "centroid-b", skills=("centroid-beta",))

    def tearDown(self):
        self._tmp.cleanup()

    def skill(self, plugin_dir, skill, text):
        write(plugin_dir / "skills" / skill / "SKILL.md",
              f"---\nname: {skill}\ndescription: t\n---\n{text}")

    def test_clean_tree(self):
        write(self.a / "skills/centroid-alpha/reference/r.md", "# Ref Head\n")
        self.skill(self.a, "centroid-alpha", "See [r](reference/r.md#ref-head) and `centroid-alpha`.\n")
        self.assertEqual(csl.check_tree(self.root), [])

    def test_broken_link_and_anchor(self):
        write(self.a / "skills/centroid-alpha/reference/r.md", "# Ref\n")
        self.skill(self.a, "centroid-alpha", "[x](reference/missing.md)\n[y](reference/r.md#nope)\n")
        misses = csl.check_tree(self.root)
        self.assertTrue(any("broken link reference/missing.md" in m for m in misses))
        self.assertTrue(any("broken anchor reference/r.md#nope" in m for m in misses))

    def test_unknown_skill_name(self):
        self.skill(self.a, "centroid-alpha", "See `centroid-cnc12-gmcodes`.\n")
        self.assertTrue(any("unknown skill centroid-cnc12-gmcodes" in m for m in csl.check_tree(self.root)))

    def test_plugin_names_are_known(self):
        write(self.root / "README.md", "Install `centroid-a`.\n")
        self.assertEqual(csl.check_tree(self.root), [])

    def test_cross_plugin_reference_needs_citation(self):
        self.skill(self.a, "centroid-alpha", "Use `centroid-beta` for that.\n")
        self.assertTrue(any("cross-plugin skill centroid-beta" in m for m in csl.check_tree(self.root)))

    def test_cross_plugin_reference_with_citation_ok(self):
        self.skill(self.a, "centroid-alpha",
                   "If installed, use `centroid-beta`; otherwise see (VCP Manual p.44).\n")
        self.assertEqual(csl.check_tree(self.root), [])

    def test_specs_are_not_checked(self):
        write(self.root / "docs/superpowers/specs/x.md", "`centroid-nope` [x](gone.md)\n")
        self.assertEqual(csl.check_tree(self.root), [])

    def test_fenced_code_headings_are_not_anchors(self):
        write(self.root / "docs/a.md", "```\n# Not A Heading\n```\n# Real\n")
        write(self.root / "docs/b.md", "[x](a.md#not-a-heading) [y](a.md#real)\n")
        misses = csl.check_tree(self.root)
        self.assertEqual(len(misses), 1)
        self.assertIn("a.md#not-a-heading", misses[0])


if __name__ == "__main__":
    unittest.main()
