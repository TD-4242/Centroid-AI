import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

from tools.tests.helpers import REPO, write
sys.path.insert(0, str(REPO / "shared"))
import centroid_config as cc


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name) / "home"
        self._env = dict(os.environ)
        os.environ["CENTROID_AI_HOME"] = str(self.home)
        os.environ.pop("CENTROID_AI_MANUALS", None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        self._tmp.cleanup()

    def test_defaults_without_file(self):
        cfg = cc.load()
        self.assertEqual(cfg["manuals"]["autoDownload"], "ask")
        self.assertIsNone(cfg["mpucomp"]["path"])

    def test_set_then_load_round_trip(self):
        cc.set_value("mpucomp.path", "C:/cncr/mpucomp.exe")
        self.assertEqual(cc.load()["mpucomp"]["path"], "C:/cncr/mpucomp.exe")
        self.assertEqual(cc.load()["manuals"]["autoDownload"], "ask")

    def test_rejects_bad_auto_download(self):
        with self.assertRaises(ValueError):
            cc.set_value("manuals.autoDownload", "sometimes")

    def test_manuals_dir_precedence(self):
        self.assertEqual(cc.manuals_dir(), self.home / "manuals")
        cc.set_value("manuals.dir", str(Path(self._tmp.name) / "cfg"))
        self.assertEqual(cc.manuals_dir(), Path(self._tmp.name) / "cfg")
        os.environ["CENTROID_AI_MANUALS"] = str(Path(self._tmp.name) / "env")
        self.assertEqual(cc.manuals_dir(), Path(self._tmp.name) / "env")

    def test_invalid_json_is_one_line_error(self):
        write(self.home / "config.json", "{broken")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(cc.main(["show"]), 2)
        self.assertIn("config.json is not valid JSON", err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())

    def test_top_level_not_object_is_one_line_error(self):
        write(self.home / "config.json", "[1, 2]")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(cc.main(["show"]), 2)
        self.assertIn("config.json must be a JSON object", err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())

    def test_section_not_object_is_rejected(self):
        write(self.home / "config.json", '{"manuals": "x"}')
        with self.assertRaises(ValueError):
            cc.manuals_dir()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(cc.main(["show"]), 2)
        self.assertIn("section 'manuals' must be a JSON object", err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())

    def test_cli_set_null(self):
        cc.main(["set", "mpucomp.path", "X"])
        cc.main(["set", "mpucomp.path", "null"])
        self.assertIsNone(cc.load()["mpucomp"]["path"])


if __name__ == "__main__":
    unittest.main()
