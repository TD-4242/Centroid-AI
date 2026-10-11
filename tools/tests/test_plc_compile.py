import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.tests.helpers import REPO, write
sys.path.insert(0, str(REPO / "shared"))
sys.path.insert(0, str(REPO / "plugins" / "centroid-plc" / "scripts"))
import mpucomp_locate
import plc_compile as pc

OK_LOG = "Compiling...\nWarning: unused X\nWarning: unused Y\nCompilation successful\nProgram size: 1234\n"
BAD_LOG = "Error Line 12: unknown symbol Foo\nCompilation failed\n"


class ParseTest(unittest.TestCase):
    def test_success(self):
        r = pc.parse_log(OK_LOG, 0)
        self.assertTrue(r.ok)
        self.assertEqual(len(r.warnings), 2)
        self.assertEqual(r.summary, ["Compilation successful", "Program size: 1234"])

    def test_failure(self):
        r = pc.parse_log(BAD_LOG, 0)
        self.assertFalse(r.ok)
        self.assertIn("Error Line 12: unknown symbol Foo", r.errors)

    def test_nonzero_exit_without_error_text_shows_whole_log(self):
        r = pc.parse_log("weird crash\n", 3)
        self.assertFalse(r.ok)
        self.assertEqual(r.errors, ["weird crash"])

    def test_command_windows_and_wine(self):
        exe = Path("/c/mpucomp.exe")
        self.assertEqual(pc.build_command(exe, "a.src", "o.plc", True), [str(exe), "-w", "a.src", "o.plc"])
        self.assertEqual(pc.build_command(exe, "a.src", "o.plc", False)[:2], ["wine", str(exe)])


class CliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        t = Path(self._tmp.name)
        self.src = write(t / "my.src", "x")
        self.exe = write(t / "mpucomp.exe", "MZ")
        self._env = dict(os.environ)
        os.environ["CENTROID_AI_HOME"] = str(t / "home")
        self._locate, self._run, self._which = pc.locate, pc.RUNNER, pc.shutil.which
        pc.shutil.which = lambda name: "/usr/bin/wine"

    def tearDown(self):
        pc.locate, pc.RUNNER, pc.shutil.which = self._locate, self._run, self._which
        os.environ.clear()
        os.environ.update(self._env)
        self._tmp.cleanup()

    def cli(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = pc.main([str(self.src), *args])
        return code, out.getvalue()

    def fake_run(self, log, rc=0):
        def run(cmd, **kw):
            self.cmd, self.kw = cmd, kw
            return subprocess.CompletedProcess(cmd, rc, stdout=log, stderr="")
        pc.RUNNER = run

    def test_success_reports_warning_count(self):
        self.fake_run(OK_LOG)
        code, out = self.cli()
        self.assertEqual(code, 0)
        self.assertIn("Warnings: 2", out)
        self.assertEqual(self.kw["cwd"], self.src.resolve().parent)

    def test_compile_error_exit_1(self):
        self.fake_run(BAD_LOG)
        code, out = self.cli()
        self.assertEqual(code, 1)
        self.assertIn("Error Line 12", out)

    def test_not_found_prints_friendly_help(self):
        pc.locate = lambda *a, **k: None
        code, out = self.cli()
        self.assertEqual(code, 2)
        self.assertIn("Centroid's PLC compiler", out)
        self.assertIn("C:\\cncr", out)

    def test_cnc12_hit_needs_confirmation(self):
        pc.locate = lambda *a, **k: mpucomp_locate.Found(Path("/w/drive_c/cncr/mpucomp.exe"), "cnc12")
        code, out = self.cli()
        self.assertEqual(code, 3)
        self.assertIn("CONFIRM COMPILER: /w/drive_c/cncr/mpucomp.exe", out)

    def test_missing_wine_explained(self):
        if os.name == "nt":
            self.skipTest("Wine is not used on Windows")
        pc.shutil.which = lambda name: None
        code, out = self.cli("--compiler", str(self.exe))
        self.assertEqual(code, 2)
        self.assertIn("Wine", out)

    def test_missing_source(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            self.assertEqual(pc.main([str(self.src) + ".nope"]), 2)


class RealCompilerTest(unittest.TestCase):
    """Set CENTROID_AI_TEST_SRC to a .src whose folder (or repo) holds mpucomp.exe."""

    def test_real_source_compiles(self):
        src = os.environ.get("CENTROID_AI_TEST_SRC")
        if not src:
            self.skipTest("CENTROID_AI_TEST_SRC not set")
        found = mpucomp_locate.locate(Path(src))
        if found is None:
            self.skipTest("no mpucomp.exe next to the test source")
        self.assertTrue(pc.compile_src(Path(src), found.path).ok)


if __name__ == "__main__":
    unittest.main()
