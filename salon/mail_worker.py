"""Durable due-job delivery; failures remain visible for explicit retry."""

import json
import smtplib
import ssl
from email.message import EmailMessage

from salon.events import record


def run_once(store, clock, transport):
    """Deliver pending mail whose due time has arrived in one transaction.

    Args:
        store: Store providing a SQLite transaction.
        clock: Callable returning an aware datetime for the due-time cutoff.
        transport: Object with send(kind, payload) that delivers one message.

    Returns:
        Number of messages successfully handed to the transport in this pass.

    Notes:
        Transport exceptions mark jobs failed and are not propagated. Failed jobs
        are not automatically retried. The transaction remains locked during I/O;
        a crash after SMTP acceptance and before commit can duplicate delivery.
        Storage errors propagate to the caller.
    """
    sent = 0
    # Serialize with cancellation/rescheduling. SMTP timeout bounds this lock.
    # Crash after SMTP acceptance but before commit can duplicate a message.
    with store.transaction() as db:
        rows = db.execute(
            "SELECT * FROM mail WHERE state='pending' AND due<=? ORDER BY due,rowid",
            (clock().timestamp(),),
        ).fetchall()
        for row in rows:
            try:
                transport.send(row["kind"], json.loads(row["payload"]))
            except Exception:
                db.execute(
                    "UPDATE mail SET state='failed' WHERE id=?", (row["id"],)
                )
                record("mail.send", 500, row["id"], "MAIL_DELIVERY_FAILED")
            else:
                db.execute(
                    "UPDATE mail SET state='sent' WHERE id=?", (row["id"],)
                )
                record("mail.send", 200, row["id"])
                sent += 1
    return sent


class SMTPTransport:
    """Deliver outbox messages over SMTP with optional STARTTLS and login."""

    def __init__(
        self, host, port, sender, starttls=True, username=None, password=None
    ):
        """Store SMTP connection settings without opening a connection.

        Args:
            host: SMTP hostname.
            port: SMTP TCP port integer.
            sender: From address used for generated messages.
            starttls: Whether to negotiate STARTTLS; defaults to True.
            username: Optional login username.
            password: Optional login password, used when username is supplied.
        """
        self.host, self.port, self.sender = host, port, sender
        self.starttls, self.username, self.password = (
            starttls,
            username,
            password,
        )

    def send(self, kind, payload):
        """Send a notification using a new SMTP connection with a 10s timeout.

        Args:
            kind: created, changed, cancelled or reminder notification kind.
            payload: Dictionary with to and booking, as persisted in the outbox.

        Raises:
            SMTPException: If negotiation, authentication or delivery fails.
            OSError: If the network connection fails.

        Notes:
            Returns None on success; does not update the outbox state itself.
        """
        message = build_message(self.sender, kind, payload)
        with smtplib.SMTP(self.host, self.port, timeout=10) as smtp:
            if self.starttls:
                smtp.starttls(context=ssl.create_default_context())
            if self.username:
                smtp.login(self.username, self.password)
            smtp.send_message(message)


def build_message(sender, kind, payload):
    """Build a plain-text notification from the persisted booking snapshot.

    Args:
        sender: From email address.
        kind: created, changed, cancelled or reminder.
        payload: Dictionary with to and a booking containing serviceSnapshot.

    Returns:
        EmailMessage with Ukrainian subject and booking details; no network I/O.

    Raises:
        KeyError: If kind is unknown or a required payload field is missing.
    """
    booking = payload["booking"]
    snapshot = booking["serviceSnapshot"]
    message = EmailMessage()
    message["From"] = sender
    message["To"] = payload["to"]
    message["Subject"] = {
        "created": "Підтвердження запису",
        "changed": "Зміна запису",
        "cancelled": "Скасування запису",
        "reminder": "Нагадування про запис",
    }[kind]
    message.set_content(
        f"{snapshot['name']}\n{snapshot['price']} {snapshot['currency']}\n"
        f"{snapshot['durationMinutes']} хв\n{booking['masterName']}\n"
        f"{booking['startsAt']} — {booking['endsAt']}\n{booking['status']}"
    )
    return message
