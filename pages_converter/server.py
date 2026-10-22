"""Loopback-only WSGI application and local Waitress launcher."""

import argparse
import json
import os
import secrets
import tempfile
import threading
import webbrowser
from contextlib import ExitStack
from pathlib import Path

from werkzeug.exceptions import HTTPException, RequestEntityTooLarge
from werkzeug.formparser import parse_form_data
from werkzeug.utils import send_file
from werkzeug.wrappers import Request, Response

from . import __version__
from .conversion import find_soffice
from .jobs import MAX_BYTES, MAX_FILES, JobManager

ROOT = Path(__file__).resolve().parents[1]
BODY_LIMIT = MAX_BYTES + 4 * 1024**2
ASSETS = {
    "/assets/app.js": "text/javascript; charset=utf-8",
    "/assets/styles.css": "text/css; charset=utf-8",
    "/assets/icons.svg": "image/svg+xml",
    "/assets/favicon.svg": "image/svg+xml",
    "/assets/fonts/InterVariable.woff2": "font/woff2",
    "/assets/fonts/Vazirmatn.woff2": "font/woff2",
}


def json_response(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False), status=status, content_type="application/json; charset=utf-8"
    )


class Application:
    def __init__(self, port=8765):
        self.port = port
        self.origin = f"http://127.0.0.1:{port}"
        self.cookie_name = f"pages_session_{port}"
        self.token = secrets.token_urlsafe(32)
        self.manager = JobManager()

    def __call__(self, environ, start_response):
        request = Request(environ)
        try:
            response = self.route(request)
        except RequestEntityTooLarge:
            response = json_response({"error": "too_large"}, 413)
        except (ValueError, HTTPException):
            response = json_response({"error": "invalid_request"}, 400)
        except Exception:
            # Never return engine output, local paths, document content, or tracebacks.
            response = json_response({"error": "server_error"}, 500)
        response.headers.update(
            {
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "no-referrer",
                "Cross-Origin-Resource-Policy": "same-origin",
                "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; font-src 'self'; img-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
                "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            }
        )
        return response(environ, start_response)

    def route(self, request):
        # Exact Host prevents DNS rebinding. No configurable network binding.
        if request.headers.get("Host") != f"127.0.0.1:{self.port}":
            return json_response({"error": "forbidden_host"}, 403)
        if request.headers.get("Sec-Fetch-Site") == "cross-site":
            return json_response({"error": "forbidden_origin"}, 403)
        origin = request.headers.get("Origin")
        if origin and origin != self.origin:
            return json_response({"error": "forbidden_origin"}, 403)
        if request.method == "GET" and request.path == "/":
            page = (ROOT / "index.html").read_text(encoding="utf-8").replace("__SESSION_TOKEN__", self.token)
            response = Response(page, content_type="text/html; charset=utf-8")
            response.set_cookie(self.cookie_name, self.token, httponly=True, samesite="Strict", path="/")
            return response
        if request.method == "GET" and request.path in ASSETS:
            return send_file(
                ROOT / request.path.lstrip("/"),
                request.environ,
                mimetype=ASSETS[request.path],
                conditional=False,
            )
        if not request.path.startswith("/api/"):
            return json_response({"error": "not_found"}, 404)
        if not secrets.compare_digest(
            request.cookies.get(self.cookie_name, "").encode("utf-8"), self.token.encode("ascii")
        ):
            return json_response({"error": "session_expired"}, 403)
        if request.method not in ("GET", "HEAD") and not secrets.compare_digest(
            request.headers.get("X-Pages-Token", "").encode("utf-8"), self.token.encode("ascii")
        ):
            return json_response({"error": "session_expired"}, 403)
        if request.path == "/api/health" and request.method == "GET":
            return json_response(
                dict(
                    ok=True,
                    version=__version__,
                    converterAvailable=bool(find_soffice()),
                    maxBytes=MAX_BYTES,
                    maxFiles=MAX_FILES,
                )
            )
        if request.path == "/api/jobs" and request.method == "POST":
            return self.upload(request)
        parts = request.path.strip("/").split("/")
        if len(parts) in (3, 4) and parts[:2] == ["api", "jobs"]:
            key = parts[2]
            if len(key) != 32 or any(c not in "0123456789abcdef" for c in key):
                return json_response({"error": "not_found"}, 404)
            if len(parts) == 3 and request.method == "GET":
                job = self.manager.public(key)
                return json_response(job) if job else json_response({"error": "job_expired"}, 404)
            if len(parts) == 3 and request.method == "DELETE":
                try:
                    removed = self.manager.discard(key)
                except ValueError:
                    return json_response({"error": "download_busy"}, 409)
                return json_response({"ok": removed})
            if len(parts) == 4 and parts[3] in ("download", "content") and request.method == "GET":
                download = self.manager.download(key)
                if not download:
                    return json_response({"error": "job_expired"}, 404)
                stream, size, release = download
                try:

                    def chunks():
                        while data := stream.read(1024 * 1024):
                            yield data

                    response = Response(chunks(), mimetype="application/octet-stream")
                    if parts[3] == "download":
                        response.mimetype = "application/zip"
                        response.headers["Content-Disposition"] = (
                            'attachment; filename="pages-converter-output.zip"'
                        )
                    response.content_length = size
                    response.call_on_close(release)
                    return response
                except BaseException:
                    release()
                    raise
        return json_response({"error": "not_found"}, 404)

    def upload(self, request):
        if request.mimetype != "multipart/form-data" or not request.content_length:
            return json_response({"error": "invalid_request"}, 400)
        if request.content_length > BODY_LIMIT:
            raise RequestEntityTooLarge()
        if not self.manager.slot.acquire(blocking=False):
            return json_response({"error": "busy"}, 409)
        handed_off = False
        try:
            with ExitStack() as streams:

                def stream_factory(**kwargs):
                    return streams.enter_context(tempfile.TemporaryFile(mode="w+b"))

                _, form, files = parse_form_data(
                    request.environ,
                    stream_factory=stream_factory,
                    max_content_length=BODY_LIMIT,
                    max_form_memory_size=2 * 1024**2,
                    max_form_parts=MAX_FILES + 1,
                    silent=False,
                )
                if set(form) != {"manifest"} or len(form.getlist("manifest")) != 1 or set(files) != {"files"}:
                    return json_response({"error": "invalid_manifest"}, 400)
                try:
                    manifest = json.loads(form["manifest"])
                    uploads = files.getlist("files")
                    size = 0
                    for file in uploads:
                        size += file.stream.seek(0, 2)
                        file.stream.seek(0)
                    if size > MAX_BYTES:
                        raise RequestEntityTooLarge()
                    key = self.manager.create(uploads, manifest)
                    handed_off = True
                    return json_response({"job": key}, 202)
                except ValueError as exc:
                    code = (
                        str(exc)
                        if str(exc) in ("invalid_path", "invalid_manifest", "storage_full")
                        else "invalid_manifest"
                    )
                    return json_response({"error": code}, 409 if code == "storage_full" else 400)
        finally:
            if not handed_off:
                self.manager.slot.release()


def main():
    parser = argparse.ArgumentParser(description="Local Apple Pages to Word converter")
    parser.add_argument("--open", action="store_true", help="Open the browser after binding the server")
    parser.add_argument("--port", type=int, default=os.environ.get("PORT", "8765"))
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Port must be between 1024 and 65535")
    from waitress import create_server

    application = Application(args.port)
    try:
        server = create_server(
            application,
            host="127.0.0.1",
            port=args.port,
            threads=4,
            connection_limit=32,
            channel_timeout=60,
            max_request_body_size=BODY_LIMIT,
            expose_tracebacks=False,
            ident="PagesConverter",
        )
    except OSError:
        application.manager.close()
        parser.exit(1, "Could not bind the local port. Close the other instance or use --port 9000.\n")
    print(f"Pages Converter {__version__} • {application.origin}\nPress Ctrl+C to stop.")
    if args.open:
        threading.Timer(0.3, lambda: webbrowser.open(application.origin)).start()
    try:
        server.run()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        application.manager.close()
