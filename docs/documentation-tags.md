# Формат документації коду — ЛР6

Використано PEP 257 і Google-style секції всередині Python docstrings.
PEP 257 визначає структуру docstring, але не наказує формат `Args:`;
цей формат є домовленістю проєкту. Docstrings англійською узгоджуються з
наявними модульними описами; навчальні документи залишаються українською.
На наступному етапі ЛР6 налаштовано Sphinx autodoc + Napoleon для цього формату;
MyST включає наявні Markdown-інструкції. Конфігурація — `docs/conf.py`,
команди й результат — у [журналі генерації](../logs/lab6-documentation.md).

Перший рядок — коротка дія/призначення із крапкою. Розгорнутий опис
відокремлено порожнім рядком; використовуються потрійні подвійні лапки.
Короткі очевидні функції можуть мати однорядковий docstring.

| Поле | Фактичне застосування |
| --- | --- |
| `Args:` | Ім'я параметра точно із сигнатури та його зміст/тип/передумова. `self` не дублюється. |
| `Returns:` | Значення, яке повертає функція; не HTTP-відповідь, якщо це внутрішній метод. |
| `Yields:` | Значення генератора: `Store.transaction`, `exact_multiple`. |
| `Raises:` | Істотний виняток та умова. Не перелік усіх теоретичних помилок Python. |
| `Notes:` | Межі відповідальності, транзакції, непогоджені D-рішення, побічні ефекти. |

Для простих функцій параметри й результат допустимо описати звичайним
реченням. `None` часто пояснено в `Notes:`; `Raises:` не потрібен, якщо немає
суттєвого спеціального винятку. Теги `@param`, `@return`, `:param:` не
використовуються. `req`/`bdd` у тестах — pytest markers, а не docstring-поля;
`x-requirement-ids` в OpenAPI — окрема контрактна простежуваність.

## Реальні приклади

[`salon/contract.py`, `validate`](../salon/contract.py):

```python
"""Validate a JSON value using the resolved OpenAPI 3.0 schema.

Args:
    schema: Contract schema, possibly containing local references.
    value: Decoded JSON value to check.

Raises:
    ValidationError: If value violates the schema or a checked format.

Notes:
    Returns None on success. Decimal multipleOf uses exact rational arithmetic.
"""
```

[`salon/store.py`, `Store.transaction`](../salon/store.py):

```python
"""Open a connection and commit or roll back a serialized transaction.

Yields:
    sqlite3.Connection: Connection with sqlite3.Row results and foreign keys on.

Raises:
    BaseException: Re-raises failures from the transaction body after rollback.
    sqlite3.Error: If opening, locking, committing or rolling back fails.

Notes:
    Uses a 15-second lock timeout and closes the connection after the body.
"""
```

Однорядковий приклад із [`salon/service.py`](../salon/service.py):

```python
def ident():
    """Return a new UUID4 hexadecimal string for an opaque resource ID."""
    return uuid.uuid4().hex
```

Розгорнуті `Args:`/`Returns:` — у `create_app`, `Bookings.execute`,
`build_message`; `Yields: ValidationError` у `exact_multiple` означає
передавання об'єкта помилки валідатору, а не `raise` з цієї функції.
`run_once` описує поглинання винятків транспорту та можливий дубль доставки
після збою; `instant` — важливу передумову явного часового offset.

Перевірки D у Ruff контролюють наявність і частину структури, але правильність
змісту перевірено читанням реалізації та наявними тестами. Docstrings не
змінюють статус адендумів і не є новими вимогами.
