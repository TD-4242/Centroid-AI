import contextlib
import io
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from tools.tests.helpers import make_plugin, write, write_catalogs
import export_plugin as ep

FIXED_NOW = datetime(2026, 10, 11, 12, 0, 0, tzinfo=timezone.utc)


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


class ExportPluginTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.out = self.root / "dist"
        self.pdir = make_plugin(self.root, "centroid-a", version="1.2.3")
        write(self.pdir / "scripts" / "x.py", "print(1)\n")
        write_catalogs(self.root, ["centroid-a"])
        write(self.root / ".gitignore", "__pycache__/\n*.pyc\ndist/\n")
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "t@example.com")
        git(self.root, "config", "user.name", "t")
        git(self.root, "config", "commit.gpgsign", "false")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "init")
        self.sha = git(self.root, "rev-parse", "HEAD")
        write(self.pdir / "scripts" / "__pycache__" / "x.cpython-312.pyc", "junk")

    def tearDown(self):
        self._tmp.cleanup()

    def export(self, plugin="centroid-a", **kw):
        return ep.export(self.root, plugin, self.out, now=FIXED_NOW, **kw)

    def names(self, zip_path):
        with zipfile.ZipFile(zip_path) as zf:
            return set(zf.namelist())

    def source(self, zip_path):
        with zipfile.ZipFile(zip_path) as zf:
            return zf.read("centroid-a/SOURCE.txt").decode("utf-8")

    def test_zip_name_and_layout(self):
        path = self.export()
        self.assertEqual(path, self.out / f"centroid-a-1.2.3-{self.sha[:7]}.zip")
        self.assertEqual(self.names(path), {
            "centroid-a/.claude-plugin/plugin.json",
            "centroid-a/plugin.json",
            "centroid-a/skills/s1/SKILL.md",
            "centroid-a/scripts/x.py",
            "centroid-a/SOURCE.txt",
        })

    def test_source_txt_fields(self):
        self.assertEqual(self.source(self.export()), (
            "repository: https://github.com/TD-4242/Centroid-AI\n"
            "plugin: centroid-a\n"
            "version: 1.2.3\n"
            f"commit: {self.sha}\n"
            "exported: 2026-10-11T12:00:00Z\n"
            "dirty: false\n"))

    def test_modified_file_refused(self):
        write(self.pdir / "scripts" / "x.py", "print(2)\n")
        with self.assertRaises(ep.ExportError) as ctx:
            self.export()
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("--allow-dirty", str(ctx.exception))
        self.assertFalse(self.out.exists())

    def test_untracked_file_is_dirty(self):
        write(self.pdir / "skills" / "s1" / "reference" / "new.md", "new\n")
        with self.assertRaises(ep.ExportError) as ctx:
            self.export()
        self.assertEqual(ctx.exception.code, 1)

    def test_allow_dirty_marks_source(self):
        write(self.pdir / "scripts" / "x.py", "print(2)\n")
        path = self.export(allow_dirty=True)
        self.assertIn("dirty: true\n", self.source(path))
        with zipfile.ZipFile(path) as zf:
            self.assertEqual(zf.read("centroid-a/scripts/x.py"), b"print(2)\n")

    def test_change_outside_plugin_not_dirty(self):
        write(self.root / "README.md", "uncommitted\n")
        make_plugin(self.root, "centroid-b")
        self.assertIn("dirty: false\n", self.source(self.export()))

    def test_unknown_plugin(self):
        with self.assertRaises(ep.ExportError) as ctx:
            self.export("nope")
        self.assertEqual(ctx.exception.code, 2)

    def test_path_like_name_rejected(self):
        for name in ("../centroid-a", "plugins/centroid-a", "centroid-a/"):
            with self.assertRaises(ep.ExportError) as ctx:
                self.export(name)
            self.assertEqual(ctx.exception.code, 2)

    def test_plugin_in_only_one_catalog(self):
        make_plugin(self.root, "centroid-b")
        write_catalogs(self.root, ["centroid-a", "centroid-b"], codex_names=["centroid-a"])
        with self.assertRaises(ep.ExportError) as ctx:
            self.export("centroid-b")
        self.assertEqual(ctx.exception.code, 2)

    def test_not_a_git_repo(self):
        shutil.rmtree(self.root / ".git")
        with self.assertRaises(ep.ExportError) as ctx:
            self.export()
        self.assertEqual(ctx.exception.code, 2)

    def test_out_dir_created(self):
        self.out = self.root / "a" / "b"
        self.assertTrue(self.export().is_file())

    def test_main_prints_path(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ep.main(["centroid-a", "--root", str(self.root), "--out", str(self.out)])
        self.assertEqual(code, 0)
        self.assertTrue(Path(out.getvalue().strip()).is_file())

    def test_main_error_is_one_line(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = ep.main(["nope", "--root", str(self.root)])
        self.assertEqual(code, 2)
        self.assertEqual(len(err.getvalue().strip().splitlines()), 1)
        self.assertTrue(err.getvalue().startswith("error: "))

    def test_main_default_out_is_root_dist(self):
        with contextlib.redirect_stdout(io.StringIO()):
            ep.main(["centroid-a", "--root", str(self.root)])
        self.assertEqual(len(list((self.root / "dist").glob("centroid-a-1.2.3-*.zip"))), 1)


if __name__ == "__main__":
    unittest.main()
