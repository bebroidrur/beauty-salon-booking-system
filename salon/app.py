"""Application factory. RED scaffold: no product routes yet."""
from datetime import datetime, timezone
from flask import Flask
from salon.store import Store


def create_app(database, clock=None):
    app = Flask(__name__)
    app.extensions['store'] = Store(database)
    app.extensions['clock'] = clock or (lambda: datetime.now(timezone.utc))
    return app
