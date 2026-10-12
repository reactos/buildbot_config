"""
Fetch a rostests folder from the artifact server (host_server.py) on the build machine.

Usage: fetch_tests.py [--server URL] [--timeout SECONDS] FOLDER_NAME LOCAL_DEST

FOLDER_NAME is the name of the folder on the server (the basename of
"${ROSTESTS_PREFIX}-${SUFFIX}"), which identifies the commit/run to test.
The folder is only downloaded once the build machine has created the
"FOLDER_NAME.ready" marker next to it, signalling that it is complete.
"""
import argparse
import os
import shutil
import sys
import time
import urllib
import urllib2
import urlparse
from HTMLParser import HTMLParser

DEFAULT_SERVER_URL = "http://192.168.37.16:8000"
DEFAULT_TIMEOUT = 4 * 60 * 60  # Seconds to wait for the folder to become ready, 0 = forever
POLL_INTERVAL = 5  # Seconds to wait before checking again
READY_SUFFIX = ".ready"
NOTIFY_ATTEMPTS = 5
REMOVE_ATTEMPTS = 12


class SimpleDirectoryParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr, value in attrs:
                if attr == "href":
                    self.links.append(value)


def remove_tree(path):
    # Virus scanners, the search indexer or a test process that is still exiting
    # can briefly hold a handle on the folder, so retry for a while before giving up.
    for attempt in range(REMOVE_ATTEMPTS):
        if not os.path.exists(path):
            return
        try:
            shutil.rmtree(path)
            return
        except OSError as e:
            print "[CLIENT] Could not delete " + path + " (" + str(e) + "), retrying..."
            time.sleep(POLL_INTERVAL)

    if os.path.exists(path):
        shutil.rmtree(path)


def replace_tree(src, dest):
    try:
        remove_tree(dest)
    except OSError:
        # The folder itself is still held open, but its contents can usually still be replaced
        print "[CLIENT] " + dest + " is still in use, replacing its contents instead."
        for name in os.listdir(dest):
            path = os.path.join(dest, name)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        for name in os.listdir(src):
            os.rename(os.path.join(src, name), os.path.join(dest, name))
        os.rmdir(src)
        return

    os.rename(src, dest)


def make_url(server_url, name, is_folder=False):
    # Build the URL from its components, so it is combined and quoted correctly
    parts = urlparse.urlparse(server_url)
    path = parts.path.rstrip("/") + "/" + urllib.quote(name) + ("/" if is_folder else "")
    return urlparse.urlunparse((parts.scheme, parts.netloc, path, "", "", ""))


def is_ready(server_url, folder_name):
    try:
        urllib2.urlopen(make_url(server_url, folder_name + READY_SUFFIX), timeout=10)
        return True
    except urllib2.HTTPError as e:
        if e.code == 404:
            # The folder isn't complete yet
            return False
        raise


def download_file(remote_url, local_path):
    response = urllib2.urlopen(remote_url, timeout=60)
    with open(local_path, "wb") as f:
        shutil.copyfileobj(response, f)


def download_folder(remote_url, local_dir):
    # remote_url must end with a slash, so the relative links of the listing resolve below it
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    parser = SimpleDirectoryParser()
    parser.feed(urllib2.urlopen(remote_url, timeout=60).read().decode("utf-8"))

    for link in parser.links:
        if link in ["../", "./", "/"] or link.startswith("?"):
            continue

        name = urllib.unquote(link.rstrip("/"))
        # Never let a listing entry escape local_dir (e.g. "%2e%2e%2f", "C:", or a link to another host)
        if not name or name in [".", ".."] or "/" in name or "\\" in name or os.path.splitdrive(name)[0]:
            raise ValueError("Unsafe directory entry: " + repr(name))
        if link.endswith("/"):
            download_folder(urlparse.urljoin(remote_url, link), os.path.join(local_dir, name))
        else:
            download_file(urlparse.urljoin(remote_url, link), os.path.join(local_dir, name))


def notify_download_complete(server_url, folder_name):
    done_url = make_url(server_url, "download-complete")

    for attempt in range(NOTIFY_ATTEMPTS):
        try:
            req = urllib2.Request(done_url, data=folder_name.encode("utf-8"))
            response = urllib2.urlopen(req, timeout=10)
            if response.getcode() == 200:
                print "[CLIENT] Win7 server notified and unblocked."
                return True
        except Exception as e:
            print "[CLIENT] Failed to notify Win7 server: " + str(e)
        time.sleep(POLL_INTERVAL)

    return False


def fetch(server_url, folder_name, local_dest, timeout):
    print "[CLIENT] Waiting for " + folder_name + " on " + server_url + "..."

    deadline = time.time() + timeout if timeout > 0 else None
    last_error = None
    while True:
        try:
            if is_ready(server_url, folder_name):
                break
        except Exception as e:
            # Server isn't up yet or failed. Only print an error when it changes,
            # so hours of polling don't flood the build log.
            if str(e) != last_error:
                print "[CLIENT] Error checking " + folder_name + ": " + str(e) + ", retrying every " + str(POLL_INTERVAL) + "s..."
                last_error = str(e)

        if deadline is not None and time.time() > deadline:
            print "[CLIENT] Timed out waiting for " + folder_name + " to become ready."
            return False
        time.sleep(POLL_INTERVAL)

    print "[CLIENT] Found test folder: " + folder_name
    print "[CLIENT] Downloading to " + local_dest + "..."

    # Download into a temporary folder, so an aborted download never looks like a complete one
    partial_dest = local_dest + ".partial"
    remove_tree(partial_dest)

    download_folder(make_url(server_url, folder_name, is_folder=True), partial_dest)
    replace_tree(partial_dest, local_dest)
    print "[CLIENT] Download complete."

    # Notify Win7 to delete the source folder and exit host_server.py
    if not notify_download_complete(server_url, folder_name):
        print "[CLIENT] Error: Win7 server was not notified, its copy of " + folder_name + " is left behind."
        return False

    return True


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Fetch a rostests folder from the artifact server.")
    arg_parser.add_argument("--server", default=DEFAULT_SERVER_URL, help="URL of host_server.py")
    arg_parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Seconds to wait for the folder, 0 = forever")
    arg_parser.add_argument("folder_name", help="Name of the folder on the server")
    arg_parser.add_argument("local_dest", help="Local path to download the folder to")
    args = arg_parser.parse_args()

    if args.folder_name.strip() in ["", ".", ".."]:
        arg_parser.error("Invalid folder name: '" + args.folder_name + "'")
    if any(ord(c) < 32 for c in args.folder_name):
        # Usually a CR from a builder_config.inc with Windows line endings
        arg_parser.error("Folder name contains control characters: " + repr(args.folder_name))

    if not fetch(args.server, args.folder_name, args.local_dest, args.timeout):
        sys.exit(1)
