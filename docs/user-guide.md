# Інструкція користувача

Доступні REST API та адміністративний CLI; сторінок входу, календаря чи
графічного кабінету немає. Приклади нижче — для локального сервера на порту
8000 і тестових даних. HTTP-довідник: [операції](lab4/resource-model.md),
[поля об'єктів](lab4/schemas.md), [помилки](lab4/errors.md).

## Підготовка

1. Установіть залежності й створіть адміністратора командами з README у корені
   репозиторію. Запустіть `serve` з БД `runtime/salon.sqlite3`.
2. В іншому терміналі, теж з кореня репозиторію, задайте адресу:

```sh
BASE_URL='http://127.0.0.1:8000'
```

3. Після кожного запиту перевіряйте HTTP-статус (`curl -i` показує його).
   Значення в кутових дужках далі замініть даними зі своїх відповідей;
   не надсилайте `<service-id>` або `<token>` буквально.
   Не використовуйте наведений демонстраційний пароль для реальних даних.

## Клієнт: реєстрація й вхід

1. Зареєструйте тестового клієнта:

```sh
curl -i -X POST "$BASE_URL/users" -H 'Content-Type: application/json' \
  -d '{"name":"Тестовий клієнт","phone":"+380000000000","email":"client@example.test","password":"demo-only-password"}'
```

Очікується **201** і User із `id`, профілем та `role=client`, без пароля.
Збережіть `id`, якщо адміністратор записуватиме вас сам. Повторна реєстрація
цього email дає **409 EMAIL_IN_USE** — у такому разі перейдіть до входу.

2. Увійдіть:

```sh
curl -i -X POST "$BASE_URL/sessions" -H 'Content-Type: application/json' \
  -d '{"email":"client@example.test","password":"demo-only-password"}'
```

Очікується **200** з `accessToken`, `tokenType=Bearer` і `user`. Невірний
пароль — **401 UNAUTHENTICATED**. Скопіюйте отриманий токен у змінну:

```sh
CLIENT_TOKEN='<accessToken клієнта>'
```

Токен дає доступ до ваших записів; не публікуйте його. Endpoint виходу,
оновлення токена й відновлення пароля відсутній.

## Адміністратор: підготувати каталог і графік

1. Увійдіть через `POST /sessions` із email/паролем, які задали в `create-admin`
   (у запиті попереднього розділу замініть обидва значення).
   Збережіть окремий токен:

```sh
ADMIN_TOKEN='<accessToken адміністратора>'
```

2. Створіть послугу:

```sh
curl -i -X POST "$BASE_URL/services" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"Стрижка","description":"Стрижка волосся","price":500,"durationMinutes":60}'
```

Очікується **201 Service**, `active=true`, `currency=UAH`. Запишіть її `id`:

```sh
SERVICE_ID='<id послуги>'
```

3. Створіть майстра, який виконує цю послугу:

```sh
curl -i -X POST "$BASE_URL/masters" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"name\":\"Олена\",\"serviceIds\":[\"$SERVICE_ID\"]}"
```

Очікується **201 Master**. Запишіть `id`:

```sh
MASTER_ID='<id майстра>'
```

4. Новий майстер має неробочий графік. Для навчального прикладу встановіть
   щодня 09:00–18:00 (реальний графік салону задайте відповідно до потреб):

```sh
curl -i -X PATCH "$BASE_URL/masters/$MASTER_ID/schedule" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"weekly":{
    "monday":{"working":true,"interval":{"start":"09:00","end":"18:00"}},
    "tuesday":{"working":true,"interval":{"start":"09:00","end":"18:00"}},
    "wednesday":{"working":true,"interval":{"start":"09:00","end":"18:00"}},
    "thursday":{"working":true,"interval":{"start":"09:00","end":"18:00"}},
    "friday":{"working":true,"interval":{"start":"09:00","end":"18:00"}},
    "saturday":{"working":true,"interval":{"start":"09:00","end":"18:00"}},
    "sunday":{"working":true,"interval":{"start":"09:00","end":"18:00"}}
  },"exceptions":[]}'
```

Очікується **200 Schedule**. Цей запит замінює весь тиждень та очищує
винятки; не застосовуйте його до чинного графіка без наміру такої заміни.
Невміщення актуальних записів у новий графік дає **409 SCHEDULE_CONFLICT**.
Перевірте збережені дані:

```sh
curl -i "$BASE_URL/masters/$MASTER_ID/schedule" -H "Authorization: Bearer $ADMIN_TOKEN"
```

Щоб задати відпустку, PATCH передає `exceptions` із об'єктами
`{"date":"YYYY-MM-DD","kind":"vacation","day":{"working":false}}`;
весь переданий масив замінює попередній. Повторні дати заборонені.

## Клієнт: каталог і створення запису

1. Каталог доступний без входу:

```sh
curl -i "$BASE_URL/services"
curl -i "$BASE_URL/masters"
```

Очікується **200** з `items`. Якщо масив порожній, каталог ще не налаштований.
У списках видно і неактивні сутності; для нового запису обидві мають бути
active=true, а serviceId має входити в serviceIds майстра.

2. Погодьте час із салоном окремо: API доступних слотів ще немає.
   Для щойно створених тестових сутностей із графіком вище можна взяти
   10:00 через два календарні дні. Команда обчислює дату й offset Kyiv,
   тому не залежить від застарілого прикладу дати:

```sh
STARTS_AT=$(.venv/bin/python -c 'from datetime import datetime,timedelta; from zoneinfo import ZoneInfo; print((datetime.now(ZoneInfo("Europe/Kyiv"))+timedelta(days=2)).replace(hour=10,minute=0,second=0,microsecond=0).isoformat())')
```

3. Створіть власний запис, **без clientId**:

```sh
curl -i -X POST "$BASE_URL/bookings" \
  -H "Authorization: Bearer $CLIENT_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"serviceId\":\"$SERVICE_ID\",\"masterId\":\"$MASTER_ID\",\"startsAt\":\"$STARTS_AT\"}"
```

Очікується **201 Booking** із `status=confirmed`, `category=current`,
`serviceSnapshot` і розрахованим `endsAt` (для прикладу — 11:00).
За конфлікту клієнта/майстра — **409 TIME_UNAVAILABLE**: погодьте інший час.
За межами графіка або менш ніж за 2 години — **422 BOOKING_RULE_VIOLATION**.

```sh
BOOKING_ID='<id створеного запису>'
```

Адміністратор може створити запис аналогічним POST зі своїм токеном і
додатковим `clientId` зареєстрованого клієнта. Йому не застосовується мінімум
2 години; решта перевірок залишається. Пошуку клієнтів за email через API немає.

## Клієнт: перегляд і скасування

1. Перегляньте власні актуальні записи та деталі:

```sh
curl -i "$BASE_URL/bookings?category=current" -H "Authorization: Bearer $CLIENT_TOKEN"
curl -i "$BASE_URL/bookings/$BOOKING_ID" -H "Authorization: Bearer $CLIENT_TOKEN"
```

Очікується **200**; чужий запис дає **403 FORBIDDEN**, невідомий ID — **404**.
Запис залишається актуальним до розрахованого завершення, включно з його початком.

2. Скасуйте не пізніше ніж за 24 години до початку:

```sh
curl -i -X POST "$BASE_URL/bookings/$BOOKING_ID/cancellation" \
  -H "Authorization: Bearer $CLIENT_TOKEN"
```

Очікується **200 Booking**, `status=cancelled`, `category=history`; час
звільнено. За меншого строку — **422 CANCELLATION_TOO_LATE**: зверніться до
адміністратора поза системою. Повторне скасування — **409 HISTORICAL_BOOKING**.

3. Перегляньте історію:

```sh
curl -i "$BASE_URL/bookings?category=history" -H "Authorization: Bearer $CLIENT_TOKEN"
```

Очікується **200**, запис є в `items`. Історія також містить записи, чий
розрахований кінець минув; це не підтверджує фактичного виконання послуги.

## Адміністратор: зміна запису й керування доступністю

Для цього розділу потрібен **інший актуальний** запис: можна повторити
створення після скасування та оновити BOOKING_ID. Історичний запис змінити не можна.

1. Погодьте новий час; у навчальному прикладі — 10:00 через три дні:

```sh
NEW_STARTS_AT=$(.venv/bin/python -c 'from datetime import datetime,timedelta; from zoneinfo import ZoneInfo; print((datetime.now(ZoneInfo("Europe/Kyiv"))+timedelta(days=3)).replace(hour=10,minute=0,second=0,microsecond=0).isoformat())')
curl -i -X PATCH "$BASE_URL/bookings/$BOOKING_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"startsAt\":\"$NEW_STARTS_AT\"}"
```

Очікується **200** з новими startsAt/endsAt; snapshot послуги зберігається.
При конфлікті — **409 BOOKING_CHANGE_CONFLICT**, старий запис не змінюється.
Клієнт із власним токеном не може виконати PATCH (403).
Заміна послуги через `serviceId` оновлює snapshot; пара з майстром має бути сумісною.

2. Адміністратор скасовує актуальний запис тим самим cancellation-запитом
   зі своїм токеном, зокрема коли залишилося менш ніж 24 години.
3. Для заборони нових записів деактивуйте послугу (аналогічно майстра):

```sh
curl -i -X PATCH "$BASE_URL/services/$SERVICE_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"active":false}'
```

Очікується **200**, наявні записи збережені. Фізичний DELETE послуги/майстра
можливий лише без пов'язаних записів: за актуальних — 409, за історичних
поточна реалізація повертає guard D-06 (500). Деактивація не є видаленням.

## Сповіщення й відомі обмеження

Email про створення/зміну/скасування ставиться в чергу, але успішний HTTP
не засвідчує доставки. Оператор запускає SMTP worker за README. Для прикладу
через два дні створюється reminder на 24 години до початку; при скасуванні
він скасовується. Без worker/SMTP листа не буде; failed автоматично не повторюється.

- `GET /masters/{masterId}/slots` повертає 404: вибору вільного часу немає.
- На 29-й/30-й різниці дат, при деяких перенесеннях без попереднього reminder,
  несумісності чи неактивності при PATCH можливий 500 з D-02–D-06.
  Це незавершені правила, а не підтверджений запис; перевірте поточні дані
  через GET і зверніться до адміністратора. Точні умови — в API-довіднику.
- Графік має один робочий інтервал на день; UI, SMS, оплати, reset password,
  самостійне перенесення клієнтом і кабінет майстра відсутні.
