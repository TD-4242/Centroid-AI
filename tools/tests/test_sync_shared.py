import tempfile
import unittest
from pathlib import Path

from tools.tests.helpers import make_plugin, write
import sync_shared


class SyncSharedTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        for name in sync_shared.SHARED:
            write(self.root / "shared" / name, f"# {name}\n")
        self.plugin = make_plugin(self.root, "centroid-a")

    def tearDown(self):
        self._tmp.cleanup()

    def test_check_reports_missing_copies(self):
        drift = sync_shared.sync(self.root, check=True)
        self.assertIn("plugins/centroid-a/scripts/fetch_manual.py", drift)
        self.assertFalse((self.plugin / "scripts").exists())

    def test_sync_then_check_is_clean(self):
        sync_shared.sync(self.root, check=False)
        self.assertEqual((self.plugin / "scripts" / "fetch_manual.py").read_text(), "# fetch_manual.py\n")
        self.assertEqual(sync_shared.sync(self.root, check=True), [])

    def test_check_detects_edited_copy(self):
        sync_shared.sync(self.root, check=False)
        write(self.plugin / "scripts" / "centroid_config.py", "# edited\n")
        self.assertEqual(sync_shared.sync(self.root, check=True),
                         ["plugins/centroid-a/scripts/centroid_config.py"])

    def test_no_plugins_dir_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(Path(tmp) / "shared" / "centroid_config.py", "x\n")
            self.assertEqual(sync_shared.sync(tmp, check=True), [])


if __name__ == "__main__":
    unittest.main()
