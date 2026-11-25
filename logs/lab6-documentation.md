# ЛР6 — автогенерація, HTTP-довідник та інструкція користувача

Дата: 2026-11-25. Гілка `lab6`, початковий коміт етапу `be7ef80`.
Продовження [попереднього огляду](lab6-code-review.md), без повторної зміни
бізнес-логіки. Використано docstrings попереднього етапу та фактичний код.

## Структура документації

| Шлях | Роль |
| --- | --- |
| `README.md` | Призначення, стек, структура, залежності, встановлення, конфігурація, CLI/API, тести, генерація |
| `requirements-docs.txt` | Runtime і прямі pins Sphinx 8.2.3 / myst-parser 4.0.1 |
| `docs/conf.py` | autodoc, Napoleon (Google), MyST; sys.path кореня; локальна тема; виправлення singlehtml-навігації |
| `docs/index.rst` | Зміст збірки й посилання на контракт для завантаження |
| `docs/python-api.rst` | 15 automodule-директив; сигнатури та тексти читаються з Python, не вписані вручну |
| `docs/lab4/resource-model.md` | Оновлений наявний HTTP-довідник: 17 реалізованих операцій та окремо listSlots |
| `docs/lab4/schemas.md`, `errors.md` | Уточнені поля/обмеження запитів і відповідей, реальні коди помилок |
| `docs/lab4/README.md` | Відокремлено історичний mock від runtime; старі команди Prism збережено |
| `docs/user-guide.md` | Покрокові API-сценарії клієнта/адміністратора, curl, очікувані результати й обмеження |
| `docs/documentation-tags.md` | Оновлено згадку про нове використання Sphinx/Napoleon |
| `docs/generated/html/` | Багатосторінкова збірка з навігацією, пошуком, Python-індексами |
| `docs/generated/singlehtml/` | Одна сторінка для окремого подання з локальними ресурсами |

Генератор читає шість джерельних сторінок: index, python-api, user-guide та
три сторінки lab4. Markdown не скопійовано в інший набір вихідних файлів.
В обох результатах — 15 модулів і **47** визначених у коді публічних
функцій/класів/методів/конструкторів; перевірено HTML anchors проти AST.
`src.booking` позначено як історичну заготовку. Імпорт CLI не викликає main.
Імпорти не замокано: autodoc працює зі справжніми runtime-залежностями.

Склад згенерованих каталогів:

```text
docs/generated/
  html/
    index.html, python-api.html, user-guide.html
    lab4/{resource-model,schemas,errors}.html
    genindex.html, py-modindex.html, search.html, searchindex.js
    _static/, _downloads/, objects.inv, .buildinfo
  singlehtml/
    index.html
    _static/, _downloads/, objects.inv, .buildinfo
```

У `_downloads` Sphinx автоматично упаковує незмінні openapi.yaml та
адендум ЛР4; побайтову тотожність оригіналам перевірено. Це ресурси
експортованого документа, не нові редакції специфікації. Doctree-кеш
винесено у `/tmp/beauty-lab6-doctrees/`, у Git його немає.

## Середовище й точні команди

Фактичне середовище: Python 3.13.0; Sphinx 8.2.3; myst-parser 4.0.1;
docutils 0.21.2; Alabaster 1.0.0; pytest 9.2.0 (pin репозиторію — 8.4.2).
Прямі docs-залежності зафіксовано окремо, старий runtime/test lock не змінено.
Повний транзитивний lock документації не заявляється.

Спочатку Sphinx був відсутній. Команда встановлення:

```sh
.venv/bin/python -m pip install Sphinx==8.2.3 myst-parser==4.0.1
```

Sandbox-спроба мала DNS/network помилку. Повторний запуск із дозволом
завершився exit 0. Для нового середовища еквівалентне встановлення прямих
залежностей наведено у README через `-r requirements-docs.txt`.

Фінальна генерація, з кореня репозиторію:

```sh
.venv/bin/python -m sphinx -b html -E -a -W --keep-going -d /tmp/beauty-lab6-doctrees/html docs docs/generated/html
.venv/bin/python -m sphinx -b singlehtml -E -a -W --keep-going -d /tmp/beauty-lab6-doctrees/singlehtml docs docs/generated/singlehtml
```

`-E -a` змушує перечитати джерела та згенерувати всі сторінки;
`-W --keep-going` не приховує попередження й повертає failure за їх наявності.
Exit code фінальних команд зафіксовано через subprocess.returncode,
stdout/stderr об'єднано, результат не підмінено exit code команди cat/tee.

| Builder | Exit code | WARNING | Результат |
| --- | ---: | ---: | --- |
| html | 0 | 0 | build succeeded. |
| singlehtml | 0 | 0 | build succeeded. |

Фінальні повідомлення генератора:

```text
build succeeded.
The HTML pages are in docs/generated/html.
build succeeded.
The HTML page is in docs/generated/singlehtml.
```

## Попередження й виправлення

Перший пробний HTML-запуск повідомив **3 warnings**:

- `docs/index.rst:2`: Title underline too short.
- `docs/python-api.rst:2`: Title underline too short.
- `docs/lab4/schemas.md:5`: Unknown source document 'lab4/addendum'.

Його stdout закінчувався `build finished with problems, 3 warnings (with
warnings treated as errors)`; окремий exit code Sphinx того пробного shell
ланцюжка не було збережено. Подовжено RST-підкреслення; адендум підключено
як download, без редагування його вмісту. У фінальній збірці warnings = 0,
їх не приховано suppress_warnings.

Додаткова перевірка HTML виявила те, чого не знайшов Sphinx: singlehtml
посилався на відсутні genindex/search і мав подвійні fragments у посиланнях
ApiError (разом 15 нерозв'язаних посилань), а автоматичні IDs українських
заголовків дублювалися між сторінками. У `conf.py` через Sphinx events:

- прибрано посилання теми на відсутні сторінки лише для singlehtml;
- нормалізовано внутрішні подвійні fragments;
- IDs секцій отримують префікс сторінки до збирання toctree.

Проміжна перевірка префіксування виявила 45 посилань на зміщені module-ID;
виправлено правило, яке тепер зберігає `module-*` anchors autodoc.
Фінально локальні посилання й унікальність усіх ID перевірено повторно.
Готові HTML-файли **не редагувалися вручну**; всі виправлення відтворює збірка.

## Перевірки результату

| Результат | HTML-сторінок | Локальних href/src/action | Нерозв'язаних посилань | Дублікатів ID |
| --- | ---: | ---: | ---: | ---: |
| html | 9 | 453 | 0 | 0 |
| singlehtml | 1 | 119 | 0 | 0 |

Перевірка одноразовим Python HTMLParser проходила всі локальні посилання,
перевіряла існування файлів/fragment-ID, унікальність ID та наявність усіх
47 символів і 15 модулів із AST. Зовнішні URL не перевірялися мережею.
Порівняння `_downloads` — через read_bytes з оригіналами.

На тимчасовій SQLite БД виконано CLI `create-admin` та запити Flask test_client
із буквальними JSON-payloads інструкції: реєстрація, вхід, каталог, графік,
запис, скасування, історія, новий запис, admin PATCH і деактивація.
Додаткові запити охопили всі 17 operationId, чисті DELETE та відомі обмеження.
Це перевірка payloads/поведінки, не заява про запуск кожного curl з документа.
Результат одноразового smoke, exit 0:

```text
PASS documented create-admin CLI, exit 0 (temporary database)
PASS literal guide payloads, registration/login/catalog/schedule/book/cancel/history/admin move/deactivation
PASS 17 implemented operationIds exercised and present in the reference
PASS documented limits: slots 404 INVALID_REQUEST; missing service createBooking 404 NOT_FOUND; history deletion D-06 500
```

Наявні перевірки:

```sh
.venv/bin/python -m salon --help
.venv/bin/python -m pytest tests/lab5 tests/network -q
.venv/bin/python scripts/check_lab4.py
.venv/bin/python -m ruff check --no-cache salon src docs/conf.py
.venv/bin/python -m ruff format --no-cache --check salon src docs/conf.py
git diff --exit-code -- salon src spec docs/lab4/addendum.md docs/lab5/spec-addendum-bookings.md
```

- CLI help — exit 0, команди serve/create-admin/worker.
- Регресія із дозволом loopback — **99 passed, 2 skipped in 36.19s**, exit 0.
  Обидва skips — незмінений D-03 у test_e_contract.py.
- Static checker — exit 0: OpenAPI 3.0.3, 18 операцій, 161 приклад,
  8 незмінних SHA-256 baseline, 75 рядків простежуваності.
- Ruff — exit 0, All checks passed; formatter — 16 files already formatted.
- Diff runtime, історичної заготовки, spec і адендумів — порожній, exit 0.
- Source diff whitespace check — без зауважень. У згенерованому HTML
  шаблони Sphinx/Alabaster містять пробільні порожні рядки: Git whitespace
  check для singlehtml їх позначає (exit 3 при `--no-index`); це не помилки
  генерації/посилань. Вручну або додатковим форматером HTML не переписувався.

## Межі HTTP-довідника

Збережено наявну структуру ЛР4: resource-model, schemas, errors замість нового
дублюючого API-файлу. Реалізовані маршрути мають метод, URI, доступ,
параметри, request/response schema, статус успіху та спеціальні помилки;
спільні коди визначено окремо. Відсутній listSlots винесено в окрему таблицю.

Зафіксовано фактичні відмінності: login → UNAUTHENTICATED; відсутні URL →
INVALID_REQUEST; createBooking може повернути неоголошений 404; optional
ApiError.details не формується; каталоги показують неактивні сутності.
Guards D-02–D-06 та SMTP crash window залишаються обмеженнями.
Жоден із цих описів не затверджує адендум і не змінює OpenAPI.

## Окреме подання

Відкрити `docs/generated/singlehtml/index.html` локально; для передавання
зберегти всю папку `singlehtml/` разом з `_static/` і `_downloads/`.
Для пошуку по одній сторінці використовуйте пошук браузера. Збірка html
має власну сторінку пошуку. Наявність HTML не означає публікацію сайту.

Джерела інструментів: [Sphinx autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html),
[Napoleon](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html),
[sphinx-build](https://www.sphinx-doc.org/en/master/man/sphinx-build.html).

Коміт етапу: `docs(lab6): generate API and user documentation`; push не виконується.
