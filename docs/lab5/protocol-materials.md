# Матеріали до Word-протоколу ЛР5

Обсяг цієї редакції: дозволений один функціональний модуль Bookings. Інші модулі не реалізовувалися в межах цього продовження. Усі Gate-рішення нижче розділяють технічну перевірку та людське приймання.

| Пункт | Фактичний доказ | Команда / результат | Git / файли | Обмеження та рекомендація для скриншота |
| --- | --- | --- | --- | --- |
| 1. Аудит і межі | [final-report](final-report.md), [plan review](plan-review.md) | `git status --short`; PLAN-GATE REVISE | `2500cda`; `docs/lab5/audit.md`, `docs/lab5/final-report.md` | Не заявляти повний API; скриншот статусу гілки й таблиці п'яти operationId |
| 2. OpenAPI Bookings | [bookings traceability](bookings-traceability.md), `spec/openapi.yaml` | `scripts/check_lab4.py`: PASS, 18 operations/161 examples/64 F-ID, 8 hashes unchanged | `a465438`; `logs/lab5/final/verification/protocol-openapi.txt` | `listSlots` є окремим operationId і не входить до скороченого Bookings; скриншот п'яти `/bookings` шляхів |
| 3. TDD RED | [TEST-GATE](test-gate.md) | `pytest tests/lab5/test_b_bookings.py -q`: 23 failed до реалізації; причина — 404 відсутніх Booking routes | `78664ca`; `logs/lab5/red/b-bookings.txt` | Це справжній RED, не помилка імпорту; скриншот summary та commit |
| 4. TEST-GATE/GREEN/REFACTOR | [TDD report](tdd-report.md) | GREEN 44 passed; REFACTOR 44 passed; загальна технічна регресія 99 passed/2 skipped | `cf4317a`, `6e834fb`; `logs/lab5/green/b-bookings.txt`, `logs/lab5/refactor/b-bookings.txt` | TEST-GATE Bookings: PASS WITH LIMITATIONS; загальний: REVISE. Скриншот трьох комітів і summary |
| 5. Поведінка Bookings | [tdd-report](tdd-report.md), [traceability](bookings-traceability.md) | Snapshot, ownership, conflicts, concurrency, history, cancellation, rollback, reminders covered by marked tests | `salon/booking_service.py`, `tests/lab5/test_b_bookings.py` | D-02/D-04/D-05/D-06 мають guards або відкладені правила; не показувати їх як accepted |
| 6. Логування | `tests/lab5/test_c_notifications_logging.py`, runtime events | Safe fields `requestId/operation/status/code`; secrets and personal data absent; relevant tests passed in prior GREEN/regression | `30e6229`, `d56fabc`; `salon/events.py`, `logs/lab5/final/verification/regression.txt` | Це виконання поточного безпечного logging scope, не прийнята REQ-F-065-B; скриншот sanitized log/assertions |
| 7. Addendum / SPEC-ADDENDUM-GATE | [addendum](spec-addendum-bookings.md), [gate](spec-addendum-gate.md) | Impact/SRS/OpenAPI/AC/BDD/traceability/risk map documented; decision REVISE / NOT APPROVED | `2500cda`; `logs/lab5/spec-addendum-gate/decision.md` | Human approval, retention/access/rotation and dedicated new tests outstanding; TDD REQ-F-065-B must not start. Скриншот decision and impact table |
| 8. Verification, validation, handoff | Final evidence and Git history | Contract 24 passed/2 skipped; full loopback regression 99 passed/2 skipped; OpenAPI PASS; `git diff --check` PASS | `logs/lab5/final/verification/protocol-*`, `git log --oneline` | Validation by user/Human not performed; screenshots should show commands, exit 0, skipped D-03, clean status |

## Команди для відтворення

```sh
/tmp/beauty-lab5-runtime/bin/python -m pytest tests/lab5/test_b_bookings.py -q
/tmp/beauty-lab5-runtime/bin/python -m pytest tests/lab5 -m contract -q
/tmp/beauty-lab5-runtime/bin/python scripts/check_lab4.py
/tmp/beauty-lab5-runtime/bin/python -m pytest tests/lab5 tests/network -q --tb=short
git diff --check
git status --short
```

Loopback-команда потребує дозволу bind. Sandbox-запуск зафіксував 97 passed, 2 skipped і 2 EPERM; повторний запуск із дозволеним loopback дав 99 passed, 2 skipped. Це дві різні фактичні перевірки, а не прихований результат.

## Підготовлений пакет Human Review

Передати `spec-addendum-bookings.md`, `spec-addendum-gate.md`, `logs/lab5/spec-addendum-gate/decision.md`, `bookings-traceability.md`, `final-report.md` і ризики R-07/R-10/R-12/R-16. Human має окремо погодити вузький обсяг REQ-F-065-B, два AC, BDD-сценарій, retention/access/rotation і момент додавання нових зв'язків у baseline matrix. До цього погодження TDD нової вимоги має статус **BLOCKED / NOT STARTED**.

## Що готово / що незавершено

Готові фактичні Booking implementation, RED/GREEN/REFACTOR докази, контрактна перевірка, безпечне logging, traceability supplements, протокол матеріали та addendum package. Незавершені: Human Review, SPEC-ADDENDUM-GATE GO, REQ-F-065-B TDD, D-03 slots, D-02/D-04/D-05/D-06, повний 18-operation API, NF/UI validation і зовнішня production email політика.
