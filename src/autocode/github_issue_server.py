import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Tuple

from autocode.agent_dev import agent as dev_agent

logger = logging.getLogger(__name__)


class GitHubIssueWebhookHandler(BaseHTTPRequestHandler):
    """A very small HTTP handler able to receive GitHub issue webhooks.

    When an issue is *opened*, the body and the title are forwarded to the
    developer agent as a prompt. The conversation is executed in a background
    thread so that the HTTP server can immediately acknowledge the webhook and
    stay responsive.
    """

    # GitHub will ping the root path ("/") by default – we don't care about the
    # exact URL, accept anything.

    def _set_response(self, status: int = 200, body: str = "OK") -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_POST(self):  # noqa: N802 – keep the original name for the callback
        content_length_header = self.headers.get("Content-Length")
        if not content_length_header:
            logger.warning("Missing Content-Length header – cannot read payload")
            self._set_response(411, "Missing Content-Length header")
            return

        try:
            length = int(content_length_header)
        except ValueError:
            self._set_response(400, "Invalid Content-Length header")
            return

        payload = self.rfile.read(length)
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            self._set_response(400, "Invalid JSON payload")
            return

        event = self.headers.get("X-GitHub-Event")
        if event != "issues":
            # Not an issue event, ignore.
            self._set_response(202, "Ignored – not an issues event")
            return

        if data.get("action") != "opened":
            # We only care about new issues.
            self._set_response(202, "Ignored – not an opened action")
            return

        issue = data.get("issue", {})
        title: str | None = issue.get("title")
        body: str | None = issue.get("body", "")

        if title is None:
            self._set_response(400, "Missing issue title")
            return

        prompt = f"{title}\n\n{body}"
        logger.info("Received issue webhook – starting dev agent:\n%s", prompt)

        # Run the agent in a separate thread so that the request can be
        # acknowledged quickly.
        thread = threading.Thread(target=_run_agent_conversation, args=(prompt,))
        thread.daemon = True  # Do not block process exit.
        thread.start()

        self._set_response(200, "Issue received")

    # GitHub sends a ping (GET) when setting up the webhook.
    def do_GET(self):  # noqa: N802 – keep callback name
        self._set_response(200, "pong")


def _run_agent_conversation(prompt: str) -> None:
    """Run the developer agent with the given prompt and print messages."""
    try:
        for message in dev_agent.run_conversation(prompt):
            # We intentionally do not use images here – just render as text.
            print(message.to_terminal(display_image=False))
    except Exception as exc:  # pragma: no cover – best effort logging
        logger.exception("Error while processing GitHub issue: %s", exc)


def serve(address: Tuple[str, int] = ("0.0.0.0", 8000)) -> None:
    """Start the HTTP server and block forever."""
    host, port = address
    server = HTTPServer(address, GitHubIssueWebhookHandler)
    logger.info("Listening for GitHub issue webhooks on http://%s:%d", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server…")
        server.server_close()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Listen to GitHub issue webhooks and feed them to the dev agent."
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Address to bind the HTTP server to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to listen on (default: 8000)"
    )
    args = parser.parse_args()

    serve((args.host, args.port))


if __name__ == "__main__":  # pragma: no cover
    main()
