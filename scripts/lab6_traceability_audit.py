"""Generate and audit the completed laboratory 6 traceability matrix.

The script intentionally checks links and identifiers only.  It cannot decide
whether a passing test proves every acceptance criterion or whether a human
has accepted an open design decision.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "spec/traceability-matrix.md"
MATRIX = ROOT / "docs/lab6/traceability-matrix.md"


def rows(path: Path) -> list[list[str]]:
    """Read requirement rows from a Markdown matrix."""
    result = []
    for line in path.read_text().splitlines():
        if re.match(r"\| REQ-(?:F|NF)-\d{3} \|", line):
            result.append(
                [cell.strip() for cell in line.strip("|").split("|")]
            )
    return result


def file_references(text: str) -> list[str]:
    """Return local Markdown links and code-path references."""
    refs = re.findall(r"\[[^]]+\]\(([^)]+)\)|`([^`]+)`", text)
    found = [
        a or b
        for a, b in refs
        if (a or b) and not (a or b).startswith(("http:", "https:"))
    ]
    found.extend(
        re.findall(
            r"(?<![\w/])(?:spec|docs|tests|salon|src|scripts)/[\w./-]+", text
        )
    )
    return found


def audit() -> dict[str, object]:
    """Audit identifiers, links, test markers, and documentation anchors."""
    baseline = rows(BASELINE)
    current = rows(MATRIX)
    baseline_ids = [row[0] for row in baseline]
    current_ids = [row[0] for row in current]
    errors: list[str] = []
    if len(current) != len(baseline):
        errors.append(f"row count {len(current)} != baseline {len(baseline)}")
    if set(current_ids) != set(baseline_ids):
        errors.append("matrix IDs differ from baseline")
    duplicates = sorted(
        {rid for rid in current_ids if current_ids.count(rid) > 1}
    )
    errors.extend(f"duplicate requirement ID {rid}" for rid in duplicates)

    incomplete = 0
    not_implemented = 0
    complete = 0
    for row in current:
        if len(row) != 10:
            errors.append(f"{row[0]} has {len(row)} columns, expected 10")
            continue
        rid, source, criterion, ticket, test, code, api, docs, status, note = (
            row
        )
        if any(not cell or cell == "—" for cell in row[1:]):
            errors.append(f"{rid} contains an empty traceability link")
        if status == "IMPLEMENTED":
            complete += 1
        else:
            incomplete += 1
        if status == "NOT IMPLEMENTED":
            not_implemented += 1
        for ref in file_references(" ".join(row[1:])):
            if ref.startswith("#") or "{" in ref or ref.startswith("/tmp"):
                continue
            ref_path = (ROOT / ref.split("#", 1)[0]).resolve()
            if not ref_path.exists():
                errors.append(f"{rid} references missing file {ref}")

    test_files = list((ROOT / "tests").rglob("test_*.py"))
    tests_without_requirements = [
        str(path.relative_to(ROOT))
        for path in test_files
        if "@pytest.mark.req" not in path.read_text()
    ]
    docs_without_components = []
    for path in [ROOT / "README.md", ROOT / "docs/user-guide.md"]:
        text = path.read_text()
        if not any(
            token in text for token in ("/services", "createBooking", "salon")
        ):
            docs_without_components.append(str(path.relative_to(ROOT)))
    errors.extend(
        f"test file has no @pytest.mark.req: {path}"
        for path in tests_without_requirements
    )
    errors.extend(
        f"documentation has no known component reference: {path}"
        for path in docs_without_components
    )
    return {
        "requirements": len(current),
        "complete": complete,
        "incomplete": incomplete,
        "not_implemented": not_implemented,
        "duplicates": duplicates,
        "tests_without_requirements": tests_without_requirements,
        "documentation_without_components": docs_without_components,
        "errors": errors,
    }


if __name__ == "__main__":
    result = audit()
    for key, value in result.items():
        print(f"{key}: {value}")
    raise SystemExit(1 if result["errors"] else 0)
