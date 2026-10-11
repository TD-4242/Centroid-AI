import os
import sys
import tempfile
import unittest
from pathlib import Path

from tools.tests.helpers import REPO, write
sys.path.insert(0, str(REPO / "shared"))
sys.path.insert(0, str(REPO / "plugins" / "centroid-plc" / "scripts"))
import centroid_config
import mpucomp_locate as ml


class LocateTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.t = Path(self._tmp.name)
        self._env = dict(os.environ)
        os.environ["CENTROID_AI_HOME"] = str(self.t / "home")
        self.project = self.t / "proj"
        (self.project / ".git").mkdir(parents=True)
        self.src = write(self.project / "plc" / "my.src", "x")
        self.wine = self.t / "wine"
        self.kw = dict(is_windows=False, wineprefix=self.wine)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        self._tmp.cleanup()

    def exe(self, path):
        return write(path, "MZ")

    def test_nothing_found(self):
        self.assertIsNone(ml.locate(self.src, **self.kw))

    def test_next_to_source_is_project(self):
        exe = self.exe(self.project / "plc" / "mpucomp.exe")
        self.assertEqual(ml.locate(self.src, **self.kw), ml.Found(exe, "project"))

    def test_repo_root_is_project(self):
        exe = self.exe(self.project / "mpucomp.exe")
        self.assertEqual(ml.locate(self.src, **self.kw), ml.Found(exe, "project"))

    def test_wine_cnc12_folder_needs_confirmation_origin(self):
        exe = self.exe(self.wine / "drive_c" / "cncr" / "mpucomp.exe")
        self.assertEqual(ml.locate(self.src, **self.kw), ml.Found(exe, "cnc12"))

    def test_windows_cnc12_folder(self):
        exe = self.exe(self.t / "C" / "cncm" / "mpucomp.exe")
        found = ml.locate(self.src, is_windows=True, windows_root=self.t / "C")
        self.assertEqual(found, ml.Found(exe, "cnc12"))

    def test_uppercase_exe_found(self):
        exe = self.exe(self.wine / "drive_c" / "cncm" / "MPUCOMP.EXE")
        self.assertEqual(ml.locate(self.src, **self.kw).path, exe)

    def test_config_beats_project(self):
        cfg_exe = self.exe(self.t / "elsewhere" / "mpucomp.exe")
        self.exe(self.project / "mpucomp.exe")
        centroid_config.set_value("mpucomp.path", str(cfg_exe))
        self.assertEqual(ml.locate(self.src, **self.kw), ml.Found(cfg_exe, "config"))

    def test_explicit_beats_everything(self):
        exe = self.exe(self.t / "x" / "mpucomp.exe")
        self.exe(self.project / "mpucomp.exe")
        self.assertEqual(ml.locate(self.src, explicit=str(exe), **self.kw), ml.Found(exe, "explicit"))

    def test_explicit_folder_is_searched(self):
        exe = self.exe(self.t / "cncr" / "mpucomp.exe")
        self.assertEqual(ml.locate(self.src, explicit=str(self.t / "cncr"), **self.kw).path, exe)

    def test_explicit_missing_raises_not_falls_through(self):
        self.exe(self.project / "mpucomp.exe")
        with self.assertRaises(FileNotFoundError) as ctx:
            ml.locate(self.src, explicit=str(self.t / "typo.exe"), **self.kw)
        self.assertIn("typo.exe", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
