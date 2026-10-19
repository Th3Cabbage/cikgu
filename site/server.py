"""Loopback-only static server for the built Cikgu study site, site/dist (Python standard library only).

    python -I site/server.py [--port 8800] [--tries 20] [--port-file PATH] [--nonce TEXT] [--watch-pid PID]

Serves exactly what Netlify publishes (site/dist), so the local site and the hosted site behave the same:
one origin, real directories, hash routes inside each lecture, no chat backend. Build first with
`node site/build.mjs` (launch_study.ps1 does both).

- Binds 127.0.0.1 with an exclusive bind; tries --port, --port+1, ... and reports the port it got.
- GET /__site_health returns {"app": "CikguSite", "pid", "nonce"} so the launcher can confirm it
  started this exact process (the nonce is random per launch).
- Checks the Host header (DNS rebinding), never lists directories, refuses dot-paths and anything
  outside site/dist, redirects directory URLs to a trailing slash, serves explicit MIME types and
  single byte ranges so the MP4 clips can seek. Only GET and HEAD are accepted.
- --watch-pid: exit when the launcher process exits, even if it was killed.
Stop with Ctrl+C.
"""
import argparse
import json
import os
import re
import socket
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "dist")
APP = "CikguSite"
MIME = {
    ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
    ".mp4": "video/mp4", ".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf",
    ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".txt": "text/plain; charset=utf-8",
    "": "application/octet-stream",
}
RANGE_RE = re.compile(r"^([0-9]*)-([0-9]*)$")


class Handler(SimpleHTTPRequestHandler):
    extensions_map = MIME
    server_version = APP
    sys_version = ""
    nonce = ""

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("[cikgu-site] " + (fmt % args) + "\n")

    def guess_type(self, path):
        # The lectures' static api/status file has no extension (Netlify gets the same type from netlify.toml).
        if os.path.basename(path) == "status" and os.path.basename(os.path.dirname(path)) == "api":
            return "application/json; charset=utf-8"
        return super().guess_type(path)

    def send_json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        port = self.server.server_address[1]
        if self.headers.get("Host", "") not in (f"127.0.0.1:{port}", f"localhost:{port}"):
            return self.send_json(421, {"ok": False, "error": "Unexpected Host header."})
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if path == "/__site_health":
            return self.send_json(200, {"app": APP, "pid": os.getpid(), "nonce": self.nonce})
        if any(p.startswith(".") for p in path.split("/") if p):
            return self.send_error(404)
        fs = self.translate_path(self.path)
        if os.path.isdir(fs):
            index = os.path.join(fs, "index.html")
            if not os.path.isfile(index):
                return self.send_error(404)
            if not path.endswith("/"):
                self.send_response(301)
                self.send_header("Location", path + "/")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            fs = index
        real = os.path.realpath(fs)
        root = os.path.realpath(DIST)
        if not real.startswith(root + os.sep) or not os.path.isfile(real):
            return self.send_error(404)
        return self.send_file(real)

    def list_directory(self, path):  # never list directories
        self.send_error(404)
        return None

    def send_file(self, path):
        size = os.path.getsize(path)
        rng = self.headers.get("Range")
        start, end, partial_req = 0, size - 1, False
        if rng and rng.startswith("bytes="):
            try:
                m = RANGE_RE.match(rng[6:].split(",")[0].strip())
                if not m or (m.group(1) == "" and m.group(2) == ""):
                    raise ValueError
                a, b = m.group(1), m.group(2)
                if a == "":
                    if int(b) <= 0:
                        raise ValueError
                    start = max(0, size - int(b))
                else:
                    start = int(a)
                    end = min(int(b), size - 1) if b else size - 1
                if start > end or start >= size:
                    raise ValueError
                partial_req = True
            except ValueError:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
        self.send_response(206 if partial_req else 200)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        if partial_req:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        if self.command == "HEAD":
            return
        with open(path, "rb") as f:
            f.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = f.read(min(65536, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                    return
                remaining -= len(chunk)

    def do_POST(self):
        # A static site has no chat backend; the lectures do not send questions when status says so.
        self.send_json(405, {"ok": False, "code": "not_configured", "error": "This study site has no chat server."})

    do_PUT = do_DELETE = do_PATCH = do_OPTIONS = do_POST


class LoopbackServer(ThreadingHTTPServer):
    allow_reuse_address = False
    daemon_threads = True
    request_queue_size = 64   # the default backlog of 5 refuses bursts of parallel still/clip requests on Windows

    def server_bind(self):
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def make_server(port, tries=20, nonce=""):
    """Bind 127.0.0.1 on the first free port in [port, port + tries). Returns the server or None."""
    handler = partial(type("BoundHandler", (Handler,), {"nonce": nonce}), directory=DIST)
    for p in range(port, port + max(1, tries)):
        try:
            return LoopbackServer(("127.0.0.1", p), handler)
        except OSError:
            print(f"Port {p} is in use; trying {p + 1}.", flush=True)
    return None


def watch_parent(pid, server):
    """Stop the server when process `pid` (the launcher) exits. Windows: wait on its handle; else poll."""
    def run():
        if os.name == "nt":
            import ctypes
            k32 = ctypes.windll.kernel32
            handle = k32.OpenProcess(0x00100000, False, int(pid))   # SYNCHRONIZE
            if handle:
                k32.WaitForSingleObject(handle, 0xFFFFFFFF)
                k32.CloseHandle(handle)
        else:
            import time
            while True:
                try:
                    os.kill(int(pid), 0)
                except OSError:
                    break
                time.sleep(1)
        print("Launcher exited; stopping the server.", flush=True)
        server.shutdown()
    threading.Thread(target=run, daemon=True).start()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=8800)
    ap.add_argument("--tries", type=int, default=20)
    ap.add_argument("--port-file", default=None)
    ap.add_argument("--nonce", default="")
    ap.add_argument("--watch-pid", type=int, default=None, help="exit when this process (the launcher) exits")
    args = ap.parse_args()
    if not os.path.isfile(os.path.join(DIST, "index.html")):
        print(f"{DIST} has not been built. Run: node site/build.mjs", file=sys.stderr)
        sys.exit(3)
    server = make_server(args.port, args.tries, args.nonce)
    if server is None:
        print(f"No free port in {args.port}-{args.port + args.tries - 1}.", file=sys.stderr)
        sys.exit(2)
    port = server.server_address[1]
    if args.port_file:
        with open(args.port_file, "w", encoding="ascii") as f:
            f.write(str(port))
    print(f"Serving {DIST} at http://127.0.0.1:{port}/  (Ctrl+C to stop)", flush=True)
    if args.watch_pid:
        watch_parent(args.watch_pid, server)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("Server stopped.", flush=True)


if __name__ == "__main__":
    main()
