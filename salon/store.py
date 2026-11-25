"""SQLite persistence; each operation owns a connection and a transaction."""

import json
import sqlite3
from contextlib import contextmanager


class Store:
    """Persist users, sessions, entities and mail jobs in a SQLite file.

    Each transaction opens a connection and uses BEGIN IMMEDIATE, including reads.
    This serializes writes but is not a production throughput guarantee.
    """

    def __init__(self, path):
        """Initialize tables at filesystem path without creating parent directories.

        Raises:
            sqlite3.Error: If the database cannot be opened or initialized.
        """
        self.path = str(path)
        with self.transaction() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id));
                CREATE TABLE IF NOT EXISTS entities (
                    kind TEXT NOT NULL, id TEXT NOT NULL, data TEXT NOT NULL,
                    PRIMARY KEY(kind, id));
                CREATE TABLE IF NOT EXISTS mail (
                    id TEXT PRIMARY KEY, booking_id TEXT NOT NULL, kind TEXT NOT NULL,
                    due REAL NOT NULL, state TEXT NOT NULL, payload TEXT NOT NULL);
            """)

    @contextmanager
    def transaction(self):
        """Open a connection and commit or roll back a serialized transaction.

        Yields:
            sqlite3.Connection: Connection with sqlite3.Row results and foreign keys on.

        Raises:
            BaseException: Re-raises failures from the transaction body after rollback.
            sqlite3.Error: If opening, locking, committing or rolling back fails.

        Notes:
            Uses a 15-second lock timeout and closes the connection after the body.
        """
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def get(db, kind, ident):
        """Return the decoded entity for kind and ident, or None if absent.

        Args:
            db: Open transaction connection with sqlite3.Row results.
            kind: Entity kind string.
            ident: Entity identifier within that kind.
        """
        row = db.execute(
            "SELECT data FROM entities WHERE kind=? AND id=?", (kind, ident)
        ).fetchone()
        return json.loads(row["data"]) if row else None

    @staticmethod
    def all(db, kind):
        """Return decoded dictionaries of kind from db in row insertion order.

        Args:
            db: Open transaction connection with sqlite3.Row results.
            kind: Entity kind string; no role or ownership filtering is applied.
        """
        return [
            json.loads(r["data"])
            for r in db.execute(
                "SELECT data FROM entities WHERE kind=? ORDER BY rowid",
                (kind,),
            )
        ]

    @staticmethod
    def put(db, kind, value):
        """Insert or replace an entity payload without committing.

        Args:
            db: Open transaction connection.
            kind: Entity kind string.
            value: JSON-serializable dictionary containing its id.

        Raises:
            KeyError: If value has no id.
            sqlite3.Error: If the write fails.

        Notes:
            Returns None; callers own validation, commit and rollback.
        """
        db.execute(
            "INSERT INTO entities VALUES (?,?,?) ON CONFLICT(kind,id) DO UPDATE SET data=excluded.data",
            (kind, value["id"], json.dumps(value, ensure_ascii=False)),
        )
