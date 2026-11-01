# ЛР5 — запуск реалізованого піднабору

Стан: 17 REST-маршрутів із 18 для погоджених випадків; `GET /masters/{masterId}/slots` **ще не реалізовано**, D-03 очікує рішення користувача. D-02–D-06 мають явні обмеження нижче. Це не завершений API і не готовий production deployment. Baseline/OpenAPI не змінено.

## Встановлення та запуск

З кореня репозиторію, Python 3.13:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m salon --database runtime/salon.sqlite3 create-admin
.venv/bin/python -m salon --database runtime/salon.sqlite3 serve --port 8000
```

`create-admin` запитує ім'я/телефон/email та пароль через getpass; публічна реєстрація створює лише клієнта. Default admin або пароль не закладено. Локальні БД, runtime та venv ігноруються Git. CLI server — локальний WSGI-сервер, без заяви про deployment/TLS/NF приймання. Сесії opaque Bearer, зберігаються у БД як SHA-256 токена; TTL/logout/refresh не додано до контракту. Вхід — POST /sessions. У server access log не записуються URL/query; application log містить operation/status/code/requestId/time без request body, токенів чи ПД.

Для email запустити окремий процес із тією самою БД:

```sh
.venv/bin/python -m salon --database runtime/salon.sqlite3 worker
```

Потрібні змінні середовища `SALON_SMTP_HOST`, `SALON_SMTP_SENDER`; порт `SALON_SMTP_PORT` за замовчуванням 587. STARTTLS увімкнено (`SALON_SMTP_STARTTLS=1`); для контрольного loopback SMTP без TLS можна явно задати 0. `SALON_SMTP_USER`/`SALON_SMTP_PASSWORD` — лише через середовище/менеджер секретів, не файл у Git. `worker --once` обробляє один пакет. Без SMTP-конфігурації worker не запускається; черга зберігається, але API сам листів мережею не доставляє.

Відмова SMTP переводить задачу у failed і логує безпечний код; автоматичних повторів немає. Політика retry відкрита D-07. Збій після прийняття SMTP, але до commit, може спричинити дубль при перезапуску; exactly-once не обіцяється. SMTP-виклик утримує SQLite write lock і має timeout 10s; для великих навантажень потрібне окреме проєктування, NF-продуктивність не заявляється.

## Тести

```sh
.venv/bin/python -m pytest tests/lab5 -q
.venv/bin/python -m pytest tests/lab5 -m unit -q
.venv/bin/python -m pytest tests/lab5 -m contract -q
.venv/bin/python -m pytest tests/lab5 tests/network -m integration -q
.venv/bin/python -m pytest tests/lab5 tests/network -q
.venv/bin/python scripts/check_lab4.py
```

`tests/network` підіймає локальні HTTP і SMTP на випадкових loopback-портах. Потрібен дозвіл bind; жодного зовнішнього листа. SMTP smoke використовує лише synthetic@example.test у локальному приймачі. Unit transport double не є доказом зовнішньої доставки; loopback smoke є доказом мережевої передачі контрольному SMTP.

Для нового журналу використовувати нове ім'я (runner відмовляється перезаписувати докази):

```sh
.venv/bin/python scripts/lab5_run.py logs/lab5/final/verification/new-run.txt .venv/bin/python -m pytest tests/lab5 tests/network -q
```

У `/tmp/beauty-lab5-runtime` встановлено ізольоване середовище фактичних запусків цього сеансу; це тимчасовий шлях, не гарантована частина репозиторію.

## Незавершені правила — не підмінені припущеннями

- D-03: listSlots відсутній; точна прив'язка 30-хвилинної сітки не обрана. Початок ≤ now під час create/update теж потребує уточнення; поточний guard повертає 500, не вигаданий бізнес-критерій.
- D-02: дні з різницею 29/30 календарних дат консервативно заблоковані до погодження останньої дати; >30 відхиляється, внутрішні дати перевіряються. Guard повертає 500; це **не завершена реалізація REQ-F-021**.
- D-04: перенесення на ≥24h запису, для якого раніше не створювалося нагадування, заблоковане з rollback; інші перевірені випадки перепланування працюють.
- D-05: несумісна пара при PATCH заблокована до рішення; create несумісної пари відхиляється за baseline.
- D-06: PATCH із неактивними сутностями та видалення сутності з історією заблоковані; за актуальних записів DELETE повертає погоджений 409.

Guards для невирішених випадків повертають ApiError 500 з позначенням потрібного D-рішення; вони не є затвердженою бізнес-поведінкою або заявою про відповідність цих випадків. Відсутній маршрут слотів повертає 404. Не використовувати цей піднабір як повністю сумісний із контрактом сервер. Пакет уточнень D-02–D-06 вже запитано в користувача; відповіді під час реалізації не отримано. NF-пороги, UI, браузери, TLS deployment і SLA не приймались. Нова REQ-F-065 не внесена.

Докази й межі: [TDD](tdd-report.md), [TEST-GATE](test-gate.md), [рефакторинг](refactoring-report.md), [повторний огляд плану](plan-review.md), [простежуваність](traceability.md).
