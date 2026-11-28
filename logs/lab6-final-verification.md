# ЛР6 — фінальна верифікація репозиторію

Дата: 2026-11-26. Перевірки виконано в локальному `.venv`; для мережевих тестів окремо надано дозвіл bind до loopback. Дані runtime та секрети до Git не додавалися.

| Перевірка | Команда | Фактичний результат | Статус | Доказ/межа |
| --- | --- | --- | --- | --- |
| Traceability audit | `.venv/bin/python scripts/lab6_traceability_audit.py` | 75 вимог; 55 повних; 20 неповних; 9 NOT IMPLEMENTED; 0 errors | PASS | `logs/lab6-traceability-audit.md` |
| Модульні, контрактні та регресійні тести | `.venv/bin/python -m pytest tests/lab5 tests/network -q` | 99 passed, 2 skipped, 30.37 s | PASS з відомими skip | Обидва skip — D-03/listSlots; це не повна SRS-верифікація |
| Loopback transport tests | `.venv/bin/python -m pytest tests/network -q` | 2 passed, 0 failed, 0.97 s | PASS | HTTP/SMTP локальні sink; зовнішня доставка не перевірялась |
| OpenAPI/static contract | `.venv/bin/python scripts/check_lab4.py` | OpenAPI 3.0.3; 18 operations; 64 F IDs; 161 examples; 8 baseline hashes; 75 trace rows | PASS | Baseline hashes unchanged |
| Ruff diagnostics | `.venv/bin/python -m ruff check --no-cache salon src scripts/lab6_traceability_audit.py scripts/lab6_generate_matrix.py` | All checks passed | PASS | Scope is repository Python implementation and Lab 6 scripts |
| Ruff formatting | `.venv/bin/python -m ruff format --no-cache --check salon src scripts/lab6_traceability_audit.py scripts/lab6_generate_matrix.py` | 17 files already formatted | PASS | — |
| Sphinx HTML | `.venv/bin/python -m sphinx -b html -E -a -W --keep-going -d /tmp/beauty-lab6-doctrees-final/html docs docs/generated/html` | build succeeded; 0 warnings | PASS | Generated HTML committed |
| Sphinx singlehtml | `.venv/bin/python -m sphinx -b singlehtml -E -a -W --keep-going -d /tmp/beauty-lab6-doctrees-final/singlehtml docs docs/generated/singlehtml` | build succeeded; 0 warnings | PASS | Generated singlehtml committed |

## Середовищний результат

Перший запуск повного набору без спеціального bind-дозволу дав `97 passed, 2 skipped, 2 failed`: `test_real_http` і `test_real_smtp_outbox` отримали `PermissionError: Operation not permitted` під час loopback bind. Повторний запуск `tests/network` з дозволом дав `2 passed`; повторний повний запуск дав наведені вище `99 passed, 2 skipped`. Це обмеження середовища, а не виправлення коду.

## Відомі відхилення та обмеження

- `GET /masters/{masterId}/slots` (`listSlots`) не реалізований; два контрактні тести залишаються skipped через D-03.
- Частина booking/reminder/catalog правил має статус PARTIAL через відкриті D-02–D-06 та межі погодженого addendum.
- NF-001 не має benchmark-вимірювання; NF-003, NF-005 та UI/browser/accessibility/availability NF не реалізовані в обсязі ЛР5.
- Тести охоплюють фактичний обсяг ЛР5, а не всю SRS; passing tests не перетворюють 17 реалізованих контрактних операцій на повне приймання всіх 64 функціональних і 11 нефункціональних вимог.
- Sphinx і OpenAPI підтверджують документацію та форму контракту, але не замінюють людську валідацію бізнес-правил.

## Питання для рішення людиною

1. Погодити або уточнити D-02–D-06: горизонт, сітку початків, перенесення ближче 24 годин, сумісність PATCH і правила видалення.
2. Вирішити, чи реалізовувати `listSlots` і як приймати REQ-F-004/018.
3. Прийняти обсяг і докази нефункціональних вимог: benchmark, recovery, TLS, UI/browser/accessibility та availability.
4. Окремо прийняти політику SMTP delivery/retry/crash window і потребу зовнішнього mail-provider тесту.

На момент складання цього verification log FINAL-GATE ще очікував Human review. Після підтвердження 2026-11-28 рішення зафіксовано як **GO для погодженого скороченого API-модуля / REVISE для повної SRS** у [docs/final-gate.md](../docs/final-gate.md). Наведені технічні результати не змінювалися.
