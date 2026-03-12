from __future__ import annotations

import argparse
import http.server
import socketserver
from functools import partial
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the frontend/public directory.")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind.")
    parser.add_argument("--port", default=3000, type=int, help="Port to serve on.")
    args = parser.parse_args()

    public_dir = Path(__file__).resolve().parent / "public"
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(public_dir))

    with socketserver.TCPServer((args.host, args.port), handler) as httpd:
        print(f"Serving {public_dir} at http://{args.host}:{args.port}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()