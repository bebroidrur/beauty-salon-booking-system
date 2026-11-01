from datetime import datetime
import pytest
from jsonschema.exceptions import ValidationError
from salon.contract import validate
from salon.time_rules import instant,local
from salon.booking_service import Bookings

pytestmark=pytest.mark.unit


@pytest.mark.req('REQ-F-045')
@pytest.mark.parametrize('value,valid',[(0,True),(0.07,True),(0.29,True),(4.01,True),(0.001,False),(-1,False)])
def test_decimal_rule(value,valid):
    schema=dict(type='number',minimum=0,multipleOf=0.01)
    if valid:
        validate(schema,value)
    else:
        with pytest.raises(ValidationError):validate(schema,value)


@pytest.mark.req('REQ-F-017')
def test_offset_conversion_same_instant():
    assert instant('2026-11-04T12:00:00Z')==instant('2026-11-04T14:00:00+02:00')
    assert local(instant('2026-11-04T12:00:00Z'))=='2026-11-04T14:00:00+02:00'


@pytest.mark.req('REQ-F-022','REQ-F-049')
@pytest.mark.bdd('GWT-008','GWT-009','GWT-027')
@pytest.mark.parametrize('start,end,expected',[('17:00','18:00',True),('17:30','18:30',False),('08:30','09:30',False)])
def test_work_interval_rule(start,end,expected):
    schedule=dict(weekly={'wednesday':dict(working=True,interval=dict(start='09:00',end='18:00'))},exceptions=[])
    begin=instant('2026-11-04T'+start+':00+02:00');finish=instant('2026-11-04T'+end+':00+02:00')
    assert Bookings.fits(schedule,begin,finish)==expected
    schedule['exceptions']=[dict(date='2026-11-04',day=dict(working=False))]
    assert not Bookings.fits(schedule,begin,finish)
