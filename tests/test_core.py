import importlib.util
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pages_converter", ROOT / "app.py")
app = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(app)


class PagesConverterTests(unittest.TestCase):
    def tearDown(self):
        for job_id in list(app.JOBS):
            app.cleanup_job(job_id)

    def test_sanitizes_relative_paths(self):
        result = app.safe_relative_path("../../Project/../Report.pages", "fallback.pages")
        self.assertEqual(result.as_posix(), "Project/Report.pages")

    def test_preserves_structure_and_copies_other_files(self):
        temp_dir = Path(tempfile.mkdtemp())
        incoming = temp_dir / "incoming"
        incoming.mkdir()
        pages_file = incoming / "Report.pages"
        pdf_file = incoming / "Reference.pdf"
        pages_file.write_bytes(b"pages")
        pdf_file.write_bytes(b"original-pdf")

        original_converter = app.convert_pages
        app.convert_pages = lambda source, destination: destination.write_bytes(b"docx")
        job_id = "test-job"
        app.JOBS[job_id] = {
            "status": "queued", "total": 2, "processed": 0,
            "converted": 0, "copied": 0, "failed": 0,
            "current": "", "error": None, "temp_dir": str(temp_dir),
            "items": [
                (str(pages_file), "Project/Reports/Report.pages"),
                (str(pdf_file), "Project/References/Reference.pdf"),
            ],
        }
        try:
            app.process_job(job_id)
            job = app.JOBS[job_id]
            self.assertEqual(job["status"], "done")
            self.assertEqual((job["converted"], job["copied"], job["failed"]), (1, 1, 0))
            with zipfile.ZipFile(job["zip_path"]) as archive:
                self.assertEqual(sorted(archive.namelist()), [
                    "Project/References/Reference.pdf",
                    "Project/Reports/Report.docx",
                ])
                self.assertEqual(archive.read("Project/References/Reference.pdf"), b"original-pdf")
        finally:
            app.convert_pages = original_converter


if __name__ == "__main__":
    unittest.main()
