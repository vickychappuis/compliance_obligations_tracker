from __future__ import annotations

from datetime import date, timedelta

from fastapi.testclient import TestClient

RAW_TAX_ID = "123456789"
MASKED_TAX_ID = "••••6789"


def _payload(**overrides) -> dict:
    body = {
        "type": "annual_report",
        "title": "Annual report",
        "description": "File it.",
        "due_date": (date.today() + timedelta(days=10)).isoformat(),
        "owner": "Jane Founder",
        "requires_document": False,
        "company_tax_id": RAW_TAX_ID,
    }
    body.update(overrides)
    return body


def test_create_masks_tax_id_and_starts_pending(client: TestClient) -> None:
    res = client.post("/obligations", json=_payload())
    assert res.status_code == 201
    body = res.json()
    assert body["status"] == "pending"
    assert body["version"] == 1
    assert body["company_tax_id"] == MASKED_TAX_ID
    assert RAW_TAX_ID not in res.text
    assert body["allowed_transitions"] == ["in_progress"]
    assert len(body["audit"]) == 1


def test_full_lifecycle_with_document_gate_and_concurrency(client: TestClient) -> None:
    created = client.post("/obligations", json=_payload(requires_document=True)).json()
    oid = created["id"]
    assert created["can_submit"] is False

    bad = client.post(
        f"/obligations/{oid}/transition",
        json={"target_status": "done", "expected_version": 1},
    )
    assert bad.status_code == 409
    assert bad.json()["error"]["type"] == "InvalidTransition"

    moved = client.post(
        f"/obligations/{oid}/transition",
        json={"target_status": "in_progress", "expected_version": 1},
    )
    assert moved.status_code == 200
    assert moved.json()["version"] == 2

    gated = client.post(
        f"/obligations/{oid}/transition",
        json={"target_status": "submitted", "expected_version": 2},
    )
    assert gated.status_code == 422
    assert gated.json()["error"]["type"] == "DocumentRequired"

    attached = client.post(
        f"/obligations/{oid}/document",
        files={"file": ("filing.pdf", b"%PDF-1.7 data", "application/pdf")},
    )
    assert attached.status_code == 200
    body = attached.json()
    assert body["has_document"] is True
    assert body["can_submit"] is True
    assert body["documents"][0]["filename"] == "filing.pdf"
    assert body["documents"][0]["size"] == len(b"%PDF-1.7 data")

    document_id = body["documents"][0]["id"]
    url_res = client.get(f"/obligations/{oid}/documents/{document_id}/url")
    assert url_res.status_code == 200
    assert url_res.json()["url"].startswith("https://signed.example/")

    submitted = client.post(
        f"/obligations/{oid}/transition",
        json={"target_status": "submitted", "expected_version": 2},
    )
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "submitted"

    stale = client.post(
        f"/obligations/{oid}/transition",
        json={"target_status": "done", "expected_version": 2},
    )
    assert stale.status_code == 409
    assert stale.json()["error"]["type"] == "VersionConflict"


def test_attach_then_remove_document(client: TestClient) -> None:
    oid = client.post("/obligations", json=_payload(requires_document=True)).json()[
        "id"
    ]
    attached = client.post(
        f"/obligations/{oid}/document",
        files={"file": ("filing.pdf", b"%PDF-1.7 data", "application/pdf")},
    ).json()
    document_id = attached["documents"][0]["id"]

    removed = client.delete(f"/obligations/{oid}/documents/{document_id}")
    assert removed.status_code == 200
    body = removed.json()
    assert body["documents"] == []
    assert body["has_document"] is False


def test_attach_unsupported_type_returns_422(client: TestClient) -> None:
    oid = client.post("/obligations", json=_payload(requires_document=True)).json()[
        "id"
    ]
    res = client.post(
        f"/obligations/{oid}/document",
        files={"file": ("evil.exe", b"MZ payload", "application/x-msdownload")},
    )
    assert res.status_code == 422
    assert res.json()["error"]["type"] == "InvalidDocument"


def test_attach_empty_file_returns_422(client: TestClient) -> None:
    oid = client.post("/obligations", json=_payload(requires_document=True)).json()[
        "id"
    ]
    res = client.post(
        f"/obligations/{oid}/document",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert res.status_code == 422
    assert res.json()["error"]["type"] == "InvalidDocument"


def test_attach_image_is_accepted_via_wildcard(client: TestClient) -> None:
    oid = client.post("/obligations", json=_payload(requires_document=True)).json()[
        "id"
    ]
    res = client.post(
        f"/obligations/{oid}/document",
        files={"file": ("scan.png", b"\x89PNG\r\n\x1a\n", "image/png")},
    )
    assert res.status_code == 200
    assert res.json()["documents"][0]["filename"] == "scan.png"


def test_remove_missing_document_returns_404(client: TestClient) -> None:
    oid = client.post("/obligations", json=_payload()).json()["id"]
    res = client.delete(f"/obligations/{oid}/documents/nope")
    assert res.status_code == 404
    assert res.json()["error"]["type"] == "NotFound"


def test_get_missing_returns_404(client: TestClient) -> None:
    res = client.get("/obligations/nope")
    assert res.status_code == 404
    assert res.json()["error"]["type"] == "NotFound"


def test_list_filters_and_sorting(client: TestClient) -> None:
    client.post(
        "/obligations",
        json=_payload(
            owner="A", due_date=(date.today() + timedelta(days=20)).isoformat()
        ),
    )
    client.post(
        "/obligations",
        json=_payload(
            owner="B", due_date=(date.today() + timedelta(days=5)).isoformat()
        ),
    )

    res = client.get("/obligations")
    assert res.status_code == 200
    items = res.json()
    assert [i["due_date"] for i in items] == sorted(i["due_date"] for i in items)
    assert RAW_TAX_ID not in res.text

    res_a = client.get("/obligations", params={"owner": "A"})
    assert {i["owner"] for i in res_a.json()} == {"A"}


def test_summary_endpoint(client: TestClient) -> None:
    client.post(
        "/obligations",
        json=_payload(due_date=(date.today() - timedelta(days=1)).isoformat()),
    )
    client.post(
        "/obligations",
        json=_payload(due_date=(date.today() + timedelta(days=10)).isoformat()),
    )

    res = client.get("/obligations/summary")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 2
    assert body["overdue"] == 1
    assert body["upcoming"] == 1
    assert body["by_status"]["pending"] == 2
