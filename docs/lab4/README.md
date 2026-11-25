# Лабораторна №4 — REST API за специфікацією

Початковий етап ЛР4 (`lab4-api`) проєктував контракт і mock без бізнес-логіки. У ЛР6 довідник ресурсів, схеми та помилки актуалізовано за реальною реалізацією ЛР5: 17 операцій із 18, без listSlots. Історичні звіти й докази ЛР4 збережено.

Для реального сервера див. [README проєкту](../../README.md) та [інструкцію користувача](../user-guide.md). Наведені нижче команди Prism стосуються лише mock.

- [Модель ресурсів та операції](resource-model.md)
- [Матриця REQ → AC/GWT → D/Issue → API](traceability-matrix.md)
- [Схеми](schemas.md), [помилки](errors.md)
- [Сценарії](test-scenarios.md), [уточнення](addendum.md)
- [Протокол і API-GATE](verification.md), [фінальний аудит](final-audit.md)
- [Чернетка звіту](report-draft.md), [план комітів](commit-plan.md)
- [OpenAPI 3.0.3](../../spec/openapi.yaml)

## Відтворення з кореня репозиторію

Інструменти ізольовані в /tmp; Python 3.13.0, Node 22.16.0, npm 10.9.2. Потрібні доступ до PyPI/npm під час встановлення та дозвіл локального порту/HTTP. Глобальні пакети не встановлюються.

```sh
python3 -m venv /tmp/beauty-lab4-venv
/tmp/beauty-lab4-venv/bin/pip install -r tests/lab4/requirements-lock.txt
mkdir -p /tmp/beauty-lab4-prism
cp tests/lab4/package.json tests/lab4/package-lock.json /tmp/beauty-lab4-prism/
npm ci --prefix /tmp/beauty-lab4-prism --cache /tmp/beauty-lab4-npm-cache
/tmp/beauty-lab4-venv/bin/python scripts/check_lab4.py
```

Термінал 1 (залишити процес працювати; Ctrl+C для зупинки):

```sh
/tmp/beauty-lab4-prism/node_modules/.bin/prism mock spec/openapi.yaml --host 127.0.0.1 --port 4010
```

Термінал 2:

```sh
/tmp/beauty-lab4-venv/bin/python scripts/check_lab4.py --mock http://127.0.0.1:4010
curl -i http://127.0.0.1:4010/services
curl -i -X POST http://127.0.0.1:4010/users -H 'Content-Type: application/json' -d '{}'
curl -i -X POST http://127.0.0.1:4010/bookings/booking-1/cancellation -H 'Authorization: Bearer mock-token' -H 'Prefer: code=422, example=CANCELLATION_TOO_LATE'
```

Остання команда симулює пізнє скасування вибором відповіді; не перевіряє годинник або власника. Для збереження журналу додайте `> logs/lab4/mock-tests.txt 2>&1` до запуску runner; перевірте exit code, не вважайте сам факт появи файлу успіхом.

Методичні джерела: [OpenAPI 3.0.3](https://spec.openapis.org/oas/v3.0.3), [Prism mocking](https://github.com/stoplightio/prism/blob/main/docs/guides/01-mocking.md), [Prism CLI](https://github.com/stoplightio/prism/blob/main/docs/getting-started/03-cli.md). Бізнес-вимоги взято лише з локальної SRS.
