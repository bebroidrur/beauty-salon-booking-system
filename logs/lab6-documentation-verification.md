# ЛР6 — перевірка документації проти реалізації

Дата: 2026-11-25. Коміт попереднього етапу: `3be0a2c`. Цей звіт містить
фактичні результати пунктів 8–10. Перевірки виконувалися у контрольній копії
репозиторію `/var/folders/.../beauty-lab6-verify-np3f31u1` з новою `.venv` і
новою `runtime/salon.sqlite3`; робоче середовище та дані цього репозиторію не
видалялися й не використовувалися для стану перевірки.

Статуси: `PASS` — команда/елемент підтверджені; `FAIL` — невідповідність;
`NOT VERIFIED` — немає безпечного доказу; `N/A` — пункт не застосовується.

## 1. Перевірка README

| Команда або інструкція | Очікуваний результат | Фактичний результат | Статус | Доказ |
| --- | --- | --- | --- | --- |
| `python3 -m venv .venv` | Створено ізольоване Python-середовище | Exit 0, Python 3.13.0 | PASS | R01 у контрольному `verification-results.json` |
| `.venv/bin/python -m pip install -r requirements-lock.txt` | Встановлено runtime/test залежності | Exit 0; pins встановлено, зокрема Flask 3.1.2, pytest 8.4.2, Ruff 0.17.6 | PASS | R02; 7.79 s |
| `.venv/bin/python -m pip install -r requirements-docs.txt` | Встановлено docs-залежності | Exit 0; Sphinx 8.2.3, MyST 4.0.1 і транзитивні залежності встановлено | PASS | R03; 5.40 s |
| `.venv/bin/python -m salon --help` | Показано CLI `serve`, `create-admin`, `worker` | Exit 0, усі три підкоманди присутні | PASS | R04 |
| `create-admin` з чотирма рядками stdin | Створено адміністратора | Exit 0, `Administrator created.` | PASS | R05-admin |
| Повторний `create-admin` з тим самим email | Помилка унікальності | Exit 1, `sqlite3.IntegrityError: UNIQUE constraint failed: users.email` | PASS | R05-duplicate; документація попереджає про помилку |
| `serve --host 127.0.0.1 --port <free>` | Локальний HTTP сервер працює | Процес працював; `GET /services` повернув 200 `{items: []}`; завершено SIGINT | PASS | R06-serve, R06-stop |
| `GET /` за README: UI не заявлено | Немає графічного інтерфейсу | 404 `INVALID_REQUEST`; API доступний через `/services` | PASS | U00-no-ui |
| `worker --once` без SMTP-змінних | Запуск неуспішний через відсутню конфігурацію | Exit 1; змінні SMTP відсутні, зовнішній лист не надсилався | PASS | R07-worker-no-env |
| `worker --once` з локальним SMTP, STARTTLS=0 | Due outbox доставлено локальному sink | Exit 0; sink прийняв повідомлення, SQLite state оновлено | PASS | R08-worker-once, U19-mail |
| `worker` з локальним SMTP | Повторна обробка щосекунди до Ctrl+C | Процес працював, прийняв нове повідомлення, SIGINT завершив його | PASS | U20-mail, R09-worker-loop, R09-stop |
| failed job і повторний `worker --once` | Автоматичного retry немає | Failed count до/після другого запуску однаковий | PASS | R10-worker-failed, R10-worker-no-retry, U21-no-retry |
| `.env` автоматично не завантажується | CLI не бере SMTP з `.env` | Створений у контрольній копії `.env` без змінних process environment не допоміг; команда завершилася помилкою | PASS | R07-worker-no-env |
| `.venv/bin/python -m pytest tests/lab5 -q` | Unit/contract/integration набір проходить | 99 passed, 2 skipped, exit 0, 46.05 s | PASS | R11 |
| `.venv/bin/python scripts/check_lab4.py` | OpenAPI і traceability static checks проходять | OpenAPI 3.0.3, 18 операцій, 161 приклад, 8 hashes, 75 rows; exit 0 | PASS | R12; 2.15 s |
| `.venv/bin/python -m ruff check --no-cache salon src` | Цільовий lint чистий | Exit 0 | PASS | R13; 0 diagnostics |
| `.venv/bin/python -m ruff format --no-cache --check salon src` | Файли відформатовані | Exit 0 | PASS | R14; 15 files already formatted |
| Sphinx HTML команда з README | HTML створено без warning | Exit 0, `build succeeded`, 0 warnings | PASS | R15; контрольний `docs/generated/html` |
| Sphinx singlehtml команда з README | singlehtml створено без warning | Exit 0, `build succeeded`, 0 warnings | PASS | R16; контрольний `docs/generated/singlehtml` |
| Network-тести з README | Loopback HTTP/SMTP smoke | Окремо у попередньому етапі: 99 passed, 2 skipped з дозволом bind; зовнішня доставка не перевірялася | PASS | `logs/lab6-code-review.md`; локальний sink U19 |

Перший запуск R02 у sandbox був `FAIL` середовища: DNS/PyPI недоступний,
exit 1 (`No matching distribution found`). Повторний R02 з дозволом мережі
успішний; це не дефект README. Транзитивні docs pins не є повним lock-файлом,
що README прямо зазначає.

## 2. Перевірка Python API-документації

Публічні символи взято AST та `inspect.signature` із 15 модулів, імпортованих
з фактичного коду. Усі 47 символів мають autodoc anchor у згенерованому
`docs/generated/{html,singlehtml}`. Python probes дали exit 0, 13 груп
перевірок; складні runtime-гілки додатково покриті API smoke.

| Елемент документації | Файл і символ коду | Параметри | Очікувана поведінка | Фактична поведінка | Статус |
| --- | --- | --- | --- | --- | --- |
| SafeRequestHandler | `salon/__main__.py:SafeRequestHandler`, `.log_request` | Werkzeug request args; `self, code='-', size='-'` | Не писати URL/query у access log | `log_request` повертає None; probe PASS | PASS |
| CLI entry | `salon/__main__.py:main` | `()`; argparse/env/stdin | Запускає serve/create-admin/worker | help, create-admin, serve, worker перевірені | PASS |
| Flask factory | `salon/app.py:create_app` | `database, clock=None` | Flask app, Store/clock/Service extensions; 17 routes | 17 non-static routes, extensions присутні; probe PASS | PASS |
| Authentication | `salon/auth.py:authenticate` | `db, header` | User або 401 `UNAUTHENTICATED` | Порожній/unknown Bearer дає очікуваний ApiError | PASS |
| Open-decision guard | `salon/booking_service.py:unresolved` | `decision` | 500 INTERNAL_ERROR, decision у повідомленні | D-02 probe PASS | PASS |
| Bookings class/constructor | `salon/booking_service.py:Bookings`, `.__init__` | `store, clock` | Зберігає залежності | Constructor/clock probe PASS | PASS |
| Booking time/view | `Bookings.now`, `.view` | `self, value` | UTC now; current/history за cancel або endsAt | End boundary і cancel перевірені | PASS |
| Booking access/list | `Bookings.get`, `.all` | `db, kind, key`; `db` | Entity/404; categorized list | Missing, stored, category probes PASS | PASS |
| Booking use case | `Bookings.execute` | `db, op, data, params, user` | 5 booking operationId; ownership/rules | create/list/get/update/cancel HTTP smoke; missing gives 404 | PASS |
| Booking invariants | `Bookings.check`, `.fits` | `db,value,changing`; `schedule,start,end` | Schedule, horizon, overlap; interval fits | Valid interval, conflict, schedule probes PASS | PASS |
| Booking protection | `Bookings.protect`, `.protect_schedule` | `db,kind,key,operation,data`; `db,key,schedule` | Prevent destructive catalog/schedule conflicts | 409 current/schedule conflicts verified | PASS |
| Contract refs | `salon/contract.py:resolve` | `value` | Expand local `$ref`; KeyError missing ref | Probe PASS | PASS |
| Contract validation | `contract.validate` | `schema,value` | None or ValidationError; exact decimal multiple | `.29` pass, invalid string raises; probe PASS | PASS |
| API error type | `salon/errors.py:ApiError`, `.__init__` | `status,code,message` | Structured HTTP error, text=code | Attributes/text verified | PASS |
| Error raiser | `errors.reject` | `status, code, message` defaults | Always raise ApiError | Default code and custom code verified | PASS |
| Audit events | `salon/events.py:record` | `operation,status,request_id,code=None` | Allowlisted JSON log | Exactly five keys observed; PASS | PASS |
| Mail delivery | `salon/mail_worker.py:run_once` | `store,clock,transport` | Due pending jobs sent; failures failed; count | Empty batch 0, local SMTP and failed/no-retry verified | PASS |
| SMTP transport | `SMTPTransport`, `.__init__`, `.send` | host/port/sender/starttls/user/password; kind/payload | Store settings, send with 10s SMTP | Local sink accepted; settings probe PASS | PASS |
| MIME builder | `build_message` | `sender,kind,payload` | EmailMessage, four known kinds; KeyError unknown | Subject/body and KeyError verified | PASS |
| Notification outbox | `salon/notifications.py:enqueue`, `on_booking` | db/booking/kind/due; db/before/after/now | Queue/cancel/reschedule; D-04 guard | API smoke and doc restrictions verified | PASS |
| Decimal validator | `salon/numeric_validation.py:exact_multiple` | validator/divisor/instance/schema | Yield ValidationError only for invalid number | Generator probe PASS | PASS |
| Service dispatcher | `salon/service.py:ident`, `Service`, `.__init__`, `.get`, `.execute` | UUID; store/clock; db/kind/key; db/op/data/params/user | IDs, entities, all supported operations | UUID, missing, unknown op and 17 routes verified | PASS |
| Service checks | `Service.check_service_ids`, `.check_schedule` | db/ids; value | Validate service refs/schedule | valid and invalid schedule/ref probes PASS | PASS |
| SQLite store | `salon/store.py:Store`, `.__init__`, `.transaction`, `.get`, `.all`, `.put` | path; db/value as documented | schema, transaction rollback, JSON entities | table creation, rollback, missing parent, CRUD probes PASS | PASS |
| Time helpers | `salon/time_rules.py:instant`, `local` | value | offset→UTC; UTC→Europe/Kyiv | conversion and ValueError verified | PASS |
| Historical sketch | `src/booking.py:create_booking` | client_name/service/master/time | Four-field dictionary only | Exact keys, no persistence/conversion | PASS |

Для класів у таблиці також перевірено фактичні сигнатури: `Store(path)`,
`Bookings(store, clock)`, `Service(store, clock)`, `ApiError(status, code,
message)`, `SMTPTransport(host, port, sender, starttls=True, username=None,
password=None)`, `SafeRequestHandler(request, client_address, server)`.
Публічні внутрішні `handler/route/correlation` Flask callbacks не описані як
API: вони замикання фабрики, не експортовані символи. Суттєві винятки та
обмеження в docstrings збігаються з probes і API smoke; NOT VERIFIED немає.

## 3. Перевірка користувацької документації

UI відсутній, тому перевірено REST API через реальний локальний Werkzeug
server і `curl`; SMTP перевірено локальним sink без зовнішньої доставки.
Усі 73 записи runtime smoke мають PASS у контрольному
`runtime-verification.json`.

| Сценарій | Описані дії | Фактичні дії | Очікуваний результат | Фактичний результат | Статус |
| --- | --- | --- | --- | --- | --- |
| Підготовка/no UI | `serve`, BASE_URL, curl | server, GET `/`, GET `/services` | API без вебінтерфейсу | `/` 404, `/services` 200 | PASS |
| Реєстрація | POST `/users` JSON | curl client + duplicate | 201 User; duplicate 409 | 201; 409 EMAIL_IN_USE | PASS |
| Вхід | POST `/sessions`, зберегти token | client/admin login + wrong password | 200 Bearer; wrong 401 | 200; 401 UNAUTHENTICATED | PASS |
| Адмін catalog | POST `/services` | service payload із README | 201, active=true, UAH | 201, поля збігаються | PASS |
| Створення майстра | POST `/masters` з serviceIds | curl payload | 201 Master | 201, id отримано | PASS |
| Графік | PATCH і GET schedule | full weekly 09:00–18:00; vacation | 200 Schedule; duplicate date 422 | 200; vacation 200; duplicate 422 | PASS |
| Публічний каталог | GET services/masters | curl без токена | 200 items | 200/200, inactive видно | PASS |
| Створення запису клієнтом | POST `/bookings` без clientId | час +2 дні, client token | 201 confirmed/current, endsAt + duration | 201, snapshot/endsAt збігаються | PASS |
| Конфлікт | повторити той самий booking | повторний curl | 409 TIME_UNAVAILABLE | 409 | PASS |
| Перегляд записів | GET current/detail | client token, missing/foreign | 200; 404; 403 | усі відповіді збігаються | PASS |
| Скасування | POST cancellation | client current, повторно | 200 cancelled/history; repeat 409 | збігається | PASS |
| Історія | GET history | client token | booking у items | booking присутній | PASS |
| Адмін перенесення | PATCH startsAt | admin move; client PATCH | 200 snapshot preserved; client 403 | збігається | PASS |
| Захист каталогу | deactivate/delete | current conflicts, historical D-06 | 409 current; 500 historical guard | усі відповіді збігаються | PASS |
| Невідомий ресурс/роль | protected GET, missing, wrong method | curl probes | 401/403/404/405 | збігається | PASS |
| listSlots | GET slots | route probe | проєктовано, фактично 404 | 404 `INVALID_REQUEST` | PASS |
| D guards | horizon, D-02, D-03 | create +31, +29, past | 422 horizon; 500 guards | 422/500/500 | PASS |
| Адмінське створення | POST booking з clientId | admin token + clientId | 201; admin cancellation | 201/200 | PASS |
| Worker | outbox + worker once/loop | local SMTP, STARTTLS=0 | sent; no retry failed | sink accepted; counts stable | PASS |
| Bodyless cancellation | cancellation без body | також з зайвим body | body не впливає на cancellation | обидва 200 | PASS |

Виправлена невідповідність у документації: загальне речення про заборону
зайвих JSON-полів тепер обмежене операціями з `requestBody`; для cancellation
та інших body-less операцій явно описано фактичне ігнорування body. OpenAPI та
код не змінювалися.

## Підсумок і межі доказів

- README: усі виконані команди — PASS; sandbox-only DNS failure зафіксовано
  окремо, повтор з доступом до PyPI успішний.
- Python API: 47/47 символів існують, anchors autodoc присутні, probes PASS.
- HTTP API: 17 реалізованих operationId перевірено; `listSlots` має N/A щодо
  реалізації й фактичний 404, тому документація відокремлює його як
  запроєктований. У цьому звіті це перевірено як PASS для опису відсутності.
- User guide: curl-сценарії, CLI, локальний worker і помилки виконані; UI
  має статус N/A за поясненням «графічного інтерфейсу немає».
- Документація після виправлення згенерована повторно: HTML і singlehtml
  Sphinx 8.2.3, exit 0, 0 warnings. `check_lab4.py` зберіг exit 0, baseline
  hashes не змінені. Робоче дерево до цього звіту не містило runtime data.

Докази контрольного середовища не комітилися як тимчасова БД, токени або
логи процесів; у таблицях наведені команди, exit codes, відповіді й стабільні
результати. Коміт цього етапу: `test(lab6): verify documentation against implementation`.
