import contextlib
import http.client
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path

from tools.tests.helpers import REPO, write
sys.path.insert(0, str(REPO / "shared"))
import centroid_config
import fetch_manual as fm

PDF_BODY = b"%PDF-1.7\n1 0 obj << /Type /Pages >>\n2 0 obj << /Type /Page >>\n3 0 obj << /Type /Page >>\n"
PDF = PDF_BODY + b"%%EOF\n"


class FakeResponse(io.BytesIO):
    headers = {}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


class FetchManualTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self._env = dict(os.environ)
        os.environ["CENTROID_AI_HOME"] = str(tmp / "home")
        os.environ.pop("CENTROID_AI_MANUALS", None)
        self.manifest = write(tmp / "manuals.json", json.dumps([{
            "id": "m1", "title": "Test Manual", "citeAs": "Test", "url": "https://example.com/m1.pdf",
            "file": "m1.pdf", "expectRev": None, "expectPages": 2, "pdfOffset": 0, "sizeMB": 1}]))
        self.dest = tmp / "home" / "manuals" / "m1.pdf"
        self._urlopen = fm.urlopen
        self.requests = []

    def tearDown(self):
        fm.urlopen = self._urlopen
        os.environ.clear()
        os.environ.update(self._env)
        self._tmp.cleanup()

    def serve(self, body, headers=None):
        def fake(request, timeout=None):
            self.requests.append(request)
            resp = FakeResponse(body)
            resp.headers = headers or {}
            return resp
        fm.urlopen = fake

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = fm.main([*args, "--manifest", str(self.manifest)])
        return code, out.getvalue(), err.getvalue()

    def test_existing_file_prints_path(self):
        write(self.dest, "%PDF-")
        code, out, _ = self.run_cli("m1")
        self.assertEqual((code, out.strip()), (0, str(self.dest)))

    def test_ask_mode_requests_consent_without_network(self):
        self.serve(PDF)
        code, out, _ = self.run_cli("m1")
        self.assertEqual(code, 4)
        self.assertIn("Test Manual", out)
        self.assertEqual(self.requests, [])

    def test_never_mode(self):
        centroid_config.set_value("manuals.autoDownload", "never")
        code, out, _ = self.run_cli("m1")
        self.assertEqual(code, 5)
        self.assertIn("https://example.com/m1.pdf", out)

    def test_yes_downloads_with_browser_headers(self):
        self.serve(PDF)
        code, out, _ = self.run_cli("m1", "--yes")
        self.assertEqual(code, 0)
        self.assertEqual(self.dest.read_bytes(), PDF)
        self.assertIn("Mozilla", self.requests[0].get_header("User-agent"))

    def test_always_mode_downloads(self):
        centroid_config.set_value("manuals.autoDownload", "always")
        self.serve(PDF)
        self.assertEqual(self.run_cli("m1")[0], 0)

    def test_html_error_page_is_rejected_and_removed(self):
        self.serve(b"<html>blocked</html>")
        code, out, _ = self.run_cli("m1", "--yes")
        self.assertEqual(code, 1)
        self.assertFalse(self.dest.exists())
        self.assertEqual(list(self.dest.parent.glob("*")), [])
        self.assertIn("https://example.com/m1.pdf", out)

    def assert_download_failed(self, body_or_error, headers=None):
        if isinstance(body_or_error, Exception):
            def fake(request, timeout=None):
                self.requests.append(request)
                raise body_or_error
            fm.urlopen = fake
        else:
            self.serve(body_or_error, headers)
        code, out, _ = self.run_cli("m1", "--yes")
        self.assertEqual(code, 1)
        self.assertIn("https://example.com/m1.pdf", out)
        self.assertFalse(self.dest.exists())
        self.assertEqual(list(self.dest.parent.glob("*")), [])

    def test_network_error_exits_1_with_manual_url(self):
        self.assert_download_failed(urllib.error.URLError("offline"))

    def test_truncated_body_exits_1_with_manual_url(self):
        self.assert_download_failed(http.client.IncompleteRead(b"%PDF-1.7 partial"))

    def test_content_length_mismatch_exits_1(self):
        self.assert_download_failed(PDF, {"Content-Length": str(len(PDF) + 10)})

    def test_missing_eof_marker_exits_1(self):
        self.assert_download_failed(PDF_BODY)

    def test_matching_content_length_succeeds(self):
        self.serve(PDF, {"Content-Length": str(len(PDF))})
        self.assertEqual(self.run_cli("m1", "--yes")[0], 0)

    def test_eof_marker_may_be_followed_by_whitespace(self):
        self.serve(PDF_BODY + b"%%EOF\r\n\r\n  ")
        self.assertEqual(self.run_cli("m1", "--yes")[0], 0)

    def test_sequential_downloads_leave_no_part_files(self):
        self.serve(PDF)
        self.run_cli("m1", "--yes")
        self.dest.unlink()
        self.run_cli("m1", "--yes")
        self.assertEqual([p.name for p in self.dest.parent.iterdir()], ["m1.pdf"])

    def test_failed_download_keeps_unrelated_part_file(self):
        other = write(self.dest.parent / "m1.pdf.x.part", "keep")
        self.serve(b"<html>blocked</html>")
        self.assertEqual(self.run_cli("m1", "--yes")[0], 1)
        self.assertEqual(other.read_text(), "keep")
        self.assertEqual([p.name for p in self.dest.parent.iterdir()], ["m1.pdf.x.part"])

    def test_existing_dest_wins_and_temp_is_removed(self):
        def fake(request, timeout=None):
            write(self.dest, "winner")
            resp = FakeResponse(PDF)
            resp.headers = {}
            return resp
        fm.urlopen = fake
        fm.download("https://example.com/m1.pdf", self.dest)
        self.assertEqual(self.dest.read_text(), "winner")
        self.assertEqual([p.name for p in self.dest.parent.iterdir()], ["m1.pdf"])

    def test_zero_byte_body_exits_1_with_manual_url(self):
        self.assert_download_failed(b"")

    def test_page_count_mismatch_warns_but_succeeds(self):
        self.serve(PDF_BODY + b"4 0 obj << /Type /Page >>\n%%EOF\n")
        code, _, err = self.run_cli("m1", "--yes")
        self.assertEqual(code, 0)
        self.assertIn("citations may be slightly off", err)

    def test_unknown_id(self):
        self.assertEqual(self.run_cli("nope")[0], 2)

    def test_list(self):
        code, out, _ = self.run_cli("--list")
        self.assertEqual(code, 0)
        self.assertIn("m1", out)


if __name__ == "__main__":
    unittest.main()
