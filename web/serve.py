"""Serve the AX-Synth Web Editor on http://localhost:8765 (localhost only).

Web MIDI with SysEx needs a secure context; http://localhost is one. The
MIME types are set explicitly because Windows' registry can map .js to
text/plain, which browsers refuse for module scripts.

Usage: py -3 web/serve.py [port]   (start-web-editor.bat does this)
"""
import functools
import http.server
import subprocess
import sys
import webbrowser
from pathlib import Path

WEB = Path(__file__).resolve().parent
TYPES = {".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json",
         ".html": "text/html", ".css": "text/css"}


class Handler(http.server.SimpleHTTPRequestHandler):
    def guess_type(self, path):
        return TYPES.get(Path(path).suffix.lower()) or super().guess_type(path)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


def open_browser(url):
    if "--edge" in sys.argv and sys.platform == "win32":
        try:
            subprocess.Popen(["cmd", "/c", "start", "", "msedge", url])
            return
        except OSError:
            pass
    webbrowser.open(url)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    port = int(args[0]) if args else 8765
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Handler, directory=str(WEB)))
    except OSError:
        print(f"Port {port} is busy: the editor is probably already running. Opening it.")
        open_browser(f"http://localhost:{port}/")
        return
    url = f"http://localhost:{port}/"
    print(f"AX-Synth Web Editor: {url}  (close this window to stop)")
    if "--no-browser" not in sys.argv:
        open_browser(url)
    server.serve_forever()


if __name__ == "__main__":
    main()
