# HTTP API: фактична реалізація

Оновлено в ЛР6 за `salon/app.py`, `salon/service.py`, `salon/booking_service.py`
і `salon/notifications.py`. Зареєстровано **17 із 18** контрактних операцій.
Це реалізований піднабір із відомими обмеженнями, не повна відповідність SRS.
[OpenAPI](../../spec/openapi.yaml) залишено без змін; вихідний проєкт ЛР4
і його приклади не означають, що кожен сценарій уже підтриманий.

Локальна адреса: `http://127.0.0.1:8000` після запуску `python -m salon serve`.
Prism на порту 4010 — окремий mock, а не сервер нижченаведених бізнес-правил.
Графічного інтерфейсу немає. Є клієнт і адміністратор; майстер — сутність
каталогу без облікового запису. Немає платежів, філій і кабінету майстра.

## Спільні правила виклику

- JSON-запити: `Content-Type: application/json`. Відповіді, крім 204, — JSON.
- Захищені операції: `Authorization: Bearer <accessToken>` із `POST /sessions`.
  Токен непрозорий, не JWT. TTL, logout, refresh і відновлення пароля відсутні.
- `{serviceId}`, `{masterId}`, `{bookingId}` — обов'язкові непорожні рядки
  в path, отримані з попередніх відповідей. Самі назви змінних не є ID.
- Тіла й вкладені об'єкти перевіряються схемою; зайві JSON-поля заборонені.
  PATCH має містити хоча б одне дозволене поле. Передані поля замінюються;
  для графіка замінюється вся передана `weekly` та/або весь `exceptions`.
- Єдиний query-параметр реалізованих операцій — обов'язковий
  `category=current` або `category=history` у `GET /bookings`.
  Інші операції нижче не мають оголошених query-параметрів; невідомі query
  реалізація не відхиляє, але вони не дають пошуку, пагінації чи фільтрації.
- Час — RFC3339 з явним offset; збережений показ — `Europe/Kyiv`.
- Схеми запитів/відповідей і їхні поля наведені в [схемах](schemas.md).
  У таблиці нижче `—` означає відсутність request body за контрактом.
- Загальні помилки: 400 `INVALID_REQUEST` для не-JSON/пошкодженого JSON;
  422 `VALIDATION_ERROR` для невідповідності схеми. Для захищених операцій
  401 `UNAUTHENTICATED`, для недостатньої ролі — 403 `FORBIDDEN`.
  Неочікувані збої — 500 `INTERNAL_ERROR`. Повна семантика — [помилки](errors.md).
  Колонка помилок нижче доповнює ці спільні правила.

## Реалізовані операції

| Метод і маршрут | operationId / доступ | Запит → успішна відповідь | Спеціальні помилки й обмеження |
| --- | --- | --- | --- |
| POST `/users` | `registerClient`, без входу | Registration → **201 User** | 409 EMAIL_IN_USE. Створює лише client; role у тілі заборонено. |
| POST `/sessions` | `login`, без входу | Login → **200 Session** | 401 UNAUTHENTICATED для неправильного пароля/невідомого email. Не повертає INVALID_CREDENTIALS. |
| GET `/services` | `listServices`, без входу | — → **200 ServiceList** | Повертає також неактивні послуги, без пагінації. |
| POST `/services` | `createService`, administrator | ServiceCreate → **201 Service** | Сервер задає active=true, currency=UAH та id. |
| PATCH `/services/{serviceId}` | `updateService`, administrator | ServicePatch → **200 Service** | 404 NOT_FOUND. Зміна каталогу не змінює snapshot наявних записів. |
| DELETE `/services/{serviceId}` | `deleteService`, administrator | — → **204**, порожнє тіло | 404 NOT_FOUND; 409 CURRENT_BOOKINGS_EXIST; за наявності лише історії — guard D-06 (500). |
| GET `/masters` | `listMasters`, без входу | — → **200 MasterList** | Повертає також неактивних майстрів, без пагінації. |
| POST `/masters` | `createMaster`, administrator | MasterCreate → **201 Master** | 422 VALIDATION_ERROR для невідомого serviceIds. Порожній список дозволено. Початковий графік: усі дні неробочі. |
| PATCH `/masters/{masterId}` | `updateMaster`, administrator | MasterPatch → **200 Master** | 404 NOT_FOUND; 422 VALIDATION_ERROR для невідомої послуги; 409 CURRENT_BOOKINGS_CONFLICT при вилученні послуги актуального запису. |
| DELETE `/masters/{masterId}` | `deleteMaster`, administrator | — → **204**, порожнє тіло | 404 NOT_FOUND; 409 CURRENT_BOOKINGS_EXIST; історія — guard D-06. За успіху видаляється також графік. |
| GET `/masters/{masterId}/schedule` | `getSchedule`, administrator | — → **200 Schedule** | 404 NOT_FOUND. Клієнту графік цим маршрутом недоступний. |
| PATCH `/masters/{masterId}/schedule` | `updateSchedule`, administrator | SchedulePatch → **200 Schedule** | 404 NOT_FOUND; 422 VALIDATION_ERROR для повторних дат, kind/day чи start ≥ end; 409 SCHEDULE_CONFLICT, якщо графік виключає актуальний запис. |
| GET `/bookings?category=current` або `history` | `listBookings`, client/administrator | — → **200 BookingList** | Відсутня/невірна category → 422 VALIDATION_ERROR. Клієнт бачить лише власні, адміністратор — всі записи вибраної категорії. |
| POST `/bookings` | `createBooking`, client/administrator | BookingCreate → **201 Booking** | 422 VALIDATION_ERROR для clientId не за роллю; 404 NOT_FOUND для невідомої послуги/майстра; 422 BOOKING_RULE_VIOLATION для неактивності, несумісності, строку <2 год для клієнта, невміщення в графік чи горизонту >30 дат; 409 TIME_UNAVAILABLE для перетину; D-02/D-03 нижче. |
| GET `/bookings/{bookingId}` | `getBooking`, client/administrator | — → **200 Booking** | 404 NOT_FOUND; 403 FORBIDDEN для чужого запису клієнта. |
| PATCH `/bookings/{bookingId}` | `updateBooking`, administrator | BookingPatch → **200 Booking** | 404 NOT_FOUND; 409 BOOKING_CHANGE_CONFLICT для історичного запису, графіка чи перетину; 422 BOOKING_RULE_VIOLATION за горизонтом >30; D-02–D-06 нижче. |
| POST `/bookings/{bookingId}/cancellation` | `cancelBooking`, client/administrator | — → **200 Booking** | 404 NOT_FOUND; 403 FORBIDDEN для чужого запису; 409 HISTORICAL_BOOKING; 422 CANCELLATION_TOO_LATE для клієнта менш ніж за 24 год. Адміністратор може скасувати актуальний запис без цієї часової межі. |

`POST /bookings` від клієнта **не містить clientId**. Адміністратор зобов'язаний
передати ID зареєстрованого клієнта; endpoint пошуку клієнтів відсутній.
Успішне створення одразу дає `status=confirmed`; `serviceSnapshot` фіксує
назву, ціну, валюту й тривалість. `endsAt` обчислюється з цієї тривалості.
Заміна послуги адміністратором оновлює snapshot; сама зміна часу/майстра — ні.

`category=history`, якщо status=cancelled або endsAt ≤ поточний час;
інакше `current`, включно з процесом надання послуги. Це не облік явки.
Історичний запис незмінний. Скасування зберігає його, звільняє час,
скасовує pending/failed нагадування. Суміжні інтервали не конфліктують;
перетин перевіряється для майстра та клієнта в транзакції SQLite.

Email створюється в outbox у тій самій транзакції. API-відповідь не означає
доставки листа: потрібен окремий налаштований worker. Нагадування створюється
за 24 години до початку, якщо до початку залишилося ≥24 год. Після зміни
надсилається changed, після скасування — cancelled. Доставка не має
автоматичного retry; можливий дубль при збої після SMTP і до commit.

## Запроєктовано, але не реалізовано

| Метод і маршрут | Контракт | Фактичний результат |
| --- | --- | --- |
| GET `/masters/{masterId}/slots?serviceId=…&date=YYYY-MM-DD` | `listSlots`, public; path masterId, query serviceId/date обов'язкові; 200 Availability з масивом Slot | Маршрут не зареєстрований: **404 INVALID_REQUEST**, без обчислення слотів. D-03 відкритий. |

`Slot` та `Availability` у [схемах](schemas.md) описують лише проєкт.
Не можна показувати клієнту календар доступних слотів на підставі цього API.
Час доводиться погоджувати окремо; остаточна перевірка відбувається при записі.

## Відомі межі реалізації

Ці guards повертають **500 INTERNAL_ERROR** із повідомленням про D-рішення
та rollback; це тимчасові обмеження ЛР5, не затверджені правила продукту:

| Рішення | Реальна умова |
| --- | --- |
| D-02 | При create/update різниця календарних дат у Kyiv дорівнює 29 або 30. Значення >30 дає 422. Внутрішні дати перевіряються іншими правилами. |
| D-03 | При create/update початок ≤ now, якщо виконання дійшло до guard. Клієнтський create може раніше повернути 422 через правило 2 годин. Сітка 30 хв у коді не перевіряється; її прив'язка не погоджена. |
| D-04 | Перенесення на ≥24 год від now, якщо для запису ніколи не було reminder у таблиці mail. Перенесення відкочується. |
| D-05 | PATCH запису з послугою, якої немає в serviceIds майстра. При create це 422 BOOKING_RULE_VIOLATION. |
| D-06 | PATCH запису з неактивною послугою/майстром; фізичне видалення сутності, яка має історичні записи (за актуальних спочатку 409). |

Відоме розходження з OpenAPI: `createBooking` може повернути 404 NOT_FOUND
для відсутньої послуги/майстра, хоча 404 для цієї операції не оголошено.
Поточний довідник фіксує поведінку, не виправляє контракт чи сервер.
Наявність ширшого списку responses у OpenAPI не доводить досяжність кожного
коду в реалізації (наприклад, login не має гілки 409).
