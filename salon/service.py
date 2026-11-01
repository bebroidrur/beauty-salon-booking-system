"""Use cases operating within one SQLite transaction per request."""
import hashlib
import json
import secrets
import sqlite3
import uuid
from werkzeug.security import check_password_hash, generate_password_hash
from salon.errors import reject
from salon.booking_service import Bookings

from salon.time_rules import DAYS


def ident():
    return uuid.uuid4().hex


class Service:
    def __init__(self, store, clock):
        self.store, self.clock = store, clock
        self.bookings = Bookings(store, clock)

    def get(self, db, kind, key):
        value = self.store.get(db, kind, key)
        if value is None:
            reject(404, 'NOT_FOUND', 'Ресурс не знайдено.')
        return value

    def execute(self, db, op, data, params, user):
        if op in ('listBookings','createBooking','getBooking','updateBooking','cancelBooking'):
            return self.bookings.execute(db,op,data,params,user)
        if op == 'registerClient':
            value = {k:v for k,v in data.items() if k != 'password'} | {'id':ident(), 'role':'client'}
            try:
                db.execute('INSERT INTO users VALUES (?,?,?,?)',
                           (value['id'],value['email'],generate_password_hash(data['password']),json.dumps(value)))
            except sqlite3.IntegrityError:
                reject(409, 'EMAIL_IN_USE', 'Email вже використовується.')
            return value
        if op == 'login':
            row = db.execute('SELECT * FROM users WHERE email=?',(data['email'],)).fetchone()
            # Compute the same password KDF also for an unknown user.
            encoded = row['password_hash'] if row else generate_password_hash(secrets.token_hex(16))
            valid = check_password_hash(encoded,data['password'])
            if not row or not valid:
                reject(401,'UNAUTHENTICATED','Потрібен вхід або правильні облікові дані.')
            token = secrets.token_urlsafe(32)
            db.execute('INSERT INTO sessions VALUES (?,?)',(hashlib.sha256(token.encode()).hexdigest(),row['id']))
            return dict(accessToken=token,tokenType='Bearer',user=json.loads(row['data']))
        if op in ('listServices','listMasters'):
            return {'items':self.store.all(db,'service' if op=='listServices' else 'master')}
        for kind, label in [('service','Service'),('master','Master')]:
            if op == 'create'+label:
                if kind=='master':
                    self.check_service_ids(db,data['serviceIds'])
                value = data | {'id':ident(),'active':True}
                if kind=='service':
                    value['currency']='UAH'
                self.store.put(db,kind,value)
                if kind=='master':
                    self.store.put(db,'schedule',dict(id=value['id'],masterId=value['id'],timezone='Europe/Kyiv',
                                                     weekly={day:{'working':False} for day in DAYS},exceptions=[]))
                return value
            if op in ('update'+label,'delete'+label):
                key=params[kind+'Id'];value=self.get(db,kind,key)
                self.bookings.protect(db,kind,key,op,data)
                if op.startswith('delete'):
                    db.execute('DELETE FROM entities WHERE kind=? AND id=?',(kind,key))
                    if kind=='master':
                        db.execute('DELETE FROM entities WHERE kind=? AND id=?',('schedule',key))
                    return None
                if kind=='master' and 'serviceIds' in data:
                    self.check_service_ids(db,data['serviceIds'])
                value.update(data)
                self.store.put(db,kind,value)
                return value
        if op in ('getSchedule','updateSchedule'):
            key=params['masterId'];self.get(db,'master',key)
            value=self.get(db,'schedule',key)
            if op=='updateSchedule':
                value.update(data)
                self.check_schedule(value)
                self.bookings.protect_schedule(db,key,value)
                self.store.put(db,'schedule',value)
            return {k:v for k,v in value.items() if k!='id'}
        reject(404,'NOT_FOUND','Ресурс не знайдено.')

    def check_service_ids(self, db, ids):
        if any(self.store.get(db,'service',key) is None for key in ids):
            reject(422)

    @staticmethod
    def check_schedule(value):
        dates=[e['date'] for e in value['exceptions']]
        if len(dates)!=len(set(dates)):
            reject(422)
        for exception in value['exceptions']:
            if exception['day']['working'] != (exception['kind']=='changed_hours'):
                reject(422)
        for day in list(value['weekly'].values())+[e['day'] for e in value['exceptions']]:
            if day['working'] and day['interval']['start'] >= day['interval']['end']:
                reject(422)
