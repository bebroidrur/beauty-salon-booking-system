# ЛР6 — перевірка комплекту обов'язкових артефактів

Перевірено 2026-11-26 у робочому дереві гілки `lab6`. Артефакти 1–10 згруповано за результатами пунктів 2–13; нормативні SRS/OpenAPI не дублюються і не змінюються.

| № | Обов'язковий артефакт | Файл/каталог | Стан |
| ---: | --- | --- | --- |
| 1 | Coding Convention | `docs/coding-convention.md` | PRESENT |
| 2 | Documentation tags/docstrings | `docs/documentation-tags.md` | PRESENT; окремий матеріал подання |
| 3 | Sphinx configuration and source | `docs/conf.py`, `docs/index.rst`, `docs/python-api.rst` | PRESENT |
| 4 | Generated documentation | `docs/generated/html/`, `docs/generated/singlehtml/` | PRESENT; rebuilt with 0 warnings |
| 5 | API reference | `docs/lab4/resource-model.md`, `docs/lab4/schemas.md`, `docs/lab4/errors.md` | PRESENT; implementation status separated |
| 6 | README and user guide | `README.md`, `docs/user-guide.md` | PRESENT |
| 7 | Documentation verification | `logs/lab6-documentation-verification.md` | PRESENT |
| 8 | Traceability matrix | `docs/lab6/traceability-matrix.md` | PRESENT; 75 requirements |
| 9 | Traceability audit and final verification | `logs/lab6-traceability-audit.md`, `logs/lab6-final-verification.md` | PRESENT |
| 10 | Human validation and FINAL-GATE | `docs/lab6-human-validation.md`, `docs/final-gate.md`, `logs/lab6-sdd-summary.md` | PRESENT; GO scoped / REVISE full SRS recorded |

Окремі матеріали подання: [submission/README.md](../submission/README.md), [documentation tags](../docs/documentation-tags.md), [HTML](../docs/generated/html/index.html), [singlehtml](../docs/generated/singlehtml/index.html) і [source archive](../submission/lab6-source.tar.gz). Архів не містить Git, virtualenv, runtime data, секретів, кешів, залежностей або згенерованої документації.
