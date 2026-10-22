# Security policy

## Report a vulnerability privately

Use [GitHub private vulnerability reporting](https://github.com/maboox/pagestodoc/security/advisories/new). Do not publish sensitive documents, personal paths, credentials, or exploit details in an issue. Include the affected version, minimal reproduction, and expected impact using synthetic files.

Security fixes target the latest 2.x release. Version 1.x is superseded by 2.0.0.

## Intended deployment

This is a single-user, local desktop utility. The server is fixed to `127.0.0.1`. It is not a multi-user web service. Do not expose it through a reverse proxy, tunnel, container port mapping, or network bind. Local applications running as your user are outside the trust boundary: they already have access to your files.

## Controls

- Exact Host and Origin validation and cross-site Fetch Metadata rejection protect the loopback interface from browser-origin attacks and DNS rebinding.
- A random per-process session cookie (HttpOnly, SameSite=Strict, per-port name) authorizes API reads; mutations also require a CSRF header. HTTP is restricted to loopback, so the cookie cannot use a general HTTPS-only deployment assumption.
- A restrictive content security policy blocks inline scripts, framing, and third-party app resources. No CORS permission is granted.
- Werkzeug parses multipart uploads into bounded, disk-backed temporary streams. Total file data is limited to 1 GiB, 500 files, and one active batch. Waitress caps connections, body size, and idle channels.
- Paths reject traversal, absolute/drive paths, control/bidirectional override characters, Windows devices and invalid names. NFC normalization and case-insensitive allocation avoid collisions. Output filesystem storage is numbered; folder paths are logical ZIP paths.
- Pages archives get member, expansion, and encryption checks before LibreOffice is launched. These are defensive limits, not a complete hostile-document scanner.
- Each conversion has a fresh LibreOffice profile, highest macro security, a five-minute timeout, and cancellation that terminates the owned process tree. Engine diagnostics are not returned to the browser or conversion report.
- Downloads are streamed. An active reader prevents output deletion until its stream closes.
- No analytics, cloud conversion API, document database, or document content logging is present. User uploads and private configuration are excluded from version control.

## Native converter and document trust

LibreOffice is not sandboxed by the operating system. Its parser, import filters, external-resource behavior, and installed version remain part of the trust boundary. Documents may contain embedded content and links. Keep LibreOffice and Python updated, process documents you trust, and review converted files. Pass-through files are not inspected for malware; the archive can contain any file type the user selected. The app cannot promise that arbitrary documents, output archives, or third-party software are vulnerability-free.

## Data lifetime

Working data lives under system temporary directories named `pages-job-*` and private engine profiles under `pages-lo-*`. Successful jobs remove input and working copies, retaining the ZIP for one hour; expiry runs on a one-minute sweep while the app runs. Failed jobs remove working files and retain only status metadata for ten minutes. Cancelled jobs remove working files and retain status briefly. Normal shutdown cancels owned work and cleans retained jobs. Browser-saved downloads are outside this lifecycle.

A crash, forced termination, or power loss can leave temporary files. After all app/converter instances have stopped, inspect the OS temporary folder (`%TEMP%` on Windows) and manually remove this app's abandoned `pages-job-*` / `pages-lo-*` directories if appropriate. Do not remove folders belonging to an active conversion. For sensitive work, use a protected, encrypted user profile and temporary volume.

Preferences keep only language and theme in local storage. Session storage keeps only the current job ID. A local cookie stores the app session token. Clearing browser storage resets these. The app does not strip author metadata inside user documents; pass-through content is intentionally unchanged.

## Repository hygiene

Do not commit `.env` files, credentials, real user documents, diagnostic dumps, or local backup bundles. Use a GitHub noreply identity for commits. Run secret scanning on both the working tree and full Git history before releases. Enable GitHub secret scanning and push protection.

Rewriting Git refs does not erase old commits from other clones, GitHub caches, pull-request refs, or search indexes. If a real secret was ever published, revoke it immediately and follow [GitHub's sensitive-data removal procedure](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository); a force push alone is not sufficient.
