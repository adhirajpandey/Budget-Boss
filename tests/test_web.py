import concurrent.futures
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError
from urllib.request import ProxyHandler, build_opener

import helper

with patch.object(helper, "connectMongo", return_value=MagicMock()):
    import app as application


class WebTests(unittest.TestCase):
    """Check health and tracker routing without writing to MongoDB."""

    def test_health(self):
        """Serve health without requesting shop data or querying the database."""
        with patch.object(
            helper.requests, "get", side_effect=AssertionError("network")
        ):
            response = application.app.test_client().get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})

    def test_failed_submission_does_not_retry_or_write(self):
        """Make one scrape attempt per supported shop and preserve the failure page."""
        for domain, function in (
            ("amazon", "scrapeProductInfo_amzn"),
            ("flipkart", "scrapeProductInfo_flkt"),
            ("myntra", "scrapeProductInfo_mntr"),
            ("boat-lifestyle", "scrapeProductInfo_boat"),
        ):
            with self.subTest(shop=domain):
                with (
                    patch.object(
                        application, function, return_value=[-1, -1]
                    ) as scrape,
                    patch.object(application.user_collection, "insert_one") as insert,
                ):
                    response = application.app.test_client().post(
                        "/tracker",
                        data={
                            "plink": f"https://{domain}.example/item",
                            "uemail": "test@example.test",
                        },
                    )
                self.assertEqual(response.status_code, 200)
                scrape.assert_called_once()
                insert.assert_not_called()


class GunicornTests(unittest.TestCase):
    """Exercise the production Gunicorn configuration against a local API."""

    def test_health_responds_while_shop_stalls(self):
        """Serve health checks during a stalled request, then time it out."""
        started = threading.Event()
        release = threading.Event()
        calls = []

        class StalledAPI(BaseHTTPRequestHandler):
            """Accept requests but withhold a response to trigger a read timeout."""

            def do_GET(self):
                """Record the request and wait until the test releases it."""
                calls.append(self.path)
                started.set()
                release.wait(10)
                self.close_connection = True

            def log_message(self, *args):
                """Suppress HTTP server logs during the test."""

        upstream = ThreadingHTTPServer(("127.0.0.1", 0), StalledAPI)
        upstream_thread = threading.Thread(target=upstream.serve_forever, daemon=True)
        upstream_thread.start()
        # Select a free loopback port for the temporary application process.
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        opener = build_opener(ProxyHandler({}))

        def request(path, data=None):
            """Read a local app response, including HTTP error bodies."""
            try:
                with opener.open(base + path, data=data, timeout=6) as response:
                    return response.status, response.read()
            except HTTPError as error:
                with error:
                    return error.code, error.read()

        root = Path(__file__).resolve().parents[1]
        try:
            with tempfile.TemporaryDirectory() as directory:
                # Override only the upstream address, retaining real Requests I/O.
                Path(directory, "stalled_app.py").write_text(
                    "import helper\n"
                    "from unittest.mock import MagicMock\n"
                    "helper.connectMongo = MagicMock(return_value=MagicMock())\n"
                    "original_get = helper.requests.get\n"
                    "def local_get(url, **kwargs):\n"
                    f"    return original_get('http://127.0.0.1:{upstream.server_port}/', **kwargs)\n"
                    "helper.requests.get = local_get\n"
                    "from app import app\n"
                )
                environment = dict(os.environ)
                environment.pop("GUNICORN_CMD_ARGS", None)
                environment.pop("WEB_CONCURRENCY", None)
                environment["PYTHONPATH"] = os.pathsep.join((str(root), directory))
                with tempfile.TemporaryFile() as logs:
                    process = subprocess.Popen(
                        [
                            sys.executable,
                            "-m",
                            "gunicorn",
                            "--config",
                            "gunicorn.conf.py",
                            "--bind",
                            f"127.0.0.1:{port}",
                            "stalled_app:app",
                        ],
                        cwd=root,
                        env=environment,
                        stdout=logs,
                        stderr=logs,
                    )
                    try:
                        deadline = time.monotonic() + 10
                        while True:
                            if process.poll() is not None:
                                logs.seek(0)
                                self.fail(logs.read().decode())
                            try:
                                status, _ = request("/health")
                                if status == 200:
                                    break
                            except OSError:
                                pass
                            if time.monotonic() >= deadline:
                                self.fail("Gunicorn did not start")
                            time.sleep(0.05)

                        with concurrent.futures.ThreadPoolExecutor(
                            max_workers=1
                        ) as pool:
                            begin = time.monotonic()
                            submission = pool.submit(
                                request,
                                "/tracker",
                                b"plink=https%3A%2F%2Famazon.example%2Fitem&uemail=test%40example.test",
                            )
                            self.assertTrue(started.wait(2), "Upstream was not called")
                            health_begin = time.monotonic()
                            status, body = request("/health")
                            self.assertEqual(status, 200)
                            self.assertEqual(json.loads(body), {"status": "ok"})
                            self.assertLess(time.monotonic() - health_begin, 1)
                            self.assertFalse(
                                submission.done(), "Upstream should still be stalled"
                            )
                            status, body = submission.result(timeout=5)
                            self.assertEqual(status, 200)
                            self.assertNotIn(b"Internal Server Error", body)
                            self.assertLess(time.monotonic() - begin, 5)
                            self.assertEqual(len(calls), 1)
                            self.assertEqual(request("/health")[0], 200)
                    finally:
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()
        finally:
            release.set()
            upstream.shutdown()
            upstream.server_close()
            upstream_thread.join(timeout=2)
