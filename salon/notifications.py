"""Transactional email outbox; no network side effects before commit."""

import json
import uuid
from datetime import timedelta

from salon.booking_service import unresolved
from salon.time_rules import instant


def enqueue(db, booking, kind, due):
    """Insert a pending email job in the caller's transaction.

    Args:
        db: Open connection containing the booking's registered client.
        booking: Booking dictionary to snapshot in the mail payload.
        kind: Notification kind understood by build_message.
        due: Aware datetime at which the job becomes eligible for delivery.

    Notes:
        Returns None. Reads the client's email and stores it with the booking;
        does not commit or send mail. Storage errors propagate to the caller.
    """
    user = json.loads(
        db.execute(
            "SELECT data FROM users WHERE id=?", (booking["clientId"],)
        ).fetchone()["data"]
    )
    payload = dict(to=user["email"], booking=booking)
    db.execute(
        "INSERT INTO mail VALUES (?,?,?,?,?,?)",
        (
            uuid.uuid4().hex,
            booking["id"],
            kind,
            due.timestamp(),
            "pending",
            json.dumps(payload),
        ),
    )


def on_booking(db, before, after, now):
    """Schedule notifications for a successful booking mutation.

    Args:
        db: Same open transaction as the booking mutation.
        before: Previous booking dictionary, or None when creating.
        after: Saved booking dictionary with its current details.
        now: Aware datetime used for immediate delivery and reminder eligibility.

    Raises:
        ApiError: For unresolved D-04 when moving a booking without an earlier
            reminder to a start at least 24 hours away.

    Notes:
        Returns None. Cancels obsolete reminders and snapshots updated details.
        The caller must roll back the booking and outbox together on failure.
    """
    if before is None:
        enqueue(db, after, "created", now)
        due = instant(after["startsAt"]) - timedelta(hours=24)
        if due >= now:
            enqueue(db, after, "reminder", due)
        return
    cancelled = after["status"] == "cancelled"
    moved = instant(before["startsAt"]) != instant(after["startsAt"])
    if cancelled or moved:
        if moved and instant(after["startsAt"]) - now >= timedelta(hours=24):
            has_reminder = db.execute(
                "SELECT 1 FROM mail WHERE booking_id=? AND kind='reminder'",
                (after["id"],),
            ).fetchone()
            if not has_reminder:
                unresolved("D-04")
        db.execute(
            "UPDATE mail SET state='cancelled' WHERE booking_id=? AND kind='reminder' AND state IN ('pending','failed')",
            (after["id"],),
        )
    enqueue(db, after, "cancelled" if cancelled else "changed", now)
    if moved and not cancelled:
        due = instant(after["startsAt"]) - timedelta(hours=24)
        if due >= now:
            enqueue(db, after, "reminder", due)
    elif not cancelled:
        # Reminder uses updated details when service/master changes without moving.
        rows = db.execute(
            "SELECT id,payload FROM mail WHERE booking_id=? AND kind='reminder' AND state='pending'",
            (after["id"],),
        ).fetchall()
        for row in rows:
            payload = json.loads(row["payload"])
            payload["booking"] = after
            db.execute(
                "UPDATE mail SET payload=? WHERE id=?",
                (json.dumps(payload), row["id"]),
            )
