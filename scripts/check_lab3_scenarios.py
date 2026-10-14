"""Reproduce lab 3 planning scenarios, not product acceptance or PLAN-GATE.

Run from any directory. Default: verify generated scenario sections without writes.
--write-docs: replace only generated scenario sections in three planning documents.
All scheduling units are two working hours; fixed Monday reviews affect Human only.
"""
from pathlib import Path
from datetime import datetime, timedelta
import argparse
import re

ROOT = Path(__file__).resolve().parents[1]
START = datetime(2026, 10, 19, 9)
MARKER = '<!-- LAB3-GATES-SCENARIO -->'


def slot(value):
    dt = datetime.strptime(value, '%Y-%m-%d %H:%M')
    days = (dt.date() - START.date()).days
    assert dt.weekday() < 5 and dt.hour in (9, 11, 13, 15, 17)
    return sum((START + timedelta(days=i)).weekday() < 5 for i in range(days)) * 4 + (dt.hour - 9) // 2


def date(value, end=False):
    day, part = divmod(value, 4)
    if end and part == 0 and value:
        day -= 1
        part = 4
    return (START + timedelta(days=day // 5 * 7 + day % 5, hours=part * 2)).strftime('%Y-%m-%d %H:%M')


def number(value):
    return f'{value:g}'.replace('.', ',')


def read_rows():
    result = {}
    source = (ROOT / 'docs/lab3/gantt.md').read_text().split(MARKER)[0]
    for line in source.splitlines():
        if not re.match(r'^\| D-\d\d —', line):
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        key = cells[0][:4]
        times = lambda s: [slot(v) for v in re.findall(r'\d{4}-\d\d-\d\d \d\d:\d\d', s)]
        assert key not in result
        result[key] = dict(a=times(cells[4]), h=times(cells[5]), resource=cells[4][:4],
                           wait=int(float(cells[6].split('+')[0].replace(',', '.')) * 4),
                           deps=re.findall(r'D-\d\d', cells[7]))
    assert set(result) == {f'D-{i:02}' for i in range(1, 46)}
    return result


def calculate(rows, extra=False, mode='R'):
    duration, pred, resource, original = {}, {}, {}, {}
    for key, row in rows.items():
        deps = [d + ':H' for d in row['deps'] if not (mode == 'L' and key == 'D-41' and d == 'D-40')]
        if row['a']:
            node = key + ':A'
            duration[node] = row['a'][1] - row['a'][0]
            pred[node], resource[node], original[node] = deps, row['resource'], row['a'][0]
            deps = [node]
        if row['wait']:
            node = key + ':W'
            duration[node], pred[node], resource[node] = row['wait'], deps, 'W'
            deps = [node]
        node = key + ':H'
        duration[node] = row['h'][1] - row['h'][0] + int(extra and key in ('D-40', 'D-41', 'D-44'))
        pred[node], resource[node], original[node] = deps, 'H', row['h'][0]
    if extra:
        duration['G-R4:W'], pred['G-R4:W'], resource['G-R4:W'] = 4, ['D-10:H'], 'W'
        duration['G-R4:H'], pred['G-R4:H'], resource['G-R4:H'] = 2, ['D-08:H', 'D-09:H', 'G-R4:W'], 'H'
        pred['D-41:A'].append('G-R4:H')
    if mode == 'R':
        for res in ('AI-1', 'AI-2', 'H'):
            sequence = sorted((n for n in original if resource[n] == res), key=original.get)
            if extra and res == 'H':
                sequence.insert(sequence.index('D-11:H') + 1, 'G-R4:H')
            for before, after in zip(sequence, sequence[1:]):
                pred[after].append(before)
    # Ten protected Monday slots for scenario S2, validated against its ending week.
    blocked = {20 * week for week in range(10)} if extra and mode == 'R' else set()
    early, occupied, active, order = {}, {}, set(), []

    def forward(node):
        if node in early:
            return early[node]
        assert node not in active, f'Cycle at {node}'
        active.add(node)
        ready = max([forward(p)[1] for p in pred[node]] or [0])
        cursor, used = ready, []
        while len(used) < duration[node]:
            if resource[node] != 'H' or cursor not in blocked:
                used.append(cursor)
            cursor += 1
        early[node], occupied[node] = (used[0], cursor), used
        active.remove(node)
        order.append(node)
        return early[node]

    for node in duration:
        forward(node)
    finish = early['D-44:H'][1]
    assert max(e for s, e in early.values()) == finish
    successors = {n: [] for n in duration}
    for node, deps in pred.items():
        for parent in set(deps):
            successors[parent].append(node)
            assert early[parent][1] <= early[node][0]
    latest = {}
    for node in reversed(order):
        limit = min([latest[n][0] for n in successors[node]] or [finish])
        cursor, used = limit - 1, []
        while len(used) < duration[node]:
            if resource[node] != 'H' or cursor not in blocked:
                used.append(cursor)
            cursor -= 1
        latest[node] = (min(used), max(used) + 1)
        assert latest[node][0] >= early[node][0]
    # Validate backward feasibility, including all successor and calendar constraints.
    for node, deps in pred.items():
        assert all(latest[p][1] <= latest[node][0] for p in deps)
    if mode == 'R':
        for res in ('AI-1', 'AI-2', 'H'):
            slots = [t for n in duration if resource[n] == res for t in occupied[n]]
            assert len(slots) == len(set(slots)), res
            if res == 'H':
                assert not set(slots) & blocked
        if not extra:
            for key, row in rows.items():
                assert early[key + ':H'] == tuple(row['h'])
                if row['a']:
                    assert early[key + ':A'] == tuple(row['a'])
        else:
            assert (finish - 1) // 20 + 1 == len(blocked)
    human = 2 * (sum(duration[n] for n in duration if resource[n] == 'H') + len(blocked))
    weeks = [2 * (sum(t // 20 == w for n in duration if resource[n] == 'H' for t in occupied[n]) + sum(t // 20 == w for t in blocked)) for w in range(10)]
    queue = {}
    for key, row in rows.items():
        if row['wait']:
            ready = early[key + ':W'][1]
        elif row['a']:
            ready = early[key + ':A'][1]
        else:
            ready = max([early[d + ':H'][1] for d in row['deps']] or [0])
        queue[key] = (ready, early[key + ':H'][0] - ready)
    return dict(early=early, occupied=occupied, duration=duration, resource=resource,
                pred=pred, finish=finish, human=human, weeks=weeks, blocked=blocked,
                floats={n: latest[n][0] - early[n][0] for n in duration}, queue=queue)


def window(model, node):
    if node not in model['early']:
        return '—'
    s, e = model['early'][node]
    return f'{date(s)} → {date(e, True)}'


def sections(rows, base, s2, logical):
    g = ['## Сценарій S2 — додаткові Gate (пункт 17)', '',
         'Базовий сценарій B0 вище збережено. S2 застосовує погоджений користувачем порядок із [additional-gates.md](additional-gates.md). Погоджено планування контрольних точок, не їх проходження. Умовний кінець — **21.12.2026 13:00**, 224 години Human. Невідомі NF-роботи й підготовка пакета G-R4 не включені; D-41–D-44 та G-R4 залишаються умовними резервами.', '',
         'G-R4 стоїть у Human-черзі після D-11 і перед D-14:H, має 4 години H та 1 робочий день W після D-10. Готовність NF-пакета наприкінці D-10 — припущення сценарію. G-R4 → D-41 є логічною передумовою; G-R4 → D-14:H є лише ресурсним порядком. G-R1/G-R2 вбудовано без додаткового часу; G-R3 додає 2 години D-40:H, G-R6 — по 2 години D-41:H і D-44:H. Десять G-R5 займають понеділки 09:00–11:00; H-сесія може перериватися на цей слот. Ночі/вихідні всередині оболонки вікна не є роботою.', '',
         '| D-ID | AI-потік і вікно S2 | Human-вікно S2 | Активно AI/H, год | W / Q, роб. дні |',
         '| --- | --- | --- | --- | --- |']
    for key, row in rows.items():
        an, hn = key + ':A', key + ':H'
        ai = (row['resource'] + ': ' + window(s2, an)) if row['a'] else '—'
        flag = ' †' if key in ('D-41', 'D-42', 'D-43', 'D-44') else ''
        g.append(f"| {key}{flag} | {ai} | {window(s2, hn)} | {s2['duration'].get(an, 0)*2} / {s2['duration'][hn]*2} | {number(row['wait']/4)} / {number(s2['queue'][key][1]/4)} |")
    g += ['', '† — умовний резерв. Q до першого старту H не включає переривання вже розпочатої H-сесії під час G-R5.', '',
          '| Окрема контрольна точка | Human-вікно S2 | Активно, год |', '| --- | --- | --- |',
          f"| G-R4 † | {window(s2, 'G-R4:H')} | 4 |"]
    for i, t in enumerate(sorted(s2['blocked']), 1):
        g.append(f'| G-R5, сесія {i} | {date(t)} → {date(t+1, True)} | 2 |')
    g += ['', '### Діаграма S2', '', 'Кожна неперервна частина H виділена окремо, щоб G-R5 не виглядав як накладання. Діаграма показує календарні оболонки; точний активний час задається таблицею та 2-годинною моделлю.', '', '```mermaid', 'gantt', '    title S2 — додаткові Gate, NF умовно', '    dateFormat YYYY-MM-DD HH:mm', '    axisFormat %d.%m']
    for res in ('AI-1', 'AI-2', 'H'):
        g.append('    section ' + ('Human' if res == 'H' else res))
        for node in sorted((n for n in s2['early'] if s2['resource'][n] == res), key=lambda n:s2['early'][n]):
            parts = []
            for t in s2['occupied'][node]:
                if parts and t == parts[-1][-1] + 1:
                    parts[-1].append(t)
                else:
                    parts.append([t])
            for j, part in enumerate(parts):
                label = node.replace(':', ' ')
                if node.startswith(('D-41', 'D-42', 'D-43', 'D-44', 'G-R4')):
                    label += ' УМОВНО'
                ident = node.replace('-', '').replace(':', '').lower() + str(j)
                g.append(f'    {label} :{ident}, {date(part[0])}, {date(part[-1]+1, True)}')
    g.append('    section G-R5 Human')
    for i, t in enumerate(sorted(s2['blocked'])):
        g.append(f'    G-R5 {i+1} :gr5s{i}, {date(t)}, {date(t+1, True)}')
    g += ['```', '', 'Передумови D-тікетів успадковано з базової таблиці; додано лише описані правила S2. Усі 45 D-тікетів збережено, нових D-ID немає. Сумарний активний бюджет S2 — **64,25 людино-дня**: 36,25 AI + 28 Human; це не календарні 45,5 дня. Повне приймання NF не має підтвердженої дати.']

    c = ['## Сценарій S2 — перерахунок критичного шляху (пункт 17)', '',
         'Вище наведено незмінні результати B0. Для S2 відтворено прямий та зворотний проходи з подовженням D-40:H/D-41:H/D-44:H, окремим G-R4 і календарними слотами G-R5. Повна NF-гілка не оцінена.', '',
         '| Модель | B0, роб. дні | S2, роб. дні | Межі |', '| --- | --- | --- | --- |',
         f"| L — логічна за планом | 31,75 | {number(logical['L']['finish']/4)} | Без обмеження виконавців і G-R5; додано відомий G-R4 та збільшені H. |",
         f"| G — логічна з D-40 → D-41 | 34,75 | {number(logical['G']['finish']/4)} | Планова послідовність Ганта, без ресурсної черги. |",
         f"| R — ресурсний календар | 42,5 | {number(s2['finish']/4)} | Фіксований порядок двох AI та одного Human, десять G-R5. |", '',
         'У R G-R5 є фіксованими недоступними слотами Human, а не продуктовими залежностями. Прямий прохід пропускає ці слоти для H. Зворотний прохід від кінця 21.12 13:00 для кожної частини шукає найпізніші доступні слоти до найранішого LS наступників; TF = LS − ES у 2-годинному робочому календарі. Для A/W календар G-R5 не застосовується. Це резерв зсуву старту при фіксованих контрольних слотах, а не дозвіл одночасно витратити всі резерви.', '',
         '### Резерви всіх D-тікетів у S2', '', '| D-ID | TF L | TF G | R-A | R-H | R-W | Нульові частини R |', '| --- | --- | --- | --- | --- | --- | --- |']
    zero = []
    for key in rows:
        phases = [p for p in 'AHW' if key + ':' + p in s2['floats']]
        zeros = [p for p in phases if s2['floats'][key + ':' + p] == 0]
        if zeros:
            zero.append(key)
        vals = [number(logical[m]['floats'][key+':H']/4) for m in ('L','G')]
        vals += [number(s2['floats'][key+':'+p]/4) if p in phases else '—' for p in 'AHW']
        c.append('| ' + key + (' †' if key in ('D-41','D-42','D-43','D-44') else '') + ' | ' + ' | '.join(vals) + ' | ' + (', '.join(zeros) or '—') + ' |')
    route = ['D-44:H']
    while True:
        candidates = [n for n in s2['pred'][route[-1]] if s2['floats'][n] == 0]
        if not candidates:
            break
        route.append(max(candidates, key=lambda n: s2['early'][n][1]))
    route.reverse()
    c += ['', 'Один ресурсно-критичний маршрут нульових частин (між ними враховано календар G-R5):', '', '```text', ' → '.join(route), '```']
    c += ['', 'TF L/G наведено за кінцевою H-частиною тікета; R — окремо для A/H/W. † означає резерв умовної завершальної роботи, а не доведеного повного приймання.', '',
          f"**{len(zero)} із 45 D-тікетів** містять нульову частину R у S2: " + ', '.join(zero) + '.', '',
          f"G-R4: ресурсний TF H = {number(s2['floats']['G-R4:H']/4)} дня, TF W = {number(s2['floats']['G-R4:W']/4)} дня. G-R5 має фіксовані дати: його CPM-резерв не визначається цією моделлю, зміна дат означає новий календар.", '',
          'Ресурсна послідовність містить D-11:H → G-R4:H → D-14:H. Далі контроль залежного ланцюга D-19 → D-21 → D-23 → D-27 → D-29 → D-33 → D-37 → D-39 → D-40 залишається потрібним; його нульові частини див. у таблиці. Розгалуження через D-12/D-13/D-34 перераховано, а не успадковано з B0. Календар G-R5 може поглинати окремий зсув до захищеного слота, тому кількість нульових частин і чутливість не зобов’язані збігатися з B0.', '',
          'Загальна довжина R зростає на 3 робочі дні до **45,5**, кінець — **21.12.2026 13:00**. Це найраніше завершення відомого графа за заданого порядку та календаря, не оптимізація черги і не гарантія повного NF-приймання. Додавання невідомих NF-робіт, підготовки G-R4, повторних рецензій або відсутності Human потребує нового розрахунку.']
    h = ['## Сценарій S2 — ресурсний план із додатковими Gate (пункт 17)', '',
         'B0 і окремий сценарій недоступності S1 вище збережено. S2 не включає відсутність Human 27.10 із S1. Тут 45 початкових H-сесій, одна G-R4 та десять G-R5: **56 сесій**, без дублювання вбудованих перевірок. 194 + 4 G-R4 + 20 G-R5 + 2 D-40 + 2 D-41 + 2 D-44 = **224 години**. D-41–D-44 займають 32 умовні години замість 28; окремий G-R4 також умовний.', '',
         '| Тиждень від | B0, год | S2, год | Місткість, год | S2, % |', '| --- | --- | --- | --- | --- |']
    for i, (b,s) in enumerate(zip(base['weeks'],s2['weeks'])):
        h.append(f'| {date(i*20)[:10]} | {b} | {s} | 40 | {number(s/40*100)} |')
    h += ['', 'B0: 194/360 = 53,89% за його дев’ять повних тижнів. S2: 224/400 = **56%** за десять повних тижнів. У перші три тижні S2 — 114/120 = **95%**; 02–06.11 — 100%. Вільні пізні години не усувають ранню чергу. Місткість повних тижнів не дорівнює доступному часу до середини останнього дня.', '',
          '### Очікування до Human у S2', '', '| D-ID | H, год | W, роб. дні | Q до старту, роб. дні | Переривання H через G-R5, год |', '| --- | --- | --- | --- | --- |']
    interrupted = 0
    for key, row in rows.items():
        n=key+':H'; a,b=s2['early'][n]
        gap=(b-a-s2['duration'][n])*2;interrupted+=gap
        h.append(f"| {key} | {s2['duration'][n]*2} | {number(row['wait']/4)} | {number(s2['queue'][key][1]/4)} | {gap} |")
    totalq=sum(v[1] for v in s2['queue'].values())/4
    peak=max(sum(ready<=t<s2['early'][k+':H'][0] for k,(ready,q) in s2['queue'].items()) for t in range(s2['finish']))
    h += ['', f'Для 45 D-сесій: Q = **{number(totalq)} задачо-дня**, W = 11,5 задачо-дня; пік черги готових, але ще не розпочатих D-пакетів — **{peak}**. Переривання вже розпочатих H-сесій через G-R5 — **{interrupted} годин**; вони не входять до Q чи активного H. Ці суми не додаються до календарного строку.', '',
          f"Окремо G-R4: 4 години H, 1 день W; Q після W до першого старту = {number((s2['early']['G-R4:H'][0]-s2['early']['G-R4:W'][1])/4)} дня. G-R5 — десять фіксованих сесій по 2 години без нормативної добової паузи. Вимір Q і піку вище охоплює лише 45 D-пакетів для зіставлення з B0.", '',
          'Резерв 6–8 годин на тиждень не оголошено створеним: потрібне окреме перепланування, якщо Human його затвердить як обов’язковий. Після додаткового тижня виконання додається ще один G-R5; нові NF-роботи та повторні Gate у 224 години не включені. Умовний кінець S2 — **21.12.2026 13:00**, не повний PASS.']
    return {'gantt.md':'\n'.join(g), 'critical-path.md':'\n'.join(c), 'human-review-capacity.md':'\n'.join(h)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-docs', action='store_true')
    args=parser.parse_args()
    rows=read_rows()
    base=calculate(rows)
    s2=calculate(rows, True)
    logical={m:calculate(rows, True, m) for m in ('L','G')}
    assert calculate(rows, False, 'L')['finish']==127
    assert calculate(rows, False, 'G')['finish']==139
    assert base['finish']==170 and base['human']==194
    assert s2['finish']==182 and s2['human']==224
    assert s2['weeks']==[38,36,40,26,12,20,12,12,24,4]
    assert sum(s2['weeks'])==224 and max(s2['weeks'])<=40
    for name, section in sections(rows,base,s2,logical).items():
        path=ROOT/'docs/lab3'/name
        old=path.read_text()
        expected=old.split(MARKER)[0].rstrip()+'\n\n'+MARKER+'\n\n'+section+'\n'
        if args.write_docs:
            path.write_text(expected)
        else:
            assert old==expected, f'Stale generated section: {path}'
    # Source and artifact consistency beyond the generated schedule.
    draft=(ROOT/'docs/lab3/decomposition-draft.md').read_text()
    assert set(re.findall(r'^### (D-\d{2}) ',draft,re.M))==set(rows)
    srs=(ROOT/'spec/SRS.md').read_text()
    known_req=set(re.findall(r'REQ-(?:NF|F)-\d{3}',srs))
    risk=(ROOT/'docs/lab3/risk-register.md').read_text()
    known_risk=set(re.findall(r'\bR-\d{2}\b',risk))
    for name in ('implementation-plan.md','gantt.md','critical-path.md','human-review-capacity.md','risk-register.md','additional-gates.md'):
        path=ROOT/'docs/lab3'/name
        text=path.read_text()
        assert set(re.findall(r'REQ-(?:NF|F)-\d{3}',text))<=known_req, name
        assert set(re.findall(r'\bD-\d{2}\b',text))<=set(rows), name
        assert set(re.findall(r'\bR-\d{2}\b',text))<=known_risk, name
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if not link.startswith(('https:', 'http:', '#')):
                assert (path.parent/link.split('#')[0]).exists(), (name,link)
        for block in re.split(r'\n\s*\n',text):
            table=[line for line in block.splitlines() if line.startswith('|')]
            if table:
                assert len({line.count('|') for line in table})==1, (name,table[0])
    riskrows=[r.split('|')[1:-1] for r in risk.splitlines() if re.match(r'^\| R-\d{2} \|',r)]
    assessment=[r for r in riskrows if len(r)==8]
    assert len(assessment)==16
    for r in assessment:
        assert int(r[3])*int(r[4])==int(re.search(r'\d+',r[5])[0])
    gates=(ROOT/'docs/lab3/additional-gates.md').read_text()
    assert set(re.findall(r'^### (G-R\d)',gates,re.M))=={f'G-R{i}' for i in range(1,7)}
    print('PASS: six source documents: D/REQ/risk IDs, local links, Markdown tables; 16 risk scores and six Gate passports.')
    print('PASS: B0 reproduces all 45 published AI/Human windows; L=31.75, G=34.75, R=42.5 workdays.')
    print('PASS: S2 Human=224 hours; R=45.5 workdays; end=2026-12-21 13:00 Europe/Kyiv.')
    print('PASS: S2 L='+str(logical['L']['finish']/4)+'; G='+str(logical['G']['finish']/4)+'. Forward/backward passes feasible.')
    print('PASS: dependencies acyclic; per-resource slots disjoint; ten Monday G-R5; weekly Human <=40 hours.')
    print('PASS: all generated scenario tables and diagram match model.')
    print('LIMIT: unknown NF work and G-R4 preparation excluded; no Gate or product acceptance performed.')


if __name__=='__main__':
    main()
