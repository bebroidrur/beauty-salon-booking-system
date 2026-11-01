"""SQLite persistence; each operation owns a connection and a transaction."""
import json
import sqlite3
from contextlib import contextmanager


class Store:
    def __init__(self, path):
        self.path = str(path)
        with self.transaction() as db:
            db.executescript('''
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
            ''')

    @contextmanager
    def transaction(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def get(db, kind, ident):
        row = db.execute('SELECT data FROM entities WHERE kind=? AND id=?', (kind, ident)).fetchone()
        return json.loads(row['data']) if row else None

    @staticmethod
    def all(db, kind):
        return [json.loads(r['data']) for r in db.execute('SELECT data FROM entities WHERE kind=? ORDER BY rowid', (kind,))]

    @staticmethod
    def put(db, kind, value):
        db.execute('INSERT INTO entities VALUES (?,?,?) ON CONFLICT(kind,id) DO UPDATE SET data=excluded.data',
                   (kind, value['id'], json.dumps(value, ensure_ascii=False)))
