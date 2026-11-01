"""Real loopback HTTP and SMTP; requires permission to bind local ports."""
from datetime import datetime, timezone
from email import policy
from email.parser import BytesParser
import json
import socketserver
from threading import Thread
from urllib.request import urlopen
import pytest
from werkzeug.serving import make_server
from salon.app import create_app
from salon.__main__ import SafeRequestHandler
from salon.mail_worker import SMTPTransport, run_once
from salon.store import Store


@pytest.mark.req('REQ-F-001')
@pytest.mark.integration
def test_real_http(tmp_path):
    app=create_app(tmp_path/'http.sqlite3')
    server=make_server('127.0.0.1',0,app,request_handler=SafeRequestHandler)
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with urlopen(f'http://127.0.0.1:{server.server_port}/services',timeout=5) as response:
            assert response.status==200
            assert json.loads(response.read())=={'items':[]}
    finally:
        server.shutdown();thread.join(timeout=5);server.server_close()


class SMTPSink(socketserver.StreamRequestHandler):
    def handle(self):
        self.wfile.write(b'220 local test SMTP\r\n')
        while line:=self.rfile.readline():
            command=line.split(b' ',1)[0].strip().upper()
            if command in (b'EHLO',b'HELO'):
                self.wfile.write(b'250 localhost\r\n')
            elif command==b'DATA':
                self.wfile.write(b'354 send data\r\n');data=[]
                while (line:=self.rfile.readline())!=b'.\r\n':
                    if not line:return
                    data.append(line)
                self.server.messages.append(b''.join(data))
                self.wfile.write(b'250 accepted\r\n')
            elif command==b'QUIT':
                self.wfile.write(b'221 bye\r\n');return
            else:
                self.wfile.write(b'250 ok\r\n')


@pytest.mark.req('REQ-F-056','REQ-F-059')
@pytest.mark.integration
def test_real_smtp_outbox(tmp_path):
    server=socketserver.TCPServer(('127.0.0.1',0),SMTPSink)
    server.messages=[]
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    store=Store(tmp_path/'smtp.sqlite3')
    payload=dict(to='synthetic@example.test',booking=dict(startsAt='2026-11-04T14:00:00+02:00',
        endsAt='2026-11-04T15:00:00+02:00',masterName='Synthetic',status='confirmed',
        serviceSnapshot=dict(name='Hair',price=500,currency='UAH',durationMinutes=60)))
    with store.transaction() as db:
        db.execute('INSERT INTO mail VALUES (?,?,?,?,?,?)',('message','booking','created',0,'pending',json.dumps(payload)))
    try:
        transport=SMTPTransport('127.0.0.1',server.server_address[1],'salon@example.test',starttls=False)
        assert run_once(store,lambda:datetime.now(timezone.utc),transport)==1
        assert len(server.messages)==1
        message=BytesParser(policy=policy.default).parsebytes(server.messages[0])
        assert message['To']=='synthetic@example.test'
        assert 'Hair' in message.get_body().get_content()
        with store.transaction() as db:
            assert db.execute('SELECT state FROM mail').fetchone()['state']=='sent'
    finally:
        server.shutdown();thread.join(timeout=5);server.server_close()
