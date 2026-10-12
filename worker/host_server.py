"""
Serve built rostests folders to the test machine (fetch_tests.py).

Usage: host_server.py [--dir ARTIFACTS_DIR] [--port PORT] [--folder FOLDER_NAME]

A folder is only considered complete once build_rostests has created the
"FOLDER_NAME.ready" marker next to it. When the client confirms a download,
the folder and its marker are deleted.
With --folder, the server exits once that exact folder has been confirmed,
so it can be used as a blocking BuildBot step for one specific run.
Without it, the server keeps running and serves every run.
"""
import argparse
import functools
import http.server
import shutil
import socketserver
import sys
import urllib.parse
from pathlib import Path

DEFAULT_ARTIFACTS_DIR = r"C:\Tests_For_Carrier-Win2003-x64"
DEFAULT_PORT = 8000
READY_SUFFIX = ".ready"


class ArtifactHandler(http.server.SimpleHTTPRequestHandler):

    def send_text(self, code, text):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(text.encode("utf-8"))

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)

        if parsed_path.path != "/download-complete":
            self.send_error(404, "Unknown endpoint")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        folder_name = self.rfile.read(content_length).decode("utf-8").strip()

        safe_folder_name = Path(folder_name).name
        if safe_folder_name in ["", ".."]:
            self.send_error(400, "Invalid folder name")
            return

        expected = self.server.expected_folder
        if expected is not None and safe_folder_name != expected:
            self.send_error(409, f"Waiting for {expected}, not {safe_folder_name}")
            return

        target_path = self.server.artifacts_dir / safe_folder_name
        ready_path = target_path.with_name(target_path.name + READY_SUFFIX)
        if not ready_path.exists():
            self.send_error(409, f"{safe_folder_name} is not ready")
            return

        # Cleanup source artifacts on Win7 host. Remove the marker first,
        # so the folder is never served again while it is being deleted.
        try:
            ready_path.unlink()
            if target_path.is_dir():
                shutil.rmtree(target_path)
            print(f"[SERVER] Cleaned up served folder: {safe_folder_name}")
        except Exception as e:
            print(f"[SERVER] Error deleting {safe_folder_name}: {str(e)}")

        # Respond to Vista before exiting
        self.send_text(200, "Download confirmed. Releasing Win7 Buildbot step.")

        if expected is not None:
            self.server.should_exit = True


class StoppableTCPServer(socketserver.TCPServer):

    def __init__(self, artifacts_dir, expected_folder, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.artifacts_dir = Path(artifacts_dir)
        self.expected_folder = expected_folder
        self.should_exit = False

    def serve_until_done(self):
        while not self.should_exit:
            self.handle_request()


def run_server(artifacts_dir, port, expected_folder):
    # On Windows, SO_REUSEADDR lets a second server silently bind the same port and steal requests,
    # so only use it elsewhere (where it just avoids TIME_WAIT errors on restart).
    socketserver.TCPServer.allow_reuse_address = sys.platform != "win32"
    handler = functools.partial(ArtifactHandler, directory=artifacts_dir)
    server = StoppableTCPServer(artifacts_dir, expected_folder, ("", port), handler)

    if expected_folder is None:
        print(f"[SERVER] Serving {artifacts_dir} on port {port}.")
    else:
        print(
            f"[SERVER] Serving {artifacts_dir} on port {port}. Waiting for download of {expected_folder}..."
        )
    server.serve_until_done()
    print("[SERVER] Download complete! Releasing Win7 pipeline.")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Serve built rostests folders to the test machine.")
    arg_parser.add_argument("--dir", default=DEFAULT_ARTIFACTS_DIR, help="Directory containing the rostests folders")
    arg_parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    arg_parser.add_argument("--folder", help="Exit once this folder has been downloaded")
    args = arg_parser.parse_args()

    run_server(args.dir, args.port, args.folder)
