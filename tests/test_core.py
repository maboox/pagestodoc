import io
import json
import tempfile
import threading
import time
import unittest
import zipfile
from pathlib import Path, PurePosixPath
from unittest.mock import patch

from werkzeug.datastructures import FileStorage, MultiDict
from werkzeug.test import Client
from werkzeug.wrappers import Response

from pages_converter.conversion import Cancelled, ConversionError, validate_pages
from pages_converter.jobs import JobManager
from pages_converter.paths import PathAllocator, validate_path
from pages_converter.server import BODY_LIMIT, Application


class PathsTests(unittest.TestCase):
    def test_rejects_unsafe_and_windows_paths(self):
        for path in (
            "../secret",
            "/etc/passwd",
            "a/../b",
            "C:/data",
            "a//b",
            "CON.pages",
            "aux/x",
            "LPT1",
            "a/NUL.txt",
            "trailing. ",
            "a\x00b",
            "a:b",
            "a/",
            "a/./b",
            "\u202efile",
            5,
            None,
        ):
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_path(path)

    def test_unicode_and_backslashes(self):
        self.assertEqual(validate_path("پروژه\\نامه‌ها.pages").as_posix(), "پروژه/نامه‌ها.pages")
        self.assertEqual(validate_path("cafe\u0301.pages").name, "café.pages")

    def test_case_and_file_directory_collisions(self):
        allocator = PathAllocator()
        paths = ["Folder", "folder/One.pdf", "FOLDER/two.pdf", "REPORT.docx", "report.docx"]
        output = [str(allocator.reserve(PurePosixPath(path))) for path in paths]
        self.assertEqual(
            output, ["Folder", "folder-2/One.pdf", "folder-2/two.pdf", "REPORT.docx", "report-2.docx"]
        )


class JobTests(unittest.TestCase):
    def setUp(self):
        self.manager = JobManager()

    def tearDown(self):
        self.manager.close()

    def start(self, paths, contents=None):
        files = [
            FileStorage(io.BytesIO(content), filename=Path(str(path)).name)
            for path, content in zip(paths, contents or [b"original"] * len(paths), strict=True)
        ]
        self.assertTrue(self.manager.slot.acquire(False))
        try:
            return self.manager.create(files, paths)
        except BaseException:
            self.manager.slot.release()
            raise

    def finish(self, key):
        self.manager.jobs[key]["worker"].join(10)
        self.assertFalse(self.manager.jobs[key]["worker"].is_alive())
        return self.manager.jobs[key]

    def test_conversion_does_not_overwrite_existing_word_file(self):
        def convert(source, destination, cancel):
            destination.write_bytes(b"converted")

        with patch("pages_converter.jobs.convert_pages", convert):
            key = self.start(
                ["Project/Report.pages", "Project/report.docx", "Project/تصویر.png"],
                [b"pages", b"existing", b"picture"],
            )
            job = self.finish(key)
        self.assertEqual(job["status"], "done")
        self.assertEqual((job["converted"], job["copied"], job["failed"]), (1, 2, 0))
        with zipfile.ZipFile(job["archive"]) as bundle:
            self.assertEqual(bundle.read("Project/Report-2.docx"), b"converted")
            self.assertEqual(bundle.read("Project/report.docx"), b"existing")
            self.assertEqual(bundle.read("Project/تصویر.png"), b"picture")
            report = json.loads(bundle.read("pages-converter-report.json"))
            self.assertEqual(report["files"][0]["output"], "Project/Report-2.docx")
        self.assertFalse((job["temp"] / "input").exists())

    def test_failure_keeps_original_and_report_does_not_overwrite_input(self):
        with patch("pages_converter.jobs.convert_pages", side_effect=ConversionError("invalid_pages")):
            key = self.start(["Bad.pages", "pages-converter-report.json"], [b"bad", b"user report"])
            job = self.finish(key)
        self.assertEqual(job["failed"], 1)
        with zipfile.ZipFile(job["archive"]) as bundle:
            self.assertEqual(bundle.read("Bad.pages"), b"bad")
            self.assertEqual(bundle.read("pages-converter-report.json"), b"user report")
            report = json.loads(bundle.read("pages-converter-report-2.json"))
            self.assertEqual(report["files"][0]["error"], "invalid_pages")

    def test_case_collisions_and_long_logical_paths(self):
        long_path = "a" * 100 + "/" + "b" * 100 + ".pdf"
        key = self.start(["ONE.txt", "one.txt", long_path])
        job = self.finish(key)
        self.assertEqual(job["status"], "done")
        with zipfile.ZipFile(job["archive"]) as bundle:
            self.assertEqual(len(bundle.namelist()), 4)
            self.assertIn("one-2.txt", bundle.namelist())
            self.assertIn(long_path, bundle.namelist())

    def test_active_cancellation_cleans_files_and_releases_slot(self):
        entered = threading.Event()

        def convert(source, destination, cancel):
            entered.set()
            cancel.wait(5)
            raise Cancelled()

        with patch("pages_converter.jobs.convert_pages", convert):
            key = self.start(["test.pages"])
            self.assertTrue(entered.wait(3))
            self.manager.discard(key)
            job = self.finish(key)
        self.assertEqual(job["status"], "cancelled")
        self.assertFalse(job["temp"].exists())
        self.assertTrue(self.manager.slot.acquire(False))
        self.manager.slot.release()

    def test_expiry_and_active_download(self):
        key = self.start(["one.pdf"])
        job = self.finish(key)
        stream, _, release = self.manager.download(key)
        try:
            job["expires"] = time.monotonic() - 1
            self.manager.expire()
            self.assertIsNotNone(self.manager.public(key))
            with self.assertRaises(ValueError):
                self.manager.discard(key)
            self.assertTrue(stream.read(2))
        finally:
            release()
        self.manager.expire()
        self.assertIsNone(self.manager.public(key))
        self.assertFalse(job["temp"].exists())

    def test_unexpected_failure_is_redacted(self):
        with patch(
            "pages_converter.jobs.convert_pages", side_effect=OSError("private-user/private-document")
        ):
            key = self.start(["test.pages"])
            job = self.finish(key)
        self.assertEqual(job["status"], "error")
        self.assertNotIn("private", json.dumps(self.manager.public(key)))
        self.assertFalse(job["temp"].exists())

    def test_completed_result_is_deleted_while_worker_finishes(self):
        key = self.start(["file.pdf"])
        job = self.finish(key)
        with patch.object(job["worker"], "is_alive", return_value=True):
            self.assertTrue(self.manager.discard(key))
        self.assertIsNone(self.manager.public(key))
        self.assertFalse(job["temp"].exists())

    def test_shutdown_with_reader_cleans_when_reader_closes(self):
        key = self.start(["file.pdf"])
        job = self.finish(key)
        _, _, release = self.manager.download(key)
        self.manager.close()
        self.assertTrue(job["temp"].exists())
        release()
        release()  # WSGI middleware may close an iterable more than once.
        self.assertFalse(job["temp"].exists())

    def test_storage_bound_and_invalid_manifest(self):
        for _ in range(3):
            self.finish(self.start(["file.pdf"]))
        with self.assertRaisesRegex(ValueError, "storage_full"):
            self.start(["file.pdf"])

    def test_validation_does_not_create_workspace(self):
        with patch("pages_converter.jobs.tempfile.mkdtemp") as mkdtemp:
            for paths in (["../outside"], [], [None]):
                with self.assertRaises(ValueError):
                    self.start(paths)
            mkdtemp.assert_not_called()


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.application = Application()
        self.client = Client(self.application, Response)
        self.base = "http://127.0.0.1:8765"
        self.get("/")

    def tearDown(self):
        self.application.manager.close()

    def get(self, path, **kwargs):
        return self.client.get(path, base_url=self.base, **kwargs)

    def post(self, data=None, **kwargs):
        return self.client.post(
            "/api/jobs",
            base_url=self.base,
            data=data,
            headers={"X-Pages-Token": self.application.token},
            **kwargs,
        )

    def test_security_headers_and_no_external_assets(self):
        response = self.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])
        self.assertNotIn("unsafe-inline", response.headers["Content-Security-Policy"])
        self.assertIn("HttpOnly", response.headers["Set-Cookie"])
        self.assertIn("SameSite=Strict", response.headers["Set-Cookie"])
        asset = self.get("/assets/app.js")
        self.assertEqual(asset.status_code, 200)
        asset.close()
        self.assertEqual(self.get("/assets/../app.py").status_code, 404)
        self.assertEqual(self.get("/.git/config").status_code, 404)

    def test_session_and_csrf_required(self):
        anonymous = Client(self.application, Response)
        self.assertEqual(anonymous.get("/api/health", base_url=self.base).status_code, 403)
        self.assertEqual(self.client.post("/api/jobs", base_url=self.base).status_code, 403)
        self.assertEqual(self.get("/api/health").status_code, 200)
        invalid = self.client.post("/api/jobs", base_url=self.base, headers={"X-Pages-Token": "é"})
        self.assertEqual(invalid.status_code, 403)

    def test_sessions_on_different_ports_do_not_overwrite_each_other(self):
        other = Application(8766)
        try:

            def dispatch(environ, start_response):
                target = other if environ.get("HTTP_HOST", "").endswith(":8766") else self.application
                return target(environ, start_response)

            client = Client(dispatch, Response)
            client.get("/", base_url=self.base)
            client.get("/", base_url="http://127.0.0.1:8766")
            self.assertEqual(client.get("/api/health", base_url=self.base).status_code, 200)
            self.assertEqual(client.get("/api/health", base_url="http://127.0.0.1:8766").status_code, 200)
        finally:
            other.manager.close()

    def test_rejects_foreign_host_origin_and_fetch_site(self):
        self.assertEqual(self.client.get("/", base_url="http://evil.test:8765").status_code, 403)
        self.assertEqual(self.get("/", headers={"Origin": "https://evil.test"}).status_code, 403)
        self.assertEqual(self.get("/", headers={"Sec-Fetch-Site": "cross-site"}).status_code, 403)

    def test_invalid_upload_is_rejected_without_leaking_slot(self):
        for manifest in ({}, ["../escape.pdf"], ["CON.txt"], [], [1]):
            data = {"manifest": json.dumps(manifest), "files": (io.BytesIO(b"data"), "file.pdf")}
            response = self.post(data)
            self.assertEqual(response.status_code, 400, response.text)
            self.assertTrue(self.application.manager.slot.acquire(False))
            self.application.manager.slot.release()

    def test_malformed_multipart_and_oversize(self):
        response = self.post(b"broken", content_type="multipart/form-data; boundary=test")
        self.assertEqual(response.status_code, 400)
        response = self.client.open(
            "/api/jobs",
            method="POST",
            base_url=self.base,
            headers={"X-Pages-Token": self.application.token},
            content_type="multipart/form-data; boundary=test",
            environ_overrides={"CONTENT_LENGTH": str(BODY_LIMIT + 1)},
        )
        self.assertEqual(response.status_code, 413)

    def test_http_roundtrip_download_and_delete(self):
        data = MultiDict(
            [
                ("manifest", json.dumps(["Project/one.pdf", "Project/two.txt"])),
                ("files", (io.BytesIO(b"pdf"), "one.pdf")),
                ("files", (io.BytesIO(b"text"), "two.txt")),
            ]
        )
        started = self.post(data)
        self.assertEqual(started.status_code, 202, started.text)
        key = started.json["job"]
        self.application.manager.jobs[key]["worker"].join(10)
        response = self.get(f"/api/jobs/{key}")
        self.assertEqual(response.json["status"], "done")
        download = self.get(f"/api/jobs/{key}/download")
        with zipfile.ZipFile(io.BytesIO(download.data)) as bundle:
            self.assertEqual(bundle.read("Project/one.pdf"), b"pdf")
        download.close()
        self.assertEqual(self.application.manager.jobs[key]["readers"], 0)
        content = self.get(f"/api/jobs/{key}/content")
        self.assertNotIn("Content-Disposition", content.headers)
        self.assertEqual(content.data, download.data)
        content.close()
        deleted = self.client.delete(
            f"/api/jobs/{key}", base_url=self.base, headers={"X-Pages-Token": self.application.token}
        )
        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(self.get(f"/api/jobs/{key}").status_code, 404)

    def test_busy_upload(self):
        self.application.manager.slot.acquire()
        try:
            result = self.post({"manifest": "[]"}, content_type="multipart/form-data")
            self.assertEqual(result.status_code, 409)
            self.assertEqual(result.json["error"], "busy")
        finally:
            self.application.manager.slot.release()


class ConversionTests(unittest.TestCase):
    def test_rejects_non_pages_and_expansion_bomb(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "file.pages"
            source.write_bytes(b"not a zip")
            with self.assertRaisesRegex(ConversionError, "invalid_pages"):
                validate_pages(source)
            with zipfile.ZipFile(source, "w", zipfile.ZIP_DEFLATED) as bundle:
                bundle.writestr("index.xml", b"0" * 1024**2)
            with self.assertRaisesRegex(ConversionError, "archive_limit"):
                validate_pages(source)


if __name__ == "__main__":
    unittest.main()
