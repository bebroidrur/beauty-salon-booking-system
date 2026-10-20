# Модель REST-ресурсів

Статус: проєкт лабораторної №4, не нова baseline. [Контракт](../../spec/openapi.yaml).
Основа: [SRS 1.0](../../spec/SRS.md), [глосарій](../../spec/glossary.md), [scope](../../spec/scope.md).
7 типів ресурсів, 18 операцій, 11 шаблонів URI. Скасування — команда над записом, не восьмий тип сутності.

| Ресурс | URI | Значення |
| --- | --- | --- |
| Обліковий запис клієнта | /users | Лише реєстрація; довільний CRUD користувачів не передбачений |
| Сесія доступу | /sessions | Вхід; технічне представлення доступу, не нова роль |
| Послуга | /services, /services/{serviceId} | Ціна UAH, єдина тривалість, active |
| Майстер | /masters, /masters/{masterId} | Ім’я, послуги, active; без акаунта |
| Графік | /masters/{masterId}/schedule | Тиждень із сімома днями, винятки дат |
| Доступні слоти | /masters/{masterId}/slots | Похідна колекція за serviceId та date |
| Запис | /bookings, /bookings/{bookingId} | Один клієнт, послуга й майстер; знімок послуги |

GET читає; POST створює або скасовує; PATCH змінює передані поля; DELETE фізично видаляє послугу/майстра за відсутності пов’язаних актуальних записів. Скасування POST /bookings/{bookingId}/cancellation повертає збережений запис, а не видаляє історію. Повторне скасування історичного запису: 409 (REQ-F-041).

Власність визначається сесією. Клієнт не може PATCH запису чи адміністративних ресурсів. При створенні клієнт не передає clientId; адміністратор передає ID зареєстрованого клієнта. Це рольові умови, які mock із довільним Bearer не перевіряє. Публічні відповіді не містять контактів клієнтів. Master — сутність салону, а не користувач.

Час передається RFC3339 з offset; календарні межі й показ часу — Europe/Kyiv. durationMinutes не зобов’язана бути кратною 30: 30 хвилин — крок початків. Скасовані записи не займають час. category=current до endsAt, history після настання endsAt або скасування; status не має completed/no-show.

Email-підтвердження, зміна, скасування й нагадування є побічними ефектами погоджених операцій, не окремими публічними ресурсами. У цій лабораторній вони не виконуються. Немає платежів, філій, обладнання, перерв або кабінету майстра.

## Каталог операцій

| Метод і URI | operationId | Доступ | Успіх | Request schema |
| --- | --- | --- | --- | --- |
| POST `/users` | `registerClient` | public | 201 | Registration |
| POST `/sessions` | `login` | public | 200 | Login |
| GET `/services` | `listServices` | public | 200 | — |
| POST `/services` | `createService` | administrator | 201 | ServiceCreate |
| PATCH `/services/{serviceId}` | `updateService` | administrator | 200 | ServicePatch |
| DELETE `/services/{serviceId}` | `deleteService` | administrator | 204 | — |
| GET `/masters` | `listMasters` | public | 200 | — |
| POST `/masters` | `createMaster` | administrator | 201 | MasterCreate |
| PATCH `/masters/{masterId}` | `updateMaster` | administrator | 200 | MasterPatch |
| DELETE `/masters/{masterId}` | `deleteMaster` | administrator | 204 | — |
| GET `/masters/{masterId}/schedule` | `getSchedule` | administrator | 200 | — |
| PATCH `/masters/{masterId}/schedule` | `updateSchedule` | administrator | 200 | SchedulePatch |
| GET `/masters/{masterId}/slots` | `listSlots` | public | 200 | — |
| GET `/bookings` | `listBookings` | client or administrator | 200 | — |
| POST `/bookings` | `createBooking` | client or administrator | 201 | BookingCreate |
| GET `/bookings/{bookingId}` | `getBooking` | client or administrator | 200 | — |
| PATCH `/bookings/{bookingId}` | `updateBooking` | administrator | 200 | BookingPatch |
| POST `/bookings/{bookingId}/cancellation` | `cancelBooking` | client or administrator | 200 | — |
