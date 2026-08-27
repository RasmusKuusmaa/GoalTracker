import uuid

from httpx import AsyncClient


async def _auth_headers(client: AsyncClient, email: str) -> dict[str, str]:
    response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "hunter2hunter2",
            "display_name": "Commitment Test",
            "timezone": "Europe/Tallinn",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _binary_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": str(uuid.uuid4()),
        "title": "Gym",
        "type": "binary",
        "cadence": "daily",
        "active_from": "2026-01-01",
    }
    payload.update(overrides)
    return payload


async def test_create_commitment(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "create@example.com")

    response = await client.post("/commitments", json=_binary_payload(), headers=headers)

    assert response.status_code == 201
    assert response.json()["title"] == "Gym"
    assert response.json()["archived_at"] is None


async def test_create_commitment_rejects_cross_user_goal(client: AsyncClient) -> None:
    owner_headers = await _auth_headers(client, "goal-owner@example.com")
    other_headers = await _auth_headers(client, "goal-other@example.com")
    goal_id = str(uuid.uuid4())
    await client.post("/goals", json={"id": goal_id, "title": "Root"}, headers=owner_headers)

    response = await client.post(
        "/commitments",
        json=_binary_payload(goal_id=goal_id),
        headers=other_headers,
    )

    assert response.status_code == 404


async def test_list_commitments_scoped_to_user(client: AsyncClient) -> None:
    owner_headers = await _auth_headers(client, "list-owner@example.com")
    other_headers = await _auth_headers(client, "list-other@example.com")
    await client.post("/commitments", json=_binary_payload(), headers=owner_headers)
    await client.post("/commitments", json=_binary_payload(), headers=other_headers)

    response = await client.get("/commitments", headers=owner_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_active_only_excludes_archived(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "active-only@example.com")
    created = await client.post("/commitments", json=_binary_payload(), headers=headers)
    commitment_id = created.json()["id"]
    await client.post(f"/commitments/{commitment_id}/archive", headers=headers)

    all_response = await client.get("/commitments", headers=headers)
    active_response = await client.get("/commitments?active_only=true", headers=headers)

    assert len(all_response.json()) == 1
    assert len(active_response.json()) == 0


async def test_archive_sets_archived_at(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "archive@example.com")
    created = await client.post("/commitments", json=_binary_payload(), headers=headers)
    commitment_id = created.json()["id"]

    response = await client.post(f"/commitments/{commitment_id}/archive", headers=headers)

    assert response.status_code == 200
    assert response.json()["archived_at"] is not None


async def test_patch_rejects_cross_user_commitment(client: AsyncClient) -> None:
    owner_headers = await _auth_headers(client, "patch-owner@example.com")
    other_headers = await _auth_headers(client, "patch-other@example.com")
    created = await client.post("/commitments", json=_binary_payload(), headers=owner_headers)
    commitment_id = created.json()["id"]

    response = await client.patch(
        f"/commitments/{commitment_id}", json={"title": "Hijacked"}, headers=other_headers
    )

    assert response.status_code == 404


async def test_soft_delete_removes_from_list(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "delete@example.com")
    created = await client.post("/commitments", json=_binary_payload(), headers=headers)
    commitment_id = created.json()["id"]

    response = await client.delete(f"/commitments/{commitment_id}", headers=headers)
    assert response.status_code == 204

    listed = await client.get("/commitments", headers=headers)
    assert listed.json() == []
