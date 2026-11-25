# ЛР6 — огляд коду й документації

Дата: 2026-11-25. Гілка: `lab6`, створена з чистої `lab6-docs`, початковий
коміт `5b9dd0e2767ef321801c362026cf6f4300fbf344`. Push не виконується.

## Проаналізовані артефакти та обсяг

- `spec/SRS.md`, `spec/glossary.md`, `spec/openapi.yaml`; SRS консолідує
  64 F, 11 NF, 57 AC і 35 GWT. Базову специфікацію не редаговано.
- `docs/lab4/addendum.md`, `docs/lab5/spec-addendum-bookings.md` і матеріали
  ЛР5: README, final-report, refactoring-report. REQ-F-065-B залишається
  PROPOSED / NOT APPROVED; D-02–D-06 не закрито цією роботою.
- `salon/`: Flask adapter → Service/Bookings → SQLite Store; transactional
  outbox → SMTP worker. П'ять операцій Bookings реалізовані; listSlots відсутній.
- `tests/lab5/`: каталог/доступ, Bookings, сповіщення/логи, worker,
  контракт, числові й часові правила; `tests/network/`: loopback HTTP/SMTP.
  `pytest.ini` за замовчуванням збирає лише tests/lab5, тому обидві папки
  явно передано в команді регресії.
- `src/booking.py` — історична заготовка. `scripts/`, імпортер issues,
  `tests/lab4/` — допоміжні артефакти попередніх робіт, не frontend.

Форматування та docstrings застосовано до 15 Python-файлів `salon/` і `src/`;
14 файлів змінилися, `salon/__init__.py` вже мав належний опис.
Не додано функціональності, нових тестів або нових вимог.
Публічні сигнатури, назви, JSON-структури, SQL-літерали та повідомлення збережено.

## Середовище та команди

Фактично: Python 3.13.0, Flask 3.1.2, pytest **9.2.0**, PyYAML 6.0.2,
openapi-schema-validator 0.6.3, Ruff 0.17.6. У requirements зафіксовано pytest
8.4.2: наявний virtualenv не є точним відтворенням lock-файлу, тому результати
нижче не видаються за запуск на pytest 8.4.2.

Ruff спочатку був відсутній (`No module named ruff`). Встановлено
`.venv/bin/python -m pip install ruff`; фактичну версію 0.17.6 додано до
requirements-dev.txt і requirements-lock.txt. Перша sandbox-спроба не мала
доступу до PyPI; повторне встановлення з дозволом завершилося успішно.

Команди до змін (з кореня репозиторію):

```sh
.venv/bin/python -m pytest tests/lab5 tests/network -q
.venv/bin/python -m ruff check --no-cache --select E4,E7,E9,F,D --config 'lint.pydocstyle.convention="google"' salon src --output-format json
.venv/bin/python -m ruff check --no-cache --select E4,E7,E9,F,D --config 'lint.pydocstyle.convention="google"' --select I salon src --output-format json
.venv/bin/python -m ruff format --no-cache --line-length 79 --check salon src
.venv/bin/python -m ruff check --no-cache --select E4,E7,E9,F . --output-format json
```

Повторні `--select` у другому аудиті Ruff об'єднали набори: фактичний JSON
містив E702, D100–D107 та I001. Еквівалентний однозначний запис —
`--select E4,E7,E9,F,I,D`. До появи ruff.toml решту параметрів передано CLI.
Перший аудит без I: 57 порушень; повний цільовий аудит з I: 67.
Це два заміри одного коду, їх не потрібно додавати.

## Результати тестів

| Етап | Результат | Exit code | Час |
| --- | --- | --- | --- |
| До змін, sandbox | 97 passed, 2 failed, 2 skipped | 1 | 27.97 s |
| До змін, дозвіл на loopback | 99 passed, 2 skipped | 0 | 33.00 s |
| Після змін, дозвіл на loopback | 99 passed, 2 skipped | 0 | 28.79 s |
| Після встановлення статичного валідатора, фінальний прогін | 99 passed, 2 skipped | 0 | 29.55 s |

Обидва початкові failures — `test_real_http` і `test_real_smtp_outbox`:
`PermissionError: [Errno 1] Operation not permitted` на socket.bind;
Werkzeug додатково перетворив перший виняток у SystemExit. Це окремий
середовищний результат, він не прихований під успішним повторним прогоном.

Обидва skips до й після — у `tests/lab5/test_e_contract.py`:
`BLOCKED D-03: grid origin requires Human decision; route not implemented`
та `BLOCKED D-03: listSlots not implemented`. Нових skip/xfail немає.

## Лінтер і форматування

Цільовий набір — E4/E7/E9/F/I/D, Google docstrings. Кількість діагностик,
не кількість файлів або невдалих тестів:

| Код | До | Після | Рішення |
| --- | ---: | ---: | --- |
| D100 | 2 | 0 | Додано описи errors і історичного booking модуля |
| D101 | 6 | 0 | Описано класи |
| D102 | 19 | 0 | Описано публічні методи |
| D103 | 17 | 0 | Описано функції |
| D107 | 5 | 0 | Описано конструктори |
| E702 | 8 | 0 | Розділено оператори форматером |
| I001 | 10 | 0 | Упорядковано імпорти |
| **Разом** | **67** | **0** | Цільовий обсяг salon + src |

Formatter до: 14 files would be reformatted, 1 file already formatted (exit 1).
Після: 15 files already formatted (exit 0). Ruff після: All checks passed!
(exit 0). `--unsafe-fixes` не використовувався. Автовиправлення — лише I;
решта — formatter і ручний зміст docstrings.

Ширший аудит усього репозиторію за E4/E7/E9/F: **67 → 59** (exit 1 до й після).
Це інший набір правил/файлів, його не додавати до цільового аудиту.
Залишкові 59 діагностик належать незміненим тестам і скриптам попередніх ЛР.
Їх не приховано exclude/noqa; загальний `ruff check .` не оголошено чистим.
Для компактності ці допоміжні артефакти не переформатовано в цьому коміті.

| Файл | Залишкові коди й кількість |
| --- | --- |
| `scripts/check_lab3_scenarios.py` | E702: 2, E731: 1 |
| `scripts/check_lab4.py` | E701: 5, E702: 4 |
| `scripts/lab5_traceability.py` | E701: 1, E741: 1 |
| `tests/lab5/test_a_catalog_access.py` | E702: 2 |
| `tests/lab5/test_b_bookings.py` | E702: 15 |
| `tests/lab5/test_c_notifications_logging.py` | E702: 4 |
| `tests/lab5/test_d_mail_worker.py` | E702: 6 |
| `tests/lab5/test_e_contract.py` | E701: 5, E702: 1 |
| `tests/lab5/test_unit_rules.py` | E701: 1, E702: 1, F401: 1 |
| `tests/network/test_local_transports.py` | E701: 1, E702: 8 |

Приклади до виправлення: `salon/__main__.py:28` — E702 (налаштування
serve в одному рядку), `salon/errors.py:1` — відсутні описи модуля/класу;
`Bookings.execute` не описував транзакційну передумову, snapshot і D-guards.
Повний список діагностик відтворюється наведеними командами на початковому
коміті; результати тут отримані з фактичного JSON Ruff до/після.

## Перевірка глосарію

| Канонічне поняття | Реалізація / контракт | Висновок і рішення |
| --- | --- | --- |
| Клієнт, адміністратор | User; role client/administrator, clientId | Відповідає; User — спільний технічний контейнер двох ролей. |
| Майстер | master, masterId, Master, serviceIds | Відповідає; не є обліковим записом і не має власної ролі. |
| Послуга | service, Service schema, serviceSnapshot | Відповідає. Python-клас Service — диспетчер застосунку, а не сутність послуги: неоднозначність пояснено docstring, назву не змінено. |
| Запис | booking, Bookings, п'ять Booking operationId | Відповідає. Множина Bookings позначає набір операцій, дані запису — словник. |
| Актуальний / історичний запис | category current/history, Bookings.view | Категорія залежить від endsAt та cancelled; не лише від майбутнього startsAt, не означає факту виконання. |
| Скасований запис | status cancelled | Статус відрізняється від обчислюваної category history; нових статусів не додано. |
| Зафіксовані дані послуги | serviceSnapshot | Назва, ціна, currency, durationMinutes зберігаються; заміна послуги оновлює snapshot, саме перенесення — ні. |
| Робочий графік, виняток | schedule, weekly, exceptions, Bookings.fits | Дата винятку має пріоритет; весь інтервал мусить уміщуватися. |
| Час початку / розрахований кінець | startsAt / endsAt, instant/local, KYIV | Europe/Kyiv збережено; endsAt — розрахунок зі snapshot, не фактичне завершення роботи. |
| Конфлікт часу | Bookings.check | Перетин інтервалів майстра або клієнта; суміжність допустима, cancelled не займає часу. |
| Email-сповіщення / нагадування | mail, notifications, reminder, on_booking | mail/outbox — технічні назви доставки, не додатковий канал; D-04 лишається відкритим. |
| Деактивація / фізичне видалення | active / deleteService, deleteMaster | Не змішуються; захист актуальних записів і D-06 збережено. |
| Часовий слот | listSlots у контракті, маршрут відсутній | Відома неповнота ЛР5, не перейменування; реалізація не додавалася через D-03. |
| Запис в історичній заготовці | src.create_booking: client/service/master/time | Не відповідає повній Booking schema: немає ID, snapshot, endsAt. Позначено як історичний приклад без валідації/збереження; публічні ключі не змінено. |

CamelCase у JSON/operationId — збережена контрактна форма, не порушення
семантики глосарію. `Store`, `ApiError`, `SMTPTransport` — технічні поняття.
Публічних перейменувань не виконано; окремого погодження для них не вимагалось.

## Докази незмінності й межі

1. Порівняно AST усіх 15 Python-файлів `salon/` і `src/` із HEAD до коміту:
   після вилучення docstrings та нормалізації порядку імпортів дерева рівні.
   Імена, аргументи, гілки, виклики, константи, SQL і відповіді не змінено.
   Така перевірка не доводить відсутності будь-якого ефекту порядку імпортів;
   регресія додатково перевіряє фактичний запуск.
2. Усі публічні модулі, класи, функції, методи та конструктори цільового
   обсягу мають docstrings; перевірено AST та Ruff D. Вкладені Flask callbacks
   не є публічним Python API і не отримали штучних шаблонних описів.
3. `git diff --exit-code -- spec docs/lab4/addendum.md
   docs/lab5/spec-addendum-bookings.md` — exit 0, змін немає.
4. `.venv/bin/python scripts/check_lab4.py` спочатку завершився exit 1:
   `ModuleNotFoundError: No module named 'openapi_spec_validator'`.
   Встановлено вже передбачену залежність командою
   `.venv/bin/python -m pip install openapi-spec-validator==0.7.2` з дозволом.
   Вона змінила referencing 0.37.0 → 0.36.2, тому виконано додаткову регресію: 99 passed, 2 skipped (29.55 s).
   Повторний статичний checker: exit 0:

```text
PASS OpenAPI 3.0.3: openapi-spec-validator 0.7.2
PASS 18 unique operations; 64 real functional REQ IDs mapped; 161 examples validated
PASS 8 baseline SHA-256 hashes unchanged
PASS 75 traceability rows preserve baseline AC/GWT and lab3 D/Issue links
```

Команди внесення безпечних правок і фінальних перевірок:

```sh
.venv/bin/python -m ruff check --no-cache --select I --fix salon src
.venv/bin/python -m ruff format --no-cache salon src
.venv/bin/python -m ruff check --no-cache salon src
.venv/bin/python -m ruff format --no-cache --check salon src
.venv/bin/python -m pytest tests/lab5 tests/network -q
.venv/bin/python scripts/check_lab4.py
git diff --check
git diff --stat
```

Опис стандартів — [coding-convention](../docs/coding-convention.md);
поля й реальні приклади — [documentation-tags](../docs/documentation-tags.md).
Нових генераторів документації, функцій продукту або змін адендумів немає.
Наявні пропуски, D-guards, SMTP crash window і невиконане NF-приймання
не усуваються оформленням коду.

Фінально: `git diff --check` — exit 0; цільовий Ruff — exit 0; formatter —
15 files already formatted; дослівність прикладів документації підтверджено
зіставленням з `ast.get_docstring`. Зміни готові до коміту
`docs(lab6): standardize code and docstrings`.
