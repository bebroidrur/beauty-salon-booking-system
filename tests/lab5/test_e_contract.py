import json
from pathlib import Path
import pytest
from openapi_schema_validator import OAS30Validator
from conftest import API, resolve, auth
from test_b_bookings import created

OPERATIONS=[]
for path,methods in API['paths'].items():
    for method,op in methods.items():
        marks=[pytest.mark.req(*op['x-requirement-ids'])]
        if op['operationId']=='listSlots':
            marks.append(pytest.mark.skip(reason='BLOCKED D-03: grid origin requires Human decision; route not implemented'))
        OPERATIONS.append(pytest.param(path,method,op,id=op['operationId'],marks=marks))


@pytest.mark.contract
@pytest.mark.parametrize('path,method,op',OPERATIONS)
def test_success_contract(catalog,path,method,op):
    client=catalog[1]
    params=dict(serviceId='svc',masterId='master')
    if '{bookingId}' in path:
        params['bookingId']=created(client)['id']
    uri=path.format(**params)
    query={p['name']:p['example'] for p in op.get('parameters',[]) if p['in']=='query'}
    body=op.get('requestBody',{}).get('content',{}).get('application/json',{}).get('example')
    body=json.loads(json.dumps(body)) if body is not None else None
    if body:
        if 'serviceIds' in body:body['serviceIds']=['svc']
        if 'serviceId' in body:body['serviceId']='svc'
        if 'masterId' in body:body['masterId']='master'
        if 'startsAt' in body:body['startsAt']='2026-11-05T14:00:00+02:00'
    who='admin'
    if op['operationId']=='registerClient':
        body['email']='registered@example.test'
    if op['operationId']=='login':
        body=dict(email='alice@example.test',password='test-password')
    if op['operationId']=='createBooking':
        who='alice'
    headers=auth(who) if op['security'] else {}
    response=client.open(uri,method=method.upper(),json=body,headers=headers,query_string=query)
    status=next(s for s in op['responses'] if s.startswith('2'))
    assert response.status_code==int(status),response.json
    definition=resolve(op['responses'][status])
    if status=='204':
        assert not response.data
    else:
        assert response.content_type.startswith('application/json')
        OAS30Validator(resolve(definition['content']['application/json']['schema']),
                       format_checker=OAS30Validator.FORMAT_CHECKER).validate(response.json)


@pytest.mark.req('REQ-F-005','REQ-F-007','REQ-F-010','REQ-F-011','REQ-F-039','REQ-F-048')
@pytest.mark.contract
@pytest.mark.parametrize('case',json.loads(Path('tests/lab4/negative-inputs.json').read_text()),ids=lambda c:c['id'])
def test_existing_negative_inputs(catalog,case):
    if case['id']=='missing-slot-query':
        pytest.skip('BLOCKED D-03: listSlots not implemented')
    client=catalog[1]
    headers=case.get('headers',{}).copy()
    if 'Authorization' in headers:headers=auth()
    response=client.open(case['path'],method=case['method'],json=case.get('body'),headers=headers)
    assert response.status_code==case['status']
    OAS30Validator(resolve(API['components']['schemas']['ApiError'])).validate(response.json)


@pytest.mark.req('REQ-F-045','REQ-F-046')
@pytest.mark.parametrize('price',[0.07,0.29,4.01])
def test_valid_fractional_uah(catalog,price):
    r=catalog[1].post('/services',headers=auth(),json=dict(name='Fractional',description='',price=price,durationMinutes=1))
    assert r.status_code==201 and r.json['price']==price


@pytest.mark.req('REQ-F-051','REQ-F-053')
def test_contract_conflict_codes(catalog):
    client=catalog[1];created(client)
    assert client.delete('/services/svc',headers=auth()).json['code']=='CURRENT_BOOKINGS_EXIST'
    assert client.patch('/masters/master',json={'serviceIds':[]},headers=auth()).json['code']=='CURRENT_BOOKINGS_CONFLICT'
