import re
import unittest

from tools.tests.helpers import REPO

GUIDE = REPO / "docs" / "chatgpt-browser.md"


class ChatGPTBrowserDocTest(unittest.TestCase):
    def setUp(self):
        self.text = GUIDE.read_text(encoding="utf-8")

    def test_prompt_placeholders_are_the_table_columns(self):
        prompt = self.text.split("Create a private plugin", 1)[1].split("```", 1)[0]
        self.assertEqual(re.findall(r"<[^>]+>", prompt),
                         ["<plugin name>", "<display name>", "<short description>"])

    def test_browser_claims_marked_unverified(self):
        paragraphs = self.text.split("\n\n")
        for claim in ("work as knowledge plugins", "Knowledge answers work in the browser"):
            para = next(p for p in paragraphs if claim in p)
            self.assertIn("*(unverified)*", para, claim)
