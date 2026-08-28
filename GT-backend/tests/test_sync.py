import uuid
from datetime import UTC, datetime, timedelta

from httpx import AsyncClient


async def _auth_headers(client: AsyncClient, email: str) -> dict[str, str]:
    response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "hunter2hunter2",
            "display_name": "Sync Test",
            "timezone": "Europe/Tallinn",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _user_id(client: AsyncClient, headers: dict[str, str]) -> str:
    response = await client.get("/auth/me", headers=headers)
    user_id: str = response.json()["id"]
    return user_id


def _goal_row(user_id: str, goal_id: str, updated_at: str) -> dict[str, object]:
    return {
        "id": goal_id,
        "user_id": user_id,
        "parent_id": None,
        "title": "Learn Rust",
        "description": None,
        "target_date": None,
        "status": "active",
        "completed_at": None,
        "sort_order": 0,
        "created_at": updated_at,
        "updated_at": updated_at,
        "deleted_at": None,
    }


async def test_push_then_pull_round_trip(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "sync-round-trip@example.com")
    user_id = await _user_id(client, headers)
    goal_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat()
    push_payload = {"goals": [_goal_row(user_id, goal_id, now)]}

    push_response = await client.post("/sync", json=push_payload, headers=headers)
    assert push_response.status_code == 200
    assert push_response.json()["goals"][0]["id"] == goal_id

    pull_response = await client.get("/sync", headers=headers)
    assert pull_response.status_code == 200
    body = pull_response.json()
    assert any(goal["id"] == goal_id for goal in body["goals"])


async def test_push_rejects_row_with_foreign_user_id(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "sync-scope-foreign@example.com")
    other_headers = await _auth_headers(client, "sync-scope-other@example.com")
    other_user_id = await _user_id(client, other_headers)
    now = datetime.now(UTC).isoformat()
    push_payload = {"goals": [_goal_row(other_user_id, str(uuid.uuid4()), now)]}

    response = await client.post("/sync", json=push_payload, headers=headers)

    assert response.status_code == 403


async def test_push_rejects_id_collision_with_another_users_row(client: AsyncClient) -> None:
    owner_headers = await _auth_headers(client, "sync-collision-owner@example.com")
    owner_id = await _user_id(client, owner_headers)
    goal_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat()
    await client.post(
        "/sync", json={"goals": [_goal_row(owner_id, goal_id, now)]}, headers=owner_headers
    )

    attacker_headers = await _auth_headers(client, "sync-collision-attacker@example.com")
    attacker_id = await _user_id(client, attacker_headers)
    later = datetime.now(UTC).isoformat()
    response = await client.post(
        "/sync",
        json={"goals": [_goal_row(attacker_id, goal_id, later)]},
        headers=attacker_headers,
    )

    assert response.status_code == 403


async def test_empty_cursor_returns_everything(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "sync-empty-cursor@example.com")
    user_id = await _user_id(client, headers)
    now = datetime.now(UTC).isoformat()
    goal_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
    await client.post(
        "/sync",
        json={"goals": [_goal_row(user_id, goal_id, now) for goal_id in goal_ids]},
        headers=headers,
    )

    response = await client.get("/sync", headers=headers)

    assert response.status_code == 200
    returned_ids = {goal["id"] for goal in response.json()["goals"]}
    assert set(goal_ids) <= returned_ids


async def test_cursor_returns_only_deltas(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "sync-deltas@example.com")
    user_id = await _user_id(client, headers)
    now = datetime.now(UTC).isoformat()
    first_goal_id = str(uuid.uuid4())
    await client.post(
        "/sync", json={"goals": [_goal_row(user_id, first_goal_id, now)]}, headers=headers
    )

    first_pull = await client.get("/sync", headers=headers)
    cursor = first_pull.json()["cursor"]

    second_goal_id = str(uuid.uuid4())
    later = (datetime.now(UTC) + timedelta(seconds=1)).isoformat()
    await client.post(
        "/sync", json={"goals": [_goal_row(user_id, second_goal_id, later)]}, headers=headers
    )

    delta_pull = await client.get("/sync", params={"cursor": cursor}, headers=headers)

    delta_ids = {goal["id"] for goal in delta_pull.json()["goals"]}
    assert delta_ids == {second_goal_id}


async def test_older_updated_at_does_not_overwrite_newer_row(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "sync-lww@example.com")
    user_id = await _user_id(client, headers)
    goal_id = str(uuid.uuid4())
    newer = datetime.now(UTC).isoformat()
    older = (datetime.now(UTC) - timedelta(hours=1)).isoformat()

    newer_row = _goal_row(user_id, goal_id, newer)
    newer_row["title"] = "Newer title"
    await client.post("/sync", json={"goals": [newer_row]}, headers=headers)

    older_row = _goal_row(user_id, goal_id, older)
    older_row["title"] = "Stale title"
    push_response = await client.post("/sync", json={"goals": [older_row]}, headers=headers)

    assert push_response.json()["goals"][0]["title"] == "Newer title"

    pull_response = await client.get("/sync", headers=headers)
    pulled = next(g for g in pull_response.json()["goals"] if g["id"] == goal_id)
    assert pulled["title"] == "Newer title"


async def test_tombstones_propagate(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "sync-tombstones@example.com")
    user_id = await _user_id(client, headers)
    goal_id = str(uuid.uuid4())
    created = datetime.now(UTC).isoformat()
    await client.post(
        "/sync", json={"goals": [_goal_row(user_id, goal_id, created)]}, headers=headers
    )

    deleted_at = (datetime.now(UTC) + timedelta(seconds=1)).isoformat()
    deleted_row = _goal_row(user_id, goal_id, deleted_at)
    deleted_row["deleted_at"] = deleted_at
    await client.post("/sync", json={"goals": [deleted_row]}, headers=headers)

    pull_response = await client.get("/sync", headers=headers)
    pulled = next(g for g in pull_response.json()["goals"] if g["id"] == goal_id)
    assert pulled["deleted_at"] is not None
