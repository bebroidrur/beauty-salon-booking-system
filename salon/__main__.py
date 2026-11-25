"""Local development server, administrator provisioning and email worker."""

import argparse
import getpass
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from werkzeug.security import generate_password_hash
from werkzeug.serving import WSGIRequestHandler, make_server

from salon.app import create_app
from salon.contract import API, validate
from salon.mail_worker import SMTPTransport, run_once


class SafeRequestHandler(WSGIRequestHandler):
    """Suppress Werkzeug access lines that could disclose query personal data."""

    def log_request(self, code="-", size="-"):
        # App emits an allowlisted event; Werkzeug URL logging may expose query PII.
        """Ignore code and size supplied by Werkzeug and return None.

        Application events provide the allowlisted request diagnostics instead.
        """
        pass


def main():
    """Run the development server, admin provisioning or outbox worker CLI.

    Reads process arguments and SMTP environment variables; provisioning prompts
    for profile and password. Returns None when a finite command completes.
    The server and worker without --once run until interrupted.

    Raises:
        SystemExit: For argparse help or invalid command-line arguments.
        KeyError: If required SMTP environment settings are absent.
        ValidationError: If the administrator profile violates the contract.
        sqlite3.Error: If database initialization or provisioning fails.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default="runtime/salon.sqlite3")
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    sub.add_parser("create-admin")
    worker = sub.add_parser("worker")
    worker.add_argument("--once", action="store_true")
    args = parser.parse_args()
    Path(args.database).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    app = create_app(args.database)
    store = app.extensions["store"]
    if args.command == "serve":
        with make_server(
            args.host,
            args.port,
            app,
            threaded=True,
            request_handler=SafeRequestHandler,
        ) as server:
            server.serve_forever()
    elif args.command == "create-admin":
        data = dict(
            name=input("Name: "),
            phone=input("Phone: "),
            email=input("Email: "),
            password=getpass.getpass(),
        )
        validate(API["components"]["schemas"]["Registration"], data)
        password = data.pop("password")
        data.update(id=uuid.uuid4().hex, role="administrator")
        with store.transaction() as db:
            db.execute(
                "INSERT INTO users VALUES (?,?,?,?)",
                (
                    data["id"],
                    data["email"],
                    generate_password_hash(password),
                    json.dumps(data),
                ),
            )
        print("Administrator created.")
    else:
        host = os.environ["SALON_SMTP_HOST"]
        sender = os.environ["SALON_SMTP_SENDER"]
        transport = SMTPTransport(
            host,
            int(os.environ.get("SALON_SMTP_PORT", "587")),
            sender,
            starttls=os.environ.get("SALON_SMTP_STARTTLS", "1") == "1",
            username=os.environ.get("SALON_SMTP_USER"),
            password=os.environ.get("SALON_SMTP_PASSWORD"),
        )
        while True:
            run_once(store, lambda: datetime.now(timezone.utc), transport)
            if args.once:
                break
            time.sleep(1)


if __name__ == "__main__":
    main()
