"""Loopback-only static server for courses/ode/browser/dist (standard library only).

    python -I serve_local.py [--port 8765] [--tries 20] [--port-file PATH] [--nonce TEXT]

- Binds 127.0.0.1 only, never 0.0.0.0.
- Uses an exclusive bind (SO_EXCLUSIVEADDRUSE on Windows, no SO_REUSEADDR), so an
  occupied port is detected and skipped instead of being shared.
- Tries --port, --port+1, ... and reports the port it actually got (stdout and --port-file).
- GET /__guide_health returns {"app": "SecondOrderODE", "pid": <pid>, "nonce": <--nonce>} so
  a launcher can confirm it is talking to the server it started (the nonce is random per
  launch) and can stop that exact process (a venv python.exe is a launcher stub whose
  child is the real server, so the stub's PID is not enough).
- Explicit MIME types (Windows registry mappings can be wrong) and single byte-range
  support so the MP4 clips can seek.
Stop with Ctrl+C.
"""
import argparse
import json
import os
import socket
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
MIME = {
    ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
    ".mp4": "video/mp4", ".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf",
    ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".txt": "text/plain; charset=utf-8", "": "text/plain",
}


class Handler(SimpleHTTPRequestHandler):
    extensions_map = MIME
    nonce = ""

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("[serve_local] " + (fmt % args) + "\n")

    def do_GET(self):
        if self.path.split("?")[0] == "/__guide_health":
            body = json.dumps({"app": "SecondOrderODE", "pid": os.getpid(), "nonce": self.nonce}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        if rng and rng.startswith("bytes=") and os.path.isfile(path):
            return self.send_range(path, rng)
        return super().do_GET()

    def send_range(self, path, rng):
        size = os.path.getsize(path)
        try:
            start_s, end_s = rng[6:].split(",")[0].split("-")
            if start_s == "":
                start, end = max(0, size - int(end_s)), size - 1
            else:
                start = int(start_s)
                end = min(int(end_s), size - 1) if end_s else size - 1
            if start > end or start >= size:
                raise ValueError
        except ValueError:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = f.read(min(65536, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (ConnectionResetError, BrokenPipeError):
                    return
                remaining -= len(chunk)


class LoopbackServer(ThreadingHTTPServer):
    allow_reuse_address = False
    daemon_threads = True

    def server_bind(self):
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--tries", type=int, default=20)
    ap.add_argument("--port-file", default=None)
    ap.add_argument("--nonce", default="")
    args = ap.parse_args()
    Handler.nonce = args.nonce
    handler = partial(Handler, directory=DIST)
    server = None
    for port in range(args.port, args.port + args.tries):
        try:
            server = LoopbackServer(("127.0.0.1", port), handler)
            break
        except OSError:
            print(f"Port {port} is in use; trying {port + 1}.", flush=True)
    if server is None:
        print(f"No free port in {args.port}-{args.port + args.tries - 1}.", file=sys.stderr)
        sys.exit(2)
    port = server.server_address[1]
    if args.port_file:
        with open(args.port_file, "w", encoding="ascii") as f:
            f.write(str(port))
    print(f"Serving {DIST} at http://127.0.0.1:{port}/  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("Server stopped.", flush=True)


if __name__ == "__main__":
    main()
