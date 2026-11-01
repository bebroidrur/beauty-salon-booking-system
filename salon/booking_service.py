"""Agreed booking invariants. Unresolved specification cases fail explicitly."""
from datetime import datetime, timedelta, timezone
import json
import uuid
from salon.errors import reject

from salon.time_rules import KYIV, DAYS, instant, local


def unresolved(decision):
    # Never invent an acceptance rule from an unapproved example.
    reject(500, 'INTERNAL_ERROR', 'Потрібне погодження правила специфікації: '+decision+'.')


class Bookings:
    def __init__(self, store, clock):
        self.store, self.clock = store, clock

    def now(self):
        return self.clock().astimezone(timezone.utc)

    def view(self, value):
        return value | {'category':'history' if value['status']=='cancelled' or instant(value['endsAt'])<=self.now() else 'current'}

    def get(self, db, kind, key):
        value=self.store.get(db,kind,key)
        if value is None:
            reject(404,'NOT_FOUND','Ресурс не знайдено.')
        return value

    def all(self, db):
        return [self.view(b) for b in self.store.all(db,'booking')]

    def execute(self, db, op, data, params, user):
        if op=='listBookings':
            return {'items':[b for b in self.all(db) if b['category']==params['category'] and
                             (user['role']=='administrator' or b['clientId']==user['id'])]}
        if op=='createBooking':
            if user['role']=='client':
                if 'clientId' in data:
                    reject(422)
                owner=user['id']
            else:
                owner=data.get('clientId')
                row=db.execute('SELECT data FROM users WHERE id=?',(owner,)).fetchone()
                if not row or json.loads(row['data'])['role']!='client':
                    reject(422)
            service=self.get(db,'service',data['serviceId'])
            master=self.get(db,'master',data['masterId'])
            if not service['active'] or not master['active'] or service['id'] not in master['serviceIds']:
                reject(422,'BOOKING_RULE_VIOLATION')
            value=dict(id=uuid.uuid4().hex,clientId=owner,serviceId=service['id'],masterId=master['id'],
                       masterName=master['name'],startsAt=local(instant(data['startsAt'])),status='confirmed',
                       serviceSnapshot={k:service[k] for k in ('name','price','currency','durationMinutes')})
            value['endsAt']=local(instant(value['startsAt'])+timedelta(minutes=value['serviceSnapshot']['durationMinutes']))
            if user['role']=='client' and instant(value['startsAt'])-self.now()<timedelta(hours=2):
                reject(422,'BOOKING_RULE_VIOLATION')
            self.check(db,value,changing=False)
            self.store.put(db,'booking',value)
            return self.view(value)
        value=self.view(self.get(db,'booking',params['bookingId']))
        if user['role']=='client' and value['clientId']!=user['id']:
            reject(403,'FORBIDDEN','Операція недоступна для цього користувача.')
        if op=='getBooking':
            return value
        if value['category']=='history':
            reject(409,'HISTORICAL_BOOKING' if op=='cancelBooking' else 'BOOKING_CHANGE_CONFLICT','Історичний запис не можна змінити.')
        if op=='cancelBooking':
            if user['role']=='client' and instant(value['startsAt'])-self.now()<timedelta(hours=24):
                reject(422,'CANCELLATION_TOO_LATE','До початку менше 24 годин. Зверніться до адміністратора.')
            value['status']='cancelled'
        elif op=='updateBooking':
            service=self.get(db,'service',data.get('serviceId',value['serviceId']))
            master=self.get(db,'master',data.get('masterId',value['masterId']))
            if not service['active'] or not master['active']:
                unresolved('D-06')
            if service['id'] not in master['serviceIds']:
                unresolved('D-05')
            if 'serviceId' in data and data['serviceId']!=value['serviceId']:
                value['serviceSnapshot']={k:service[k] for k in ('name','price','currency','durationMinutes')}
            value.update(data)
            value['masterName']=master['name']
            value['startsAt']=local(instant(value['startsAt']))
            value['endsAt']=local(instant(value['startsAt'])+timedelta(minutes=value['serviceSnapshot']['durationMinutes']))
            self.check(db,value,changing=True)
        self.store.put(db,'booking',value)
        return self.view(value)

    def check(self, db, value, changing):
        start,end=instant(value['startsAt']),instant(value['endsAt'])
        days=(start.astimezone(KYIV).date()-self.now().astimezone(KYIV).date()).days
        if days>30:
            reject(422,'BOOKING_RULE_VIOLATION')
        if days in (29,30):
            unresolved('D-02')
        if start<=self.now():
            unresolved('D-03')
        if not self.fits(self.get(db,'schedule',value['masterId']),start,end):
            reject(409 if changing else 422,'BOOKING_CHANGE_CONFLICT' if changing else 'BOOKING_RULE_VIOLATION')
        for other in self.store.all(db,'booking'):
            if other['id']==value['id'] or other['status']=='cancelled':
                continue
            if (other['masterId']==value['masterId'] or other['clientId']==value['clientId']) and start<instant(other['endsAt']) and instant(other['startsAt'])<end:
                reject(409,'BOOKING_CHANGE_CONFLICT' if changing else 'TIME_UNAVAILABLE',
                       'Обраний час недоступний. Оберіть інший час.')

    @staticmethod
    def fits(schedule,start,end):
        day_date=start.astimezone(KYIV).date()
        day=next((e['day'] for e in schedule['exceptions'] if e['date']==day_date.isoformat()),
                 schedule['weekly'][DAYS[day_date.weekday()]])
        if not day['working']:
            return False
        left=datetime.fromisoformat(day_date.isoformat()+'T'+day['interval']['start']).replace(tzinfo=KYIV).astimezone(timezone.utc)
        right=datetime.fromisoformat(day_date.isoformat()+'T'+day['interval']['end']).replace(tzinfo=KYIV).astimezone(timezone.utc)
        return left<=start<end<=right

    def protect(self, db, kind, key, operation, data):
        related=[b for b in self.all(db) if b[kind+'Id']==key]
        live=[b for b in related if b['category']=='current']
        if operation.startswith('delete'):
            if live:
                reject(409,'CURRENT_BOOKINGS_EXIST','Є актуальні записи.')
            if related:
                unresolved('D-06')
        if kind=='master' and 'serviceIds' in data and any(b['serviceId'] not in data['serviceIds'] for b in live):
            reject(409,'CURRENT_BOOKINGS_CONFLICT','Є актуальні записи.')

    def protect_schedule(self,db,key,schedule):
        if any(b['masterId']==key and b['category']=='current' and not self.fits(schedule,instant(b['startsAt']),instant(b['endsAt'])) for b in self.all(db)):
            reject(409,'SCHEDULE_CONFLICT','Графік суперечить актуальним записам.')
