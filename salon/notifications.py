"""Transactional email outbox; no network side effects before commit."""
import json
import uuid
from datetime import timedelta
from salon.time_rules import instant
from salon.booking_service import unresolved


def enqueue(db, booking, kind, due):
    user=json.loads(db.execute('SELECT data FROM users WHERE id=?',(booking['clientId'],)).fetchone()['data'])
    payload=dict(to=user['email'],booking=booking)
    db.execute('INSERT INTO mail VALUES (?,?,?,?,?,?)',
               (uuid.uuid4().hex,booking['id'],kind,due.timestamp(),'pending',json.dumps(payload)))


def on_booking(db, before, after, now):
    if before is None:
        enqueue(db,after,'created',now)
        due=instant(after['startsAt'])-timedelta(hours=24)
        if due>=now:
            enqueue(db,after,'reminder',due)
        return
    cancelled=after['status']=='cancelled'
    moved=instant(before['startsAt'])!=instant(after['startsAt'])
    if cancelled or moved:
        if moved and instant(after['startsAt'])-now>=timedelta(hours=24):
            has_reminder=db.execute("SELECT 1 FROM mail WHERE booking_id=? AND kind='reminder'",(after['id'],)).fetchone()
            if not has_reminder:
                unresolved('D-04')
        db.execute("UPDATE mail SET state='cancelled' WHERE booking_id=? AND kind='reminder' AND state IN ('pending','failed')",(after['id'],))
    enqueue(db,after,'cancelled' if cancelled else 'changed',now)
    if moved and not cancelled:
        due=instant(after['startsAt'])-timedelta(hours=24)
        if due>=now:
            enqueue(db,after,'reminder',due)
    elif not cancelled:
        # Reminder uses updated details when service/master changes without moving.
        rows=db.execute("SELECT id,payload FROM mail WHERE booking_id=? AND kind='reminder' AND state='pending'",(after['id'],)).fetchall()
        for row in rows:
            payload=json.loads(row['payload']);payload['booking']=after
            db.execute('UPDATE mail SET payload=? WHERE id=?',(json.dumps(payload),row['id']))
