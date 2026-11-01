# Фінальний звіт ЛР5 — скорочений обсяг Bookings

## Обсяг і статус

Виконано дозволений скорочений обсяг: один функціональний модуль Bookings, а не всі 18 REST-операцій. Реалізовано п'ять Booking operationId із OpenAPI: `listBookings`, `createBooking`, `getBooking`, `updateBooking`, `cancelBooking`. Супровідні залежності — сесії, послуги, майстри, графік, SQLite persistence, outbox email і безпечні runtime events. `listSlots` залишається поза цим модулем через невирішений D-03 і не видається за реалізований Booking endpoint.

PLAN-GATE залишається REVISE. Локальний TEST-GATE для Bookings має фактичний цикл RED/GREEN/REFACTOR, але загальний TEST-GATE — REVISE через пропущені `listSlots`, відкриті D-02–D-06 та відсутність Human Review. SPEC-ADDENDUM-GATE для вузького `REQ-F-065-B` — REVISE / NOT APPROVED; вимогу до baseline не додано.

## TDD-докази

| Фаза | Фактичний результат | Доказ | Коміт |
| --- | --- | --- | --- |
| RED | 23 failed, 0 passed, 0 skipped; маршрути Bookings повертали 404 | `logs/lab5/red/b-bookings.txt` | `78664ca` |
| TEST-GATE | Технічний PASS для переходу до GREEN погодженого піднабору; D-02–D-06 явно заблоковані | `docs/lab5/test-gate.md` | — |
| GREEN | 44 passed, 0 failed, 0 skipped разом із попередньою регресією | `logs/lab5/green/b-bookings.txt` | `cf4317a` |
| REFACTOR | 44 passed, 0 failed, 0 skipped; спільні Kyiv/UTC правила винесені | `logs/lab5/refactor/b-bookings.txt` | `6e834fb` |

Контрактна регресія після всіх змін: 24 passed, 2 skipped; сукупна регресія: 99 passed, 0 failed, 2 skipped. Пропуски — тільки `listSlots` і пов'язаний негативний query case, обидва BLOCKED D-03. OpenAPI static validator: 18 описаних операцій, 161 приклад, 64 F-ID, baseline hashes PASS. Bookings-only поведінковий результат не додається вдруге до загальної кількості: його фактичний журнал — 44 passed.

## Перевірені Booking-сценарії

Покрито позитивні, негативні й граничні випадки: snapshot та `endsAt`, client/admin ownership, 2-годинну межу, графік і винятки, конфлікти майстра/клієнта, суміжні інтервали, атомарне конкурентне бронювання (рівно один 201 і один 409), current/history boundary, 24-годинне скасування, історичну незмінність, admin update/rollback, заміну послуги, збереження snapshot, restart persistence, outbox confirmation/reminders/cancellation та відсутність секретів у логах. Реальний loopback HTTP/SMTP smoke: 2 passed.

Матриця фактичних тестів — [traceability.md](traceability.md), а вузька карта п'яти Booking operationId — [bookings-traceability.md](bookings-traceability.md); повний TDD-опис — [tdd-report.md](tdd-report.md). Матриця не перетворює маркер REQ на повне приймання всіх AC/GWT.

## Команди

```sh
.venv/bin/python -m pytest tests/lab5/test_b_bookings.py -q
.venv/bin/python -m pytest tests/lab5 -q
.venv/bin/python scripts/check_lab4.py
.venv/bin/python -m pytest tests/lab5 tests/network -q
```

Фактичні команди, stdout/stderr, exit code і source hashes збережені у `logs/lab5/red`, `green`, `refactor` та `final/verification`.

## Залишкові проблеми

Не реалізовано `GET /masters/{masterId}/slots`; не погоджено точну сітку й календарний горизонт D-02/D-03. D-04/D-05/D-06 мають явні guards, а не вигадані результати. SMTP delivery має crash window між зовнішньою доставкою і commit; retry/retention/access policy не погоджені. NF, UI, браузерне приймання, зовнішня доставка і людська validation не закриті. Робочі секрети, БД і virtualenv не комітовано.

Підготовка до майбутнього addendum описана в [spec-addendum-bookings.md](spec-addendum-bookings.md) і [gate](spec-addendum-gate.md). До людського погодження `REQ-F-065-B` не є вимогою продукту.

Матеріали для Word-протоколу з доказами за всіма вісьмома пунктами: [protocol-materials.md](protocol-materials.md). Повторний loopback regression підтвердив 99 passed / 2 skipped; sandbox-спроба з EPERM збережена окремо як середовищний результат.
