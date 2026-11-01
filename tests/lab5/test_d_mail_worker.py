from datetime import datetime,timedelta
import json
import logging
import pytest
from conftest import auth
from test_b_bookings import created
from test_c_notifications_logging import messages
from salon.mail_worker import run_once


class CaptureTransport:
    def __init__(self):
        self.sent=[]

    def send(self,kind,payload):
        self.sent.append((kind,payload))


@pytest.mark.req('REQ-F-056','REQ-F-059')
@pytest.mark.integration
def test_deliver_only_due_once(catalog):
    app,client,now=catalog;value=created(client);transport=CaptureTransport()
    assert run_once(app.extensions['store'],lambda:now[0],transport)==1
    assert [kind for kind,_ in transport.sent]==['created']
    assert transport.sent[0][1]['to']=='alice@example.test'
    assert transport.sent[0][1]['booking']['id']==value['id']
    assert run_once(app.extensions['store'],lambda:now[0],transport)==0
    now[0]=datetime.fromisoformat(value['startsAt'])-timedelta(hours=24)
    assert run_once(app.extensions['store'],lambda:now[0],transport)==1
    assert [kind for kind,_ in transport.sent]==['created','reminder']


@pytest.mark.req('REQ-F-057','REQ-F-058','REQ-F-061','REQ-F-062')
@pytest.mark.bdd('GWT-031','GWT-035')
def test_old_reminder_never_sent(catalog):
    app,client,now=catalog;value=created(client);transport=CaptureTransport()
    client.patch('/bookings/'+value['id'],json={'startsAt':'2026-11-05T14:00:00+02:00'},headers=auth())
    client.post('/bookings/'+value['id']+'/cancellation',headers=auth('alice'))
    now[0]=datetime.fromisoformat('2026-11-05T14:00:00+02:00')
    assert run_once(app.extensions['store'],lambda:now[0],transport)==3
    assert [kind for kind,_ in transport.sent]==['created','changed','cancelled']
    assert all(row['state']=='cancelled' for row in messages(app) if row['kind']=='reminder')


@pytest.mark.req('REQ-F-056','REQ-NF-006')
def test_transport_failure_safe_and_retained(catalog,caplog):
    app,client,now=catalog;created(client)
    class Failure:
        def send(self,*args):
            raise RuntimeError('private-smtp-password@example.test')
    caplog.set_level(logging.INFO,logger='salon.events')
    assert run_once(app.extensions['store'],lambda:now[0],Failure())==0
    assert any(row['state']=='failed' for row in messages(app))
    assert 'MAIL_DELIVERY_FAILED' in caplog.text
    assert 'private-smtp-password@example.test' not in caplog.text


@pytest.mark.req('REQ-F-056','REQ-NF-006')
def test_worker_logs_system_events(catalog,caplog):
    app,client,now=catalog;created(client)
    caplog.set_level(logging.INFO,logger='salon.events')
    run_once(app.extensions['store'],lambda:now[0],CaptureTransport())
    records=[json.loads(r.message) for r in caplog.records if r.name=='salon.events']
    assert any(r['operation']=='mail.send' and r['status']==200 for r in records)
    assert 'alice@example.test' not in caplog.text


@pytest.mark.req('REQ-F-056','REQ-F-057','REQ-F-058','REQ-F-059')
def test_smtp_message_and_tls(monkeypatch):
    import smtplib
    from salon.mail_worker import SMTPTransport
    calls=[]
    class SMTP:
        def __init__(self,*args,**kwargs):
            calls.append('connect')
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def starttls(self,**kwargs): calls.append('tls')
        def login(self,*args): calls.append('login')
        def send_message(self,message): calls.append(message)
    monkeypatch.setattr(smtplib,'SMTP',SMTP)
    payload=dict(to='alice@example.test',booking=dict(startsAt='2026-11-04T14:00:00+02:00',
        endsAt='2026-11-04T15:00:00+02:00',masterName='Stylist',status='confirmed',
        serviceSnapshot=dict(name='Hair',price=500,currency='UAH',durationMinutes=60)))
    SMTPTransport('localhost',2525,'salon@example.test',username='test',password='test').send('created',payload)
    assert calls[:3]==['connect','tls','login']
    message=calls[3]
    assert message['To']=='alice@example.test'
    assert 'Hair' in message.get_content() and '500' in message.get_content()
    assert 'Stylist' in message.get_content() and '2026-11-04' in message.get_content()
