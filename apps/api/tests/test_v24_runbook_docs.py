from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _read_doc(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8").lower()


def test_release_runbook_has_required_sections():
    body = _read_doc("docs/ops/release-runbook.md")

    for phrase in [
        "pre-release checks",
        "ci checks",
        "migration",
        "deployment smoke",
        "rollback",
        "acceptable warnings",
        "evidence paths",
    ]:
        assert phrase in body


def test_incident_response_runbook_has_required_sections():
    body = _read_doc("docs/ops/incident-response-runbook.md")

    for phrase in [
        "ci red",
        "api startup failure",
        "auth failure",
        "migration failure",
        "qwenpaw failure",
        "public h5 failure",
        "repo hygiene failure",
    ]:
        assert phrase in body
