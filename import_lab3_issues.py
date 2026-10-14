#!/usr/bin/env python3
"""Import Lab 3 decomposition proposals into GitHub Issues using GitHub CLI.
Run from repository root. Preview by default; use --apply to create issues.
"""
import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = 'bebroidrur/beauty-salon-booking-system'
HEADING = re.compile(r'^### (D-\d{2}) — (.+)$', re.M)
TYPE = re.compile(r'^- \*\*Тип:\*\* ([^\n]+)', re.M)


def gh(*args):
    p = subprocess.run(['gh', *args], text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(f"gh {' '.join(args)} failed:\n{p.stderr.strip()}")
    return p.stdout


def parse(path):
    content = path.read_text(encoding='utf-8')
    matches = list(HEADING.finditer(content))
    if len(matches) != 45:
        raise ValueError(f'Expected 45 ticket headings; found {len(matches)}')
    tickets = []
    for i, match in enumerate(matches):
        end = matches[i+1].start() if i+1 < len(matches) else content.find('\n## Поточна робоча матриця', match.end())
        if end == -1:
            end = len(content)
        body = content[match.end():end].strip()
        kind = TYPE.search(body)
        if not kind:
            raise ValueError(f'Missing type in {match.group(1)}')
        tickets.append(dict(id=match.group(1), title=match.group(2).strip(), type=kind.group(1).strip().rstrip('.'), body=body))
    if [t['id'] for t in tickets] != [f'D-{i:02d}' for i in range(1, 46)]:
        raise ValueError('Unexpected ticket IDs or ordering')
    return tickets


def existing_issues():
    # --state all includes closed issues, to avoid duplicate creation.
    items = json.loads(gh('issue', 'list', '--repo', REPO, '--state', 'all', '--limit', '1000', '--json', 'number,title,url'))
    result = {}
    for item in items:
        match = re.match(r'^\[(D-\d{2})\]\s', item['title'])
        if match:
            if match.group(1) in result:
                raise ValueError(f'Duplicate existing issues for {match.group(1)}')
            result[match.group(1)] = item
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--file', default='docs/lab3/decomposition-draft.md')
    p.add_argument('--apply', action='store_true', help='Actually create missing issues')
    args = p.parse_args()
    tickets = parse(Path(args.file))
    print(f'Parsed {len(tickets)} tickets from {args.file}')
    gh('auth', 'status')
    labels = {x['name'] for x in json.loads(gh('label', 'list', '--repo', REPO, '--limit', '1000', '--json', 'name'))}
    missing = sorted({t['type'] for t in tickets} - labels)
    if missing:
        raise RuntimeError(f'Missing GitHub labels: {missing}. Create them first.')
    existing = existing_issues()
    print(f'Found {len(existing)} existing D-issues; {len(tickets)-sum(t["id"] in existing for t in tickets)} to create')
    for ticket in tickets:
        title = f'[{ticket["id"]}] {ticket["title"]}'
        if ticket['id'] in existing:
            print(f'SKIP {ticket["id"]}: {existing[ticket["id"]]["url"]}')
        elif not args.apply:
            print(f'PREVIEW {title} [{ticket["type"]}]')
        else:
            body = (f'**Локальний ID плану:** {ticket["id"]}\n'
                    '**Статус:** заплановано; роботу не розпочато.\n\n'
                    f'{ticket["body"]}\n\n'
                    '> Залежності D-XX є посиланнями на локальні ID; відповідність GitHub Issue # зберігається в issue-mapping.csv.\n')
            url = gh('issue', 'create', '--repo', REPO, '--title', title,
                     '--label', ticket['type'], '--body', body).strip()
            number = re.search(r'/issues/(\d+)$', url)
            if not number:
                raise RuntimeError(f'Unexpected issue URL: {url}')
            existing[ticket['id']] = dict(number=int(number.group(1)), title=title, url=url)
            print(f'CREATED {ticket["id"]}: {url}')
    if args.apply:
        out = Path('docs/lab3/issue-mapping.csv')
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open('w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['D-ID', 'GitHub Issue #', 'GitHub URL', 'Type', 'Title'])
            for t in tickets:
                x = existing.get(t['id'])
                writer.writerow([t['id'], x['number'] if x else '', x['url'] if x else '', t['type'], t['title']])
        print(f'Mapping saved to {out}')
    else:
        print('Preview only: no GitHub issues created. Use --apply after checking.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
