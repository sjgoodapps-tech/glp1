#!/usr/bin/env python3
"""Case-sensitive static preview with the declared Jekyll compatibility routes."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from build_app_store_aliases import ROOT, URLS, body


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        route = unquote(urlsplit(self.path).path)
        if route in URLS['aliases']:
            payload = body(route, URLS['aliases'][route]).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        current = Path(self.directory)
        for component in Path(route.lstrip('/')).parts:
            if component in {'.', '..'} or not current.is_dir() or component not in {p.name for p in current.iterdir()}:
                self.send_error(404)
                return
            current /= component
        super().do_GET()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=4198)
    args = parser.parse_args()
    print(f'Case-sensitive draft preview: http://127.0.0.1:{args.port}/', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), partial(Handler, directory=str(ROOT))).serve_forever()
