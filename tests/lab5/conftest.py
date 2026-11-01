import hashlib
import json
from datetime import datetime
from pathlib import Path

import pytest
import yaml
from openapi_schema_validator import OAS30Validator
from werkzeug.security import generate_password_hash

from salon.app import create_app

API = yaml.safe_load(Path('spec/openapi.yaml').read_text())


def resolve(value):
    if isinstance(value, dict):
        if '$ref' in value:
            result = API
            for part in value['$ref'][2:].split('/'):
                result = result[part]
            return resolve(result)
        return {k: resolve(v) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(v) for v in value]
    return value


def schema_check(name, value):
    OAS30Validator(resolve(API['components']['schemas'][name]),
                   format_checker=OAS30Validator.FORMAT_CHECKER).validate(value)


@pytest.fixture
def env(tmp_path):
    now = [datetime.fromisoformat('2026-11-02T10:00:00+02:00')]
    app = create_app(tmp_path / 'test.sqlite3', clock=lambda: now[0])
    store = app.extensions['store']
    with store.transaction() as db:
        for role, ident in [('administrator','admin'),('client','alice'),('client','bob')]:
            data = dict(id=ident, name=f'Control {ident}', phone='+380000000000',
                        email=f'{ident}@example.test', role=role)
            db.execute('INSERT INTO users VALUES (?,?,?,?)',
                       (ident,data['email'],generate_password_hash('test-password'),json.dumps(data)))
            db.execute('INSERT INTO sessions VALUES (?,?)',
                       (hashlib.sha256(f'test-{ident}'.encode()).hexdigest(),ident))
    return app, app.test_client(), now


def auth(who='admin'):
    return {'Authorization': f'Bearer test-{who}'}


@pytest.fixture
def catalog(env):
    app, client, now = env
    # Arrange independent persisted entities, not a fake application service.
    with app.extensions['store'].transaction() as db:
        store = app.extensions['store']
        for ident in ('svc','svc2'):
            store.put(db,'service',dict(id=ident,name='Hair',description='Cut',price=500,
                                       currency='UAH',durationMinutes=60,active=True))
        for ident in ('master','master2'):
            store.put(db,'master',dict(id=ident,name='Stylist',serviceIds=['svc','svc2'],active=True))
            store.put(db,'schedule',dict(id=ident,masterId=ident,timezone='Europe/Kyiv',
                       weekly={day:dict(working=True,interval=dict(start='09:00',end='18:00'))
                               for day in ('monday','tuesday','wednesday','thursday','friday','saturday','sunday')},exceptions=[]))
    return env


def pytest_collection_modifyitems(items):
    for item in items:
        item.user_properties.append(('requirements',','.join(sorted({rid for marker in item.iter_markers('req') for rid in marker.args}))))
        item.user_properties.append(('bdd',','.join(sorted({rid for marker in item.iter_markers('bdd') for rid in marker.args}))))
