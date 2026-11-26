"""Build the Lab 6 matrix from the baseline and Lab 4 mapping."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse(path: str) -> list[list[str]]:
    """Read requirement rows from a Markdown matrix."""
    result = []
    for line in (ROOT / path).read_text().splitlines():
        if re.match(r"\| REQ-(?:F|NF)-\d{3} \|", line):
            result.append(
                [cell.strip() for cell in line.strip("|").split("|")]
            )
    return result


baseline = parse("spec/traceability-matrix.md")
lab4 = {row[0]: row for row in parse("docs/lab4/traceability-matrix.md")}
tests: dict[str, set[str]] = {}
for path in (ROOT / "tests").rglob("test_*.py"):
    for marker in re.findall(
        r"@pytest\.mark\.req\(([^)]*)\)", path.read_text()
    ):
        for requirement in re.findall(r"REQ-[FN]-\d{3}", marker):
            tests.setdefault(requirement, set()).add(
                str(path.relative_to(ROOT))
            )

not_implemented = {
    "REQ-F-004",
    "REQ-F-018",
    "REQ-NF-003",
    "REQ-NF-005",
    "REQ-NF-007",
    "REQ-NF-008",
    "REQ-NF-009",
    "REQ-NF-010",
    "REQ-NF-011",
}
partial = {
    "REQ-F-021",
    "REQ-F-040",
    "REQ-F-043",
    "REQ-F-053",
    "REQ-F-054",
    "REQ-F-055",
    "REQ-F-059",
    "REQ-F-060",
    "REQ-F-063",
    "REQ-F-064",
    "REQ-NF-001",
}


def status(requirement: str) -> str:
    """Return the evidence status assigned to a requirement."""
    return (
        "NOT IMPLEMENTED"
        if requirement in not_implemented
        else "PARTIAL"
        if requirement in partial
        else "IMPLEMENTED"
    )


def code(requirement: str) -> str:
    """Return the implementation module or an explicit N/A explanation."""
    number = int(requirement[-3:])
    if requirement.startswith("REQ-NF-"):
        return {
            "REQ-NF-002": "salon/store.py",
            "REQ-NF-004": "salon/auth.py",
            "REQ-NF-006": "salon/events.py, salon/mail_worker.py",
        }.get(requirement, "N/A — UI/deployment or benchmark outside Lab 5")
    if number <= 3 or number in (5, 6, 7, 10, 45, 46, 47, 48, 49):
        return "salon/service.py, salon/auth.py"
    if number == 4:
        return "N/A — listSlots is not implemented"
    if number >= 56:
        return "salon/notifications.py, salon/mail_worker.py"
    return "salon/booking_service.py"


def note(requirement: str, state: str) -> str:
    """Return the scope and limitation note for a requirement."""
    if requirement == "REQ-F-004":
        return "Контракт listSlots є, але runtime повертає 404; D-03 BLOCKED."
    if requirement == "REQ-F-018":
        return "Крок початку перевіряється лише через booking rules; окремого listSlots немає."
    if requirement.startswith("REQ-NF-") and state == "NOT IMPLEMENTED":
        return "UI/deployment/availability evidence відсутні в Lab 5; passing API tests цього не доводять."
    if requirement == "REQ-NF-001":
        return "Відповідь не вимірювалась benchmark-тестом."
    if state == "PARTIAL":
        return "Є реалізація й тести, але залишаються відкриті D-02–D-06 або межі addendum; потрібне людське рішення."
    return "Поведінкова або контрактна перевірка є в Lab 5; це не повне приймання всіх AC/GWT."


lines = [
    "# ЛР6 — завершена матриця простежуваності",
    "",
    "Базові ідентифікатори та тексти взято без змін із [baseline](../../spec/traceability-matrix.md), SRS, AC/GWT, затверджених адендумів і ЛР3 issue mapping. Матриця описує фактичний обсяг ЛР5: п’ять Bookings operationId та супровідний каталог/auth/schedule/outbox. Статус `IMPLEMENTED` означає наявність коду й пов’язаних тестів; `PARTIAL` зберігає відкриті design decisions; `NOT IMPLEMENTED` не приховує вимогу.",
    "",
    "| ID вимоги | Джерело | Критерій прийняття | ID тікета | Тест | Модуль коду | Елемент інтерфейсу або API | Розділ документації | Статус | Примітка |",
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
]
for row in baseline:
    requirement, _name, ac, gwt, *_ = row
    criterion = (
        f"AC: {ac}; GWT: {gwt}"
        if ac != "—" and gwt != "—"
        else f"AC: {ac}"
        if ac != "—"
        else f"GWT: {gwt}"
        if gwt != "—"
        else "N/A — у baseline немає прямого AC/GWT"
    )
    old = lab4.get(requirement, [""] * 9)
    ticket = (
        old[5]
        if len(old) > 5 and old[5] not in ("", "—")
        else "N/A — ticket mapping відсутній у baseline"
    )
    test = (
        ", ".join(sorted(tests.get(requirement, set())))
        if requirement in tests
        else "N/A — пов’язаного pytest marker немає"
    )
    state = status(requirement)
    api = (
        old[7]
        if len(old) > 7 and old[7] not in ("", "—")
        else "N/A — no direct REST operation"
    )
    source = (
        "spec/functional-requirements.md"
        if requirement.startswith("REQ-F-")
        else "spec/non-functional-requirements.md"
    )
    values = [
        requirement,
        source,
        criterion,
        ticket,
        test,
        code(requirement),
        api,
        "docs/lab4/resource-model.md; docs/lab5/traceability.md; docs/user-guide.md",
        state,
        note(requirement, state),
    ]
    lines.append("| " + " | ".join(values) + " |")
(ROOT / "docs/lab6/traceability-matrix.md").write_text("\n".join(lines) + "\n")
print(f"generated {len(baseline)} rows")
