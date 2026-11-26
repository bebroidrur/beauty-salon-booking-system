# ЛР6 — автоматичний аудит простежуваності

Дата: 2026-11-26. Матриця: [docs/lab6/traceability-matrix.md](../docs/lab6/traceability-matrix.md). Baseline: [spec/traceability-matrix.md](../spec/traceability-matrix.md).

Аудит відтворюється командою:

```sh
.venv/bin/python scripts/lab6_traceability_audit.py
```

| Перевірка | Результат | Статус |
| --- | ---: | --- |
| Кількість актуальних вимог | 75 | PASS |
| Повні зв’язки (`IMPLEMENTED`) | 55 | PASS |
| Неповні зв’язки (`PARTIAL` або `NOT IMPLEMENTED`) | 20 | PASS |
| Нереалізовані вимоги | 9 | PASS |
| Дублікати ID | 0 | PASS |
| Відсутні ID порівняно з baseline | 0 | PASS |
| Порожні зв’язки | 0 | PASS |
| Посилання на неіснуючі файли | 0 | PASS |
| Файли тестів без `@pytest.mark.req` | 0 | PASS |
| Документація без відомого компонента | 0 | PASS |
| Помилки аудиту | 0 | PASS |

Фактичний stdout:

```text
requirements: 75
complete: 55
incomplete: 20
not_implemented: 9
duplicates: []
tests_without_requirements: []
documentation_without_components: []
errors: []
```

[`scripts/lab6_traceability_audit.py`](../scripts/lab6_traceability_audit.py) порівнює ID матриці з baseline, перевіряє дублікати, десять колонок кожного рядка, порожні зв’язки, локальні Markdown/code-посилання, наявність `@pytest.mark.req` у тестових файлах і мінімальну наявність компонентів у README та user guide. Матрицю відтворює [`scripts/lab6_generate_matrix.py`](../scripts/lab6_generate_matrix.py).

Автоматичний аудит не доводить семантичну повноту вимоги, якість assertion, покриття кожного AC/GWT, коректність людського рішення або фактичне приймання нефункціонального порогу. `IMPLEMENTED` у матриці не є FINAL-GATE.

Нереалізовані вимоги залишено в матриці: `REQ-F-004`, `REQ-F-018`, `REQ-NF-003`, `REQ-NF-005`, `REQ-NF-007`–`REQ-NF-011`. Частковими залишено вимоги з відкритими D-02–D-06, addendum або відсутнім benchmark evidence. Базову SRS, OpenAPI та адендуми не змінено.
