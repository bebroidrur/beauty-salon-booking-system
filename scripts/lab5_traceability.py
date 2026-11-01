"""Build a requirement/test evidence index from an actual JUnit report."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
report=ET.parse(root/'logs/lab5/final/verification/junit.xml')
links={}
for case in report.iter('testcase'):
    props={p.attrib['name']:p.attrib['value'] for p in case.findall('./properties/property')}
    outcome='SKIPPED' if case.find('skipped') is not None else 'FAILED' if case.find('failure') is not None or case.find('error') is not None else 'PASSED'
    node=case.attrib['classname']+'::'+case.attrib['name']
    level='contract' if case.attrib['name'].startswith(('test_success_contract','test_existing_negative_inputs')) else 'behavior'
    for rid in filter(None,props.get('requirements','').split(',')):
        links.setdefault(rid,[]).append((node,outcome,level))
rows=[]
for line in (root/'spec/traceability-matrix.md').read_text().splitlines():
    if re.match(r'\| REQ-(?:F|NF)-\d{3} \|',line):
        cells=[c.strip() for c in line.strip('|').split('|')]
        rows.append(cells[:4])
lines=['# ЛР5 — індекс простежуваності за фактичним JUnit','',
       'Джерело: `logs/lab5/final/verification/junit.xml`. Згенеровано `scripts/lab5_traceability.py`. Baseline AC/GWT перенесено без нових ID. Позначка PASSED означає результат пов’язаного тесту, **не повне приймання вимоги або всіх її AC/GWT**. Контрактний smoke перевіряє форму відповіді, не всі побічні ефекти. BDD-маркери позначають пов’язаний сценарій; повний Then може потребувати сукупності тестів, а відкриті випадки залишаються BLOCKED.','',
       'Код: F-001–003/005–007/010/045–049 — `salon/service.py`, `salon/auth.py`, `salon/contract.py`; F-008–044/050–055 — `salon/booking_service.py`; F-056–064 — `salon/notifications.py`, `salon/mail_worker.py`; NF-004/006 — password hashing, `salon/events.py`; сховище — `salon/store.py`. F-004/018 (слоти) не реалізовані. F-021, F-040/043, F-053–055, F-060/063 мають обмеження D-02–D-06; деталі в README. Решта NF не приймались.','',
       '| REQ | Назва | Прямі AC baseline | Прямі GWT baseline | Поведінкові тести: passed / failed / skipped | Контрактні тести: passed / failed / skipped |','| --- | --- | --- | --- | --- | --- |']
for rid,title,ac,gwt in rows:
    def counts(level):
        cases=[s for _,s,l in links.get(rid,[]) if l==level]
        return ' / '.join(str(cases.count(s)) for s in ('PASSED','FAILED','SKIPPED')) if cases else '—'
    lines.append(f'| {rid} | {title} | {ac} | {gwt} | {counts("behavior")} | {counts("contract")} |')
lines+=['','## Точні testcase ID з JUnit','']
for rid,_,_,_ in rows:
    lines+=['### '+rid,'']
    cases=links.get(rid,[])
    if not cases:lines+=['Виконаних пов’язаних тестів немає.','']
    else:
        lines += [f'- `{node}` — {state}, {level}.' for node,state,level in cases]
        lines.append('')
(root/'docs/lab5/traceability.md').write_text('\n'.join(lines)+'\n')
print(f'Indexed {len(rows)} baseline requirements and {sum(1 for _ in report.iter("testcase"))} actual test cases; not acceptance coverage.')
