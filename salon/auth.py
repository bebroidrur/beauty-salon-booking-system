"""Bearer authentication independent of domain use cases."""

import hashlib
import json

from salon.errors import reject


def authenticate(db, header):
    """Resolve a Bearer session to its stored user.

    Args:
        db: Open SQLite connection with row access by name.
        header: Authorization header text, possibly empty.

    Returns:
        User dictionary, including its client or administrator role.

    Raises:
        ApiError: With status 401 for a malformed or unknown session token.
    """
    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        reject(401, "UNAUTHENTICATED", "Потрібен вхід.")
    row = db.execute(
        "SELECT u.data FROM sessions s JOIN users u ON s.user_id=u.id WHERE s.token_hash=?",
        (hashlib.sha256(parts[1].encode()).hexdigest(),),
    ).fetchone()
    if not row:
        reject(401, "UNAUTHENTICATED", "Потрібен вхід.")
    return json.loads(row["data"])
