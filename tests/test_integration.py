"""Optional native-engine tests. CI explicitly enables these with pinned fixtures."""

import os
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path

from pages_converter.conversion import convert_pages, find_soffice


@unittest.skipUnless(
    os.environ.get("PAGES_TEST_FIXTURES"), "Set PAGES_TEST_FIXTURES for native conversion tests"
)
class NativeConversionTests(unittest.TestCase):
    def test_pages4_and_pages5_produce_valid_word_packages(self):
        self.assertIsNotNone(find_soffice(), "LibreOffice is required for the enabled integration test")
        with tempfile.TemporaryDirectory() as directory:
            for name in ("pages4-file.pages", "pages5-file.pages"):
                with self.subTest(document=name):
                    source = Path(os.environ["PAGES_TEST_FIXTURES"]) / name
                    destination = Path(directory) / source.with_suffix(".docx").name
                    convert_pages(source, destination, threading.Event())
                    with zipfile.ZipFile(destination) as archive:
                        self.assertIn("[Content_Types].xml", archive.namelist())
                        self.assertIn("word/document.xml", archive.namelist())
                        self.assertGreater(len(archive.read("word/document.xml")), 500)


if __name__ == "__main__":
    unittest.main()
