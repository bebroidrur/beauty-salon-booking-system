# ЛР5 — звіт про рефакторинг

Baseline і OpenAPI не змінено. Рефакторинг виконувався після GREEN відповідної групи; нижче фактичні повторні прогони, не очікувані результати.

| Група | GREEN | Зміна структури | REFACTOR / доказ |
| --- | --- | --- | --- |
| A | 21 passed | Bearer-перевірку винесено з use-case service до `salon/auth.py` | 21 passed; `logs/lab5/refactor/a-catalog-access.txt` |
| B | 44 passed | Перетворення UTC/Europe/Kyiv та DAYS зосереджено в `salon/time_rules.py` | 44 passed; `logs/lab5/refactor/b-bookings.txt` |
| C | 54 passed | Формування дозволених полів журналу винесено до `salon/events.py`; HTTP й worker використовують спільний формат | 54 passed; `logs/lab5/refactor/c-notifications-logging.txt` |
| D | 59 passed | Чисте формування MIME-повідомлення відділено від SMTP I/O (`build_message`) | 59 passed; `logs/lab5/refactor/d-mail-worker.txt` |
| E | 87 passed, 2 skipped | Точну арифметику multipleOf винесено до `salon/numeric_validation.py` | 87 passed, 2 skipped; `logs/lab5/refactor/e-contract-regression.txt` |

У цих прогонах 0 failed. Два пропуски E — listSlots, не дефекти, приховані xfail. GREEN E виправляв поведінку (decimal і коди), а наступний REFACTOR лише відокремив числовий валідатор. Окремі Git-коміти для фаз наведено в tdd-report.md.

Архітектурна межа: Flask адаптує незмінний контракт; use cases працюють у транзакції Store; Bookings містить інваріанти; notifications формує outbox у тій самій транзакції; worker виконує зовнішню доставку. Перевірка response schema відбувається до commit, тому помилка формування відповіді не залишає успішно збережену часткову зміну. Годинник ін'єктується для детермінованих тестів.

Залишкові обмеження: SQLite серіалізує write requests; worker утримує транзакцію під час SMTP; READ теж використовує BEGIN IMMEDIATE. Це простий навчальний вибір, не доказ пропускної здатності. Декомпозиція не означає завершення D-02–D-06, UI чи NF. Source `src/booking.py` залишено як історичну заготовку; executable backend міститься у `salon/` і її не використовує.
