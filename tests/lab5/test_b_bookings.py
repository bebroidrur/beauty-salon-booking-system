from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier
import pytest
from conftest import auth, schema_check
from salon.app import create_app


def book(client, who='alice', **changes):
    return client.post('/bookings',json=dict(serviceId='svc',masterId='master',startsAt='2026-11-04T14:00:00+02:00')|changes,headers=auth(who))


def created(client, **changes):
    r=book(client,**changes)
    assert r.status_code==201
    return r.json


@pytest.mark.req('REQ-F-008','REQ-F-011','REQ-F-012','REQ-F-014','REQ-F-015','REQ-F-016','REQ-F-017','REQ-F-031')
@pytest.mark.bdd('GWT-001')
def test_create_snapshot(catalog):
    client=catalog[1];value=created(client)
    schema_check('Booking',value)
    assert value['clientId']=='alice' and value['status']=='confirmed'
    assert value['serviceSnapshot']==dict(name='Hair',price=500,currency='UAH',durationMinutes=60)
    assert value['endsAt']=='2026-11-04T15:00:00+02:00'
    assert client.get('/bookings/'+value['id'],headers=auth('alice')).json==value
    assert client.post('/bookings',json={}).status_code==401


@pytest.mark.req('REQ-F-013','REQ-F-019','REQ-F-020')
@pytest.mark.bdd('GWT-003','GWT-004','GWT-005')
@pytest.mark.parametrize('who,minutes,status',[('alice',120,201),('alice',119,422),('admin',60,201)])
def test_lead_boundary(catalog,who,minutes,status):
    _,client,now=catalog
    start=datetime.fromisoformat('2026-11-04T14:00:00+02:00')
    now[0]=start-timedelta(minutes=minutes)
    r=book(client,who,**({'clientId':'alice'} if who=='admin' else {}))
    assert r.status_code==status


@pytest.mark.req('REQ-F-009','REQ-F-010','REQ-F-013','REQ-F-038')
@pytest.mark.bdd('GWT-019')
def test_ownership_and_roles(catalog):
    client=catalog[1];value=created(client);path='/bookings/'+value['id']
    assert client.get(path,headers=auth('bob')).status_code==403
    assert client.post(path+'/cancellation',headers=auth('bob')).status_code==403
    assert client.patch(path,json={'startsAt':'2026-11-05T14:00:00+02:00'},headers=auth('alice')).status_code==403
    assert client.get('/bookings?category=current',headers=auth('bob')).json['items']==[]
    assert len(client.get('/bookings?category=current',headers=auth()).json['items'])==1
    assert book(client,'alice',clientId='bob').status_code==422
    assert book(client,'admin').status_code==422
    assert book(client,'admin',clientId='missing').status_code==422


@pytest.mark.req('REQ-F-012','REQ-F-022','REQ-F-055')
@pytest.mark.bdd('GWT-002','GWT-008','GWT-009','GWT-030')
@pytest.mark.parametrize('starts,status',[('2026-11-04T17:00:00+02:00',201),('2026-11-04T17:30:00+02:00',422)])
def test_work_interval(catalog,starts,status):
    assert book(catalog[1],startsAt=starts).status_code==status


@pytest.mark.req('REQ-F-012','REQ-F-054','REQ-F-055')
def test_incompatible_and_inactive(catalog):
    client=catalog[1]
    assert client.patch('/masters/master',json={'serviceIds':[]},headers=auth()).status_code==200
    assert book(client).status_code==422
    client.patch('/masters/master',json={'serviceIds':['svc']},headers=auth())
    value=created(client)
    client.patch('/services/svc',json={'active':False},headers=auth())
    assert book(client,startsAt='2026-11-05T14:00:00+02:00').status_code==422
    assert client.get('/bookings/'+value['id'],headers=auth('alice')).json==value


@pytest.mark.req('REQ-F-023','REQ-F-024','REQ-F-026','REQ-F-027','REQ-F-029')
@pytest.mark.bdd('GWT-010','GWT-011','GWT-012','GWT-013')
@pytest.mark.parametrize('who,master',[('bob','master'),('alice','master2')])
def test_conflicts_and_adjacency(catalog,who,master):
    client=catalog[1];created(client)
    r=book(client,who,masterId=master,startsAt='2026-11-04T14:30:00+02:00')
    assert r.status_code==409
    assert r.json['code']=='TIME_UNAVAILABLE'
    assert 'інший час' in r.json['message']
    assert book(client,who,masterId=master,startsAt='2026-11-04T15:00:00+02:00').status_code==201


@pytest.mark.req('REQ-F-028','REQ-F-029')
@pytest.mark.bdd('GWT-014')
@pytest.mark.integration
@pytest.mark.parametrize('same_client',[False,True])
def test_atomic_competition(catalog,same_client):
    app,_,_=catalog;barrier=Barrier(2)
    def attempt(i):
        with app.test_client() as client:
            barrier.wait(timeout=5)
            return book(client,'alice' if same_client or i==0 else 'bob',
                        masterId='master2' if same_client and i else 'master').status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses=list(pool.map(attempt,[0,1]))
    assert sorted(statuses)==[201,409]
    with app.extensions['store'].transaction() as db:
        assert len(app.extensions['store'].all(db,'booking'))==1


@pytest.mark.req('REQ-F-030','REQ-F-032','REQ-F-033','REQ-F-041')
@pytest.mark.bdd('GWT-028','GWT-029')
def test_history_boundary(catalog):
    _,client,now=catalog;value=created(client);path='/bookings/'+value['id']
    now[0]=datetime.fromisoformat(value['endsAt'])-timedelta(seconds=1)
    assert client.get(path,headers=auth('alice')).json['category']=='current'
    now[0]+=timedelta(seconds=1)
    assert client.get(path,headers=auth('alice')).json['category']=='history'
    assert len(client.get('/bookings?category=history',headers=auth('alice')).json['items'])==1
    assert client.patch(path,json={'masterId':'master2'},headers=auth()).status_code==409
    assert client.post(path+'/cancellation',headers=auth()).status_code==409


@pytest.mark.req('REQ-F-025','REQ-F-034','REQ-F-035','REQ-F-036','REQ-F-037','REQ-F-041')
@pytest.mark.bdd('GWT-015','GWT-016','GWT-017','GWT-018')
@pytest.mark.parametrize('who,minutes,status',[('alice',1440,200),('alice',1439,422),('admin',60,200)])
def test_cancellation_boundary(catalog,who,minutes,status):
    _,client,now=catalog;value=created(client);path='/bookings/'+value['id']
    now[0]=datetime.fromisoformat(value['startsAt'])-timedelta(minutes=minutes)
    r=client.post(path+'/cancellation',headers=auth(who))
    assert r.status_code==status
    if status==200:
        assert r.json['status']=='cancelled' and r.json['category']=='history'
        assert client.post(path+'/cancellation',headers=auth()).status_code==409
        assert book(client,'admin',clientId='alice').status_code==201
    else:
        assert 'адміністратора' in r.json['message']
        assert client.get(path,headers=auth('alice')).json==value


@pytest.mark.req('REQ-F-039','REQ-F-042','REQ-F-043','REQ-F-044','REQ-F-052')
@pytest.mark.bdd('GWT-020','GWT-021')
def test_patch_snapshots(catalog):
    client=catalog[1];value=created(client);path='/bookings/'+value['id']
    client.patch('/services/svc',json=dict(name='Changed',price=600,durationMinutes=90),headers=auth())
    assert client.get(path,headers=auth('alice')).json==value
    r=client.patch(path,json=dict(startsAt='2026-11-05T14:00:00+02:00',masterId='master2'),headers=auth())
    assert r.status_code==200 and r.json['serviceSnapshot']==value['serviceSnapshot']
    assert r.json['endsAt']=='2026-11-05T15:00:00+02:00'
    client.patch('/services/svc2',json=dict(price=700,durationMinutes=90),headers=auth())
    r=client.patch(path,json={'serviceId':'svc2'},headers=auth())
    assert r.status_code==200 and r.json['serviceSnapshot']['price']==700
    assert r.json['endsAt']=='2026-11-05T15:30:00+02:00'


@pytest.mark.req('REQ-F-040')
@pytest.mark.bdd('GWT-022','GWT-023','GWT-024')
@pytest.mark.parametrize('change',[{'startsAt':'2026-11-04T17:30:00+02:00'},
    {'startsAt':'2026-11-04T16:30:00+02:00'},
    {'startsAt':'2026-11-04T16:30:00+02:00','masterId':'master2'}])
def test_patch_rollback(catalog,change):
    client=catalog[1];value=created(client);path='/bookings/'+value['id']
    created(client,startsAt='2026-11-04T16:00:00+02:00')
    assert client.patch(path,json=change,headers=auth()).status_code==409
    assert client.get(path,headers=auth('alice')).json==value


@pytest.mark.req('REQ-F-050','REQ-F-051','REQ-F-053')
@pytest.mark.bdd('GWT-025','GWT-026')
def test_protect_live_bookings(catalog):
    client=catalog[1];value=created(client)
    exception=dict(date='2026-11-04',kind='day_off',day={'working':False})
    assert client.patch('/masters/master/schedule',json={'exceptions':[exception]},headers=auth()).status_code==409
    assert client.get('/masters/master/schedule',headers=auth()).json['exceptions']==[]
    assert client.patch('/masters/master',json={'serviceIds':[]},headers=auth()).status_code==409
    assert client.delete('/masters/master',headers=auth()).status_code==409
    assert client.delete('/services/svc',headers=auth()).status_code==409
    client.post('/bookings/'+value['id']+'/cancellation',headers=auth('alice'))
    assert client.patch('/masters/master/schedule',json={'exceptions':[exception]},headers=auth()).status_code==200


@pytest.mark.req('REQ-F-015','REQ-F-031','REQ-NF-002')
@pytest.mark.integration
def test_restart_persistence(catalog):
    app,client,now=catalog;value=created(client)
    restarted=create_app(app.extensions['store'].path,clock=lambda:now[0]).test_client()
    assert restarted.get('/bookings/'+value['id'],headers=auth('alice')).json==value


@pytest.mark.req('REQ-F-021')
def test_far_outside_horizon(catalog):
    assert book(catalog[1],startsAt='2027-02-01T14:00:00+02:00').status_code==422
