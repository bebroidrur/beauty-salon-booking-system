# Інформаційна система онлайн-запису до салону краси

Навчальний проєкт для одного салону: каталог послуг і майстрів, реєстрація
клієнтів, графіки, створення/перегляд/зміна/скасування записів та email-outbox.
Є REST API і CLI; графічного інтерфейсу немає. Реалізовано 17 із 18
контрактних операцій для підтриманих сценаріїв. `listSlots` відсутній;
D-02–D-06 обмежують частину операцій. Це не завершений production-сервіс.

## Технології й структура

Python 3.13, Flask 3.1.2, SQLite зі стандартної бібліотеки, PyYAML 6.0.2,
openapi-schema-validator 0.6.3; pytest, Ruff; Sphinx 8.2.3 + MyST 4.0.1
для документації. Prism у ЛР4 використовується лише як контрактний mock.

| Шлях | Призначення |
| --- | --- |
| `salon/` | HTTP adapter, сценарії, SQLite, outbox/SMTP, CLI |
| `src/booking.py` | Історична заготовка, не backend |
| `spec/` | SRS, глосарій, незмінений OpenAPI 3.0.3 |
| `tests/lab5/`, `tests/network/` | Регресія, контракт, unit/integration, loopback HTTP/SMTP |
| `scripts/` | Перевірки й навчальні інструменти попередніх ЛР |
| `docs/lab4/` | HTTP-довідник і історичні матеріали проєктування |
| `docs/lab5/` | TDD, простежуваність і відомі обмеження реалізації |
| `docs/conf.py`, `docs/index.rst`, `docs/python-api.rst` | Sphinx-конфігурація й autodoc-директиви |
| `docs/generated/html/`, `docs/generated/singlehtml/` | Згенерована документація, включена в Git |
| `logs/` | Фактичні результати перевірок лабораторних |
| `runtime/` | Локальна БД, ігнорується Git |

## Встановлення

Команди виконуються з кореня репозиторію в POSIX shell. Потрібні Python 3.13,
`venv`, доступ до PyPI під час встановлення; для прикладів користувача — curl.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m pip install -r requirements-docs.txt
```

`requirements.txt` — runtime; `requirements-dev.txt` — додаткові інструменти
розробки; `requirements-lock.txt` — зафіксований runtime/test набір;
`requirements-docs.txt` — runtime та прямі залежності генератора.
Останній не є повним lock транзитивних Sphinx-залежностей.
Фактичні версії виконаних перевірок наведено в журналах, вони можуть
відрізнятися від pin у старому virtualenv.

## Конфігурація й запуск

```sh
.venv/bin/python -m salon --help
.venv/bin/python -m salon --database runtime/salon.sqlite3 create-admin
.venv/bin/python -m salon --database runtime/salon.sqlite3 serve --host 127.0.0.1 --port 8000
```

`create-admin` один раз запитує ім'я, телефон, email і пароль; стандартного
акаунта немає. Повторний email спричинить помилку унікальності.
Сервер працює до Ctrl+C. `--database` — глобальний аргумент **перед** командою;
типово `runtime/salon.sqlite3`, host — 127.0.0.1, port — 8000.
CLI створює батьківський каталог БД. API без UI доступний за
`http://127.0.0.1:8000/services`; відкриття `/` не показує вебсайт.

Email: окремий процес із тією самою БД; API лише ставить завдання в outbox.
Перед запуском задайте у середовищі свої `SALON_SMTP_HOST` і
`SALON_SMTP_SENDER`. Файл `.env` автоматично **не завантажується**.

| Змінна | Значення |
| --- | --- |
| SALON_SMTP_HOST, SALON_SMTP_SENDER | Обов'язкові hostname SMTP та адреса відправника |
| SALON_SMTP_PORT | Типово 587 |
| SALON_SMTP_STARTTLS | Типово `1`; лише точне `1` вмикає STARTTLS; `0` придатне для контрольного локального SMTP |
| SALON_SMTP_USER, SALON_SMTP_PASSWORD | Необов'язкові; login виконується, якщо задано USER |

```sh
.venv/bin/python -m salon --database runtime/salon.sqlite3 worker --once
.venv/bin/python -m salon --database runtime/salon.sqlite3 worker
```

Перша команда обробляє due-пакет, друга повторює перевірку щосекунди.
Без SMTP-конфігурації worker завершується помилкою. Автоматичного retry для
failed немає; можлива повторна доставка після crash до commit. Сервер є
локальним Werkzeug WSGI-сервером без TLS deployment. Секрети не комітити.

## Тести й перевірки

```sh
.venv/bin/python -m pytest tests/lab5 -q
.venv/bin/python -m pytest tests/lab5 tests/network -q
.venv/bin/python scripts/check_lab4.py
.venv/bin/python -m ruff check --no-cache salon src
.venv/bin/python -m ruff format --no-cache --check salon src
```

Network-тести потребують дозволу на bind до loopback і не надсилають зовнішні
листи. Два skips стосуються відкритого D-03. Межі lint та результати попереднього
етапу — [огляд ЛР6](logs/lab6-code-review.md).

## Документація

```sh
.venv/bin/python -m sphinx -b html -E -a -W --keep-going -d /tmp/beauty-lab6-doctrees/html docs docs/generated/html
.venv/bin/python -m sphinx -b singlehtml -E -a -W --keep-going -d /tmp/beauty-lab6-doctrees/singlehtml docs docs/generated/singlehtml
```

Обидві команди читають поточний Python-код через autodoc; Napoleon розбирає
Google docstrings. MyST включає наявні Markdown-сторінки HTTP-довідника та
інструкції. `-W` робить попередження причиною ненульового exit code;
`-E -a` перебудовує все. Doctree-кеш зберігається поза Git.

- [HTML: початкова сторінка](docs/generated/html/index.html)
- [Singlehtml для окремого подання](docs/generated/singlehtml/index.html)
- [HTTP API](docs/lab4/resource-model.md), [схеми](docs/lab4/schemas.md), [помилки](docs/lab4/errors.md)
- [Інструкція користувача](docs/user-guide.md)
- [Coding Convention](docs/coding-convention.md), [формат docstrings](docs/documentation-tags.md)
- [Журнал генерації ЛР6](logs/lab6-documentation.md)

HTML слід відкрити локально після завантаження репозиторію; Git-хостинг може
показувати лише вихідний текст. Для подання singlehtml передайте **всю папку**
`docs/generated/singlehtml/`: `index.html` використовує локальні `_static/`
та завантажувані джерела. Це одна сторінка змісту, не один автономний файл.
Базова специфікація й адендуми лишаються окремими нормативними артефактами.
