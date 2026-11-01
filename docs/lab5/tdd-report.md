# ЛР5 — фактичний звіт TDD

Дата: 2026-11-01. Гілка `lab5-tdd`. Вихідна редакція `fa016c8cc7a18f571f081d0642bb58f932dcde9d`. **Результат частковий: реалізовано 17 REST-маршрутів для погодженого піднабору; не всі 18 операцій завершено.** Baseline SRS, AC, BDD, матриця baseline та OpenAPI не змінені. PLAN-GATE — REVISE; новий людський GO не створений. Дозвіл на незалежні пакети й невирішені правила описані у [plan-review](plan-review.md).

## Реалізовані маршрути

| Метод | URI | Реалізована поведінка |
| --- | --- | --- |
| POST | /users | Валідація, унікальність email, роль client, scrypt password hash, збереження |
| POST | /sessions | Перевірка пароля, випадковий Bearer, збереження hash токена |
| GET, POST | /services | Публічний каталог; admin створення із UAH та єдиною тривалістю |
| PATCH, DELETE | /services/{serviceId} | Admin зміна/деактивація; захист актуальних записів; історичне видалення BLOCKED D-06 |
| GET, POST | /masters | Публічний список; admin створення з перевіркою serviceIds |
| PATCH, DELETE | /masters/{masterId} | Admin зміни, захист переліку послуг/актуальних записів; D-06 обмежує історію |
| GET, PATCH | /masters/{masterId}/schedule | Admin тижневий графік/винятки, семантична перевірка, rollback конфліктного графіка |
| GET, POST | /bookings | Власність/категорії; атомарне створення, snapshot, графік, конфлікти master/client, 2h client, email outbox |
| GET, PATCH | /bookings/{bookingId} | Права, деталі/історія, admin зміна, snapshot/endsAt, rollback; неоднозначні D-02–D-06 заблоковані |
| POST | /bookings/{bookingId}/cancellation | 24h client, виняток admin, незмінність історії, скасування нагадувань |
| **Не реалізовано: GET** | **/masters/{masterId}/slots** | **BLOCKED D-03: не погоджена прив'язка сітки; не підмінено статичними слотами** |

Детальні обмеження кожного D-випадку й тимчасових fail-fast guards наведені в [README](README.md). 500 для відкритого правила не є погодженим бізнес-результатом; ці випадки не прийнято. Без відповіді на запит уточнень не можна чесно заявити повну відповідність контракту та SRS.

## Реальні цикли

Кожна фаза має окремий Git-коміт, справжній журнал stdout/stderr, exit code, HEAD і source SHA-256. Runner: `scripts/lab5_run.py`; журнали не перезаписуються. RED коміти навмисно містять відсутню поведінку; фінальний код не використовує ці заглушки. Початкові документи аудиту також включено до першого RED-коміту, бо до цього вони були untracked.

| Група | RED | Причина RED | GREEN | REFACTOR |
| --- | --- | --- | --- | --- |
| A: доступ/каталог/графік | 21 failed | 404 замість потрібної поведінки: маршрути відсутні | 21 passed | 21 passed |
| B: бронювання | 23 failed | Booking routes відсутні; fixtures й SQLite працюють | 44 passed (A+B) | 44 passed |
| C: outbox/логування | 10 failed | Немає email jobs та logger events | 54 passed | 54 passed |
| D: worker/SMTP | 4 failed, потім розширений 5 failed | Worker не виконує доставку, SMTP interface не формує лист | 59 passed | 59 passed |
| E: незалежна контрактна регресія | 4 failed, 24 passed, 2 skipped | Float multipleOf помилково відхиляє валідні копійки; коди конфлікту відрізняються | 87 passed, 2 skipped | 87 passed, 2 skipped |

У GREEN/REFACTOR немає failed; пропуски E не приховані. RED 1/2/3/4 не були імпортними помилками. Помилки PyPI/DNS і bind/EPERM розглядалися як проблеми середовища, а не RED. Залежності встановлено після дозволеного доступу до PyPI; loopback тести повторено після дозволу bind. Історичний невдалий аудит ЛР4 не видалено; новий валідатор успішно виконано.

| Група | RED commit | GREEN commit | REFACTOR commit |
| --- | --- | --- | --- |
| A | `4c6bf8d` | `0113bbe` | `ef580ea` |
| B | `78664ca` | `cf4317a` | `6e834fb` |
| C | `50eb4e0` | `d56fabc` | `30e6229` |
| D | `5d9282a` | `a33edcb` | `7b42cd3` |
| E | `cd4b582` | `b5910b2` | `a465438` |

## Фінальні докази

- Повна фактично доступна регресія: **99 passed / 0 failed / 2 skipped**, exit 0; [regression.txt](../../logs/lab5/final/verification/regression.txt), [JUnit](../../logs/lab5/final/verification/junit.xml). 101 зібраний testcase; два skipped — success listSlots і негативний missing-slot-query, обидва BLOCKED D-03. Exit 0 не перетворює неповний API на прийнятий.
- Окремі unit-перевірки: **10 passed, 89 deselected**, exit 0; [unit.txt](../../logs/lab5/final/verification/unit.txt). Перевіряють точну десяткову кратність, межі робочого інтервалу, винятки та UTC/Kyiv.
- Реальний loopback HTTP/SMTP: **2 passed**, exit 0; [local-transports.txt](../../logs/lab5/final/verification/local-transports.txt). SMTP лист прийняв локальний контрольний сервер; зовнішня доставка не перевірялась.
- OpenAPI static: **PASS**, 18 operationId, 64 F-ID, 161 приклад, 8 baseline SHA-256, 75 рядків збережених зв'язків; [openapi-static.txt](../../logs/lab5/final/verification/openapi-static.txt). Контрактні приклади не підтверджують усю бізнес-поведінку.
- Контрактний піднабір: **24 passed, 2 skipped, 73 deselected**, exit 0; `contract-suite.txt`. Інтеграційний піднабір: **6 passed, 95 deselected**, exit 0; `integration-suite.txt`. Усі ці тести також входять у сукупну регресію; кількості не потрібно додавати до 99.

Фактичні команди запусків з абсолютним interpreter path записані в кожному журналі. Переносимі команди встановлення/запуску API, worker і всіх наборів: [README](README.md). Стек Flask/SQLite та залежності зафіксовано в requirements-lock.txt. Віртуальне середовище, тестові БД й робочі секрети не включено у коміти. Credentials у fixtures — лише синтетичні контрольні рядки.

## Покриття та проблеми

[Матриця ЛР5](traceability.md) згенерована з фактичного JUnit, містить усі 75 baseline REQ, їхні незмінені прямі AC/GWT, testcase ID та outcomes. Контрактні та поведінкові зв'язки розділено. Наявність REQ-маркера означає зв'язок, а не повне виконання всіх Then чи усіх AC; відсоток повного приймання не вигадано. GWT-006/007 і точні часові/сіткові очікування залишаються відкритими; GWT-013 у повному вигляді з попереднім GET slots ще не доведений. F-004/018 не завершено; D-02–D-06 обмежують відповідні F. NF-004 має реальні перевірки; persistence та безпечна діагностика реалізовані на пряме доручення, але це не затвердження всієї NF-гілки.

Виявлені та виправлені дефекти: десяткові ціни, коди конфліктів. Відомі відкриті питання: сітка/горизонт/окремі правила PATCH і нагадувань, технічна політика email retry, production TLS/ресурсні NF, UI/браузери. SQLite write lock під час SMTP та crash window між SMTP acceptance і commit описано в README. Немає гарантії exactly-once або зовнішньої доставки. Тест перезапуску перевіряє повторну ініціалізацію застосунку на тому самому файлі БД, не аварійне відновлення процесу/носія.

## Gate, верифікація та готовність до addendum

Технічні локальні TEST-GATE A–E перевірені перед відповідним GREEN, [рішення](test-gate.md). **Повний TEST-GATE — REVISE**, PLAN-GATE — REVISE, Human Review/Validation — NOT REVIEWED/NOT RUN. Не створено вигаданого Human GO; поточне доручення користувача дозволяло підготовку коду й технічні рішення, а не імітацію людського приймання.

Верифікація реалізованого піднабору виконана. Валідація користувачем не виконана: немає протоколу приймання/UI. Для вузького `REQ-F-065-B` підготовлено SPEC-ADDENDUM-GATE з рішенням **REVISE / NOT APPROVED**; REQ-F-065 до baseline не додано, а TDD нової вимоги не розпочинається до Human Review. До окремого addendum технічно підготовлені модулі й докази, але повне baseline API ще не завершене. Наступний крок — отримати відповідь на вже поданий пакет D-02–D-06, виконати окремий RED/GREEN/REFACTOR для слотів і погоджених меж, повторити весь набір, а потім повторно розглянути нову вимогу.
