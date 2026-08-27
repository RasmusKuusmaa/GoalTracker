import uuid

from httpx import AsyncClient


async def _auth_headers(client: AsyncClient, email: str) -> dict[str, str]:
    response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "hunter2hunter2",
            "display_name": "Goal Test",
            "timezone": "Europe/Tallinn",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_create_root_goal(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "root@example.com")

    response = await client.post(
        "/goals",
        json={"id": str(uuid.uuid4()), "title": "Run a marathon"},
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["parent_id"] is None


async def test_create_child_goal(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "child@example.com")
    root_id = str(uuid.uuid4())
    await client.post("/goals", json={"id": root_id, "title": "Root"}, headers=headers)

    response = await client.post(
        "/goals",
        json={"id": str(uuid.uuid4()), "title": "Child", "parent_id": root_id},
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["parent_id"] == root_id


async def test_reject_cross_user_parent(client: AsyncClient) -> None:
    owner_headers = await _auth_headers(client, "owner@example.com")
    other_headers = await _auth_headers(client, "other@example.com")
    root_id = str(uuid.uuid4())
    await client.post("/goals", json={"id": root_id, "title": "Root"}, headers=owner_headers)

    response = await client.post(
        "/goals",
        json={"id": str(uuid.uuid4()), "title": "Child", "parent_id": root_id},
        headers=other_headers,
    )

    assert response.status_code == 404


async def test_reject_cycle(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "cycle@example.com")
    root_id = str(uuid.uuid4())
    child_id = str(uuid.uuid4())
    await client.post("/goals", json={"id": root_id, "title": "Root"}, headers=headers)
    await client.post(
        "/goals",
        json={"id": child_id, "title": "Child", "parent_id": root_id},
        headers=headers,
    )

    response = await client.patch(
        f"/goals/{root_id}", json={"parent_id": child_id}, headers=headers
    )

    assert response.status_code == 400


async def test_reject_depth_six(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "depth@example.com")
    parent_id: str | None = None
    for level in range(5):
        goal_id = str(uuid.uuid4())
        payload = {"id": goal_id, "title": f"Level {level}"}
        if parent_id is not None:
            payload["parent_id"] = parent_id
        response = await client.post("/goals", json=payload, headers=headers)
        assert response.status_code == 201
        parent_id = goal_id

    response = await client.post(
        "/goals",
        json={"id": str(uuid.uuid4()), "title": "Level 5", "parent_id": parent_id},
        headers=headers,
    )

    assert response.status_code == 400


async def test_cascade_soft_delete(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "cascade@example.com")
    root_id = str(uuid.uuid4())
    child_id = str(uuid.uuid4())
    grandchild_id = str(uuid.uuid4())
    await client.post("/goals", json={"id": root_id, "title": "Root"}, headers=headers)
    await client.post(
        "/goals",
        json={"id": child_id, "title": "Child", "parent_id": root_id},
        headers=headers,
    )
    await client.post(
        "/goals",
        json={"id": grandchild_id, "title": "Grandchild", "parent_id": child_id},
        headers=headers,
    )

    response = await client.delete(f"/goals/{root_id}", headers=headers)
    assert response.status_code == 204

    listed = await client.get("/goals", headers=headers)
    assert listed.json() == []

    for goal_id in (root_id, child_id, grandchild_id):
        response = await client.get(f"/goals/{goal_id}", headers=headers)
        assert response.status_code == 404
