"""Bounded jobs, cancellation, collision-safe output, and expiring downloads."""

import atexit
import json
import shutil
import tempfile
import threading
import time
import uuid
import zipfile
from pathlib import Path

from .conversion import Cancelled, ConversionError, convert_pages
from .paths import PathAllocator, validate_path

MAX_BYTES = 1024**3
MAX_FILES = 500
MAX_JOBS = 3
RETENTION = 3600
PUBLIC_KEYS = ("id", "status", "total", "processed", "converted", "copied", "failed", "current", "error")


class JobManager:
    def __init__(self):
        self.lock = threading.RLock()
        self.slot = threading.BoundedSemaphore(1)
        self.jobs = {}
        self.closed = threading.Event()
        self.reaper = threading.Thread(target=self._reap, daemon=True)
        self.reaper.start()
        atexit.register(self.close)

    def _reap(self):
        while not self.closed.wait(60):
            self.expire()

    def expire(self):
        with self.lock:
            for key, job in list(self.jobs.items()):
                if job.get("expires", float("inf")) <= time.monotonic() and not job["readers"]:
                    self._delete(key)

    def _delete(self, key):
        job = self.jobs.pop(key)
        shutil.rmtree(job["temp"], ignore_errors=True)

    def close(self):
        self.closed.set()
        atexit.unregister(self.close)
        with self.lock:
            workers = []
            for job in self.jobs.values():
                job["cancel"].set()
                workers.append(job["worker"])
        for worker in workers:
            worker.join(timeout=20)
        with self.lock:
            for key in list(self.jobs):
                if not self.jobs[key]["worker"].is_alive() and not self.jobs[key]["readers"]:
                    self._delete(key)

    def public(self, key):
        with self.lock:
            job = self.jobs.get(key)
            return {name: job.get(name) for name in PUBLIC_KEYS} if job else None

    def update(self, key, **values):
        with self.lock:
            self.jobs[key].update(values)

    def create(self, files, manifest):
        """Caller owns slot until successful return; worker owns it thereafter."""
        self.expire()
        with self.lock:
            if self.closed.is_set():
                raise ValueError("server_closed")
            if len(self.jobs) >= MAX_JOBS:
                raise ValueError("storage_full")
        if not isinstance(manifest, list) or len(manifest) != len(files) or not 0 < len(files) <= MAX_FILES:
            raise ValueError("invalid_manifest")
        paths = [validate_path(item) for item in manifest]
        workspace = Path(tempfile.mkdtemp(prefix="pages-job-"))
        try:
            incoming = workspace / "input"
            incoming.mkdir()
            allocator = PathAllocator()
            originals = [allocator.reserve(path) for path in paths]
            items = []
            for index, (file, original, requested) in enumerate(zip(files, originals, manifest, strict=True)):
                # Numbered storage avoids input directory/file conflicts and Windows path limits.
                source = incoming / (str(index) + original.suffix)
                file.save(source)
                target = (
                    allocator.reserve(original.with_suffix(".docx"))
                    if original.suffix.lower() == ".pages"
                    else original
                )
                items.append((source, original, target, requested))
            report = allocator.reserve(validate_path("pages-converter-report.json"))
            key = uuid.uuid4().hex
            worker = threading.Thread(target=self._process, args=(key,), daemon=True)
            job = dict(
                id=key,
                status="queued",
                total=len(items),
                processed=0,
                converted=0,
                copied=0,
                failed=0,
                current="",
                error=None,
                temp=workspace,
                items=items,
                report=report,
                cancel=threading.Event(),
                readers=0,
                worker=worker,
            )
            with self.lock:
                if self.closed.is_set():
                    raise ValueError("server_closed")
                self.jobs[key] = job
                try:
                    worker.start()
                except Exception:
                    self.jobs.pop(key, None)
                    raise
            return key
        except BaseException:
            shutil.rmtree(workspace, ignore_errors=True)
            raise

    def _process(self, key):
        with self.lock:
            job = self.jobs[key]
        output = job["temp"] / "output"
        results = []
        zip_entries = []
        try:
            output.mkdir()
            self.update(key, status="processing")
            for index, (source, original, target, requested) in enumerate(job["items"]):
                if job["cancel"].is_set():
                    raise Cancelled()
                self.update(key, current=str(original))
                # Logical folder paths exist only inside the ZIP, avoiding MAX_PATH
                # and reserved-name quirks in the temporary filesystem.
                destination = output / (str(index) + target.suffix)
                error = None
                if original.suffix.lower() == ".pages":
                    try:
                        convert_pages(source, destination, job["cancel"])
                        outcome = "converted"
                    except ConversionError as exc:
                        outcome, error, target = "failed", str(exc), original
                        destination = output / (str(index) + original.suffix)
                        shutil.copyfile(source, destination)
                else:
                    shutil.copyfile(source, destination)
                    outcome = "copied"
                results.append(dict(input=requested, output=str(target), status=outcome, error=error))
                zip_entries.append((destination, target.as_posix()))
                with self.lock:
                    job[outcome] += 1
                    job["processed"] += 1
            self.update(key, status="packing", current="")
            report_path = output / "report.json"
            report_path.write_text(
                json.dumps({"format": 1, "files": results}, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            zip_entries.append((report_path, job["report"].as_posix()))
            archive = job["temp"] / "pages-converter-output.zip"
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=3) as bundle:
                for file, logical_path in zip_entries:
                    if job["cancel"].is_set():
                        raise Cancelled()
                    with (
                        file.open("rb") as source,
                        bundle.open(logical_path, "w", force_zip64=True) as target,
                    ):
                        while chunk := source.read(1024 * 1024):
                            if job["cancel"].is_set():
                                raise Cancelled()
                            target.write(chunk)
            if job["cancel"].is_set():
                raise Cancelled()
            shutil.rmtree(output)
            shutil.rmtree(job["temp"] / "input")
            self.update(key, status="done", current="", archive=archive, expires=time.monotonic() + RETENTION)
        except Cancelled:
            shutil.rmtree(job["temp"], ignore_errors=True)
            self.update(key, status="cancelled", current="", expires=time.monotonic() + 60)
        except Exception:
            shutil.rmtree(job["temp"], ignore_errors=True)
            self.update(
                key, status="error", current="", error="processing_failed", expires=time.monotonic() + 600
            )
        finally:
            self.slot.release()

    def discard(self, key):
        with self.lock:
            job = self.jobs.get(key)
            if not job:
                return False
            if job["readers"]:
                raise ValueError("download_busy")
            if job["status"] not in ("done", "error", "cancelled"):
                job["cancel"].set()
            else:
                self._delete(key)
            return True

    def download(self, key):
        with self.lock:
            job = self.jobs.get(key)
            if not job or job["status"] != "done":
                return None
            stream = job["archive"].open("rb")
            job["readers"] += 1
            size = job["archive"].stat().st_size

        released = False

        def release():
            nonlocal released
            stream.close()
            with self.lock:
                if released:
                    return
                released = True
                job["readers"] -= 1
                if self.closed.is_set() and not job["readers"] and key in self.jobs:
                    self._delete(key)

        return stream, size, release
