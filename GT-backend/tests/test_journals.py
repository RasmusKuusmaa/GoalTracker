import uuid

from httpx import AsyncClient


async def _auth_headers(client: AsyncClient, email: str) -> dict[str, str]:
    response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "hunter2hunter2",
            "display_name": "Journal Test",
            "timezone": "Europe/Tallinn",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _create_journal(
    client: AsyncClient, headers: dict[str, str], **overrides: object
) -> str:
    payload: dict[str, object] = {
        "id": str(uuid.uuid4()),
        "name": "Food Log",
        "kind": "numeric",
        "unit": "kcal",
    }
    payload.update(overrides)
    response = await client.post("/journals", json=payload, headers=headers)
    id_ = response.json()["id"]
    assert isinstance(id_, str)
    return id_


async def test_upsert_twice_creates_one_row(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "journal-upsert-twice@example.com")
    journal_id = await _create_journal(client, headers)
    payload = {
        "id": str(uuid.uuid4()),
        "journal_id": journal_id,
        "local_date": "2026-01-02",
        "value": "2500",
    }

    first = await client.put("/journal-entries", json=payload, headers=headers)
    second = await client.put("/journal-entries", json=payload, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]

    listed = await client.get(
        "/journal-entries",
        params={"journal_id": journal_id, "from": "2026-01-01", "to": "2026-01-31"},
        headers=headers,
    )
    assert len(listed.json()) == 1


async def test_numeric_journal_rejects_missing_value(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "journal-missing-value@example.com")
    journal_id = await _create_journal(client, headers, kind="numeric")
    payload = {
        "id": str(uuid.uuid4()),
        "journal_id": journal_id,
        "local_date": "2026-01-02",
    }

    response = await client.put("/journal-entries", json=payload, headers=headers)

    assert response.status_code == 422


async def test_text_journal_rejects_value(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "journal-text-rejects-value@example.com")
    journal_id = await _create_journal(client, headers, name="Notes", kind="text", unit=None)
    payload = {
        "id": str(uuid.uuid4()),
        "journal_id": journal_id,
        "local_date": "2026-01-02",
        "body": "wrote something",
        "value": "5",
    }

    response = await client.put("/journal-entries", json=payload, headers=headers)

    assert response.status_code == 422


async def test_cross_user_journal_rejected(client: AsyncClient) -> None:
    owner_headers = await _auth_headers(client, "journal-owner@example.com")
    journal_id = await _create_journal(client, owner_headers)
    other_headers = await _auth_headers(client, "journal-other@example.com")
    payload = {
        "id": str(uuid.uuid4()),
        "journal_id": journal_id,
        "local_date": "2026-01-02",
        "value": "2500",
    }

    response = await client.put("/journal-entries", json=payload, headers=other_headers)

    assert response.status_code == 404
