# Схеми запитів і відповідей

Джерело істини: [openapi.yaml](../../spec/openapi.yaml), components/schemas. У таблиці required — обов’язкові поля; решта дозволених полів є optional. additionalProperties=false на об’єктах обмежує контракт його полями. Порожні PATCH заборонені minProperties=1. Числові обмеження й формат полів — проєктні рішення, див. [адендум](addendum.md).

| Схема | Поля | Обов’язкові |
| --- | --- | --- |
| ServiceCreate | name: string, description: string, price: number, durationMinutes: integer | name, description, price, durationMinutes |
| ServicePatch | name: string, description: string, price: number, durationMinutes: integer, active: boolean |  |
| Service | id: string, name: string, description: string, price: number, durationMinutes: integer, currency: string, active: boolean | id, name, description, price, durationMinutes, currency, active |
| MasterCreate | name: string, serviceIds: array | name, serviceIds |
| MasterPatch | name: string, serviceIds: array, active: boolean |  |
| Master | id: string, name: string, serviceIds: array, active: boolean | id, name, serviceIds, active |
| Registration | name: string, phone: string, email: string, password: string | name, phone, email, password |
| User | id: string, name: string, phone: string, email: string, role: string | id, name, phone, email, role |
| Login | email: string, password: string | email, password |
| Session | accessToken: string, tokenType: string, user: User | accessToken, tokenType, user |
| WorkInterval | start: string, end: string | start, end |
| Day |  |  |
| Week | monday: Day, tuesday: Day, wednesday: Day, thursday: Day, friday: Day, saturday: Day, sunday: Day | monday, tuesday, wednesday, thursday, friday, saturday, sunday |
| ScheduleException | date: string, kind: string, day: Day | date, kind, day |
| SchedulePatch | weekly: Week, exceptions: array |  |
| Schedule | masterId: string, timezone: string, weekly: Week, exceptions: array | masterId, timezone, weekly, exceptions |
| Slot | startsAt: string, endsAt: string | startsAt, endsAt |
| Availability | masterId: string, serviceId: string, timezone: string, slots: array | masterId, serviceId, timezone, slots |
| BookingCreate | serviceId: string, masterId: string, startsAt: string, clientId: string | serviceId, masterId, startsAt |
| BookingPatch | serviceId: string, masterId: string, startsAt: string |  |
| ServiceSnapshot | name: string, price: number, currency: string, durationMinutes: integer | name, price, currency, durationMinutes |
| Booking | id: string, clientId: string, serviceId: string, masterId: string, startsAt: string, masterName: string, serviceSnapshot: ServiceSnapshot, endsAt: string, status: string, category: string | id, clientId, serviceId, masterId, startsAt, masterName, serviceSnapshot, endsAt, status, category |
| ServiceList | items: array | items |
| MasterList | items: array | items |
| BookingList | items: array | items |
| ApiError | code: string, message: string, details: array | code, message |

Day — oneOf: working=false без interval або working=true з interval. Week має рівно сім іменованих днів. SchedulePatch замінює weekly та/або весь exceptions; винятки мають унікальні дати й переважають тижневий графік. Порядок start < end, відповідність kind/day і конфлікти записів — семантичні умови, не реалізовані JSON Schema чи mock.

Списки повертають {items: [...]}; порожній список є успішним 200. Пагінацію, сортування й обмеження розміру не вигадано. Slots потребує serviceId та date; bookings потребує category=current/history. Усі path ID — непрозорі непорожні рядки, не ключі БД.

BookingCreate: clientId optional у схемі, але обов’язковий для адміністратора й не дозволений клієнту; така залежність від сесії описана словами. BookingPatch не містить clientId. ServiceSnapshot містить назву, ціну UAH та тривалість на момент створення/заміни послуги. Незалежна зміна каталогу знімок не змінює. endsAt розраховується із зафіксованої тривалості.

Registration приймає name, phone, email, password; password writeOnly та відсутній у User/Session. Role не задається при реєстрації. Bearer — домовленість про транспорт доступу, не обіцянка JWT. Продуктові TLS, життєвий цикл сесій і зберігання паролів не перевірялися.

204 не має тіла. Для кожної іншої відповіді задані application/json, схема та приклад. Статичні приклади використовують умовний now=2026-10-20T12:00:00+03:00; вони не стають часовим годинником mock і не адаптуються до дати запуску.
