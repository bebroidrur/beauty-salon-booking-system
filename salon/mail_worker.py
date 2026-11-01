"""Durable due-job delivery; failures remain visible for explicit retry."""
import json
import smtplib
import ssl
from email.message import EmailMessage
from salon.events import record


def run_once(store, clock, transport):
    sent=0
    # Serialize with cancellation/rescheduling. SMTP timeout bounds this lock.
    # Crash after SMTP acceptance but before commit can duplicate a message.
    with store.transaction() as db:
        rows=db.execute("SELECT * FROM mail WHERE state='pending' AND due<=? ORDER BY due,rowid",(clock().timestamp(),)).fetchall()
        for row in rows:
            try:
                transport.send(row['kind'],json.loads(row['payload']))
            except Exception:
                db.execute("UPDATE mail SET state='failed' WHERE id=?",(row['id'],))
                record('mail.send',500,row['id'],'MAIL_DELIVERY_FAILED')
            else:
                db.execute("UPDATE mail SET state='sent' WHERE id=?",(row['id'],))
                record('mail.send',200,row['id'])
                sent+=1
    return sent


class SMTPTransport:
    def __init__(self, host, port, sender, starttls=True, username=None, password=None):
        self.host,self.port,self.sender=host,port,sender
        self.starttls,self.username,self.password=starttls,username,password

    def send(self,kind,payload):
        booking=payload['booking'];snapshot=booking['serviceSnapshot']
        message=EmailMessage()
        message['From']=self.sender
        message['To']=payload['to']
        message['Subject']={'created':'Підтвердження запису','changed':'Зміна запису',
                            'cancelled':'Скасування запису','reminder':'Нагадування про запис'}[kind]
        message.set_content(f"{snapshot['name']}\n{snapshot['price']} {snapshot['currency']}\n"
                            f"{snapshot['durationMinutes']} хв\n{booking['masterName']}\n"
                            f"{booking['startsAt']} — {booking['endsAt']}\n{booking['status']}")
        with smtplib.SMTP(self.host,self.port,timeout=10) as smtp:
            if self.starttls:
                smtp.starttls(context=ssl.create_default_context())
            if self.username:
                smtp.login(self.username,self.password)
            smtp.send_message(message)
