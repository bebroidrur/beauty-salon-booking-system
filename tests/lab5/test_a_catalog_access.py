import json
import pytest
from conftest import auth, schema_check


@pytest.mark.req('REQ-F-001','REQ-F-002','REQ-F-003')
@pytest.mark.parametrize('path,schema', [('/services','ServiceList'),('/masters','MasterList')])
def test_public_catalog(catalog,path,schema):
    _, client, _ = catalog
    r=client.get(path)
    assert r.status_code==200
    schema_check(schema,r.json)
    assert len(r.json['items'])==2


@pytest.mark.req('REQ-F-005','REQ-F-006','REQ-F-007','REQ-NF-004')
def test_registration_login_persistence(env):
    app,client,_=env
    data=dict(name='Control New',phone='+380999999999',email='new@example.test',password='sentinel-password')
    r=client.post('/users',json=data)
    assert r.status_code==201
    schema_check('User',r.json)
    assert r.json['role']=='client'
    assert client.post('/users',json=data).status_code==409
    login=client.post('/sessions',json={k:data[k] for k in ('email','password')})
    assert login.status_code==200
    schema_check('Session',login.json)
    assert client.get('/bookings',headers={'Authorization':'Bearer '+login.json['accessToken']}).status_code!=401
    with app.extensions['store'].transaction() as db:
        user=db.execute('SELECT * FROM users WHERE email=?',(data['email'],)).fetchone()
        assert user['password_hash'].startswith('scrypt:')
        assert data['password'] not in json.dumps(dict(user))
        assert not db.execute('SELECT 1 FROM sessions WHERE token_hash=?',(login.json['accessToken'],)).fetchone()


@pytest.mark.req('REQ-F-005','REQ-F-007')
@pytest.mark.parametrize('payload', [{},{'name':'N','phone':'P','email':'not-email','password':'p'},
    {'name':'N','phone':'P','email':'n@example.test','password':'p','role':'administrator'},
    {'name':'','phone':'P','email':'n@example.test','password':'p'}])
def test_invalid_registration(env,payload):
    r=env[1].post('/users',json=payload)
    assert r.status_code==422
    schema_check('ApiError',r.json)


@pytest.mark.req('REQ-F-007')
@pytest.mark.parametrize('email,password', [('alice@example.test','wrong'),('absent@example.test','test-password')])
def test_bad_credentials(env,email,password):
    r=env[1].post('/sessions',json=dict(email=email,password=password))
    assert r.status_code==401
    schema_check('ApiError',r.json)


@pytest.mark.req('REQ-F-010','REQ-F-045','REQ-F-046','REQ-F-047','REQ-F-054')
@pytest.mark.parametrize('kind,payload,schema', [('services',dict(name='N',description='',price=0,durationMinutes=1),'Service'),
                                               ('masters',dict(name='M',serviceIds=[]),'Master')])
def test_crud_boundary(env,kind,payload,schema):
    client=env[1]
    assert client.post('/'+kind,json=payload).status_code==401
    assert client.post('/'+kind,json=payload,headers=auth('alice')).status_code==403
    r=client.post('/'+kind,json=payload,headers=auth())
    assert r.status_code==201
    schema_check(schema,r.json)
    path='/'+kind+'/'+r.json['id']
    r=client.patch(path,json={'active':False},headers=auth())
    assert r.status_code==200 and not r.json['active']
    assert client.patch(path,json={},headers=auth()).status_code==422
    assert client.patch(path,json={'name':'Changed'},headers=auth()).json['name']=='Changed'
    r=client.delete(path,headers=auth())
    assert r.status_code==204 and r.data==b''
    assert client.delete(path,headers=auth()).status_code==404


@pytest.mark.req('REQ-F-045','REQ-F-046')
@pytest.mark.parametrize('change',[{'durationMinutes':0},{'price':-1},{'price':0.001},{'durationMinutes':True}])
def test_invalid_service(env,change):
    r=env[1].post('/services',json=dict(name='N',description='',price=10,durationMinutes=60,**{})|change,headers=auth())
    assert r.status_code==422


@pytest.mark.req('REQ-F-047')
def test_missing_master_service(env):
    r=env[1].post('/masters',json=dict(name='N',serviceIds=['missing']),headers=auth())
    assert r.status_code==422


@pytest.mark.req('REQ-F-048','REQ-F-049','REQ-F-010')
def test_schedule_replace_and_permissions(catalog):
    client=catalog[1];path='/masters/master/schedule'
    r=client.get(path,headers=auth())
    assert r.status_code==200
    schema_check('Schedule',r.json)
    exceptions=[dict(date='2026-11-03',kind='day_off',day={'working':False})]
    r=client.patch(path,json={'exceptions':exceptions},headers=auth())
    assert r.status_code==200 and r.json['exceptions']==exceptions
    assert r.json['weekly']['monday']['working']
    assert client.patch(path,json={'exceptions':[]},headers=auth()).json['exceptions']==[]
    assert client.get(path).status_code==401
    assert client.get(path,headers=auth('alice')).status_code==403


@pytest.mark.req('REQ-F-048','REQ-F-049')
@pytest.mark.parametrize('exceptions', [
    [dict(date='2026-11-03',kind='changed_hours',day={'working':False})],
    [dict(date='2026-11-03',kind='day_off',day={'working':False})]*2,
    [dict(date='2026-11-03',kind='changed_hours',day=dict(working=True,interval={'start':'18:00','end':'09:00'}))]])
def test_invalid_schedule_rolls_back(catalog,exceptions):
    client=catalog[1];path='/masters/master/schedule'
    assert client.patch(path,json={'exceptions':exceptions},headers=auth()).status_code==422
    assert client.get(path,headers=auth()).json['exceptions']==[]


@pytest.mark.req('REQ-F-005')
def test_malformed_json(env):
    r=env[1].post('/users',data='{',content_type='application/json')
    assert r.status_code==400
    schema_check('ApiError',r.json)
