# ЛР5 — аудит перед реалізацією

Дата: 2026-11-01. Гілка: `lab5-tdd`; вихідний HEAD: `fa016c8cc7a18f571f081d0642bb58f932dcde9d`. Початковий `git status --short` порожній. Обсяг: локальний репозиторій, без перевірки поточного стану GitHub Issues або розгортання. AGENTS.md у дереві проєкту не знайдено. Бізнес-логіку, тести продукту та контракт на цьому етапі не змінено.

## 1. Знайдені артефакти

| Артефакт | Джерело | Фактичний стан |
| --- | --- | --- |
| Опис проєкту, SKED, межі, словник | `docs/project.md`, `spec/idea.md`, `spec/questions.md`, `spec/scope.md`, `spec/glossary.md` | Наявні; один салон, без оплати, гостьового бронювання та акаунта майстра |
| SRS 1.0 | [SRS](../../spec/SRS.md) | 64 F + 11 NF; NF не всі погоджено |
| Окремі вимоги | [F](../../spec/functional-requirements.md), [NF](../../spec/non-functional-requirements.md) | Стабільні REQ-ID |
| Приймання та BDD | [57 AC](../../spec/acceptance-criteria.md), [35 GWT](../../spec/given-when-then.md) | Текстові сценарії; виконуваних BDD-тестів немає |
| Простежуваність baseline | [Матриця](../../spec/traceability-matrix.md) | 75 рядків; Test/Code порожні навмисно |
| Простежуваність плану й API | [Декомпозиція](../lab3/decomposition-draft.md), [матриця ЛР4](../lab4/traceability-matrix.md), `docs/lab3/issue-mapping.csv` | REQ → AC/GWT → D/Issue → operationId; не доказ реалізації |
| SPEC-GATE | [Рішення](../../logs/spec-gate.md), `logs/spec-independent-review.txt` | PASS WITH NON-BLOCKING OBSERVATIONS; OBS-01–05 відкриті |
| REST контракт | [OpenAPI](../../spec/openapi.yaml) | OAS 3.0.3, версія 0.1.0; 18 операцій; сам документ називає HTTP-рішення проєктними |
| API-GATE | [Протокол](../lab4/verification.md) | GO лише для контракту/mock; не приймання продукту й не закриття PLAN-GATE |
| Докази ЛР4 | `logs/lab4/`, [сценарії](../lab4/test-scenarios.md), [аудит](../lab4/final-audit.md) | Історичні 147 HTTP-запитів, з них 121 відтворення відповіді; не новий запуск |
| Проєктний план | [План](../lab3/implementation-plan.md), `docs/lab3/gantt.md`, `critical-path.md`, `workflow.md`, `human-review-capacity.md` | D-01–D-45, сценарії B0/S2; це план, а не виконані Feature |
| PLAN-GATE | [Рішення](../lab3/plan-gate.md) | REVISE: NF-обсяг, підготовка G-R4, ресурсний перегляд та Human Review |
| Ризики | [Реєстр](../lab3/risk-register.md), [додаткові Gates](../lab3/additional-gates.md) | 16 ризиків; контрольні G-R1–G-R6; заходи не доводять зниження ризику |
| Уточнення ЛР4 | [Addendum](../lab4/addendum.md) | Проєкти рішень, не погоджені нові вимоги |

## 2. Код, технології, тести та логування

`src/booking.py` містить лише `create_booking(client_name, service, master, time)`, що повертає словник із чотирма переданими значеннями. Це демонстраційна заготовка: немає ID запису, перевірки користувача, часу, конфліктів, snapshot, збереження чи email. Навіть REQ-F-011 не можна вважати реалізованою повністю лише за наявністю параметрів service/master. **Жодна вимога продукту не підтверджена реалізацією і тестом; REST endpoints не реалізовані.**

Наявний Python-код, `.venv`, утиліта `import_lab3_issues.py` для процесу планування. У `tests/lab4/` — JSON негативних запитів і залежності інструментів контракту: PyYAML 6.0.2, openapi-spec-validator 0.7.2, openapi-schema-validator 0.6.3, Prism CLI 5.14.2 (npm), lock-файли. Це не стек backend. Фреймворк сервера, БД, міграції, HTTP entrypoint, менеджер залежностей застосунку, pytest-конфігурація, unit/integration/product acceptance tests та CI у переглянутому дереві відсутні. Версії Python/Node з протоколу ЛР4 є історичними, не гарантією поточного середовища.

`check_lab3_scenarios.py` перевіряє планування; `check_lab4.py` — контракт і опційно Prism. Його `--mock` використовує синтетичний токен і Prefer для вибору відповідей, тому цей режим не можна використати як тест бізнес-логіки реального сервера.

`logs/` вже існує: журнали перевірок документів і mock не є журналом дій користувачів. У `src/booking.py` немає logger, аудиту або системної діагностики. Транзитивна logging-залежність Prism у npm lock не реалізує логування застосунку. REQ-NF-004 погоджена (не зберігати відкриті паролі); REQ-NF-006 про нерозголошення діагностичних даних потребує погодження й прямо не вводить функції аудиту.

## 3. Узгодженість і прогалини

Повторна локальна звірка: 8 SHA-256 із SPEC-GATE збігаються; 64 F, 11 NF, 57 AC, 35 GWT мають унікальні ID й ті самі визначення в SRS. Тексти збігаються після нормалізації рівнів заголовків, HTML-якорів та внутрішніх посилань. Доказ: [baseline-check.txt](../../logs/lab5/audit/baseline-check.txt).

Покриття AC/GWT вибіркове: за SPEC-GATE 19 вимог без окремого AC, 32 без GWT; це прогалина приймального покриття, не дозвіл придумувати погоджені критерії. OpenAPI пов'язує всі 64 F із операціями; email-вимоги позначають побічні ефекти, а не окремі endpoints. NF не підтверджуються контрактними прикладами. Повний автоматичний OpenAPI/матриця check у цьому середовищі не завершився — див. розділ 5.

| Питання | Джерело | Наслідок для ЛР5 |
| --- | --- | --- |
| Відлік 30 календарних днів | OBS-01, D-02, REQ-F-021 | Не призначати конкретну останню дату до рішення |
| Сітка початків і «рівно зараз» адміністратору | OBS-04, D-03, REQ-F-018/020 | Тести прив'язки сітки та мінімальної межі admin BLOCKED |
| Перенесення далеко вперед після створення менш ніж за добу | OBS-02, D-04, REQ-F-059/060/063 | Не обирати пріоритет правил кодом |
| Несумісна пара майстер/послуга при PATCH | OBS-03, D-05 | HTTP 422 у проєкті не затверджує відсутній негативний AC |
| Видалення за історії, зміни з неактивними сутностями | D-06 | Відокремити від однозначної заборони видалення за актуальних записів |
| TTL/logout/refresh, доставка й retry email | D-07 | Не додавати прихованих функцій; погодити технічні межі |
| NF, приймальне середовище й UI | OBS-05, D-08–D-10 | Не заявляти SLA/продуктивність/браузерне приймання; REQ-NF-005/007/008 мають погоджену основу, не всі деталі |
| Пошук клієнта адміністратором, показ неактивних, формати, PATCH schedule | Addendum ЛР4 | Контрактні форми є проєктними; не розширювати їх новими endpoints |
| Відсутні бізнес-тести, backend і runtime-журнали | Огляд src/tests | TEST-GATE не виконаний; потрібен справжній RED на поведінці |

Нова суперечність у текстах baseline не виявлена. Структурний зв'язок REQ–endpoint не доводить семантичну повноту: ролі, атомарність, часові межі, email та незмінність даних перевірятимуться на реалізації. Формальний текст методички ЛР5 у репозиторії не знайдено; критерії Gates нижче — пропозиція за поточним завданням, не вигадана методичка.

## 4. Інвентар REST-операцій

Усі рядки мають стан **лише контракт/mock, реалізації немає**. REQ взято з `x-requirement-ids`, а не виведено з назв.

| Метод | URI | operationId | REQ-ID |
| --- | --- | --- | --- |
| POST | `/users` | registerClient | REQ-F-005, REQ-F-006 |
| POST | `/sessions` | login | REQ-F-007, REQ-F-010 |
| GET | `/services` | listServices | REQ-F-001, REQ-F-002 |
| POST | `/services` | createService | REQ-F-010, REQ-F-045, REQ-F-046, REQ-F-052 |
| PATCH | `/services/{serviceId}` | updateService | REQ-F-010, REQ-F-045, REQ-F-046, REQ-F-052, REQ-F-054, REQ-F-055 |
| DELETE | `/services/{serviceId}` | deleteService | REQ-F-010, REQ-F-053 |
| GET | `/masters` | listMasters | REQ-F-003, REQ-F-012 |
| POST | `/masters` | createMaster | REQ-F-010, REQ-F-047, REQ-F-051 |
| PATCH | `/masters/{masterId}` | updateMaster | REQ-F-010, REQ-F-047, REQ-F-051, REQ-F-054, REQ-F-055 |
| DELETE | `/masters/{masterId}` | deleteMaster | REQ-F-010, REQ-F-053 |
| GET | `/masters/{masterId}/schedule` | getSchedule | REQ-F-010, REQ-F-048, REQ-F-049 |
| PATCH | `/masters/{masterId}/schedule` | updateSchedule | REQ-F-010, REQ-F-048, REQ-F-049, REQ-F-050 |
| GET | `/masters/{masterId}/slots` | listSlots | REQ-F-004, REQ-F-012, REQ-F-017, REQ-F-018, REQ-F-021, REQ-F-022, REQ-F-023, REQ-F-025, REQ-F-026, REQ-F-055 |
| GET | `/bookings` | listBookings | REQ-F-009, REQ-F-010, REQ-F-030, REQ-F-031, REQ-F-032, REQ-F-033 |
| POST | `/bookings` | createBooking | REQ-F-008, REQ-F-009, REQ-F-010, REQ-F-011, REQ-F-012, REQ-F-013, REQ-F-014, REQ-F-015, REQ-F-016, REQ-F-017, REQ-F-018, REQ-F-019, REQ-F-020, REQ-F-021, REQ-F-022, REQ-F-023, REQ-F-024, REQ-F-025, REQ-F-026, REQ-F-027, REQ-F-028, REQ-F-029, REQ-F-055, REQ-F-056, REQ-F-059, REQ-F-060 |
| GET | `/bookings/{bookingId}` | getBooking | REQ-F-009, REQ-F-010, REQ-F-031 |
| PATCH | `/bookings/{bookingId}` | updateBooking | REQ-F-010, REQ-F-017, REQ-F-021, REQ-F-022, REQ-F-023, REQ-F-024, REQ-F-025, REQ-F-026, REQ-F-027, REQ-F-038, REQ-F-039, REQ-F-040, REQ-F-041, REQ-F-042, REQ-F-043, REQ-F-044, REQ-F-057, REQ-F-062, REQ-F-063, REQ-F-064 |
| POST | `/bookings/{bookingId}/cancellation` | cancelBooking | REQ-F-009, REQ-F-010, REQ-F-025, REQ-F-034, REQ-F-035, REQ-F-036, REQ-F-037, REQ-F-041, REQ-F-058, REQ-F-061 |

## 5. Фактичні перевірки цього етапу

- `python3 scripts/check_lab3_scenarios.py`: exit 0; відтворено розрахунки B0/S2, перевірено залежності та ресурси. [Журнал](../../logs/lab5/audit/lab3-check.txt). Це не рішення PLAN-GATE.
- `/tmp/beauty-lab4-venv/bin/python scripts/check_lab4.py`: exit 1, `ModuleNotFoundError: No module named 'yaml'`. [Журнал](../../logs/lab5/audit/lab4-static-check.txt). Валідація не почалася; потрібне відновлення залежностей за lock-файлом. Не є дефектом контракту або TDD RED. Встановлення пакетів і mock HTTP у цьому аудиті не виконувалися.
- Baseline: 8/8 SHA-256 збігаються; тексти REQ/AC/GWT відповідають SRS. Історичний API-GATE збережений, нового PASS валідатора не заявлено.
- Продуктові тести, TEST-GATE, SPEC-ADDENDUM-GATE, фінальні verification/validation: **NOT RUN**.

План наступного етапу, каталог тестів, нова вимога та команди: [implementation-plan.md](implementation-plan.md). Структура доказів: [logs/lab5/README.md](../../logs/lab5/README.md).
