"""Validate the design and, optionally, exercise a running Prism mock; no server logic."""
import argparse
import hashlib
import json
import pathlib
import re
import urllib.error
import urllib.parse
import urllib.request
import yaml
from openapi_spec_validator import validate_spec
from openapi_schema_validator import OAS30Validator

ROOT = pathlib.Path(__file__).resolve().parents[1]
API = yaml.safe_load((ROOT / 'spec/openapi.yaml').read_text())


def resolve(value):
    if isinstance(value, dict):
        if '$ref' in value:
            assert value['$ref'].startswith('#/'), 'External reference not supported'
            target = API
            for part in value['$ref'][2:].split('/'):
                target = target[part]
            return resolve(target)
        return {k: resolve(v) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(v) for v in value]
    return value


def validate(schema, value):
    OAS30Validator(resolve(schema), format_checker=OAS30Validator.FORMAT_CHECKER).validate(value)


def operations():
    for path, methods in API['paths'].items():
        for method, operation in methods.items():
            yield path, method, operation


def static_checks():
    validate_spec(API)
    print('PASS OpenAPI 3.0.3: openapi-spec-validator 0.7.2')
    known = set(re.findall(r'^### (REQ-F-\d+)', (ROOT/'spec/functional-requirements.md').read_text(), re.M))
    seen, mapped, count = set(), set(), 0
    for path, method, op in operations():
        assert op['operationId'] not in seen
        seen.add(op['operationId'])
        assert op['x-requirement-ids'] and set(op['x-requirement-ids']) <= known
        assert set(op['x-roles']) <= {'public', 'client', 'administrator'}
        assert bool(op['security']) == ('public' not in op['x-roles'])
        mapped.update(op['x-requirement-ids'])
        assert set(re.findall(r'{(\w+)}', path)) == {p['name'] for p in op.get('parameters', []) if p['in']=='path'}
        for p in op.get('parameters', []):
            validate(p['schema'], p['example']); count += 1
        if 'requestBody' in op:
            media=op['requestBody']['content']['application/json']
            validate(media['schema'],media['example']); count += 1
        for status, response in op['responses'].items():
            response=resolve(response)
            if status=='204':
                assert 'content' not in response
                continue
            media=response['content']['application/json']
            if int(status) >= 400:
                assert media['schema'] == resolve(API['components']['schemas']['ApiError'])
            for example in media['examples'].values():
                validate(media['schema'], example['value']); count += 1
    assert mapped == known, known-mapped
    for schema in API['components']['schemas'].values():
        if 'example' in schema:
            validate(schema,schema['example']); count += 1
    print(f'PASS {len(seen)} unique operations; 64 real functional REQ IDs mapped; {count} examples validated')
    baseline=(ROOT/'logs/spec-gate.md').read_text()
    hashes=re.findall(r'\| (spec/[^ |]+) \| `([a-f0-9]{64})`',baseline)
    assert len(hashes)==8
    for name, expected in hashes:
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected, name
    print('PASS 8 baseline SHA-256 hashes unchanged')
    def rows(path):
        return {cells[0]: cells for line in (ROOT/path).read_text().splitlines()
                if re.match(r'\| REQ-(?:F|NF)-\d{3} \|', line)
                for cells in [[v.strip() for v in line.strip('|').split('|')]]}
    original = rows('spec/traceability-matrix.md')
    previous = rows('docs/lab3/decomposition-draft.md')
    extended = rows('docs/lab4/traceability-matrix.md')
    assert original.keys() == extended.keys() and len(extended) == 75
    for rid, row in extended.items():
        assert row[:4] == original[rid][:4]
        assert row[4:7] == previous[rid][1:4]
        expected = [op['operationId'] for _, _, op in operations()
                    if rid in op['x-requirement-ids']]
        assert row[7] == (', '.join(expected) or '—')
    print('PASS 75 traceability rows preserve baseline AC/GWT and lab3 D/Issue links')


def http(base, method, path, body=None, headers=None):
    request=urllib.request.Request(base+path, data=None if body is None else json.dumps(body).encode(), method=method.upper(), headers={'Content-Type':'application/json', **(headers or {})})
    try:
        response=urllib.request.urlopen(request, timeout=10)
    except urllib.error.HTTPError as e:
        response=e
    raw=response.read()
    return response.status, {k.lower(): v for k, v in response.headers.items()}, json.loads(raw) if raw else None


def mock_checks(base):
    count=0
    successes=0
    for path, method, op in operations():
        uri=path
        query={}
        for p in op.get('parameters', []):
            if p['in']=='path': uri=uri.replace('{'+p['name']+'}',str(p['example']))
            if p['in']=='query': query[p['name']]=p['example']
        if query: uri+='?'+urllib.parse.urlencode(query)
        body=op.get('requestBody',{}).get('content',{}).get('application/json',{}).get('example')
        headers={'Authorization':'Bearer mock-token'} if op['security'] else {}
        expected = next(iter(op['responses']))
        response = resolve(op['responses'][expected])
        status, response_headers, value = http(base, method, uri, body, headers)
        assert status == int(expected), (op['operationId'], status, value)
        if 'content' in response:
            assert response_headers.get('content-type','').startswith('application/json')
            validate(response['content']['application/json']['schema'], value)
        else:
            assert value is None
        print(f'PASS default {method.upper()} {uri} -> {status} (no Prefer header)')
        successes += 1
        for expected, response in op['responses'].items():
            response=resolve(response)
            media=response.get('content',{}).get('application/json')
            ex_name=next(iter(media['examples'])) if media else None
            h={**headers,'Prefer':f'code={expected}'+(f', example={ex_name}' if ex_name else '')}
            status, response_headers, value=http(base,method,uri,body,h)
            assert status==int(expected),(op['operationId'],expected,status,value)
            if media:
                assert response_headers.get('content-type','').startswith('application/json')
                validate(media['schema'],value)
                assert value==media['examples'][ex_name]['value'], (op['operationId'],value)
            else: assert value is None
            print(f'PASS replay {method.upper()} {uri} -> {status} ({op["operationId"]})')
            count+=1
    # Malformed input is submitted without Prefer: this checks actual mock validation.
    cases=json.loads((ROOT/'tests/lab4/negative-inputs.json').read_text())
    for case in cases:
        status, headers, value=http(base,case['method'],case['path'],case.get('body'),case.get('headers'))
        assert status==case['status'],(case['id'],status,value)
        assert headers.get('content-type','').startswith('application/json')
        validate(API['components']['schemas']['ApiError'], value)
        print(f'PASS mock-input {case["id"]}: {status}; ApiError {value["code"]} (no Prefer header)')
    print(f'PASS {successes} default successes; {count} contract response replays; {len(cases)} real mock input rejections. Business rules NOT tested.')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--mock', help='Running Prism base URL, e.g. http://127.0.0.1:4010')
    args=parser.parse_args()
    static_checks()
    if args.mock: mock_checks(args.mock)
