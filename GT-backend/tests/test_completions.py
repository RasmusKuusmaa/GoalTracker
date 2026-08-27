import uuid

from httpx import AsyncClient


async def _auth_headers(client: AsyncClient, email: str) -> dict[str, str]:
    response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "hunter2hunter2",
            "display_name": "Completion Test",
            "timezone": "Europe/Tallinn",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _create_commitment(
    client: AsyncClient, headers: dict[str, str], **overrides: object
) -> str:
    payload: dict[str, object] = {
        "id": str(uuid.uuid4()),
        "title": "Gym",
        "type": "binary",
        "cadence": "daily",
        "active_from": "2026-01-01",
    }
    payload.update(overrides)
    response = await client.post("/commitments", json=payload, headers=headers)
    id_ = response.json()["id"]
    assert isinstance(id_, str)
    return id_


async def test_upsert_twice_creates_one_row(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "upsert-twice@example.com")
    commitment_id = await _create_commitment(client, headers)
    payload = {
        "id": str(uuid.uuid4()),
        "commitment_id": commitment_id,
        "local_date": "2026-01-02",
        "status": "done",
    }

    first = await client.put("/completions", json=payload, headers=headers)
    second = await client.put("/completions", json=payload, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]

    listed = await client.get(
        "/completions",
        params={"from": "2026-01-01", "to": "2026-01-31"},
        headers=headers,
    )
    assert len(listed.json()) == 1


async def test_untick_then_retick_reuses_the_pair(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "untick-retick@example.com")
    commitment_id = await _create_commitment(client, headers)
    payload = {
        "id": str(uuid.uuid4()),
        "commitment_id": commitment_id,
        "local_date": "2026-01-02",
        "status": "done",
    }

    created = await client.put("/completions", json=payload, headers=headers)
    completion_id = created.json()["id"]

    deleted = await client.delete(f"/completions/{completion_id}", headers=headers)
    assert deleted.status_code == 204

    after_delete = await client.get(
        "/completions",
        params={"from": "2026-01-01", "to": "2026-01-31"},
        headers=headers,
    )
    assert after_delete.json() == []

    retick = await client.put("/completions", json=payload, headers=headers)
    assert retick.status_code == 200
    assert retick.json()["id"] == completion_id

    after_retick = await client.get(
        "/completions",
        params={"from": "2026-01-01", "to": "2026-01-31"},
        headers=headers,
    )
    assert len(after_retick.json()) == 1


async def test_wrong_value_type_rejected_for_binary(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "wrong-value-binary@example.com")
    commitment_id = await _create_commitment(client, headers)
    payload = {
        "id": str(uuid.uuid4()),
        "commitment_id": commitment_id,
        "local_date": "2026-01-02",
        "status": "done",
        "value": "5",
    }

    response = await client.put("/completions", json=payload, headers=headers)

    assert response.status_code == 422


async def test_wrong_value_type_rejected_for_numeric(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "wrong-value-numeric@example.com")
    commitment_id = await _create_commitment(
        client,
        headers,
        type="numeric",
        target_value="2600",
        comparator="lte",
    )
    payload = {
        "id": str(uuid.uuid4()),
        "commitment_id": commitment_id,
        "local_date": "2026-01-02",
        "status": "done",
    }

    response = await client.put("/completions", json=payload, headers=headers)

    assert response.status_code == 422
