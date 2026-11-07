#!/usr/bin/env python3
"""本地接收服务：页面把抓到的 JSON POST 到 http://127.0.0.1:<port>/<文件名>，原样落盘。

用法：python3 -I recv.py --out <raw 目录> [--port 8765]
"""
import argparse
import http.server
import os
import re
import time
import urllib.parse

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--port", type=int, default=8765)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
LOG = os.path.join(args.out, "_recv.log")


class Handler(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        name = os.path.basename(urllib.parse.urlparse(self.path).path) or "data.json"
        name = re.sub(r"[^\w.\-]", "_", name)
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        with open(os.path.join(args.out, name), "wb") as f:
            f.write(body)
        with open(LOG, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} {name} {len(body)}\n")
        self.send_response(200)
        self._cors()
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *a):
        pass


print(f"recv ready on 127.0.0.1:{args.port} -> {args.out}", flush=True)
http.server.HTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
