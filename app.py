#!/usr/bin/env python3
import html
import json
import os
import platform
import shutil
import subprocess
import tempfile
import threading
import urllib.parse
import uuid
import zipfile
from email.parser import BytesParser
from email.policy import default
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", "8765"))
MAX_BYTES = 1024 * 1024 * 1024
JOBS = {}
JOBS_LOCK = threading.Lock()


def safe_name(name: str) -> str:
    name = Path(name.replace("\\", "/")).name
    cleaned = "".join(c for c in name if c.isalnum() or c in " ._-()[]").strip(" .")
    return cleaned or "file"


def safe_relative_path(raw: str, fallback: str) -> Path:
    parts = []
    for part in str(raw or fallback).replace("\\", "/").split("/"):
        if not part or part in (".", ".."):
            continue
        cleaned = "".join(c for c in part if c.isalnum() or c in " ._-()[]").strip(" .")
        if cleaned:
            parts.append(cleaned)
    return Path(*parts) if parts else Path(safe_name(fallback))


def unique_path(folder: Path, filename: str) -> Path:
    candidate = folder / filename
    stem, suffix = candidate.stem, candidate.suffix
    i = 2
    while candidate.exists():
        candidate = folder / f"{stem}-{i}{suffix}"
        i += 1
    return candidate


def find_soffice():
    found = shutil.which("soffice") or shutil.which("libreoffice")
    if found:
        return found
    if platform.system() == "Windows":
        candidates = [
            Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "LibreOffice/program/soffice.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "LibreOffice/program/soffice.exe",
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
    return None


def convert_pages(source: Path, destination: Path) -> None:
    soffice = find_soffice()
    if soffice:
        with tempfile.TemporaryDirectory(prefix="lo-profile-") as profile_dir, tempfile.TemporaryDirectory(prefix="lo-output-") as output_dir:
            profile_uri = Path(profile_dir).resolve().as_uri()
            flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            result = subprocess.run(
                [soffice, "--headless", f"-env:UserInstallation={profile_uri}", "--convert-to", "docx", "--outdir", output_dir, str(source)],
                capture_output=True, text=True, timeout=300, creationflags=flags,
            )
            generated = Path(output_dir) / (source.stem + ".docx")
            if result.returncode == 0 and generated.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(generated), str(destination))
                return
            raise RuntimeError((result.stderr or result.stdout or "LibreOffice نتوانست فایل را باز کند.").strip())
    if platform.system() == "Darwin" and shutil.which("osascript"):
        result = subprocess.run(["osascript", str(ROOT / "convert.applescript"), str(source), str(destination)], capture_output=True, text=True, timeout=300)
        if result.returncode == 0 and destination.exists():
            return
        raise RuntimeError((result.stderr or result.stdout or "خطای نامشخص Pages").strip())
    raise RuntimeError("LibreOffice نصب یا پیدا نشد.")


def update_job(job_id, **values):
    with JOBS_LOCK:
        if job_id in JOBS:
            JOBS[job_id].update(values)


def public_job(job):
    return {k: job.get(k) for k in ("status", "total", "processed", "converted", "copied", "failed", "current", "error")}


def cleanup_job(job_id):
    with JOBS_LOCK:
        job = JOBS.pop(job_id, None)
    if job:
        shutil.rmtree(job.get("temp_dir", ""), ignore_errors=True)


def schedule_cleanup(job_id, delay):
    timer = threading.Timer(delay, cleanup_job, args=(job_id,))
    timer.daemon = True
    timer.start()


def process_job(job_id):
    with JOBS_LOCK:
        job = JOBS[job_id]
        items = list(job["items"])
        temp_dir = Path(job["temp_dir"])
    outgoing = temp_dir / "output"
    outgoing.mkdir(parents=True, exist_ok=True)
    converted = copied = failed = 0
    failures = []
    try:
        update_job(job_id, status="processing")
        for index, (source_text, relative_text) in enumerate(items, start=1):
            source = Path(source_text)
            relative = Path(relative_text)
            update_job(job_id, current=relative.as_posix())
            try:
                if relative.suffix.lower() == ".pages":
                    destination = outgoing / relative.with_suffix(".docx")
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination = unique_path(destination.parent, destination.name)
                    convert_pages(source, destination)
                    converted += 1
                else:
                    destination = outgoing / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination = unique_path(destination.parent, destination.name)
                    shutil.copy2(source, destination)
                    copied += 1
            except Exception as exc:
                failed += 1
                failures.append({"file": relative.as_posix(), "error": str(exc)[:600]})
                # Keep an unconverted Pages original so no input file disappears.
                fallback = outgoing / relative
                fallback.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, unique_path(fallback.parent, fallback.name))
            update_job(job_id, processed=index, converted=converted, copied=copied, failed=failed)

        zip_path = temp_dir / "pages-converter-output.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in outgoing.rglob("*"):
                if file.is_file():
                    zf.write(file, file.relative_to(outgoing).as_posix())
            if failures:
                report = "\n".join(f"{x['file']}: {x['error']}" for x in failures)
                zf.writestr("conversion-errors.txt", report)
        update_job(job_id, status="done", current="", zip_path=str(zip_path), failures=failures)
        schedule_cleanup(job_id, 3600)
    except Exception as exc:
        update_job(job_id, status="error", current="", error=str(exc)[:1000])
        schedule_cleanup(job_id, 600)


class Handler(BaseHTTPRequestHandler):
    server_version = "PagesConverter/1.0"

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            body = (ROOT / "index.html").read_bytes()
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        elif parsed.path == "/health":
            self.send_json(200, {"ok": True, "platform": platform.system(), "converterAvailable": find_soffice() is not None})
        elif parsed.path == "/progress":
            job_id = urllib.parse.parse_qs(parsed.query).get("job", [""])[0]
            with JOBS_LOCK:
                job = JOBS.get(job_id)
                payload = public_job(job) if job else None
            self.send_json(200, payload) if payload else self.send_json(404, {"error": "پردازش پیدا نشد."})
        elif parsed.path == "/download":
            job_id = urllib.parse.parse_qs(parsed.query).get("job", [""])[0]
            with JOBS_LOCK:
                job = JOBS.get(job_id)
                zip_path = Path(job["zip_path"]) if job and job.get("status") == "done" else None
            if not zip_path or not zip_path.exists():
                return self.send_json(404, {"error": "فایل خروجی آماده نیست."})
            data = zip_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", 'attachment; filename="pages-converter-output.zip"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers(); self.wfile.write(data)
        else:
            self.send_error(404)

    def do_POST(self):
        if urllib.parse.urlparse(self.path).path != "/start":
            return self.send_error(404)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BYTES:
                return self.send_json(413, {"error": "حجم درخواست نامعتبر یا بیشتر از ۱ گیگابایت است."})
            content_type = self.headers.get("Content-Type", "")
            if "multipart/form-data" not in content_type:
                return self.send_json(400, {"error": "فرمت درخواست معتبر نیست."})
            raw = self.rfile.read(length)
            message = BytesParser(policy=default).parsebytes((f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n").encode() + raw)
            all_parts = list(message.iter_parts())
            file_parts = [p for p in all_parts if p.get_param("name", header="content-disposition") == "files"]
            manifest_part = next((p for p in all_parts if p.get_param("name", header="content-disposition") == "manifest"), None)
            if not file_parts:
                return self.send_json(400, {"error": "هیچ فایلی دریافت نشد."})
            try:
                manifest = json.loads((manifest_part.get_payload(decode=True) or b"[]").decode("utf-8")) if manifest_part else []
            except Exception:
                manifest = []

            temp_dir = Path(tempfile.mkdtemp(prefix="pages-job-"))
            incoming = temp_dir / "incoming"; incoming.mkdir()
            items = []
            for index, part in enumerate(file_parts):
                original = safe_name(part.get_filename() or "file")
                relative = safe_relative_path(manifest[index] if index < len(manifest) else original, original)
                source = incoming / relative
                source.parent.mkdir(parents=True, exist_ok=True)
                source = unique_path(source.parent, source.name)
                source.write_bytes(part.get_payload(decode=True) or b"")
                items.append((str(source), relative.as_posix()))

            job_id = uuid.uuid4().hex
            with JOBS_LOCK:
                JOBS[job_id] = {"status": "queued", "total": len(items), "processed": 0, "converted": 0, "copied": 0, "failed": 0, "current": "", "error": None, "temp_dir": str(temp_dir), "items": items}
            threading.Thread(target=process_job, args=(job_id,), daemon=True).start()
            self.send_json(202, {"job": job_id, "total": len(items)})
        except Exception as exc:
            self.send_json(500, {"error": f"خطای سرور: {html.escape(str(exc))}"})


if __name__ == "__main__":
    print(f"Pages Converter -> http://{HOST}:{PORT}")
    print("برای توقف Ctrl+C را بزنید.")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
