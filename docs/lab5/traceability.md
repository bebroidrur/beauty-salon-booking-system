# ЛР5 — індекс простежуваності за фактичним JUnit

Джерело: `logs/lab5/final/verification/junit.xml`. Згенеровано `scripts/lab5_traceability.py`. Baseline AC/GWT перенесено без нових ID. Позначка PASSED означає результат пов’язаного тесту, **не повне приймання вимоги або всіх її AC/GWT**. Контрактний smoke перевіряє форму відповіді, не всі побічні ефекти. BDD-маркери позначають пов’язаний сценарій; повний Then може потребувати сукупності тестів, а відкриті випадки залишаються BLOCKED.

Код: F-001–003/005–007/010/045–049 — `salon/service.py`, `salon/auth.py`, `salon/contract.py`; F-008–044/050–055 — `salon/booking_service.py`; F-056–064 — `salon/notifications.py`, `salon/mail_worker.py`; NF-004/006 — password hashing, `salon/events.py`; сховище — `salon/store.py`. F-004/018 (слоти) не реалізовані. F-021, F-040/043, F-053–055, F-060/063 мають обмеження D-02–D-06; деталі в README. Решта NF не приймались.

| REQ | Назва | Прямі AC baseline | Прямі GWT baseline | Поведінкові тести: passed / failed / skipped | Контрактні тести: passed / failed / skipped |
| --- | --- | --- | --- | --- | --- |
| REQ-F-001 | Каталог послуг | — | — | 3 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-002 | Дані послуги | — | — | 2 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-003 | Інформація про майстрів | — | — | 2 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-004 | Перегляд часових слотів | — | — | — | 0 / 0 / 1 |
| REQ-F-005 | Реєстрація клієнта | AC-REQ-F-005-01 | — | 6 / 0 / 0 | 8 / 0 / 1 |
| REQ-F-006 | Унікальність email | AC-REQ-F-006-01 | — | 1 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-007 | Вхід клієнта | AC-REQ-F-007-01 | — | 7 / 0 / 0 | 8 / 0 / 1 |
| REQ-F-008 | Доступ до створення запису | — | GWT-001 | 1 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-009 | Власні записи клієнта | AC-REQ-F-009-01 | GWT-019 | 1 / 0 / 0 | 4 / 0 / 0 |
| REQ-F-010 | Адміністративний доступ | AC-REQ-F-010-01 | — | 4 / 0 / 0 | 21 / 0 / 1 |
| REQ-F-011 | Склад запису | — | GWT-001 | 1 / 0 / 0 | 8 / 0 / 1 |
| REQ-F-012 | Вибір майстра | AC-REQ-F-012-01 | GWT-001, GWT-002 | 4 / 0 / 0 | 2 / 0 / 1 |
| REQ-F-013 | Створення адміністратором | — | GWT-005 | 4 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-014 | Підтвердження запису | — | GWT-001 | 1 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-015 | Фіксація даних послуги | AC-REQ-F-015-01 | GWT-001 | 2 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-016 | Розрахунок завершення | AC-REQ-F-016-01 | GWT-001 | 1 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-017 | Часовий пояс | — | — | 2 / 0 / 0 | 2 / 0 / 1 |
| REQ-F-018 | Крок початку | AC-REQ-F-018-01 | — | — | 1 / 0 / 1 |
| REQ-F-019 | Мінімальний строк клієнта | AC-REQ-F-019-01 | GWT-003, GWT-004 | 3 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-020 | Мінімальний строк адміністратора | AC-REQ-F-020-01 | GWT-005 | 3 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-021 | Горизонт бронювання | AC-REQ-F-021-01 | GWT-006, GWT-007 | 1 / 0 / 0 | 2 / 0 / 1 |
| REQ-F-022 | Вміщення в графік | AC-REQ-F-022-01 | GWT-008, GWT-009 | 5 / 0 / 0 | 2 / 0 / 1 |
| REQ-F-023 | Конфлікт майстра | AC-REQ-F-023-01 | GWT-010 | 2 / 0 / 0 | 2 / 0 / 1 |
| REQ-F-024 | Конфлікт клієнта | AC-REQ-F-024-01 | GWT-011 | 2 / 0 / 0 | 2 / 0 / 0 |
| REQ-F-025 | Скасовані записи й доступність | AC-REQ-F-025-01 | GWT-018 | 3 / 0 / 0 | 3 / 0 / 1 |
| REQ-F-026 | Суміжні записи | AC-REQ-F-026-01 | GWT-012 | 2 / 0 / 0 | 2 / 0 / 1 |
| REQ-F-027 | Перевірка при збереженні | AC-REQ-F-027-01 | GWT-013 | 2 / 0 / 0 | 2 / 0 / 0 |
| REQ-F-028 | Одночасне бронювання | AC-REQ-F-028-01 | GWT-014 | 2 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-029 | Результат конфліктного бронювання | AC-REQ-F-029-01 | GWT-013, GWT-014 | 4 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-030 | Актуальні записи | AC-REQ-F-030-01 | GWT-029 | 1 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-031 | Деталі запису | — | — | 2 / 0 / 0 | 2 / 0 / 0 |
| REQ-F-032 | Історія записів | — | — | 1 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-033 | Перехід до історії | AC-REQ-F-033-01 | GWT-029 | 1 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-034 | Скасування клієнтом | AC-REQ-F-034-01 | GWT-015, GWT-035 | 3 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-035 | Пізнє скасування клієнтом | AC-REQ-F-035-01 | GWT-016 | 3 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-036 | Скасування адміністратором | AC-REQ-F-036-01 | GWT-017 | 3 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-037 | Результат скасування | — | GWT-015, GWT-017 | 3 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-038 | Відсутність редагування клієнтом | — | — | 1 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-039 | Редагування адміністратором | — | GWT-020, GWT-021 | 1 / 0 / 0 | 8 / 0 / 1 |
| REQ-F-040 | Перевірка зміни | AC-REQ-F-040-01 | GWT-021, GWT-022, GWT-023, GWT-024 | 3 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-041 | Незмінність історії | AC-REQ-F-041-01 | GWT-028 | 4 / 0 / 0 | 2 / 0 / 0 |
| REQ-F-042 | Зміна без заміни послуги | AC-REQ-F-042-01 | GWT-020 | 1 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-043 | Явна заміна послуги | AC-REQ-F-043-01 | GWT-021 | 1 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-044 | Завершення після перенесення | AC-REQ-F-044-01 | GWT-020 | 1 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-045 | Керування послугою | — | — | 15 / 0 / 0 | 2 / 0 / 0 |
| REQ-F-046 | Єдина тривалість | — | — | 9 / 0 / 0 | 2 / 0 / 0 |
| REQ-F-047 | Керування майстром | — | — | 3 / 0 / 0 | 2 / 0 / 0 |
| REQ-F-048 | Тижневий графік | — | — | 4 / 0 / 0 | 9 / 0 / 1 |
| REQ-F-049 | Винятки графіка | AC-REQ-F-049-01 | GWT-027 | 7 / 0 / 0 | 2 / 0 / 0 |
| REQ-F-050 | Конфлікт зміни графіка | AC-REQ-F-050-01 | GWT-025, GWT-026 | 1 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-051 | Видалення послуги з переліку майстра | AC-REQ-F-051-01 | — | 2 / 0 / 0 | 2 / 0 / 0 |
| REQ-F-052 | Захист даних запису від змін каталогу | AC-REQ-F-052-01 | — | 1 / 0 / 0 | 2 / 0 / 0 |
| REQ-F-053 | Блокування фізичного видалення | AC-REQ-F-053-01 | — | 2 / 0 / 0 | 2 / 0 / 0 |
| REQ-F-054 | Деактивація | AC-REQ-F-054-01 | GWT-030 | 3 / 0 / 0 | 2 / 0 / 0 |
| REQ-F-055 | Нові записи після деактивації | AC-REQ-F-055-01 | GWT-030 | 3 / 0 / 0 | 3 / 0 / 1 |
| REQ-F-056 | Підтвердження створення | AC-REQ-F-056-01 | GWT-001, GWT-005, GWT-034 | 9 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-057 | Повідомлення про зміну | AC-REQ-F-057-01 | GWT-020, GWT-021, GWT-031, GWT-032, GWT-033 | 6 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-058 | Повідомлення про скасування | — | GWT-015, GWT-017, GWT-035 | 3 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-059 | Нагадування | AC-REQ-F-059-01 | — | 6 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-060 | Створення менш ніж за 24 години | AC-REQ-F-060-01 | GWT-034 | 3 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-061 | Скасування нагадувань | AC-REQ-F-061-01 | GWT-015, GWT-035 | 2 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-062 | Попереднє нагадування при перенесенні | AC-REQ-F-062-01 | GWT-031, GWT-032, GWT-033 | 4 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-063 | Нове нагадування при перенесенні | AC-REQ-F-063-01, AC-REQ-F-063-02 | GWT-031, GWT-032 | 3 / 0 / 0 | 1 / 0 / 0 |
| REQ-F-064 | Перенесення менш ніж за 24 години | AC-REQ-F-064-01 | GWT-033 | 3 / 0 / 0 | 1 / 0 / 0 |
| REQ-NF-001 | Час відповіді на перегляд | AC-REQ-NF-001-01 | — | — | — |
| REQ-NF-002 | Збереження результатів після перезапуску | AC-REQ-NF-002-01 | — | 1 / 0 / 0 | — |
| REQ-NF-003 | Відновлення після відмови застосунку | AC-REQ-NF-003-01 | — | — | — |
| REQ-NF-004 | Відсутність зберігання паролів у відкритому вигляді | AC-REQ-NF-004-01 | — | 3 / 0 / 0 | — |
| REQ-NF-005 | Конфіденційність передавання | AC-REQ-NF-005-01 | — | — | — |
| REQ-NF-006 | Нерозголошення даних у технічній діагностиці | AC-REQ-NF-006-01 | — | 4 / 0 / 0 | — |
| REQ-NF-007 | Адаптивність інтерфейсу | AC-REQ-NF-007-01 | — | — | — |
| REQ-NF-008 | Робота в настільних і мобільних браузерах | AC-REQ-NF-008-01 | — | — | — |
| REQ-NF-009 | Керування клавіатурою | AC-REQ-NF-009-01 | — | — | — |
| REQ-NF-010 | Позначення полів і повідомлень | AC-REQ-NF-010-01 | — | — | — |
| REQ-NF-011 | Доступність сервісу в часі | AC-REQ-NF-011-01 | — | — | — |

## Точні testcase ID з JUnit

### REQ-F-001

- `tests.lab5.test_a_catalog_access::test_public_catalog[/services-ServiceList]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_public_catalog[/masters-MasterList]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[listServices]` — PASSED, contract.
- `tests.network.test_local_transports::test_real_http` — PASSED, behavior.

### REQ-F-002

- `tests.lab5.test_a_catalog_access::test_public_catalog[/services-ServiceList]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_public_catalog[/masters-MasterList]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[listServices]` — PASSED, contract.

### REQ-F-003

- `tests.lab5.test_a_catalog_access::test_public_catalog[/services-ServiceList]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_public_catalog[/masters-MasterList]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[listMasters]` — PASSED, contract.

### REQ-F-004

- `tests.lab5.test_e_contract::test_success_contract[listSlots]` — SKIPPED, contract.

### REQ-F-005

- `tests.lab5.test_a_catalog_access::test_registration_login_persistence` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_registration[payload0]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_registration[payload1]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_registration[payload2]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_registration[payload3]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_malformed_json` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[registerClient]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-registration-fields]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[extra-registration-role]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-email]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[empty-booking-patch]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-booking-date]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-slot-query]` — SKIPPED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-category]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-auth]` — PASSED, contract.

### REQ-F-006

- `tests.lab5.test_a_catalog_access::test_registration_login_persistence` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[registerClient]` — PASSED, contract.

### REQ-F-007

- `tests.lab5.test_a_catalog_access::test_registration_login_persistence` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_registration[payload0]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_registration[payload1]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_registration[payload2]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_registration[payload3]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_bad_credentials[alice@example.test-wrong]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_bad_credentials[absent@example.test-test-password]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[login]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-registration-fields]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[extra-registration-role]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-email]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[empty-booking-patch]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-booking-date]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-slot-query]` — SKIPPED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-category]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-auth]` — PASSED, contract.

### REQ-F-008

- `tests.lab5.test_b_bookings::test_create_snapshot` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.

### REQ-F-009

- `tests.lab5.test_b_bookings::test_ownership_and_roles` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[listBookings]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[getBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[cancelBooking]` — PASSED, contract.

### REQ-F-010

- `tests.lab5.test_a_catalog_access::test_crud_boundary[services-payload0-Service]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_crud_boundary[masters-payload1-Master]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_schedule_replace_and_permissions` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_ownership_and_roles` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[login]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[createService]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateService]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[deleteService]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[createMaster]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateMaster]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[deleteMaster]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[getSchedule]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateSchedule]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[listBookings]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[getBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[cancelBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-registration-fields]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[extra-registration-role]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-email]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[empty-booking-patch]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-booking-date]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-slot-query]` — SKIPPED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-category]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-auth]` — PASSED, contract.

### REQ-F-011

- `tests.lab5.test_b_bookings::test_create_snapshot` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-registration-fields]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[extra-registration-role]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-email]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[empty-booking-patch]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-booking-date]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-slot-query]` — SKIPPED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-category]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-auth]` — PASSED, contract.

### REQ-F-012

- `tests.lab5.test_b_bookings::test_create_snapshot` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_work_interval[2026-11-04T17:00:00+02:00-201]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_work_interval[2026-11-04T17:30:00+02:00-422]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_incompatible_and_inactive` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[listMasters]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[listSlots]` — SKIPPED, contract.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.

### REQ-F-013

- `tests.lab5.test_b_bookings::test_lead_boundary[alice-120-201]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_lead_boundary[alice-119-422]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_lead_boundary[admin-60-201]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_ownership_and_roles` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.

### REQ-F-014

- `tests.lab5.test_b_bookings::test_create_snapshot` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.

### REQ-F-015

- `tests.lab5.test_b_bookings::test_create_snapshot` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_restart_persistence` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.

### REQ-F-016

- `tests.lab5.test_b_bookings::test_create_snapshot` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.

### REQ-F-017

- `tests.lab5.test_b_bookings::test_create_snapshot` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[listSlots]` — SKIPPED, contract.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.
- `tests.lab5.test_unit_rules::test_offset_conversion_same_instant` — PASSED, behavior.

### REQ-F-018

- `tests.lab5.test_e_contract::test_success_contract[listSlots]` — SKIPPED, contract.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.

### REQ-F-019

- `tests.lab5.test_b_bookings::test_lead_boundary[alice-120-201]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_lead_boundary[alice-119-422]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_lead_boundary[admin-60-201]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.

### REQ-F-020

- `tests.lab5.test_b_bookings::test_lead_boundary[alice-120-201]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_lead_boundary[alice-119-422]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_lead_boundary[admin-60-201]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.

### REQ-F-021

- `tests.lab5.test_b_bookings::test_far_outside_horizon` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[listSlots]` — SKIPPED, contract.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.

### REQ-F-022

- `tests.lab5.test_b_bookings::test_work_interval[2026-11-04T17:00:00+02:00-201]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_work_interval[2026-11-04T17:30:00+02:00-422]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[listSlots]` — SKIPPED, contract.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.
- `tests.lab5.test_unit_rules::test_work_interval_rule[17:00-18:00-True]` — PASSED, behavior.
- `tests.lab5.test_unit_rules::test_work_interval_rule[17:30-18:30-False]` — PASSED, behavior.
- `tests.lab5.test_unit_rules::test_work_interval_rule[08:30-09:30-False]` — PASSED, behavior.

### REQ-F-023

- `tests.lab5.test_b_bookings::test_conflicts_and_adjacency[bob-master]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_conflicts_and_adjacency[alice-master2]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[listSlots]` — SKIPPED, contract.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.

### REQ-F-024

- `tests.lab5.test_b_bookings::test_conflicts_and_adjacency[bob-master]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_conflicts_and_adjacency[alice-master2]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.

### REQ-F-025

- `tests.lab5.test_b_bookings::test_cancellation_boundary[alice-1440-200]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_cancellation_boundary[alice-1439-422]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_cancellation_boundary[admin-60-200]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[listSlots]` — SKIPPED, contract.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[cancelBooking]` — PASSED, contract.

### REQ-F-026

- `tests.lab5.test_b_bookings::test_conflicts_and_adjacency[bob-master]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_conflicts_and_adjacency[alice-master2]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[listSlots]` — SKIPPED, contract.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.

### REQ-F-027

- `tests.lab5.test_b_bookings::test_conflicts_and_adjacency[bob-master]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_conflicts_and_adjacency[alice-master2]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.

### REQ-F-028

- `tests.lab5.test_b_bookings::test_atomic_competition[False]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_atomic_competition[True]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.

### REQ-F-029

- `tests.lab5.test_b_bookings::test_conflicts_and_adjacency[bob-master]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_conflicts_and_adjacency[alice-master2]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_atomic_competition[False]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_atomic_competition[True]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.

### REQ-F-030

- `tests.lab5.test_b_bookings::test_history_boundary` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[listBookings]` — PASSED, contract.

### REQ-F-031

- `tests.lab5.test_b_bookings::test_create_snapshot` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_restart_persistence` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[listBookings]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[getBooking]` — PASSED, contract.

### REQ-F-032

- `tests.lab5.test_b_bookings::test_history_boundary` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[listBookings]` — PASSED, contract.

### REQ-F-033

- `tests.lab5.test_b_bookings::test_history_boundary` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[listBookings]` — PASSED, contract.

### REQ-F-034

- `tests.lab5.test_b_bookings::test_cancellation_boundary[alice-1440-200]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_cancellation_boundary[alice-1439-422]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_cancellation_boundary[admin-60-200]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[cancelBooking]` — PASSED, contract.

### REQ-F-035

- `tests.lab5.test_b_bookings::test_cancellation_boundary[alice-1440-200]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_cancellation_boundary[alice-1439-422]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_cancellation_boundary[admin-60-200]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[cancelBooking]` — PASSED, contract.

### REQ-F-036

- `tests.lab5.test_b_bookings::test_cancellation_boundary[alice-1440-200]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_cancellation_boundary[alice-1439-422]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_cancellation_boundary[admin-60-200]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[cancelBooking]` — PASSED, contract.

### REQ-F-037

- `tests.lab5.test_b_bookings::test_cancellation_boundary[alice-1440-200]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_cancellation_boundary[alice-1439-422]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_cancellation_boundary[admin-60-200]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[cancelBooking]` — PASSED, contract.

### REQ-F-038

- `tests.lab5.test_b_bookings::test_ownership_and_roles` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.

### REQ-F-039

- `tests.lab5.test_b_bookings::test_patch_snapshots` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-registration-fields]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[extra-registration-role]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-email]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[empty-booking-patch]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-booking-date]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-slot-query]` — SKIPPED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-category]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-auth]` — PASSED, contract.

### REQ-F-040

- `tests.lab5.test_b_bookings::test_patch_rollback[change0]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_patch_rollback[change1]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_patch_rollback[change2]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.

### REQ-F-041

- `tests.lab5.test_b_bookings::test_history_boundary` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_cancellation_boundary[alice-1440-200]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_cancellation_boundary[alice-1439-422]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_cancellation_boundary[admin-60-200]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[cancelBooking]` — PASSED, contract.

### REQ-F-042

- `tests.lab5.test_b_bookings::test_patch_snapshots` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.

### REQ-F-043

- `tests.lab5.test_b_bookings::test_patch_snapshots` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.

### REQ-F-044

- `tests.lab5.test_b_bookings::test_patch_snapshots` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.

### REQ-F-045

- `tests.lab5.test_a_catalog_access::test_crud_boundary[services-payload0-Service]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_crud_boundary[masters-payload1-Master]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_service[change0]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_service[change1]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_service[change2]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_service[change3]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createService]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateService]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_valid_fractional_uah[0.07]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_valid_fractional_uah[0.29]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_valid_fractional_uah[4.01]` — PASSED, behavior.
- `tests.lab5.test_unit_rules::test_decimal_rule[0-True]` — PASSED, behavior.
- `tests.lab5.test_unit_rules::test_decimal_rule[0.07-True]` — PASSED, behavior.
- `tests.lab5.test_unit_rules::test_decimal_rule[0.29-True]` — PASSED, behavior.
- `tests.lab5.test_unit_rules::test_decimal_rule[4.01-True]` — PASSED, behavior.
- `tests.lab5.test_unit_rules::test_decimal_rule[0.001-False]` — PASSED, behavior.
- `tests.lab5.test_unit_rules::test_decimal_rule[-1-False]` — PASSED, behavior.

### REQ-F-046

- `tests.lab5.test_a_catalog_access::test_crud_boundary[services-payload0-Service]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_crud_boundary[masters-payload1-Master]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_service[change0]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_service[change1]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_service[change2]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_service[change3]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createService]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateService]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_valid_fractional_uah[0.07]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_valid_fractional_uah[0.29]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_valid_fractional_uah[4.01]` — PASSED, behavior.

### REQ-F-047

- `tests.lab5.test_a_catalog_access::test_crud_boundary[services-payload0-Service]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_crud_boundary[masters-payload1-Master]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_missing_master_service` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createMaster]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateMaster]` — PASSED, contract.

### REQ-F-048

- `tests.lab5.test_a_catalog_access::test_schedule_replace_and_permissions` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_schedule_rolls_back[exceptions0]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_schedule_rolls_back[exceptions1]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_schedule_rolls_back[exceptions2]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[getSchedule]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateSchedule]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-registration-fields]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[extra-registration-role]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-email]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[empty-booking-patch]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-booking-date]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-slot-query]` — SKIPPED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[invalid-category]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_existing_negative_inputs[missing-auth]` — PASSED, contract.

### REQ-F-049

- `tests.lab5.test_a_catalog_access::test_schedule_replace_and_permissions` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_schedule_rolls_back[exceptions0]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_schedule_rolls_back[exceptions1]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_invalid_schedule_rolls_back[exceptions2]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[getSchedule]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateSchedule]` — PASSED, contract.
- `tests.lab5.test_unit_rules::test_work_interval_rule[17:00-18:00-True]` — PASSED, behavior.
- `tests.lab5.test_unit_rules::test_work_interval_rule[17:30-18:30-False]` — PASSED, behavior.
- `tests.lab5.test_unit_rules::test_work_interval_rule[08:30-09:30-False]` — PASSED, behavior.

### REQ-F-050

- `tests.lab5.test_b_bookings::test_protect_live_bookings` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[updateSchedule]` — PASSED, contract.

### REQ-F-051

- `tests.lab5.test_b_bookings::test_protect_live_bookings` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createMaster]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateMaster]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_contract_conflict_codes` — PASSED, behavior.

### REQ-F-052

- `tests.lab5.test_b_bookings::test_patch_snapshots` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createService]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateService]` — PASSED, contract.

### REQ-F-053

- `tests.lab5.test_b_bookings::test_protect_live_bookings` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[deleteService]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[deleteMaster]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_contract_conflict_codes` — PASSED, behavior.

### REQ-F-054

- `tests.lab5.test_a_catalog_access::test_crud_boundary[services-payload0-Service]` — PASSED, behavior.
- `tests.lab5.test_a_catalog_access::test_crud_boundary[masters-payload1-Master]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_incompatible_and_inactive` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[updateService]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateMaster]` — PASSED, contract.

### REQ-F-055

- `tests.lab5.test_b_bookings::test_work_interval[2026-11-04T17:00:00+02:00-201]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_work_interval[2026-11-04T17:30:00+02:00-422]` — PASSED, behavior.
- `tests.lab5.test_b_bookings::test_incompatible_and_inactive` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[updateService]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[updateMaster]` — PASSED, contract.
- `tests.lab5.test_e_contract::test_success_contract[listSlots]` — SKIPPED, contract.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.

### REQ-F-056

- `tests.lab5.test_c_notifications_logging::test_creation_notifications[48-1]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_creation_notifications[24-1]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_creation_notifications[12-0]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_failed_mutation_no_success_mail` — PASSED, behavior.
- `tests.lab5.test_d_mail_worker::test_deliver_only_due_once` — PASSED, behavior.
- `tests.lab5.test_d_mail_worker::test_transport_failure_safe_and_retained` — PASSED, behavior.
- `tests.lab5.test_d_mail_worker::test_worker_logs_system_events` — PASSED, behavior.
- `tests.lab5.test_d_mail_worker::test_smtp_message_and_tls` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.
- `tests.network.test_local_transports::test_real_smtp_outbox` — PASSED, behavior.

### REQ-F-057

- `tests.lab5.test_c_notifications_logging::test_reschedule_notifications[48-1]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_reschedule_notifications[24-1]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_reschedule_notifications[12-0]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_failed_mutation_no_success_mail` — PASSED, behavior.
- `tests.lab5.test_d_mail_worker::test_old_reminder_never_sent` — PASSED, behavior.
- `tests.lab5.test_d_mail_worker::test_smtp_message_and_tls` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.

### REQ-F-058

- `tests.lab5.test_c_notifications_logging::test_cancellation_cancels_reminders` — PASSED, behavior.
- `tests.lab5.test_d_mail_worker::test_old_reminder_never_sent` — PASSED, behavior.
- `tests.lab5.test_d_mail_worker::test_smtp_message_and_tls` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[cancelBooking]` — PASSED, contract.

### REQ-F-059

- `tests.lab5.test_c_notifications_logging::test_creation_notifications[48-1]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_creation_notifications[24-1]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_creation_notifications[12-0]` — PASSED, behavior.
- `tests.lab5.test_d_mail_worker::test_deliver_only_due_once` — PASSED, behavior.
- `tests.lab5.test_d_mail_worker::test_smtp_message_and_tls` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.
- `tests.network.test_local_transports::test_real_smtp_outbox` — PASSED, behavior.

### REQ-F-060

- `tests.lab5.test_c_notifications_logging::test_creation_notifications[48-1]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_creation_notifications[24-1]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_creation_notifications[12-0]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[createBooking]` — PASSED, contract.

### REQ-F-061

- `tests.lab5.test_c_notifications_logging::test_cancellation_cancels_reminders` — PASSED, behavior.
- `tests.lab5.test_d_mail_worker::test_old_reminder_never_sent` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[cancelBooking]` — PASSED, contract.

### REQ-F-062

- `tests.lab5.test_c_notifications_logging::test_reschedule_notifications[48-1]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_reschedule_notifications[24-1]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_reschedule_notifications[12-0]` — PASSED, behavior.
- `tests.lab5.test_d_mail_worker::test_old_reminder_never_sent` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.

### REQ-F-063

- `tests.lab5.test_c_notifications_logging::test_reschedule_notifications[48-1]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_reschedule_notifications[24-1]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_reschedule_notifications[12-0]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.

### REQ-F-064

- `tests.lab5.test_c_notifications_logging::test_reschedule_notifications[48-1]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_reschedule_notifications[24-1]` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_reschedule_notifications[12-0]` — PASSED, behavior.
- `tests.lab5.test_e_contract::test_success_contract[updateBooking]` — PASSED, contract.

### REQ-NF-001

Виконаних пов’язаних тестів немає.

### REQ-NF-002

- `tests.lab5.test_b_bookings::test_restart_persistence` — PASSED, behavior.

### REQ-NF-003

Виконаних пов’язаних тестів немає.

### REQ-NF-004

- `tests.lab5.test_a_catalog_access::test_registration_login_persistence` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_safe_system_logs` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_internal_error_logs_no_exception_data` — PASSED, behavior.

### REQ-NF-005

Виконаних пов’язаних тестів немає.

### REQ-NF-006

- `tests.lab5.test_c_notifications_logging::test_safe_system_logs` — PASSED, behavior.
- `tests.lab5.test_c_notifications_logging::test_internal_error_logs_no_exception_data` — PASSED, behavior.
- `tests.lab5.test_d_mail_worker::test_transport_failure_safe_and_retained` — PASSED, behavior.
- `tests.lab5.test_d_mail_worker::test_worker_logs_system_events` — PASSED, behavior.

### REQ-NF-007

Виконаних пов’язаних тестів немає.

### REQ-NF-008

Виконаних пов’язаних тестів немає.

### REQ-NF-009

Виконаних пов’язаних тестів немає.

### REQ-NF-010

Виконаних пов’язаних тестів немає.

### REQ-NF-011

Виконаних пов’язаних тестів немає.

