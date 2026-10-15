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

    def test_ignored_files_not_exported(self):
        with open(self.root / ".gitignore", "a", encoding="utf-8") as f:
            f.write("*.plc\n*.exe\n")
        write(self.pdir / "out.plc", "compiled")
        write(self.pdir / "bin" / "mpucomp.exe", "binary")
        for allow_dirty in (False, True):
            names = self.names(self.export(allow_dirty=allow_dirty))
            self.assertNotIn("centroid-a/out.plc", names)
            self.assertNotIn("centroid-a/bin/mpucomp.exe", names)

    def test_allow_dirty_includes_untracked_and_skips_deleted(self):
        write(self.pdir / "skills" / "s1" / "reference" / "new.md", "new\n")
        (self.pdir / "scripts" / "x.py").unlink()
        names = self.names(self.export(allow_dirty=True))
        self.assertIn("centroid-a/skills/s1/reference/new.md", names)
        self.assertNotIn("centroid-a/scripts/x.py", names)

    def test_force_added_binary_refused(self):
        with open(self.root / ".gitignore", "a", encoding="utf-8") as f:
            f.write("*.exe\n")
        write(self.pdir / "bin" / "mpucomp.exe", "binary")
        git(self.root, "add", "-f", "plugins/centroid-a/bin/mpucomp.exe")
        git(self.root, "commit", "-qm", "oops")
        with self.assertRaises(ep.ExportError) as ctx:
            self.export()
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("mpucomp.exe", str(ctx.exception))

    @unittest.skipUnless(hasattr(Path, "symlink_to"), "no symlinks")
    def test_tracked_symlink_refused(self):
        secret = write(self.root.parent / f"{self.root.name}-outside.txt", "secret")
        self.addCleanup(secret.unlink)
        try:
            (self.pdir / "link.txt").symlink_to(secret)
        except OSError:
            self.skipTest("cannot create symlinks here")
        git(self.root, "add", "plugins/centroid-a/link.txt")
        git(self.root, "commit", "-qm", "link")
        with self.assertRaises(ep.ExportError) as ctx:
            self.export()
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("symlink", str(ctx.exception))

    def test_out_inside_plugin_refused(self):
        self.out = self.pdir / "dist"
        with self.assertRaises(ep.ExportError) as ctx:
            self.export(allow_dirty=True)
        self.assertEqual(ctx.exception.code, 2)
        self.assertFalse(self.out.exists())

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


class ExportAllTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.out = self.root / "dist"
        for name in ("centroid-b", "centroid-a"):
            make_plugin(self.root, name, version="1.0.0")
        write_catalogs(self.root, ["centroid-b", "centroid-a"])
        write(self.root / ".gitignore", "__pycache__/\n*.pyc\ndist/\n")
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "t@example.com")
        git(self.root, "config", "user.name", "t")
        git(self.root, "config", "commit.gpgsign", "false")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "init")
        self.sha = git(self.root, "rev-parse", "HEAD")

    def tearDown(self):
        self._tmp.cleanup()

    def test_catalog_plugins_in_catalog_order(self):
        self.assertEqual(ep.catalog_plugins(self.root), ["centroid-b", "centroid-a"])

    def test_all_skips_plugin_in_one_catalog(self):
        make_plugin(self.root, "centroid-c")
        write_catalogs(self.root, ["centroid-b", "centroid-a", "centroid-c"],
                       codex_names=["centroid-b", "centroid-a"])
        self.assertEqual(ep.catalog_plugins(self.root), ["centroid-b", "centroid-a"])

    def test_all_deduplicates(self):
        write_catalogs(self.root, ["centroid-b", "centroid-a", "centroid-b"])
        self.assertEqual(ep.catalog_plugins(self.root), ["centroid-b", "centroid-a"])

    def test_export_all_writes_one_zip_per_plugin(self):
        paths = ep.export_all(self.root, self.out, now=FIXED_NOW)
        self.assertEqual([p.name for p in paths],
                         [f"centroid-b-1.0.0-{self.sha[:7]}.zip", f"centroid-a-1.0.0-{self.sha[:7]}.zip"])
        self.assertTrue(all(p.is_file() for p in paths))

    def test_stable_name(self):
        path = ep.export(self.root, "centroid-a", self.out, now=FIXED_NOW, stable_name=True)
        self.assertEqual(path, self.out / "centroid-a.zip")
        with zipfile.ZipFile(path) as zf:
            self.assertIn("version: 1.0.0\n", zf.read("centroid-a/SOURCE.txt").decode("utf-8"))

    def test_stable_name_overwrites_existing_zip(self):
        write(self.out / "centroid-a.zip", "stale, not a zip")
        path = ep.export(self.root, "centroid-a", self.out, now=FIXED_NOW, stable_name=True)
        with zipfile.ZipFile(path) as zf:
            self.assertIn("centroid-a/SOURCE.txt", zf.namelist())

    def test_all_stops_on_dirty_plugin(self):
        write(self.root / "plugins" / "centroid-a" / "skills" / "s1" / "SKILL.md", "changed\n")
        with self.assertRaises(ep.ExportError) as ctx:
            ep.export_all(self.root, self.out, now=FIXED_NOW, stable_name=True)
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("plugins/centroid-a", str(ctx.exception))
        self.assertTrue((self.out / "centroid-b.zip").is_file())
        self.assertFalse((self.out / "centroid-a.zip").exists())

    def test_main_all_prints_each_path(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ep.main(["--all", "--stable-name", "--root", str(self.root), "--out", str(self.out)])
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue().splitlines(),
                         [str(self.out / "centroid-b.zip"), str(self.out / "centroid-a.zip")])

    def test_main_all_error_exit_code(self):
        write(self.root / "plugins" / "centroid-a" / "skills" / "s1" / "SKILL.md", "changed\n")
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = ep.main(["--all", "--root", str(self.root), "--out", str(self.out)])
        self.assertEqual(code, 1)
        self.assertTrue(err.getvalue().startswith("error: "))

    def test_main_plugin_and_all_is_usage_error(self):
        for argv in (["centroid-a", "--all"], []):
            with self.assertRaises(SystemExit) as ctx, contextlib.redirect_stderr(io.StringIO()):
                ep.main([*argv, "--root", str(self.root)])
            self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
