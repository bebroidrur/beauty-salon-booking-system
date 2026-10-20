# План і порядок змістовних комітів

Первинне доручення вимагало лише плану. Наступне доручення користувача явно дозволило staging і створення трьох комітів після фінального аудиту. Push заборонений. SHA перевіряються через `git log -3 --format="%H %s"`; власний SHA документа не вбудовується в його вміст.

1. `spec: design OpenAPI contract for salon booking` — `spec/openapi.yaml`.
2. `test: validate API contract and exercise Prism mock` — `scripts/check_lab4.py`, `tests/lab4/`, `logs/lab4/`.
3. `docs: document lab4 REST design traceability and API gate` — `docs/lab4/` (усі документи, включно зі сценаріями й цим планом).

Порядок забезпечує окремий перегляд контракту, доказів перевірки й документації. Коміти 2/3 залежать від контракту 1. Не включати /tmp, node_modules, віртуальні середовища або сторонні зміни. Оригінальна матриця не редагується; її розширення міститься у docs/lab4/traceability-matrix.md.
