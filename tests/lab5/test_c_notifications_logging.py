from datetime import datetime,timedelta
import json
import logging
import pytest
from conftest import auth
from test_b_bookings import created, book


def messages(app):
    with app.extensions['store'].transaction() as db:
        return [dict(row) for row in db.execute('SELECT * FROM mail ORDER BY rowid')]


@pytest.mark.req('REQ-F-056','REQ-F-059','REQ-F-060')
@pytest.mark.bdd('GWT-001','GWT-034')
@pytest.mark.parametrize('hours,reminders',[(48,1),(24,1),(12,0)])
def test_creation_notifications(catalog,hours,reminders):
    app,client,now=catalog
    now[0]=datetime.fromisoformat('2026-11-04T14:00:00+02:00')-timedelta(hours=hours)
    value=created(client)
    rows=messages(app)
    assert len([r for r in rows if r['kind']=='created' and r['state']=='pending'])==1
    rem=[r for r in rows if r['kind']=='reminder']
    assert len(rem)==reminders
    payload=json.loads(rows[0]['payload'])
    assert payload['booking']['serviceSnapshot']==value['serviceSnapshot']
    if rem:
        assert rem[0]['due']==datetime.fromisoformat(value['startsAt']).timestamp()-86400


@pytest.mark.req('REQ-F-057','REQ-F-062','REQ-F-063','REQ-F-064')
@pytest.mark.bdd('GWT-031','GWT-032','GWT-033')
@pytest.mark.parametrize('hours,expected',[(48,1),(24,1),(12,0)])
def test_reschedule_notifications(catalog,hours,expected):
    app,client,now=catalog;value=created(client)
    new_start=datetime.fromisoformat('2026-11-05T14:00:00+02:00')
    now[0]=new_start-timedelta(hours=hours)
    # Keep old appointment current when moving to the new time.
    if hours==12:
        now[0]=datetime.fromisoformat('2026-11-04T02:00:00+02:00')
        new_start=now[0]+timedelta(hours=12)
        new_start+=timedelta(minutes=30)
        now[0]+=timedelta(minutes=30)
    r=client.patch('/bookings/'+value['id'],json={'startsAt':new_start.isoformat()},headers=auth())
    assert r.status_code==200
    rows=messages(app)
    assert len([r for r in rows if r['kind']=='changed'])==1
    assert len([r for r in rows if r['kind']=='reminder' and r['state']=='cancelled'])==1
    pending=[r for r in rows if r['kind']=='reminder' and r['state']=='pending']
    assert len(pending)==expected
    if pending:
        assert pending[0]['due']==new_start.timestamp()-86400


@pytest.mark.req('REQ-F-058','REQ-F-061')
@pytest.mark.bdd('GWT-035')
def test_cancellation_cancels_reminders(catalog):
    app,client,_=catalog;value=created(client)
    assert client.post('/bookings/'+value['id']+'/cancellation',headers=auth('alice')).status_code==200
    rows=messages(app)
    assert len([r for r in rows if r['kind']=='cancelled'])==1
    assert all(r['state']=='cancelled' for r in rows if r['kind']=='reminder')
    assert any(r['kind']=='reminder' for r in rows)


@pytest.mark.req('REQ-F-056','REQ-F-057')
def test_failed_mutation_no_success_mail(catalog):
    app,client,_=catalog;value=created(client);before=messages(app)
    assert before
    assert book(client).status_code==409
    assert client.patch('/bookings/'+value['id'],json={'startsAt':'2026-11-04T17:30:00+02:00'},headers=auth()).status_code==409
    assert messages(app)==before


@pytest.mark.req('REQ-NF-004','REQ-NF-006')
def test_safe_system_logs(env,caplog):
    app,client,_=env
    caplog.set_level(logging.INFO,logger='salon.events')
    client.post('/sessions',json=dict(email='alice@example.test',password='secret-sentinel'))
    client.get('/services?private=private-sentinel',headers={'Authorization':'Bearer token-sentinel'})
    records=[json.loads(r.message) for r in caplog.records if r.name=='salon.events']
    assert len(records)>=2
    assert all('operation' in r and 'status' in r and 'requestId' in r for r in records)
    assert len({r['requestId'] for r in records})>=2
    for text in ('alice@example.test','secret-sentinel','private-sentinel','token-sentinel'):
        assert text not in caplog.text


@pytest.mark.req('REQ-NF-004','REQ-NF-006')
def test_internal_error_logs_no_exception_data(env,caplog,monkeypatch):
    app,client,_=env
    def fail(*args):
        raise RuntimeError('private-exception-sentinel')
    monkeypatch.setattr(app.extensions['service'],'execute',fail)
    caplog.set_level(logging.INFO,logger='salon.events')
    r=client.get('/services')
    assert r.status_code==500 and r.json['code']=='INTERNAL_ERROR'
    assert 'INTERNAL_ERROR' in caplog.text
    assert 'private-exception-sentinel' not in caplog.text+r.get_data(as_text=True)
